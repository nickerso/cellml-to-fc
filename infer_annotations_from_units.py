import sys
from pathlib import Path
import libcellml
from libcellml_python_utils import cellml
from rdflib import URIRef, RDF, OWL, RDFS, Literal
from rdflib.namespace import DCTERMS
from omex_metadata import OmexMetadata
import logging
import re
import argparse


def _create_units(name, args, args2=None):
    u = libcellml.Units()
    u.setName(name)
    u.addUnit(*args)
    if args2:
        u.addUnit(*args2)
    m = libcellml.Model()
    m.addUnits(u)
    return u


COMPARTMENT_MAP = {
    # proximal tubule (part of nephron)
    'pt': URIRef('https://identifiers.org/UBERON:0004134'),
    # ascending aorta
    'aa': URIRef('https://identifiers.org/UBERON:0001496'),
    # arterial system
    'ac': URIRef('https://identifiers.org/UBERON:0004572'),
    # venous system
    'vc': URIRef('https://identifiers.org/UBERON:0004582'),
    # renal glomerulus
    'gl': URIRef('https://identifiers.org/UBERON:0000074'),
    # digestive tract (note that FMA gastrointestinal tract includes liver)
    'gi': URIRef('https://identifiers.org/UBERON:0001555'),
    # epithelial cells of the proximal tubule? (proximal tubular epithelium)
    'ptEpi': URIRef('https://identifiers.org/UBERON:0008404'),
    # digestive tract epithelium
    'giEpi': URIRef('https://identifiers.org/UBERON:0003929'),
}

SPECIES_MAP = {
    'Na': URIRef('https://identifiers.org/CHEBI:29101'),  # sodium(1+)
    'W': URIRef('https://identifiers.org/CHEBI:15377'),  # Water
}


class InferTypeFromUnits:
    """
    Class to infer semantic types of model variables based on their units.
    """

    def __init__(self, logger):
        """
        Initialize the inference engine.
        """
        self.__quantities = {
            'solid_mechanics': ['metre'],
            'fluid_mechanics': ['metre', 1, 3.0],
            'electromagnetic': ['coulomb'],
            'chemical': ['mole']
        }
        self.__energy_units = _create_units('energy', ['joule'])
        self.__time_units = _create_units('time', ['second'])
        self.__quantities_units = {k: _create_units(f'{k}_quantity_units', v)
                                   for k, v in self.__quantities.items()}
        self.__quantities_flow_units = {
            f'{k}_flow': _create_units(f'{k}_flow_units', v,
                                       ['second', 1, -1.0])
            for k, v in self.__quantities.items()
        }
        self.__quantities_potential_units = {
            f'{k}_potential': _create_units(f'{k}_potential_units', ['joule'],
                                            [v[0], 1, v[2] * -1.0 if len(v) > 1 else -1.0])
            for k, v in self.__quantities.items()
        }
        self.__all_types = (
                self.__quantities_units |
                self.__quantities_flow_units |
                self.__quantities_potential_units
        )
        self._logger = logger

    def infer_type_from_units(self, model, variable):
        var_units_name = variable.units().name()
        var_units = model.units(var_units_name)
        # we know we have a valid model, so if there are no units we have a standard unit
        # create a standard unit Units for convenience with libcellml.Units.compatible()
        if var_units is None:
            var_units = _create_units('', [var_units_name])
        if libcellml.Units.compatible(var_units, self.__energy_units):
            return self.__energy_units.name()
        if libcellml.Units.compatible(var_units, self.__time_units):
            return self.__time_units.name()
        for k, u in self.__all_types.items():
            if libcellml.Units.compatible(var_units, u):
                return u.name()
        return None

    @staticmethod
    def make_local_uri(om, base_id):
        counter = 1
        while om.has_triple(om.local_ns[f'{base_id}--s{counter}']):
            counter += 1
        return om.local_ns[f'{base_id}--s{counter}']

    def define_amount_node(self, om, variable, amount_type):
        variable_name = variable.name()
        # q_{compartment}_{species}
        pattern = r"^q_(?P<compartment>[^_]+)_(?P<species>.+)$"
        match = re.match(pattern, variable_name)
        if match:
            compartment = match.group("compartment")
            species = match.group("species")
            self._logger.info(f"Compartment: {compartment}, Species: {species}")
            c = COMPARTMENT_MAP.get(compartment)
            s = SPECIES_MAP.get(species)
            if c and s:
                amount_label = f'{amount_type}-amount-{species}-{compartment}'
                local_node = om.local_ns[amount_label]
                if om.has_triple(local_node):
                    self._logger.info(f'Found an existing node for the {amount_type} amount: {amount_label}')
                else:
                    self._logger.info(f'Making a new local node for the {amount_type} amount: {amount_label}')
                    om.add_triple(local_node, om.BQBIOL_NS['is'], s)
                    om.add_triple(local_node, om.BQBIOL_NS['isPartOf'], c)
                return local_node
        self._logger.info(f'Unable to map variable {variable_name} to a known compartment and species')
        return None

    def annotate_variable(self, om, variable, variable_type):
        variable_uri = om.archive_ns[f'{om.get_annotation_source()}#{variable.id()}']
        if variable_type == 'chemical_quantity_units':
            om.annotate_molar_amount(variable_uri)
            # can we determine what we need from the variable name?
            o = self.define_amount_node(om, variable, 'molar')
            if o:
                if om.has_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o):
                    self._logger.info(f'Chemical quantity annotation exists for variable {variable_uri}')
                else:
                    om.add_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o)
        elif variable_type == 'fluid_mechanics_quantity_units':
            om.annotate_volume_amount(variable_uri)
            # can we determine what we need from the variable name?
            o = self.define_amount_node(om, variable, 'liquid')
            if o:
                if om.has_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o):
                    self._logger.info(f'Fluid mechanics quantity annotation exists for variable {variable_uri}')
                else:
                    om.add_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o)


