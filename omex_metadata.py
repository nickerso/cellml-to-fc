import logging
from rdflib import Graph, URIRef, Namespace, DCTERMS, XSD, Literal
from pathlib import Path
from datetime import date


class OmexMetadata:
    """
    Base class for working with RDF in an OMEX archive using rdflib,
    with automatic format detection and integrated logging.
    """

    EXTENSION_FORMAT_MAP = {
        ".ttl": "turtle",
        ".rdf": "xml",
        ".xml": "xml",
        ".nt": "nt",
        ".n3": "n3",
        ".jsonld": "json-ld",
        ".trig": "trig",
    }

    OMEX_LIBRARY_URL = 'http://omex-library.org/'
    OMEX_NS = Namespace(OMEX_LIBRARY_URL)
    BQBIOL_NS = Namespace('http://biomodels.net/biology-qualifiers/')
    BQMODEL_NS = Namespace('http://biomodels.net/model-qualifiers/')

    def __init__(self, archive_filename, rdf_file: str | Path, base_dir: str | Path = None, logger=None):
        """
        Initialize the RDF graph and optionally load from a file.

        Parameters:
            archive_filename (str or Path): The filename of the OMEX archive.
            rdf_file (str or Path): RDF file to load and save.
            base_dir (str or Path): Base directory for the OMEX archive, i.e., where the files are stored on disk.
            logger (logging.Logger): Optional logger to use. If not provided, a default logger is created.
        """
        self.omex_filename = archive_filename
        self.base_dir = Path(base_dir) if base_dir else None
        self.archive_ns = Namespace(f'{OmexMetadata.OMEX_LIBRARY_URL}{archive_filename}/')
        metadata_file = rdf_file.relative_to(self.base_dir) if self.base_dir else Path(rdf_file)
        self.local_ns = Namespace(f'{OmexMetadata.OMEX_LIBRARY_URL}{archive_filename}/{metadata_file.as_posix()}#')
        self.logger = logger or self._default_logger()
        self.graph = Graph()
        # default namespace bindings
        self.graph.bind('bqbiol', self.BQBIOL_NS)
        self.graph.bind('local', self.local_ns)
        self.filename = Path(rdf_file)
        self.format = None
        self._current_file = None

        if self.filename:
            self.format = self.detect_format(self.filename)
            self.logger.info(f"Loading RDF graph from {self.filename} as '{self.format}'")
            if not self.filename.exists():
                self.logger.warning(f"RDF file not found: {self.filename}")
            else:
                self.graph.parse(self.filename, format=self.format)

    @staticmethod
    def _default_logger():
        logger = logging.getLogger("cellml-to-fc.OmexMetadata")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    @staticmethod
    def detect_format(path):
        ext = Path(path).suffix.lower()
        fmt = OmexMetadata.EXTENSION_FORMAT_MAP.get(ext)
        if not fmt:
            raise ValueError(f"Could not detect RDF format from extension: {ext}")
        return fmt

    def set_annotation_source(self, filename):
        self.logger.info(f'Setting the current annotation source from: {self._current_file}; to: {filename}')
        current_file = filename.relative_to(self.base_dir) if self.base_dir else Path(filename)
        self._current_file = current_file.as_posix()
        self.logger.info(f'Current annotation source set to: {self._current_file}')

    def get_annotation_source(self):
        #self.logger.info(f'Getting the current annotation source: {self._current_file}')
        return self._current_file

    def get_annotation_source_uri(self, element_id: str = None) -> URIRef:
        self.logger.info(f'Getting the URI for element ID: {element_id} in file: {self._current_file}')
        uri = self.archive_ns[self._current_file] if not element_id else self.archive_ns[f'{self._current_file}#{element_id}']
        self.logger.info(f'Constructed URI: {uri}')
        return uri

    def save(self, destination=None, format=None, overwrite=False):
        target = Path(destination) if destination else self.filename
        fmt = format or self.format or "turtle"

        if not target:
            raise ValueError("No destination specified for saving RDF graph.")
        if target.exists() and not overwrite:
            self.logger.error(f"Output file '{target}' exists. Use overwrite=True to overwrite.")
            raise FileExistsError(f"Output file '{target}' exists. Use overwrite=True to overwrite.")

        self.graph.serialize(destination=target, format=fmt)
        self.logger.info(f"Saved RDF graph to {target} as '{fmt}'")

    def bind_prefixes(self, prefix_map):
        for prefix, uri in prefix_map.items():
            self.graph.bind(prefix, Namespace(uri))
            self.logger.debug(f"Bound prefix '{prefix}' to namespace '{uri}'")

    def query(self, sparql_string):
        self.logger.debug("Running SPARQL query")
        return self.graph.query(sparql_string)

    def has_triple(self, s=None, p=None, o=None):
        result = any(self.graph.triples((s, p, o)))
        self.logger.debug(f"Triple match for ({s}, {p}, {o}): {result}")
        return result

    def add_triple(self, s, p, o):
        if not self.has_triple(s, p, o):
            self.graph.add((s, p, o))
            self.logger.debug(f"Added triple: ({s}, {p}, {o})")

    def __len__(self):
        return len(self.graph)

    def __str__(self):
        name = self.filename.name if self.filename else "<in-memory>"
        return f"{self.__class__.__name__}('{name}', format='{self.format}') with {len(self.graph)} triples"

    def annotate_reference(self, uri: URIRef, doi: str):
        self.add_triple(
            uri,
            self.BQMODEL_NS['isDescribedBy'],
            URIRef(doi)
        )

    def annotate_creator(self, uri: URIRef, orcid: str):
        self.add_triple(
            uri,
            DCTERMS['creator'],
            URIRef(orcid)
        )

    def annotate_created(self, uri: URIRef, d: date = date.today()):
        self.add_triple(
            uri,
            DCTERMS['created'],
            Literal(d, datatype=XSD.date)
        )

    def annotate_taxon(self, uri: URIRef, taxon_id: str):
        self.add_triple(
            uri,
            self.BQBIOL_NS['hasTaxon'],
            URIRef(f'https://identifiers.org/taxonomy:{taxon_id}')
        )

    def annotate_molar_amount(self, variable):
        self.add_triple(
            variable,
            self.BQBIOL_NS['isVersionOf'],
            URIRef('https://identifiers.org/opb:OPB_00425')
        )

    def annotate_chemical_concentration(self, variable):
        self.add_triple(
            variable,
            self.BQBIOL_NS['isVersionOf'],
            URIRef('https://identifiers.org/opb:OPB_00340')
        )

    def annotate_molar_flow(self, variable):
        self.add_triple(
            variable,
            self.BQBIOL_NS['isVersionOf'],
            URIRef('https://identifiers.org/opb:OPB_00592')
        )

    def annotate_volume_amount(self, variable):
        self.add_triple(
            variable,
            self.BQBIOL_NS['isVersionOf'],
            URIRef('https://identifiers.org/opb:OPB_01322')
        )

    def annotate_volume_flow(self, variable):
        self.add_triple(
            variable,
            self.BQBIOL_NS['isVersionOf'],
            URIRef('https://identifiers.org/opb:OPB_00299')
        )

    def annotate_time(self, variable):
        self.add_triple(
            variable,
            self.BQBIOL_NS['isVersionOf'],
            URIRef('https://identifiers.org/opb:OPB_01023')
        )
