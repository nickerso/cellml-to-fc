from rdflib import Graph, Namespace, URIRef

# Create a Graph
g = Graph()

# Define namespaces
EX = Namespace("./baseline_units.cellml#")
OPB = Namespace("http://identifiers.org/opb/")

# Define custom predicate
IS_UNIT_OF = URIRef("http://semanticscience.org/resource/SIO_000222")

# Define units
ms = EX.ms
K = EX.K
m_per_s = EX.m_per_s
J = EX.J
mW = EX.mW
S = EX.S
S_per_s = EX.S_per_s
um = EX.um
m2 = EX.m2
m3 = EX.m3
rad = EX.rad
kg = EX.kg
fmol = EX.fmol
fC = EX.fC
m2_per_s = EX.m2_per_s
m3_per_s = EX.m3_per_s
rad_per_s = EX.rad_per_s
kg_per_s = EX.kg_per_s
fmol_per_s = EX.fmol_per_s
fA = EX.fA
N = EX.N
J_per_m2 = EX.J_per_m2
Pa = EX.Pa
J_per_mol = EX.J_per_mol
mV = EX.mV
kg_per_m2 = EX.kg_per_m2
kg_per_m3 = EX.kg_per_m3
mM = EX.mM
mol_per_m2 = EX.mol_per_m2
C_per_m2 = EX.C_per_m2
C_per_m3 = EX.C_per_m3
mM_per_s = EX.mM_per_s
mol_per_m2_s = EX.mol_per_m2_s
C_per_m2_s = EX.C_per_m2_s
C_per_m3_s = EX.C_per_m3_s


# Add simple unit → OPB mappings
g.add((ms, IS_UNIT_OF, OPB.OPB_00402))       # ms -> temporal location

g.add((K, IS_UNIT_OF, OPB.OPB_00293))   # K -> temperature

g.add((J, IS_UNIT_OF, OPB.OPB_00562))    # joule -> energy amount

g.add((mW, IS_UNIT_OF, OPB.OPB_00563))       # mW -> energy flow rate

g.add((S, IS_UNIT_OF, OPB.OPB_00100))        # S -> thermodynamic entropy amount

g.add((S_per_s, IS_UNIT_OF, OPB.OPB_00564))  # S_per_s -> entropy flow rate

g.add((um, IS_UNIT_OF, OPB.OPB_01064))       # um -> constant, length
g.add((um, IS_UNIT_OF, OPB.OPB_00269))       # um -> variable, translational displacement

g.add((m2, IS_UNIT_OF, OPB.OPB_00295))       # m2 -> constant, area
g.add((m2, IS_UNIT_OF, OPB.OPB_01376))       # m2 -> variable, tensile distortion

g.add((m3, IS_UNIT_OF, OPB.OPB_00523))       # m3 -> constant, spatial volume
g.add((m3, IS_UNIT_OF, OPB.OPB_00154))       # m3 -> variable, spatial amount, fluid volume

g.add((rad, IS_UNIT_OF, OPB.OPB_01072))      # rad -> constant, plane angle
g.add((rad, IS_UNIT_OF, OPB.OPB_01601))      # rad -> variable, rotational displacement

g.add((kg, IS_UNIT_OF, OPB.OPB_01226))      # kg -> mass of solid entity

g.add((fmol, IS_UNIT_OF, OPB.OPB_00425))      # fmol -> molar amount of chemical

g.add((fC, IS_UNIT_OF, OPB.OPB_00411))      # fC -> charge amount

g.add((m_per_s, IS_UNIT_OF, OPB.OPB_00251))  # m/s -> lineal translational velocity

g.add((m2_per_s, IS_UNIT_OF, OPB.OPB_01643))      # m2/s -> tensile distortion velocity

g.add((m3_per_s, IS_UNIT_OF, OPB.OPB_00299))      # m3/s -> fluid flow rate

g.add((rad_per_s, IS_UNIT_OF, OPB.OPB_01490))      # rad/s -> rotational solid velocity

g.add((kg_per_s, IS_UNIT_OF, OPB.OPB_01220))      # kg/s -> material flow rate

g.add((fmol_per_s, IS_UNIT_OF, OPB.OPB_00592))      # fmol/s -> chemical amount flow rate
g.add((fmol_per_s, IS_UNIT_OF, OPB.OPB_00544))      # fmol/s -> particle flow rate

g.add((fA, IS_UNIT_OF, OPB.OPB_00318))      # fA -> charge flow rate

g.add((N, IS_UNIT_OF, OPB.OPB_00034))      # N -> Mechanical force

g.add((J_per_m2, IS_UNIT_OF, OPB.OPB_01053))      # J/m2 -> mechanical stress

g.add((Pa, IS_UNIT_OF, OPB.OPB_00509))      # Pa -> fluid pressure
g.add((Pa, IS_UNIT_OF, OPB.OPB_01053))      # Pa -> mechanical stress

g.add((J_per_mol, IS_UNIT_OF, OPB.OPB_00378))      # J/mol -> chemical potential

g.add((mV, IS_UNIT_OF, OPB.OPB_00506))      # mV -> electrical potential (1)
g.add((mV, IS_UNIT_OF, OPB.OPB_01058))      # mV -> membrane potential
g.add((mV, IS_UNIT_OF, OPB.OPB_01169))      # mV -> electrodiffusional potential

g.add((kg_per_m2, IS_UNIT_OF, OPB.OPB_01593))      # kg/m2 -> areal density of mass
g.add((kg_per_m3, IS_UNIT_OF, OPB.OPB_01619))      # kg/m3 -> volumnal density of matter

g.add((mM, IS_UNIT_OF, OPB.OPB_00340))      # mM -> concentration of chemical, volumnal concentration of solute
g.add((mM, IS_UNIT_OF, OPB.OPB_01532))      # mM -> volumnal concentration of particle

g.add((mol_per_m2, IS_UNIT_OF, OPB.OPB_01529))      # mol/m2 -> areal concentration of chemical
g.add((mol_per_m2, IS_UNIT_OF, OPB.OPB_01530))      # mol/m2 -> areal concentration of particles

g.add((C_per_m2, IS_UNIT_OF, OPB.OPB_01238))      # C/m2 -> charge areal density

g.add((C_per_m3, IS_UNIT_OF, OPB.OPB_01237))      # C/m3 -> charge volumetric density

g.add((mM_per_s, IS_UNIT_OF, OPB.OPB_00593))      # mM/s -> chemical amount density flow rate

g.add((mol_per_m2_s, IS_UNIT_OF, OPB.OPB_00593))      # mol/m2/s -> chemical amount density flow rate

g.add((C_per_m2_s, IS_UNIT_OF, OPB.OPB_00318))      # C/m2/s -> charge flow rate
g.add((C_per_m3_s, IS_UNIT_OF, OPB.OPB_00318))      # C/m3/s -> charge flow rate


# Bind namespaces for pretty Turtle output
g.bind("ex", EX)
g.bind("opb", OPB)
g.bind("is_unit_of", IS_UNIT_OF)

# Print graph in Turtle format
print(g.serialize(format="turtle"))

