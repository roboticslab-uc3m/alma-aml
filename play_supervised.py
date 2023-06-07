import gymnasium as gym
import gymnasium_playground_fakeironing

import aml
from aml import amlSimpleLibrary as sc
from aml import amlAuxiliaryLibrary as ql

import random
from pprint import pprint

NUM_ITER_TRAINING = 30
MAX_STEPS = 10  # max length of line
NUM_TESTS = 30
TEST_EVERY = 10

WIN_BATCH_SIZE = 10
LOSE_BATCH_SIZE = 10

class ConstantsIndices:
    def __init__(self):
        self.observations = None
        self.actions = None
        self.goal = None
        self.ctx = set()

class Solver:

    def __init__(self):
        self.alg = sc.embedder()
        self.batchLearner = ql.batchLearner(self.alg)

        self.batchLearner.useReduceIndicators = True
        self.batchLearner.enforceTraceConstraints = True
        self.batchLearner.byQuotient = False
        self.batchLearner.storePositives = True

        self.batchLearner.alg.verbose = False
        self.batchLearner.verbose = False

        self.cmanager = self.alg.cmanager

    def create_constants(self, env):
        self.cmanager.constants_indices = ConstantsIndices()

        c_actions = []
        if isinstance(env.action_space, gym.spaces.discrete.Discrete):
            for ac in range(env.action_space.n):
                c = self.cmanager.setNewConstantIndexWithName("A[{ac}]")
                c_actions.append(c)

        c_observations = []
        if isinstance(env.observation_space, gym.spaces.box.Box):
            for _ in range(len(env.observation_space.low)):
                c1 = self.cmanager.setNewChainIndex()  # up
                c2 = self.cmanager.setNewChainIndex()  # down
                c_observations.append([c1, c2])

        c1 = self.cmanager.setNewConstantIndexWithName("win")
        c2 = self.cmanager.setNewConstantIndexWithName("lose")
        c_goal = {"win": c1, "lose": c2}

        self.cmanager.constants_indices.observations = c_observations
        self.cmanager.constants_indices.actions = c_actions
        self.cmanager.constants_indices.goal = c_goal

    def LCS(self, param):
        if sc.LCSegment == sc.LCSegment_impl_wChains:
            return sc.LCSegment(param, self.cmanager)
        else:
            return sc.LCSegment(param)

    def example_to_relations(self, example):
        pos_rels = []
        neg_rels = []

        constants_observations = self.cmanager.constants_indices.observations
        constants_actions = self.cmanager.constants_indices.actions
        constants_goal = self.cmanager.constants_indices.goal

        ctx_game = self.cmanager.setNewConstantIndex()
        self.cmanager.constants_indices.ctx.add(ctx_game)

        observations, actions, goal = example
        for obs, a in zip(observations, actions):
            ctx_move = self.cmanager.setNewConstantIndex()
            self.cmanager.constants_indices.ctx.add(ctx_move)

            # action < move + ctx_move
            term_left = [(constants_actions[a])]
            term_right = [(ctx_move)]
            for ch, ob in enumerate(obs):
                term_right.append((constants_observations[ch][0], ob))
                term_right.append((constants_observations[ch][1], -ob))

            pos_rels.append(
                sc.relation(
                    self.LCS(term_left),
                    self.LCS(term_right),
                    True,
                    self.alg.generation,
                    region=1,
                )
            )

            # !action !< move + ctx_move
            constants_not_actions = constants_actions.copy()
            constants_not_actions.remove(constants_actions[a])
            for not_action in constants_not_actions:
                term_left = [(not_action)]
                neg_rels.append(
                    sc.relation(
                        self.LCS(term_left),
                        self.LCS(term_right),
                        False,
                        self.alg.generation,
                        region=1,
                    )
                )

            # ctx_game < ctx_move
            pos_rels.append(
                sc.relation(
                    self.LCS([(ctx_game)]),
                    self.LCS([(ctx_move)]),
                    True,
                    self.alg.generation,
                    region=1,
                )
            )

        # goal < ctx_game
        if goal:
            c_goal = constants_goal["win"]
            c_not_goal = constants_goal["lose"]
        else:
            c_goal = constants_goal["lose"]
            c_not_goal = constants_goal["win"]
        pos_rels.append(
            sc.relation(
                self.LCS([(c_goal)]),
                self.LCS([(ctx_game)]),
                True,
                self.alg.generation,
                region=1,
            )
        )
        # !goal !< ctx_game
        neg_rels.append(
            sc.relation(
                self.LCS([(c_not_goal)]),
                self.LCS([(ctx_game)]),
                False,
                self.alg.generation,
                region=1,
            )
        )

        return pos_rels, neg_rels

    def test(self, las, env):
        constants_observations = self.cmanager.constants_indices.observations
        constants_goal_win = self.cmanager.constants_indices.goal["win"]
        all_moves = []

        obs, _ = env.reset()

        for _ in range(MAX_STEPS):
            # Calc next move
            bTerm = set()
            for ch, ob in enumerate(obs):
                bTerm.add(
                    self.cmanager.getConstantInChain(constants_observations[ch][0], ob)
                )
                bTerm.add(
                    self.cmanager.getConstantInChain(constants_observations[ch][1], -ob)
                )

            bTermAtoms = set()
            for c in bTerm:
                bTermAtoms |= las[c]

            actions = self.cmanager.constants_indices.actions
            actions_dis = []
            for a in actions:
                actions_dis.append([a, las[a] - bTermAtoms])
            random.shuffle(actions_dis)
            actions_dis.sort(key=lambda pair: len(pair[1]))
            next_move = actions_dis[0][0]
            all_moves.append(next_move)

            # Step
            obs, reward, terminated, _, _ = env.step(next_move)

            if terminated:
                break

        return reward > 0.5, all_moves

