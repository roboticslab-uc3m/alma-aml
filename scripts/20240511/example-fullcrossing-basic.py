import aml
from aml import amlSimpleLibrary as sc

constant_names = ["0", "1", "2"]

alg = sc.embedder()
alg.verbose = True
alg.binary = True # only for binary classification
alg.calculateRedundacy = True
alg.removeRepetitions = True

alg.atomization = []
for constant_name in constant_names:
    print("constant_name", constant_name)
    cIndex = alg.cmanager.setNewConstantIndexWithName(constant_name)
    cTerm = sc.LCSegment([cIndex], alg.cmanager)
    at = sc.atom(alg.epoch, alg.generation, [cIndex])
    alg.atomization.append(at)

"""
example_pos_1 = {0, 2, 5, 7} # (b,w,b,w)
example_pos_2 = {0, 2, 3, 5} # (b,w,b,b)

example_list = [example_pos_1, example_pos_2]

for example in example_list:
    print("example", example)
    exampleTerm = sc.LCSegment(example, alg.cmanager) # Here you add your examples
    region = 1
    pRel = sc.relation(vTerm, exampleTerm, True, alg.generation, region)
    alg.enforce(pRel.L, pRel.H) # full crossing
"""