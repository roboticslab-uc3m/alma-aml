import aml
from aml import amlSimpleLibrary as sc

constant_names = ["a", "b", "c"]

alg = sc.embedder()
alg.verbose = True
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
    lTerm = sc.LCSegment(alg.cmanager.definedWithName[L], alg.cmanager) # note with/without {} in first param
    rTerm = sc.LCSegment(alg.cmanager.definedWithName[R], alg.cmanager)
    return sc.relation(lTerm, rTerm, True, alg.generation, region=1)

print("* pRel1")
pRel1 = PosRel("a","b")
alg.enforce(pRel1.L, pRel1.H) # full crossing

print("* pRel2")
pRel2 = PosRel("b","c")
alg.enforce(pRel2.L, pRel2.H) # full crossing
