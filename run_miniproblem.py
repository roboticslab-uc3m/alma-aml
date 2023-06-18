import aml
from aml import amlSimpleLibrary as sc
from aml import amlAuxiliaryLibrary as ql

import random

NUM_ITER_TRAINING = 10


def batchLearning(
    batchLearner,
    alg,
):
    cOrange = "\u001b[33m"
    cGreen = "\u001b[36m"
    cReset = "\u001b[0m"

    def PosRel(L, R):
        return sc.relation(
            sc.LCSegment(L, alg.cmanager),
            sc.LCSegment(R, alg.cmanager),
            True,
            alg.generation,
            region=1,
        )

    def NegRel(L, R):
        return sc.relation(
            sc.LCSegment(L, alg.cmanager),
            sc.LCSegment(R, alg.cmanager),
            False,
            alg.generation,
            region=1,
        )

    # Embedding Constants
    L1 = alg.cmanager.setNewConstantIndexWithName("L1")
    L2 = alg.cmanager.setNewConstantIndexWithName("L2")
    L3 = alg.cmanager.setNewConstantIndexWithName("L3")
    R1 = alg.cmanager.setNewConstantIndexWithName("R1")
    R2 = alg.cmanager.setNewConstantIndexWithName("R2")
    R3 = alg.cmanager.setNewConstantIndexWithName("R3")
    # Dictionary index -> name
    cname = {idx: name for name, idx in alg.cmanager.definedWithName.items()}

    # Data
    examples = [
        (L1, R1),
        (L2, R2),
        (L3, R3),
    ]
    counterexamples = [
        (L1, R2),
        (L1, R3),
        (L2, R1),
        (L2, R3),
        (L3, R1),
        (L3, R2),
    ]

    # Embedding
    pos_rels = [PosRel([(L)], [(R)]) for L, R in examples]
    neg_rels = [NegRel([(L)], [(R)]) for L, R in counterexamples]

    for i in range(NUM_ITER_TRAINING):
        num_examples_per_batch = 1
        num_counterexamples_per_batch = 2

        pbatch = random.sample(pos_rels, num_examples_per_batch)
        nbatch = random.sample(neg_rels, num_counterexamples_per_batch)
        batchLearner.enforce(pbatch, nbatch)

        print(f"{cOrange}BATCH#: {i}{cReset}")
        print(f"seen ({batchLearner.pcount}, {batchLearner.ncount})")
        print(f"Generation: {alg.generation}")
        print(f"Union model size: {len(batchLearner.reserve)}")

        print("Relations in this batch")
        for rel in pbatch:
            L_str = " ".join([cname[idx] for idx in rel.L])
            H_str = " ".join([cname[idx] for idx in rel.H])
            print(f"  {{{L_str}}} < {{{H_str}}} - {rel.L.constants} < {rel.H.constants}")
        for rel in nbatch:
            L_str = " ".join([cname[idx] for idx in rel.L])
            H_str = " ".join([cname[idx] for idx in rel.H])
            print(f"  {{{L_str}}} !< {{{H_str}}} - {rel.L.constants} !< {rel.H.constants}")

        print("Atoms in this batch's model")
        for at in alg.atomization:
            ucs_str = " ".join([cname[idx] for idx in at.ucs.isolatedConstants])
            print(f"  {{{ucs_str}}} - {at.ucs.isolatedConstants}")

        print("Atoms in union model")
        for at in batchLearner.reserve:
            ucs_str = " ".join([cname[idx] for idx in at.ucs.isolatedConstants])
            print(f"  {{{ucs_str}}} - {at.ucs.isolatedConstants}")

        # Test
        # Get all constants used in the test set
        testConsts = sc.CSegment()
        for rel in pos_rels:
            testConsts |= rel.L
            testConsts |= rel.H
        for rel in neg_rels:
            testConsts |= rel.L
            testConsts |= rel.H
        # Precompute atoms in every constant (since the atoms in a term is equal to the union of atoms in the term's constants)
        las = ql.calculateLowerAtomicSegment(batchLearner.reserve, testConsts, True)  # fmt:skip

        TP = 0
        TN = 0
        FP = 0
        FN = 0
        print("Wrong relations")
        for L, R in examples:
            if las.get(L, set()) <= las.get(R, set()):
                TP += 1
            else:
                FN += 1
                print(f"  {cname[L]} !< {cname[R]}")
        for L, R in counterexamples:
            if las.get(L, set()) <= las.get(R, set()):
                FP += 1
                print(f"  {cname[L]} < {cname[R]}, {las.get(L, set())} <= {las.get(R, set())}")  # fmt:skip
            else:
                TN += 1
        FPR = FP / len(counterexamples)
        FNR = FN / len(examples)
        print(f"FPR: {FPR}")
        print(f"FNR: {FNR}")

        # Reserve Update
        alg.cmanager.updateConstantsTo(alg.atomization, batchLearner.reserve, alg.exampleSet) # fmt:skip


def main():
    useReduceIndicators = True
    byQuotient = False

    alg = sc.embedder()
    batchLearner = ql.batchLearner(alg)

    batchLearner.useReduceIndicators = useReduceIndicators
    batchLearner.enforceTraceConstraints = True
    batchLearner.byQuotient = byQuotient
    batchLearner.storePositives = True

    batchLearner.alg.verbose = False
    batchLearner.verbose = False

    batchLearning(
        batchLearner,
        alg,
    )


if __name__ == "__main__":
    main()
