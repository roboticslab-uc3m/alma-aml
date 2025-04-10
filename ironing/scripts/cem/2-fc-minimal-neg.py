import aml
from aml import amlSimpleLibrary as sc

constant_names = ["a", "b"]

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
    lTerm = sc.LCSegment([alg.cmanager.definedWithName[L]], alg.cmanager)
    rTerm = sc.LCSegment(alg.cmanager.definedWithName[R], alg.cmanager)
    return sc.relation(lTerm, rTerm, True, alg.generation, region=1)

def NegRel(L, R):
    lTerm = sc.LCSegment([alg.cmanager.definedWithName[L]], alg.cmanager)
    rTerm = sc.LCSegment(alg.cmanager.definedWithName[R], alg.cmanager)
    return sc.relation(lTerm, rTerm, True, alg.generation, region=1)

pRel = PosRel("a","b")
# NO hago ni enforce ni nada, da False:
print("pRel is: ", sc.AisInB( pRel.L, pRel.H, alg.atomization))

#print([at for at in alg.atomization])
#print([at.ucs for at in alg.atomization])
#print(alg.cmanager.definedWithName)
#print(alg.cmanager.consts)

# Trato de enforce el False:
nRel = NegRel("a","b")
alg.enforce(nRel.L, nRel.H)

#print([at for at in alg.atomization])
#print([at.ucs for at in alg.atomization])
#print(alg.cmanager.definedWithName)
#print(alg.cmanager.consts)

# Y empieza a dar True (mal!):
print("pRel is: ", sc.AisInB( pRel.L, pRel.H, alg.atomization))
