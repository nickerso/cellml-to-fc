import sys
import libcellml
from libcellml_python_utils import cellml


def _create_units(name, args, args2=None):
    u = libcellml.Units()
    u.setName(name)
    u.addUnit(*args)
    if args2:
        u.addUnit(*args2)
    m = libcellml.Model()
    m.addUnits(u)
    #print(cellml.print_model(m))
    return u


__quantities = {
    'mechanical': ['metre'],
    'volume': ['metre', 1, 3.0],
    'electromagnetic': ['coulomb'],
    'chemical': ['mole']
}
__energy_units = _create_units('energy', ['joule'])
__time_units = _create_units('time', ['second'])
__quantities_units = {k: _create_units(f'{k}_quantity_units', v) for k, v in __quantities.items()}
__quantities_flow_units = {
    k: _create_units(f'{k}_quantity_flow_units', v,
                     ['second', 1, -1.0]) for k, v in __quantities.items()
}
__quantities_potential_units = {
    k: _create_units(f'{k}_quantity_potential_units', ['joule'],
                     [v[0], 1, v[2]*-1.0 if len(v) > 1 else -1.0]) for k, v in __quantities.items()
}


def variable_is_quantity(model, variable):
    var_units_name = variable.units().name()
    var_units = model.units(var_units_name)
    # we know we have a valid model, so if there are no units we have a standard unit
    if var_units is None:
        var_units = _create_units('', [var_units_name])
    if libcellml.Units.compatible(var_units, __energy_units):
        print(f'Variable {variable.name()}  [{var_units_name}] is an energy variable')
        return True
    if libcellml.Units.compatible(var_units, __time_units):
        print(f'Variable {variable.name()}  [{var_units_name}] is a time variable')
        return True
    for k, u in __quantities_units.items():
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a quantity of type: {k}')
            return True
    for k, u in __quantities_flow_units.items():
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a flow of type: {k}')
            return True
    for k, u in __quantities_potential_units.items():
        if libcellml.Units.compatible(var_units, u):
            print(f'Variable {variable.name()}  [{var_units_name}] is a potential of type: {k}')
            return True
    print(f'Variable {variable.name()}  [{var_units_name}] is unknown type')
    return False


model = cellml.parse_model(sys.argv[1], False)
if cellml.validate_model(model) > 0:
    exit(-1)

for i in range(model.componentCount()):
    comp = model.component(i)
    for j in range(comp.variableCount()):
        var = comp.variable(j)
        variable_is_quantity(model, var)
