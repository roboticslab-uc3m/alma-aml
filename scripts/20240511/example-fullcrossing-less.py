import aml
from aml import amlSimpleLibrary as sc

set_of_all_constants = {0, 1, 2, 3, 4, 5, 6, 7} # de aquí sólo importa la cantidad de elementos, influirá en vIndex

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
print("vIndex", vIndex) # vIndex es importante
vTerm = sc.LCSegment([vIndex], alg.cmanager)
at = sc.atom(alg.epoch, alg.generation, [vIndex])
alg.atomization.append(at)

# WOW: Example can be of arbitrary length, but must contain vIndex
example_pos_1 = {0, 1, 2, 7} # Así da AssertionError. Si cambias cualquier valor por vIndex (8 en este ejemplo), ya no rompe
example_pos_2 = {1, 2, 4, 8} # 

example_list = [example_pos_1, example_pos_2]

for example in example_list:
    print("example", example)
    exampleTerm = sc.LCSegment(example, alg.cmanager) # Here you add your examples
    region = 1
    pRel = sc.relation(vTerm, exampleTerm, True, alg.generation, region)
    alg.enforce(pRel.L, pRel.H) # full crossing
