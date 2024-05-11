import aml
from aml import amlSimpleLibrary as sc

set_of_all_constants = {0, 1, 2, ..., 7} 

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