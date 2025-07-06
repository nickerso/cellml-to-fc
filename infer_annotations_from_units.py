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
    'solid_mechanics': ['metre'],
    'fluid_mechanics': ['metre', 1, 3.0],
    'electromagnetic': ['coulomb'],
    'chemical': ['mole']
}
__energy_units = _create_units('energy', ['joule'])
__time_units = _create_units('time', ['second'])
__quantities_units = {k: _create_units(f'{k}_quantity_units', v) for k, v in __quantities.items()}
__quantities_flow_units = {
    f'{k}_flow': _create_units(f'{k}_flow_units', v,
                               ['second', 1, -1.0]) for k, v in __quantities.items()
}
__quantities_potential_units = {
    f'{k}_potential': _create_units(f'{k}_potential_units', ['joule'],
                     [v[0], 1, v[2]*-1.0 if len(v) > 1 else -1.0]) for k, v in __quantities.items()
}
__all_types = __quantities_units | __quantities_flow_units | __quantities_potential_units


def infer_type_from_units(model, variable):
    var_units_name = variable.units().name()
    var_units = model.units(var_units_name)
    # we know we have a valid model, so if there are no units we have a standard unit
    # create a standard unit Units for convenience with libcellml.Units.compatible()
    if var_units is None:
        var_units = _create_units('', [var_units_name])
    if libcellml.Units.compatible(var_units, __energy_units):
        return __energy_units.name()
    if libcellml.Units.compatible(var_units, __time_units):
        return __time_units.name()
    for k, u in __all_types.items():
        if libcellml.Units.compatible(var_units, u):
            return u.name()
    return None


model = cellml.parse_model(sys.argv[1], False)
if cellml.validate_model(model) > 0:
    exit(-1)

for i in range(model.componentCount()):
    comp = model.component(i)
    for j in range(comp.variableCount()):
        var = comp.variable(j)
        t = infer_type_from_units(model, var)
        if t:
            print(f'{var.name()} is of type: {t}')
