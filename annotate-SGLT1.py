# Record the process of annotating the SGLT1 CellML model with additional information

# hacky way to make sure we can reuse our utilities without needing to install the package - we just add it to the path here
import sys
sys.path.insert(0, "libcellml_python_utils")

from rdflib import URIRef, Literal, XSD
from pathlib import Path
from libcellml import Annotator
from libcellml_python_utils import utilities, cellml
from omex_metadata import OmexMetadata
import logging
import argparse
from infer_variable_annotations import InferVariableAnnotations



log = logging.getLogger("cellml-to-fc")
log.setLevel(logging.INFO)
terminal_handler = logging.StreamHandler(sys.stderr)
terminal_handler.setLevel(logging.INFO)
log.addHandler(terminal_handler)

# These are the model compartments that we expect to see. The key is the abbreviation used in the variable 
# names, and the value is the corresponding ontology term for that compartment.
COMPARTMENT_MAP = {
    # intracellular - treat it as the cytosol for now
    'i': URIRef('https://identifiers.org/GO:0005829'),
    # extracellular space
    'o': URIRef('https://identifiers.org/GO:0005615'),
    # membrane
    'membrane': URIRef('https://identifiers.org/GO:0016020')
}

# These are the chemical species that we expect to see in the model. The key is the abbreviation used in the
# variable names, and the value is the corresponding ontology term for that species.
SPECIES_MAP = {
    # sodium(1+)
    'Na': URIRef('https://identifiers.org/CHEBI:29101'),
    # glucose
    'Glc': URIRef('https://identifiers.org/CHEBI:17234'),
}

SPECIES_NAME_MAPPINGS = {
    'Nai': {
        'compartment': COMPARTMENT_MAP['i'],
        'species': SPECIES_MAP['Na']
    },
    'Nao': {
        'compartment': COMPARTMENT_MAP['o'],
        'species': SPECIES_MAP['Na']
    },
    'Glci': {
        'compartment': COMPARTMENT_MAP['i'],
        'species': SPECIES_MAP['Glc']
    },
    'Glco': {
        'compartment': COMPARTMENT_MAP['o'],
        'species': SPECIES_MAP['Glc']
    },
}


