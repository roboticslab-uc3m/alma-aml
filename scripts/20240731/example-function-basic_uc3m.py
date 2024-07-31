import aml_engine
from aml_engine import amlSimpleLibrary as sc

constant_names = ["a", "b", "c"]

alg = sc.model()

print("\033[0;32mDefine constants\033[0m")
alg.atomization = []
for constant_name in constant_names:
    print("define:", constant_name)
    cIndex = alg.cmanager.setNewConstantIndexWithName(constant_name)
    at = sc.atom(alg.epoch, alg.generation, [cIndex])
    alg.atomization.append(at)


Ta = sc.LCSegment(alg.cmanager.definedWithName["a"])
Tb = sc.LCSegment(alg.cmanager.definedWithName["b"])
Tc = sc.LCSegment(alg.cmanager.definedWithName["c"])

print("\033[0;32mPrint atomization and check model\033[0m")
sc.printAtomSetWithNames("", alg.atomization, alg.cmanager)
print("A < B ?", sc.AisInB(Ta, Tb, alg.atomization))
print("B < A ?", sc.AisInB(Tb, Ta, alg.atomization))
print("A < C ?", sc.AisInB(Ta, Tc, alg.atomization))
print("C < A ?", sc.AisInB(Tc, Ta, alg.atomization))
print("B < C ?", sc.AisInB(Tb, Tc, alg.atomization))
print("C < B ?", sc.AisInB(Tc, Tb, alg.atomization))

print("\033[0;32mEnforce A < B\033[0m")
sc.enforce(
    alg,
    Ta,
    Tb,
    removeRepetitions=True,
    calculateRedundacy=False,
    binary=False,
    verbose=False,
)

print("\033[0;32mPrint atomization and check model\033[0m")
sc.printAtomSetWithNames("", alg.atomization, alg.cmanager)
print("A < B ?", sc.AisInB(Ta, Tb, alg.atomization))
print("B < A ?", sc.AisInB(Tb, Ta, alg.atomization))
print("A < C ?", sc.AisInB(Ta, Tc, alg.atomization))
print("C < A ?", sc.AisInB(Tc, Ta, alg.atomization))
print("B < C ?", sc.AisInB(Tb, Tc, alg.atomization))
print("C < B ?", sc.AisInB(Tc, Tb, alg.atomization))

print("\033[0;32mEnforce B < C\033[0m")
sc.enforce(
    alg,
    Tb,
    Tc,
    removeRepetitions=True,
    calculateRedundacy=False,
    binary=False,
    verbose=False,
)

print("\033[0;32mPrint atomization and check model\033[0m")
sc.printAtomSetWithNames("", alg.atomization, alg.cmanager)
print("A < B ?", sc.AisInB(Ta, Tb, alg.atomization))
print("B < A ?", sc.AisInB(Tb, Ta, alg.atomization))
print("A < C ?", sc.AisInB(Ta, Tc, alg.atomization))
print("C < A ?", sc.AisInB(Tc, Ta, alg.atomization))
print("B < C ?", sc.AisInB(Tb, Tc, alg.atomization))
print("C < B ?", sc.AisInB(Tc, Tb, alg.atomization))
