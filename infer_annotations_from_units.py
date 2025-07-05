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


def _create_units_per(name, args, per_args):
    u = libcellml.Units()
    u.setName(name)
    u.addUnit(*args)
    u.addUnit(*per_args)
    m = libcellml.Model()
    m.addUnits(u)
    print(cellml.print_model(m))
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
__quantities_per_volume_units = {
    k: _create_units_per(f'{k}_quantity_per_volume_units', v,
                         ['metre', 1, -3.0]) for k, v in __quantities.items()
}
__quantities_per_time_units = {
    k: _create_units_per(f'{k}_quantity_per_time_units', v,
                         ['second', 1, -1.0]) for k, v in __quantities.items()
}


def variable_is_quantity(model, variable):
    var_units_name = variable.units().name()
    var_units = model.units(var_units_name)
    # we know we have a valid model, so if there are no units we have a standard unit
    if var_units is None:
        var_units = _create_units('', [var_units_name])
    for k, u in __quantities_units.items():
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a quantity of type: {k}')
            return True
    for k, u in __quantities_per_volume_units.items():
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a quantity per volume of type: {k}')
            return True
    for k, u in __quantities_per_time_units.items():
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a quantity per time of type: {k}')
            return True
    return False


model = cellml.parse_model(sys.argv[1], False)
if cellml.validate_model(model) > 0:
    exit(-1)

for i in range(model.componentCount()):
    comp = model.component(i)
    for j in range(comp.variableCount()):
        var = comp.variable(j)
        variable_is_quantity(model, var)
