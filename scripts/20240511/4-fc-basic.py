import aml
from aml import amlSimpleLibrary as sc

constant_names = ["a", "b", "c"]

alg = sc.embedder()
alg.verbose = False
alg.binary = True # only for binary classification
alg.calculateRedundacy = True
alg.removeRepetitions = True

alg.atomization = []
for constant_name in constant_names:
    print("constant_name", constant_name)
    cIndex = alg.cmanager.setNewConstantIndexWithName(constant_name)
    at = sc.atom(alg.epoch, alg.generation, [cIndex])
    alg.atomization.append(at)

def PosRel(L, R):
    lTerm = sc.LCSegment([alg.cmanager.definedWithName[L]], alg.cmanager) # note with/without {} in first param
    rTerm = sc.LCSegment(alg.cmanager.definedWithName[R], alg.cmanager)
    return sc.relation(lTerm, rTerm, True, alg.generation, region=1)

pRelAC = PosRel("a","c")

print("pRelAC is: ", sc.AisInB( pRelAC.L, pRelAC.H, alg.atomization))

print("* pRelAB")
pRelAB = PosRel("a","b")
alg.enforce(pRelAB.L, pRelAB.H) # full crossing

print("pRelAC is: ", sc.AisInB( pRelAC.L, pRelAC.H, alg.atomization))

print("* pRelBC")
pRelBC = PosRel("b","c")
alg.enforce(pRelBC.L, pRelBC.H) # full crossing

print("pRelAC is: ", sc.AisInB( pRelAC.L, pRelAC.H, alg.atomization))
