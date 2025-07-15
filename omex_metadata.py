import logging
from rdflib import Graph, URIRef, Namespace
from pathlib import Path


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

    def __init__(self, archive_filename, filename, logger=None):
        """
        Initialize the RDF graph and optionally load from a file.

        Parameters:
            archive_filename (str or Path): The filename of the OMEX archive.
            filename (str or Path): RDF file to load and save.
            logger (logging.Logger): Optional logger to use. If not provided, a default logger is created.
        """
        self.omex_filename = archive_filename
        self.archive_ns = Namespace(f'{OmexMetadata.OMEX_LIBRARY_URL}{archive_filename}/')
        self.local_ns = Namespace(f'{OmexMetadata.OMEX_LIBRARY_URL}{archive_filename}/{filename}#')
        self.logger = logger or self._default_logger()
        self.graph = Graph()
        # default namespace bindings
        self.graph.bind('bqbiol', self.BQBIOL_NS)
        self.graph.bind('local', self.local_ns)
        self.filename = Path(filename)
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
        logger = logging.getLogger("OmexMetadata")
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
        self._current_file = filename

    def get_annotation_source(self):
        #self.logger.info(f'Getting the current annotation source: {self._current_file}')
        return self._current_file

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
        self.graph.add((s, p, o))
        self.logger.debug(f"Added triple: ({s}, {p}, {o})")

    def __len__(self):
        return len(self.graph)

    def __str__(self):
        name = self.filename.name if self.filename else "<in-memory>"
        return f"{self.__class__.__name__}('{name}', format='{self.format}') with {len(self.graph)} triples"

    def annotate_molar_amount(self, variable):
        if self.has_triple(variable, self.BQBIOL_NS['isVersionOf'],
                           URIRef('https://identifiers.org/opb:OPB_00425')):
            self.logger.debug(f'Variable {variable} already has molar amount annotation')
        else:
            self.add_triple(
                variable,
                self.BQBIOL_NS['isVersionOf'],
                URIRef('https://identifiers.org/opb:OPB_00425')
            )

    def annotate_volume_amount(self, variable):
        if self.has_triple(variable, self.BQBIOL_NS['isVersionOf'],
                           URIRef('https://identifiers.org/opb:OPB_01322')):
            self.logger.debug(f'Variable {variable} already has (liquid) volume amount annotation')
        else:
            self.add_triple(
                variable,
                self.BQBIOL_NS['isVersionOf'],
                URIRef('https://identifiers.org/opb:OPB_01322')
            )
