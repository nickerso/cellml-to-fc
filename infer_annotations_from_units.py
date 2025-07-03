import sys
from libcellml_python_utils import cellml


model = cellml.parse_model(sys.argv[1], False)
if cellml.validate_model(model) > 0:
    exit(-1)