"""
# Coordinate Systems for `.csv` and `print(numpy)`

X points down (rows); Y points right (columns); Z would point outwards.

*--> Y (columns)
|
v
X (rows)
"""
UP = 0
UP_RIGHT = 1
RIGHT = 2
DOWN_RIGHT = 3
DOWN = 4
DOWN_LEFT = 5
LEFT = 6
UP_LEFT = 7

SIM_PERIOD_MS = 500.0

env = gym.make(
    "gymnasium_playground/FakeIroning-v0",
    render_mode=None,  # "human", "text", None
    inFileStr="map1-ironing.csv",
    initX=2,
    initY=2,
    # goalX=7,
    # goalY=2,
)

# Constants
solver = Solver()
solver.create_constants(env)

cOrange = "\u001b[33m"
cGreen = "\u001b[36m"
cReset = "\u001b[0m"

def generateLine(env):
    observations = []
    actions = []

    obs, _ = env.reset()
    observations.append(obs)
    for _ in range(MAX_STEPS):
        a = env.action_space.sample()
        actions.append(a)

        obs, reward, terminated, _, _ = env.step(a)
        observations.append(obs)

        if terminated:
            break

    # Reach goal: 1, stay in path: 0, get out of path: -0.5
    if reward > 0.5:
        goal = True
    else:
        goal = False

    return observations, actions, goal

def generate_examples(env, pBatchSize, nBatchSize):
    win_examples = []
    lose_examples = []
    while len(win_examples) < pBatchSize or len(lose_examples) < nBatchSize:
        line = generateLine(env)
        if line[2]:
            if len(win_examples) < pBatchSize:
                win_examples.append(line)
        else:
            if len(lose_examples) < nBatchSize:
                lose_examples.append(line)
    return win_examples, lose_examples

for i in range(NUM_ITER_TRAINING):
    print("<Generating training set", end="", flush=True)
    # generate games
    win_batch, lose_batch = generate_examples(
        env,
        WIN_BATCH_SIZE,
        LOSE_BATCH_SIZE,
    )
    # turn games into aml relations
    pbatch = []
    nbatch = []
    for ex in win_batch:
        prels, nrels = solver.example_to_relations(ex)
        pbatch.extend(prels)
        nbatch.extend(nrels)
    print(">")

    solver.batchLearner.enforce(pbatch, nbatch)

    print(
        f"{cOrange}BATCH#: {i}{cReset}",
        f"seen ({solver.batchLearner.pcount}, {solver.batchLearner.ncount})",
        f"Generation: {solver.alg.generation}",
        f"Reserve size: {len(solver.batchLearner.reserve)}",
    )

    # Test
    if (i + 1) % TEST_EVERY == 0:
        target = solver.batchLearner.reserve
        allConstants = sc.CSegment(
            solver.cmanager.getConstantSet().constants - solver.cmanager.constants_indices.ctx
        )
        las = ql.calculateLowerAtomicSegment(target, allConstants, True)

        count_win = 0
        count_lose = 0
        for _ in range(NUM_TESTS):
            res, all_moves = solver.test(las, env)
            if res:
                count_win += 1
            else:
                count_lose += 1
            print(f"{cGreen}Wins: {count_win} / Loses: {count_lose}{cReset}")
            print(all_moves)

    # Reserve Update
    print("<Updating reserve...", end="", flush=True)
    solver.cmanager.updateConstantsTo(
        solver.alg.atomization, solver.batchLearner.reserve, solver.alg.exampleSet
    )
    print(">")
