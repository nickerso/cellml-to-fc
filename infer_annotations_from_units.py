import sys
import libcellml
from libcellml_python_utils import cellml


model = cellml.parse_model(sys.argv[1], False)
if cellml.validate_model(model) > 0:
    exit(-1)

# Create a reference "volume" units, e.g. litre or m^3
volume_units = libcellml.Units()
volume_units.addUnit("metre", 1, 3.0)

# Find volume-equivalent variables
volume_variables = []
for i in range(model.componentCount()):
    comp = model.component(i)
    for j in range(comp.variableCount()):
        var = comp.variable(j)
        var_units_name = var.units().name()
        var_units = model.units(var_units_name)
        if var_units and libcellml.Units.equivalent(var_units, volume_units):
            volume_variables.append((comp.name(), var.name(), var_units_name))

# Output
print("Variables with volume-equivalent units:")
for comp_name, var_name, units in volume_variables:
    print(f"Component: {comp_name}, Variable: {var_name}, Units: {units}")