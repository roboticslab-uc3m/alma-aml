import aml
from aml import amlSimpleLibrary as sc

set_of_all_constants = {0, 1, 2, 3, 4, 5, 6, 7} 

alg = sc.embedder()
alg.verbose = True
alg.binary = True # only for binary classification
alg.calculateRedundacy = True
alg.removeRepetitions = True

alg.atomization = []
for i in set_of_all_constants:
    c = alg.cmanager.setNewConstantIndex()
    at = sc.atom(alg.epoch, alg.generation, [c])
    alg.atomization.append(at)

vIndex = alg.cmanager.setNewConstantIndexWithName("v")
vTerm = sc.LCSegment([vIndex], alg.cmanager)
at = sc.atom(alg.epoch, alg.generation, [vIndex])
alg.atomization.append(at)

example_pos_1 = {0, 2, 5, 7}
example_pos_2 = {0, 2, 3, 5}

example_list = [example_pos_1, example_pos_2]

for example in example_list:
    exampleTerm = sc.LCSegment(example, alg.cmanager) # Here you add your examples
    region = 1
    pRel = sc.relation(vTerm, exampleTerm, True, alg.generation, region)
    alg.enforce(pRel.L, pRel.H) # full crossing


"""
<Calculating full crossing Traceback (most recent call last):
  File "/home/yo/repos/jgvictores/alma-top-secret/scripts/20240511/example-fullcrossing.py", line 32, in <module>
    alg.enforce(pRel.L, pRel.H) # full crossing
  File "amlSimpleLibrary.py", line 2107, in amlSimpleLibrary.embedder.enforce
  File "amlSimpleLibrary.py", line 899, in amlSimpleLibrary.cross
  File "amlSimpleLibrary.py", line 1161, in amlSimpleLibrary.removeRedundantAtoms
  File "amlSimpleLibrary.py", line 1117, in amlSimpleLibrary.removeRedundantAtoms_I
  File "amlSimpleLibrary.py", line 1099, in amlSimpleLibrary.removeRedundantAtoms_L
  File "amlSimpleLibrary.py", line 587, in amlSimpleLibrary.UCSegment_impl_wChains.__isub__
AssertionError
"""