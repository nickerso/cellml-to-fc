import sys
from pathlib import Path
import libcellml
from libcellml_python_utils import cellml
from rdflib import URIRef, RDF, OWL, RDFS, Literal
from rdflib.namespace import DCTERMS
from omex_metadata import OmexMetadata
import re
import argparse

# ===========================================================================
# Module-level logger
# (each module in your project should do this — they all feed into the
#  root "pmr" logger that gets configured once in main())
# ===========================================================================

import logging
log = logging.getLogger("cellml-to-fc.infer_variable_annotations")


def _create_units(name, args, args2=None):
    u = libcellml.Units()
    u.setName(name)
    u.addUnit(*args)
    if args2:
        u.addUnit(*args2)
    m = libcellml.Model()
    m.addUnits(u)
    return u


class InferVariableAnnotations:
    """
    Class to infer semantic types of model variables based on their units and names.
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

    @staticmethod
    def make_local_uri(om, base_id):
        counter = 1
        while om.has_triple(om.local_ns[f'{base_id}--s{counter}']):
            counter += 1
        return om.local_ns[f'{base_id}--s{counter}']
    
    @staticmethod
    def create_amount_node(om, amount_type, name, compartment, species):
        amount_label = f'{amount_type}-amount-{name}'
        local_node = om.local_ns[amount_label]
        if om.has_triple(local_node):
            log.info(f'Found an existing node for the {amount_type} amount: {amount_label}; so not adding any new triples')
        else:
            log.info(f'Making a new local node for the {amount_type} amount: {amount_label}')
            om.add_triple(local_node, om.BQBIOL_NS['is'], species)
            om.add_triple(local_node, om.BQBIOL_NS['isPartOf'], compartment)
        return local_node

    def define_amount_node(self, om, variable, amount_type, name_mappings):
        variable_name = variable.name()
        # q_{Name}
        pattern = r"^q_(?P<name>.+)"
        match = re.match(pattern, variable_name)
        if match:
            name = match.group("name")
            log.info(f"Name: {name}")
            # Use the name to look up the corresponding compartment and species in the mappings
            mapping = name_mappings.get(name)
            if mapping:
                compartment = mapping['compartment']
                species = mapping['species']
                log.info(f"Compartment: {compartment}, Species: {species}")
                return self.create_amount_node(om, amount_type, name, compartment, species)
        log.warning(f'Unable to map amount variable {variable_name} to a known compartment and species')
        return None

    def define_flow_node(self, om, variable, flow_type, name_mappings):
        variable_name = variable.name()
        # v_{name}
        pattern = r"^v_(?P<name>.+)$"
        match = re.match(pattern, variable_name)
        if match:
            name = match.group("name")
            log.info(f"Name: {name}")
            # Use the name to look up the corresponding compartment and species in the mappings
            mapping = name_mappings.get(name)
            if mapping:
                compartment = mapping['compartment']
                species = mapping['species']
                log.info(f"Compartment: {compartment}, Species: {species}")
                flow_label = f'{flow_type}-flow-{name}'
                local_node = om.local_ns[flow_label]
                if om.has_triple(local_node):
                    log.info(f'Found an existing node for the {flow_type} flow: {flow_label}; so not adding any new triples')
                else:
                    log.info(f'Making a new local node for the {flow_type} amount: {flow_label}')
                    om.add_triple(local_node, om.BQBIOL_NS['isVersionOf'], s)
                return local_node
        log.warning(f'Unable to map flow variable {variable_name} to a known compartment and species')
        return None

    def annotate_variable(self, om, variable, variable_type, name_mappings):
        variable_uri = om.get_annotation_source_uri(variable.id())
        if variable_type == 'time':
            om.annotate_time(variable_uri)
        elif variable_type == 'chemical_quantity_units':
            om.annotate_molar_amount(variable_uri)
            # can we determine what we need from the variable name?
            o = self.define_amount_node(om, variable, 'molar', name_mappings)
            if o:
               om.add_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o)
        elif variable_type == 'fluid_mechanics_quantity_units':
            om.annotate_volume_amount(variable_uri)
            # can we determine what we need from the variable name?
            o = self.define_amount_node(om, variable, 'liquid', name_mappings)
            if o:
                om.add_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o)
        elif variable_type == 'chemical_flow_units':
            om.annotate_molar_flow(variable_uri)
            # can we determine what we need from the variable name?
            o = self.define_flow_node(om, variable, 'molar', name_mappings)
            if o:
                om.add_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o)
        elif variable_type == 'fluid_mechanics_flow_units':
            om.annotate_volume_flow(variable_uri)
            # can we determine what we need from the variable name?
            o = self.define_flow_node(om, variable, 'volume', name_mappings)
            if o:
                om.add_triple(variable_uri, om.BQBIOL_NS['isPropertyOf'], o)
        else:
            log.debug(f'Unable to annotate {variable.name()}[{variable.id()}] of type: {variable_type}')


#
# <http://omex-library.org/physical_process.omex/model.cellml#molar_amount_Na>
#     bqbiol:isPropertyOf local:local-entity-0 ;
#     bqbiol:isVersionOf <https://identifiers.org/opb:OPB_00425> .
#
# local:local-entity-0
#     bqbiol:is <https://identifiers.org/CHEBI:17234> ;
#     bqbiol:isPartOf <https://identifiers.org/FMA:18228> .


