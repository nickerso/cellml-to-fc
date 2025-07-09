import sys
from pathlib import Path
import libcellml
from libcellml_python_utils import cellml
from rdflib import URIRef, RDF, OWL, RDFS, Literal
from rdflib.namespace import DCTERMS
from omex_metadata import OmexMetadata
import logging
import re


def _create_units(name, args, args2=None):
    u = libcellml.Units()
    u.setName(name)
    u.addUnit(*args)
    if args2:
        u.addUnit(*args2)
    m = libcellml.Model()
    m.addUnits(u)
    return u


class InferTypeFromUnits:
    """
    Class to infer semantic types of model variables based on their units.
    """

    def __init__(self):
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


def make_local_uri(om, base_id):
    counter = 1
    while om.has_triple(om.local_ns[f'{base_id}--s{counter}']):
        counter += 1
    return om.local_ns[f'{base_id}--s{counter}']


COMPARTMENT_MAP = {
    'pt': URIRef('http://purl.obolibrary.org/obo/UBERON_0004134')
}
SPECIES_MAP = {
    'Na': URIRef('https://identifiers.org/CHEBI:29101')
}

def define_molar_amount_class(om, variable):
    molar_amount = URIRef('https://identifiers.org/opb:OPB_00425')
    variable_name = variable.name()
    # q_{compartment}_{species}
    pattern = r"^q_(?P<compartment>[^_]+)_(?P<species>.+)$"
    match = re.match(pattern, variable_name)
    if match:
        compartment = match.group("compartment")
        species = match.group("species")
        print(f"Compartment: {compartment}, Species: {species}")
        c = COMPARTMENT_MAP.get(compartment)
        s = SPECIES_MAP.get(species)
        if c and s:
            custom_class = om.local_ns[f'molar-amount-{species}-{compartment}']
            if not om.has_triple(custom_class):
                om.add_triple(custom_class, RDF.type, OWL.Class)
                om.add_triple(custom_class, RDFS.label, Literal(f"Molar amount of {species} in compartment {compartment}"))
                om.add_triple(custom_class, om.BQBIOL_NS['isVersionOf'], molar_amount)
                om.add_triple(custom_class, om.BQBIOL_NS['is'], s)
                om.add_triple(custom_class, om.BQBIOL_NS['isPartOf'], c)
            return custom_class
    return None


def annotate_variable(om, variable, variable_type):
    variable_uri = URIRef(f'{om.OMEX_LIBRARY_URL}{om.get_annotation_source()}#{variable.id()}')
    if variable_type == 'chemical_quantity_units':
        # can we determine what we need from the variable name?
        o = define_molar_amount_class(om, variable)
        if o:
            om.add_triple(variable_uri, RDF.type, o)

#
# <http://omex-library.org/physical_process.omex/model.cellml#molar_amount_Na>
#     bqbiol:isPropertyOf local:local-entity-0 ;
#     bqbiol:isVersionOf <https://identifiers.org/opb:OPB_00425> .
#
# local:local-entity-0
#     bqbiol:is <https://identifiers.org/CHEBI:17234> ;
#     bqbiol:isPartOf <https://identifiers.org/FMA:18228> .


def main():
    input_file = Path(sys.argv[1])
    model = cellml.parse_model(input_file, False)
    if cellml.validate_model(model) > 0:
        exit(-1)

    units_inference = InferTypeFromUnits()

    # Setup custom logger (optional)
    logger = logging.getLogger("infer_units_annotations")
    logger.setLevel(logging.INFO)

    omex_metadata = OmexMetadata(f'aps-demo-model.omex', f'{input_file.name}.ttl')
    omex_metadata.set_annotation_source(input_file.name)

    for i in range(model.componentCount()):
        comp = model.component(i)
        for j in range(comp.variableCount()):
            var = comp.variable(j)
            t = units_inference.infer_type_from_units(model, var)
            if t:
                print(f'{var.name()} ({var.id()}) is of type: {t}')
                annotate_variable(omex_metadata, var, t)
    omex_metadata.save(overwrite=True)


if __name__ == "__main__":
    main()
