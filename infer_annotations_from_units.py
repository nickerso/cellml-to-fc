import sys
from pathlib import Path
import libcellml
from libcellml_python_utils import cellml
from rdflib import Graph, Literal, RDF, URIRef, Namespace, BNode
from rdflib.namespace import DCTERMS

__OMEX_LIBRARY_URL = 'http://omex-library.org/'
OMEX = Namespace(__OMEX_LIBRARY_URL)
BQBIOL = Namespace('http://biomodels.net/biology-qualifiers/')
STD_TERM_URI = {
    'molar_amount': URIRef('https://identifiers.org/opb:OPB_00425'),
    'Na': URIRef('https://identifiers.org/CHEBI:29101'),
    'proximal_tubule': URIRef('http://purl.obolibrary.org/obo/UBERON_0004134')
}


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


def make_local_uri(g, variable_id):
    counter = 1
    while any(g.triples((URIRef(f'{__OMEX_LIBRARY_URL}#{variable_id}--s{counter}'), None, None))):
        counter += 1
    return URIRef(f'{__OMEX_LIBRARY_URL}#{variable_id}--s{counter}')


def annotate_variable(g, variable, variable_type, filename):
    variable_uri = URIRef(f'{__OMEX_LIBRARY_URL}{filename}#{variable.id()}')
    if variable_type == 'chemical_quantity_units':
        local_node = make_local_uri(g, variable.id())
        g.add((variable_uri, BQBIOL['isPropertyOf'], local_node))
        g.add((variable_uri, BQBIOL['isVersionOf'], STD_TERM_URI['molar_amount']))
        g.add((local_node, BQBIOL['is'], STD_TERM_URI['Na']))
        g.add((local_node, BQBIOL['isPartOf'], STD_TERM_URI['proximal_tubule']))
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

    rdf_graph = Graph()
    rdf_graph.bind('bqbiol', BQBIOL)
    rdf_graph.bind('omex', OMEX)
    model_file = input_file.name
    rdf_file = model_file + '.rdf'
    for i in range(model.componentCount()):
        comp = model.component(i)
        for j in range(comp.variableCount()):
            var = comp.variable(j)
            t = units_inference.infer_type_from_units(model, var)
            if t:
                print(f'{var.name()} ({var.id()}) is of type: {t}')
                annotate_variable(rdf_graph, var, t, model_file)
    print(rdf_graph.serialize(format='ttl'))


if __name__ == "__main__":
    main()
