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
kg_per_m = EX.kg_per_m
kg_per_m2 = EX.kg_per_m2
kg_per_m3 = EX.kg_per_m3
mM = EX.mM
mol_per_m2 = EX.mol_per_m2
mol_per_m = EX.mol_per_m
C_per_m = EX.C_per_m
C_per_m2 = EX.C_per_m2
C_per_m3 = EX.C_per_m3
mM_per_s = EX.mM_per_s
mol_per_m2_s = EX.mol_per_m2_s
mol_per_m_s = EX.mol_per_m_s
C_per_m_s = EX.C_per_m_s
C_per_m2_s = EX.C_per_m2_s
C_per_m3_s = EX.C_per_m3_s
fA_per_s = EX.fA_per_s
m3_per_s2 = EX.m3_per_s2
N_m_s = EX.N_m_s
N_s = EX.N_s

# Add simple unit → OPB mappings
g.add((ms, IS_UNIT_OF, OPB.OPB_00402))       # ms -> temporal location

g.add((K, IS_UNIT_OF, OPB.OPB_00293))   # K -> temperature

g.add((J, IS_UNIT_OF, OPB.OPB_00562))    # joule -> energy amount

g.add((mW, IS_UNIT_OF, OPB.OPB_00563))       # mW -> energy flow rate

g.add((S, IS_UNIT_OF, OPB.OPB_00100))        # S -> thermodynamic entropy amount

g.add((S_per_s, IS_UNIT_OF, OPB.OPB_00564))  # S_per_s -> entropy flow rate

g.add((um, IS_UNIT_OF, OPB.OPB_00269))       # um -> translational displacement

g.add((m2, IS_UNIT_OF, OPB.OPB_00295))       # m2 -> constant, area

g.add((m3, IS_UNIT_OF, OPB.OPB_00154))       # m3 -> fluid volume

g.add((rad, IS_UNIT_OF, OPB.OPB_01434))      # rad -> Joint rotational displacement

g.add((kg, IS_UNIT_OF, OPB.OPB_01226))      # kg -> mass of solid entity

g.add((fmol, IS_UNIT_OF, OPB.OPB_00425))      # fmol -> molar amount of chemical

g.add((fC, IS_UNIT_OF, OPB.OPB_00411))      # fC -> charge amount

g.add((m_per_s, IS_UNIT_OF, OPB.OPB_00251))  # m/s -> lineal translational velocity

g.add((m3_per_s, IS_UNIT_OF, OPB.OPB_00299))      # m3/s -> fluid flow rate

g.add((rad_per_s, IS_UNIT_OF, OPB.OPB_01656))      # rad/s -> Joint rotational velocity

g.add((kg_per_s, IS_UNIT_OF, OPB.OPB_01220))      # kg/s -> material flow rate

g.add((fmol_per_s, IS_UNIT_OF, OPB.OPB_00592))      # fmol/s -> chemical amount flow rate

g.add((fA, IS_UNIT_OF, OPB.OPB_00318))      # fA -> charge flow rate

g.add((N, IS_UNIT_OF, OPB.OPB_01482))      # N -> Lineal mechanical force

g.add((J_per_m2, IS_UNIT_OF, OPB.OPB_01053))      # J/m2 -> mechanical stress

g.add((Pa, IS_UNIT_OF, OPB.OPB_00509))      # Pa -> fluid pressure

g.add((J_per_mol, IS_UNIT_OF, OPB.OPB_00378))      # J/mol -> chemical potential

g.add((mV, IS_UNIT_OF, OPB.OPB_00506))      # mV -> electrical potential

g.add((kg_per_m, IS_UNIT_OF, OPB.OPB_01597))     # kg/m -> lineal density of mass
g.add((kg_per_m2, IS_UNIT_OF, OPB.OPB_01593))      # kg/m2 -> areal density of mass
g.add((kg_per_m3, IS_UNIT_OF, OPB.OPB_01619))      # kg/m3 -> volumnal density of matter

g.add((mM, IS_UNIT_OF, OPB.OPB_00340))      # mM -> concentration of chemical

g.add((mol_per_m2, IS_UNIT_OF, OPB.OPB_01529))      # mol/m2 -> areal concentration of chemical
g.add((mol_per_m, IS_UNIT_OF, OPB.OPB_01528))      # mol/m -> lineal concentration of chemical

g.add((C_per_m, IS_UNIT_OF, OPB.OPB_01239))      # C/m -> charge lineal density
g.add((C_per_m2, IS_UNIT_OF, OPB.OPB_01238))      # C/m2 -> charge areal density

g.add((C_per_m3, IS_UNIT_OF, OPB.OPB_01237))      # C/m3 -> charge volumetric density

g.add((mM_per_s, IS_UNIT_OF, OPB.OPB_00593))      # mM/s -> chemical amount density flow rate

g.add((mol_per_m2_s, IS_UNIT_OF, OPB.OPB_00593))      # mol/m2/s -> chemical amount density flow rate
g.add((mol_per_m_s, IS_UNIT_OF, OPB.OPB_00593))      # mol/m/s -> chemical amount density flow rate

g.add((C_per_m_s, IS_UNIT_OF, OPB.OPB_00318))      # C/m/s -> charge flow rate
g.add((C_per_m2_s, IS_UNIT_OF, OPB.OPB_00318))      # C/m2/s -> charge flow rate
g.add((C_per_m3_s, IS_UNIT_OF, OPB.OPB_00318))      # C/m3/s -> charge flow rate

g.add((fA_per_s, IS_UNIT_OF, OPB.OPB_01521))      # fA/s -> A momentum property that is proportional to the temporal differential of an electrical current
g.add((m3_per_s2, IS_UNIT_OF, OPB.OPB_00073))      # m3/s2 -> A momentum property that is proportional to the temporal differential of an fluid flow rate
g.add((N_m_s, IS_UNIT_OF, OPB.OPB_00163))        # Rotational momentum, N*m*s
g.add((N_s, IS_UNIT_OF, OPB.OPB_00033))          # Translational momentum, N*s

# Bind namespaces for pretty Turtle output
g.bind("ex", EX)
g.bind("opb", OPB)
g.bind("is_unit_of", IS_UNIT_OF)

# Save graph in Turtle format
g.serialize(destination="rdf_unit_cellml.ttl")

