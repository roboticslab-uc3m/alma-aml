import aml
from aml import amlSimpleLibrary as sc
from aml import amlAuxiliaryLibrary as ql

import random

cOrange = "\u001b[33m"
cGreen = "\u001b[36m"
cReset = "\u001b[0m"

NUM_ITER_TRAINING = 10


class Solver:
    def __init__(self):
        useReduceIndicators = True
        byQuotient = False

        self.alg = sc.embedder()
        self.batchLearner = ql.batchLearner(self.alg)

        self.batchLearner.useReduceIndicators = useReduceIndicators
        self.batchLearner.enforceTraceConstraints = True
        self.batchLearner.byQuotient = byQuotient
        self.batchLearner.storePositives = True

        self.alg.verbose = False
        self.batchLearner.verbose = False

        self.cmanager = self.alg.cmanager

        self.i = 0

        # Embedding Constants
        self.L1 = self.cmanager.setNewConstantIndexWithName("L1")
        self.L2 = self.cmanager.setNewConstantIndexWithName("L2")
        self.L3 = self.cmanager.setNewConstantIndexWithName("L3")
        self.R1 = self.cmanager.setNewConstantIndexWithName("R1")
        self.R2 = self.cmanager.setNewConstantIndexWithName("R2")
        self.R3 = self.cmanager.setNewConstantIndexWithName("R3")
        # Dictionary index -> name
        self.cname = {idx: name for name, idx in self.cmanager.definedWithName.items()}

    def toConstant(self, elem):
        return self.cmanager.definedWithName[elem]

    def PosRel(self, L, R):
        return sc.relation(
            sc.LCSegment([(self.toConstant(L))], self.cmanager),
            sc.LCSegment([(self.toConstant(R))], self.cmanager),
            True,
            self.alg.generation,
            region=1,
        )

    def NegRel(self, L, R):
        return sc.relation(
            sc.LCSegment([(self.toConstant(L))], self.cmanager),
            sc.LCSegment([(self.toConstant(R))], self.cmanager),
            False,
            self.alg.generation,
            region=1,
        )

    def train(self, examples, counterexamples):
        self.pbatch = [self.PosRel(L, R) for L, R in examples]
        self.nbatch = [self.NegRel(L, R) for L, R in counterexamples]

        self.batchLearner.enforce(self.pbatch, self.nbatch)

        print(f"{cOrange}BATCH#: {self.i}{cReset}")
        self.i += 1
        print(f"seen ({self.batchLearner.pcount}, {self.batchLearner.ncount})")
        print(f"Generation: {self.alg.generation}")
        print(f"Union model size: {len(self.batchLearner.reserve)}")

        print("Relations in this batch")
        for rel in self.pbatch:
            L_str = " ".join([self.cname[idx] for idx in rel.L])
            H_str = " ".join([self.cname[idx] for idx in rel.H])
            print(
                f"  {{{L_str}}} < {{{H_str}}} - {rel.L.constants} < {rel.H.constants}"
            )
        for rel in self.nbatch:
            L_str = " ".join([self.cname[idx] for idx in rel.L])
            H_str = " ".join([self.cname[idx] for idx in rel.H])
            print(
                f"  {{{L_str}}} !< {{{H_str}}} - {rel.L.constants} !< {rel.H.constants}"
            )

        print("Atoms in this batch's model")
        for at in self.alg.atomization:
            ucs_str = " ".join([self.cname[idx] for idx in at.ucs.isolatedConstants])
            print(f"  {{{ucs_str}}} - {at.ucs.isolatedConstants}")

        print("Atoms in union model")
        for at in self.batchLearner.reserve:
            ucs_str = " ".join([self.cname[idx] for idx in at.ucs.isolatedConstants])
            print(f"  {{{ucs_str}}} - {at.ucs.isolatedConstants}")

        # Reserve Update (This has no effect on this particular problem)
        # self.cmanager.updateConstantsTo(self.alg.atomization, self.batchLearner.reserve, self.alg.exampleSet)  # fmt:skip

    def predict(self, questions):
        allConstants = set()
        for L, R in questions:
            allConstants.add(self.toConstant(L))
            allConstants.add(self.toConstant(R))
        allConstants = sc.CSegment(allConstants)

        las = ql.calculateLowerAtomicSegment(self.batchLearner.reserve, allConstants, True)  # fmt:skip
        disc = []
        for L, R in questions:
            l_const = self.toConstant(L)
            r_const = self.toConstant(R)
            disc.append(len(las.get(l_const, set()) - las.get(r_const, set())))

        return disc


if __name__ == "__main__":
    solver = Solver()

    examples = [
        ("L1", "R1"),
        ("L2", "R2"),
        ("L3", "R3"),
    ]
    counterexamples = [
        ("L1", "R2"),
        ("L1", "R3"),
        ("L2", "R1"),
        ("L2", "R3"),
        ("L3", "R1"),
        ("L3", "R2"),
    ]

    for i in range(NUM_ITER_TRAINING):
        num_examples_per_batch = 1
        num_counterexamples_per_batch = 2

        pbatch = random.sample(examples, num_examples_per_batch)
        nbatch = random.sample(counterexamples, num_counterexamples_per_batch)

        solver.train(pbatch, nbatch)

        # Questions for our model
        questions_L1 = [
            ("L1", "R1"),
            ("L1", "R2"),
            ("L1", "R3"),
        ]
        questions_L2 = [
            ("L2", "R1"),
            ("L2", "R2"),
            ("L2", "R3"),
        ]
        questions_L3 = [
            ("L3", "R1"),
            ("L3", "R2"),
            ("L3", "R3"),
        ]

        print("L1: ", solver.predict(questions_L1))
        print("L2: ", solver.predict(questions_L2))
        print("L3: ", solver.predict(questions_L3))

    print("done!")