#
# <http://omex-library.org/physical_process.omex/model.cellml#molar_amount_Na>
#     bqbiol:isPropertyOf local:local-entity-0 ;
#     bqbiol:isVersionOf <https://identifiers.org/opb:OPB_00425> .
#
# local:local-entity-0
#     bqbiol:is <https://identifiers.org/CHEBI:17234> ;
#     bqbiol:isPartOf <https://identifiers.org/FMA:18228> .


def main():
    parser = argparse.ArgumentParser(description="Infer annotations for CellML variables"
                                                 " based on names and units.")
    parser.add_argument("input_file", help='Path to the input CellML file')
    parser.add_argument('-a', '--annotations', type=Path, required=True,
                        help='Path to a file containing existing annotations, if any, and updated with new annotations.')
    parser.add_argument('-o', '--omex-name', required=True,
                        help='Name of the OMEX Archive file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output.')

    args = parser.parse_args()

    # Setup custom logger (optional)
    logger = logging.getLogger("infer_units_annotations")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    if args.verbose:
        logger.setLevel(logging.INFO)
    else:
        # only log errors and warnings?
        logger.setLevel(logging.WARNING)

    input_file = Path(args.input_file)
    if not input_file.is_file():
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    model = cellml.parse_model(input_file, False)
    if cellml.validate_model(model) > 0:
        exit(-1)

    units_inference = InferTypeFromUnits(logger)

    omex_metadata = OmexMetadata(args.omex_name, args.annotations, logger)
    omex_metadata.set_annotation_source(input_file.name)

    for i in range(model.componentCount()):
        comp = model.component(i)
        for j in range(comp.variableCount()):
            var = comp.variable(j)
            t = units_inference.infer_type_from_units(model, var)
            if t:
                logger.info(f'{var.name()} ({var.id()}) is of type: {t}')
                units_inference.annotate_variable(omex_metadata, var, t)
    omex_metadata.save(overwrite=True)


if __name__ == "__main__":
    main()
