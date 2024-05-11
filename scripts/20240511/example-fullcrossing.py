import aml
from aml import amlSimpleLibrary as sc

#set_of_all_constants = {0, 1, 2, 3, 4, 5, 6, 7} # (b[0][0], b[0][1], b[1][0], b[1][1], w[0][0], ... )
set_of_all_constants = {0, 1, 2, ..., 7}

alg = sc.embedder()
alg.verbose = True
alg.binary = True # only for binary classification
alg.calculateRedundacy = True
alg.removeRepetitions = True

alg.atomization = []
for i in set_of_all_constants:
    print("i", i)
    c = alg.cmanager.setNewConstantIndex()
    at = sc.atom(alg.epoch, alg.generation, [c])
    alg.atomization.append(at)

vIndex = alg.cmanager.setNewConstantIndexWithName("v")
vTerm = sc.LCSegment([vIndex], alg.cmanager)
at = sc.atom(alg.epoch, alg.generation, [vIndex])
alg.atomization.append(at)

example_pos_1 = {0, 2, 5, 7} # (b,w,b,w)
example_pos_2 = {0, 2, 3, 5} # (b,w,b,b)

example_list = [example_pos_1, example_pos_2]

for example in example_list:
    print("example", example)
    exampleTerm = sc.LCSegment(example, alg.cmanager) # Here you add your examples
    region = 1
    pRel = sc.relation(vTerm, exampleTerm, True, alg.generation, region)
    alg.enforce(pRel.L, pRel.H) # full crossing