class OmexArchive:
    filename: Path = None
    base_dir: Path = None
    entries: list[(Path, str, bool)] = [
        # list of (relative_path, format, is_master) entries to include in the archive
        ('.', "http://identifiers.org/combine.specifications/omex", False),
        ('manifest.xml', "http://identifiers.org/combine.specifications/omex-manifest", False)
    ]
    def list_entries(self):
        print(f"OMEX Archive entries for {self.filename}:")
        for path, format, is_master in self.entries:
            print(f"  - {path} (format: {format}, master: {is_master})")
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Annotate the SGLT1 CellML model with additional information.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("SGLT1_annotated"),
        help="Directory to save the annotated model and metadata files. Default: SGLT1_annotated",
    )

    # --- Logging options ---
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        metavar="LEVEL",
        help="Log verbosity: DEBUG (most verbose) → INFO → WARNING → ERROR (least verbose). ",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging. Equivalent to --log-level DEBUG.",
    )

    parser.add_argument(
        "--infer",
        action="store_true",
        help="Infer variable annotations based on name and units.",
    )

    args = parser.parse_args()

    if args.debug:
        log.info('Debug logging enabled via --debug flag')
        log.setLevel(logging.DEBUG)
        terminal_handler.setLevel(logging.DEBUG)
    elif args.log_level:
        log.setLevel(getattr(logging, args.log_level))
        terminal_handler.setLevel(getattr(logging, args.log_level))

    # URL of the original CellML model to be annotated - the full BG version of the model
    model_source_url = "https://models.physiomeproject.org/workspace/b65/rawfile/cc4effc03581119d92df4eb4fe08eaeb698ea86e/Electrogenic%20cotransporter/CellMLV2/SGLT1_BG.cellml"
    print("Annotating SGLT1 model with additional information...")
    print(f"Original model source URL: {model_source_url}")
    
    # Output path for the annotated model / OMEX archive source files
    output_dir = args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    # Fetch and flatten the model, which also resolves imports and adds IDs to 
    # all components, variables, etc. (which is important for annotation)
    flat_sglt1_model = output_dir / "SGLT1.cellml"
    if flat_sglt1_model.exists():
        print(f"Flattened model already exists at {flat_sglt1_model}, skipping fetch and flattening.")
    else:
        # using strict model as we know this is a CellML 2.0 model and want it to fail if we get the wrong one :)
        utilities.fetch_flat_model(model_source_url, output=flat_sglt1_model, strict_mode=True, add_ids=True)
        print(f"Flattened model saved to: {flat_sglt1_model}")

    # basic check on the flattened model
    model = cellml.parse_model(flat_sglt1_model, True)
    if cellml.validate_model(model) > 0:
        print("Model is invalid after flattening, check the output for details.")
        exit(1)
    
    annotator = Annotator()
    annotator.setModel(model)
    duplicates = annotator.duplicateIds()
    if len(duplicates) > 0:
        print("There are some duplicate IDs in the model.")
        print(duplicates)

    print("Model is valid and ready for annotation.")

    # create our metadata manager which will handle the RDF graph and saving to file - we point
    # it at the output file we want to save to, which also sets up the namespaces correctly
    omex_filename = "SGLT1_annotated.omex"
    annotation_file = output_dir / "SGLT1_annotations.ttl"
    omex = OmexArchive()
    omex.filename = Path(omex_filename)
    omex.base_dir = output_dir
    omex.entries.append((flat_sglt1_model.name, "http://identifiers.org/combine.specifications/cellml", False))
    omex.entries.append((annotation_file.name, "http://identifiers.org/combine.specifications/omex-metadata", False))
    omex_metadata = OmexMetadata(archive_filename=omex_filename, rdf_file=annotation_file, base_dir=output_dir)

    # Model level anntotations
    omex_metadata.set_annotation_source(flat_sglt1_model)
    model_uri = omex_metadata.get_annotation_source_uri(model.id())
    omex_metadata.annotate_reference(model_uri, 'https://doi.org/10.1016/j.bpj.2024.12.006') # Biophs J article describing the model
    omex_metadata.annotate_reference(model_uri, 'https://doi.org/10.36903/physiome.30133342') # Physiome article
    omex_metadata.annotate_creator(model_uri, 'https://orcid.org/0000-0001-5602-5707') # Weiwei
    omex_metadata.annotate_creator(model_uri, 'https://orcid.org/0000-0001-9665-4145') # Peter
    omex_metadata.annotate_creator(model_uri, 'https://orcid.org/0000-0003-4667-9779') # Andre
    omex_metadata.annotate_taxon(model_uri, '9606') # human? probably not...

    # Annotations about the annotations
    omex_metadata.set_annotation_source(annotation_file)
    annotations_uri = omex_metadata.get_annotation_source_uri()
    omex_metadata.annotate_creator(annotations_uri, 'https://orcid.org/0000-0003-4667-9779') # Andre - we can say that Andre created the annotations themselves, even though the content is about the model created by others
    omex_metadata.annotate_created(annotations_uri)

    # Now we can use our inference engine to add annotations for the variables based on their names and units.
    annotation_inference = InferVariableAnnotations()
    # set the annotation source to the model file, so that the variable annotations will be linked to the model in the metadata
    omex_metadata.set_annotation_source(flat_sglt1_model)

    if args.infer:
        # see what annotations we can infer for all variables in the model and add them to the metadata graph
        for i in range(model.componentCount()):
            comp = model.component(i)
            for j in range(comp.variableCount()):
                var = comp.variable(j)
                t = annotation_inference.infer_type_from_units(model, var)
                if t:
                    log.info(f'{comp.name()}/{var.name()} ({var.id()}) is of type: {t}')
                    annotation_inference.annotate_variable(omex_metadata, var, t, SPECIES_NAME_MAPPINGS)


    # manual annotations
    # we know in this model that these concentrations are used in the params_BG component
    for vn in SPECIES_NAME_MAPPINGS.keys():
        variable_id = model.component('params_BG').variable(vn).id()
        variable_uri = omex_metadata.get_annotation_source_uri(variable_id)
        omex_metadata.annotate_chemical_concentration(variable_uri)
        amount_node = annotation_inference.create_amount_node(omex_metadata, 'molar', vn, SPECIES_NAME_MAPPINGS[vn]['compartment'],
                                                              SPECIES_NAME_MAPPINGS[vn]['species'])
        if amount_node:
            omex_metadata.add_triple(variable_uri, omex_metadata.BQBIOL_NS['isPropertyOf'], amount_node)

    # v_1 = flow of Na  o => membrane
    # v_2 = flow of Glc o ==> membrane
    # v_4 = flow of Glc membrane ==> i
    # v_5 = flow of Na memnbrane ==> i

    # SGLT1 in the membrane
    mediator = omex_metadata.local_ns['mediator']
    omex_metadata.add_triple(mediator, omex_metadata.BQBIOL_NS['is'], URIRef('http://purl.obolibrary.org/obo/PR_P05023'))
    omex_metadata.add_triple(mediator, omex_metadata.BQBIOL_NS['isPartOf'], URIRef('https://identifiers.org/GO:0016020'))

    # need to define the membrane molar amounts
    membrane_Na_node = annotation_inference.create_amount_node(
        omex_metadata,
        'molar',
        'Na_membrane',
        COMPARTMENT_MAP['membrane'],
        SPECIES_MAP['Na']
    )
    membrane_Glc_node = annotation_inference.create_amount_node(
        omex_metadata,
        'molar',
        'Glc_membrane',
        COMPARTMENT_MAP['membrane'],
        SPECIES_MAP['Glc']
    )
    
    molar_flows = {
        'v_1': {
            'source': (omex_metadata.local_ns['molar-amount-Nao'], '2'),
            'sink': (membrane_Na_node, '2'),
            'process-name': 'molar-flow-Na-into-membrane'
        },
        'v_5': {
            'sink': (omex_metadata.local_ns['molar-amount-Nai'], '2'),
            'source': (membrane_Na_node, '2'),
            'process-name': 'molar-flow-Na-out-of-membrane'
        },
        'v_2': {
            'source': (omex_metadata.local_ns['molar-amount-Glco'], '1'),
            'sink': (membrane_Glc_node, '1'),
            'process-name': 'molar-flow-Glc-into-membrane'
        },
        'v_4': {
            'sink': (omex_metadata.local_ns['molar-amount-Glci'], '1'),
            'source': (membrane_Glc_node, '1'),
            'process-name': 'molar-flow-Glc-out-of-membrane'
        }

    }
    for flow, info in molar_flows.items():
        v_uri = omex_metadata.get_annotation_source_uri(model.component('SGLT1_BG').variable(flow).id())
        source_participant = annotation_inference.make_local_uri(omex_metadata, 'source-participant')
        s = info['source']
        omex_metadata.add_triple(source_participant, omex_metadata.SEMSIM_NS['hasMultiplier'], Literal(s[1], datatype=XSD.double))
        omex_metadata.add_triple(source_participant, omex_metadata.SEMSIM_NS['hasPhysicalEntityReference'], s[0])
        sink_participant = annotation_inference.make_local_uri(omex_metadata, 'sink-participant')
        s = info['sink']
        omex_metadata.add_triple(sink_participant, omex_metadata.SEMSIM_NS['hasMultiplier'], Literal(s[1], datatype=XSD.double))
        omex_metadata.add_triple(sink_participant, omex_metadata.SEMSIM_NS['hasPhysicalEntityReference'], s[0])
        mediator_participant = annotation_inference.make_local_uri(omex_metadata, 'mediator-participant')
        omex_metadata.add_triple(mediator_participant, omex_metadata.SEMSIM_NS['hasPhysicalEntityReference'], mediator)
        process_node = omex_metadata.local_ns[info['process-name']]
        omex_metadata.add_triple(process_node, omex_metadata.SEMSIM_NS['hasMediatorParticipant'], mediator_participant)
        omex_metadata.add_triple(process_node, omex_metadata.SEMSIM_NS['hasSinkParticipant'], sink_participant)
        omex_metadata.add_triple(process_node, omex_metadata.SEMSIM_NS['hasSourceParticipant'], source_participant)
        omex_metadata.add_triple(process_node, omex_metadata.BQBIOL_NS['isVersionOf'], URIRef('https://identifiers.org/GO:0140104'))
        omex_metadata.add_triple(v_uri, omex_metadata.BQBIOL_NS['isPropertyOf'], process_node)

    # # molar flow Nao -> Na membrane
    # v_uri = omex_metadata.get_annotation_source_uri(model.component('SGLT1_BG').variable('v_1').id())
    # source_participant = annotation_inference.make_local_uri(omex_metadata, 'source-participant')
    # omex_metadata.add_triple(source_participant, omex_metadata.SEMSIM_NS['hasMultiplier'], Literal('2', datatype=XSD.double))
    # omex_metadata.add_triple(source_participant, omex_metadata.SEMSIM_NS['hasPhysicalEntityReference'], omex_metadata.local_ns['molar-amount-Nao'])
    # sink_participant = annotation_inference.make_local_uri(omex_metadata, 'sink-participant')
    # omex_metadata.add_triple(sink_participant, omex_metadata.SEMSIM_NS['hasMultiplier'], Literal('2', datatype=XSD.double))
    # omex_metadata.add_triple(sink_participant, omex_metadata.SEMSIM_NS['hasPhysicalEntityReference'], membrane_Na_node)
    # mediator_participant = annotation_inference.make_local_uri(omex_metadata, 'mediator-participant')
    # omex_metadata.add_triple(sink_participant, omex_metadata.SEMSIM_NS['hasPhysicalEntityReference'], mediator)
    # process_node = omex_metadata.local_ns['molar-flow-Na-o--membrane']
    # omex_metadata.add_triple(process_node, omex_metadata.SEMSIM_NS['hasMediatorParticipant'], mediator_participant)
    # omex_metadata.add_triple(process_node, omex_metadata.SEMSIM_NS['hasSinkParticipant'], sink_participant)
    # omex_metadata.add_triple(process_node, omex_metadata.SEMSIM_NS['hasSourceParticipant'], source_participant)
    # omex_metadata.add_triple(process_node, omex_metadata.BQBIOL_NS['isVersionOf'], URIRef('https://identifiers.org/GO:0140104'))
    # omex_metadata.add_triple(v_uri, omex_metadata.BQBIOL_NS['isPropertyOf'], process_node)
    

    # Save the annotations to file - we can save the RDF graph at any point, but we wait until
    # the end here just to minimize file I/O during development
    omex_metadata.save(annotation_file, format="turtle", overwrite=True)
    # These are the files that should be added to the OMEX archive. The actual creation of the archive is not yet implemented
    # in this script, but would be a simple step of zipping these files together with the correct structure and manifest.
    omex.list_entries()


    # avoid memory leak due to swig issue in libcellml 0.6.3 (see https://github.com/cellml/libcellml/issues/1129)
    del model
    del annotator
    