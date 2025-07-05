import sys
import libcellml
from libcellml_python_utils import cellml


def _create_units(name, args):
    u = libcellml.Units()
    u.setName(name)
    u.addUnit(*args)
    m = libcellml.Model()
    m.addUnits(u)
    #print(cellml.print_model(m))
    return u


__quantities = {
    'mechanical': ['metre'],
    'volume': ['metre', 1, 3.0],
    'electromagnetic': ['coulomb'],
    'chemical': ['mole'],
    'time': ['second'],
    'energy': ['joule'],
}
__quantities_units = {k: _create_units(f'{k}_quantity_units', v) for k, v in __quantities.items()}


def variable_is_quantity(model, variable):
    var_units_name = variable.units().name()
    var_units = model.units(var_units_name)
    # we know we have a valid model, so if there are no units we have a standard unit
    if var_units is None:
        var_units = _create_units('', [var_units_name])
    for k, u in __quantities_units.items():
        #print(f'{variable.name()} -- {var_units.name()} -- {k} -- {u.name()}')
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a quantity of type: {k}')
    return True


model = cellml.parse_model(sys.argv[1], False)
if cellml.validate_model(model) > 0:
    exit(-1)

# Find volume-equivalent variables
volume_variables = []
for i in range(model.componentCount()):
    comp = model.component(i)
    for j in range(comp.variableCount()):
        var = comp.variable(j)
        variable_is_quantity(model, var)

# Output
print("Variables with volume-equivalent units:")
for comp_name, var_name, units in volume_variables:
    print(f"Component: {comp_name}, Variable: {var_name}, Units: {units}")