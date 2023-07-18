import gymnasium as gym
import gymnasium_playground_fakeironing

import aml
from aml import amlSimpleLibrary as sc
from aml import amlAuxiliaryLibrary as ql

import numpy as np

import random

NUM_EPOCHS = 30
MAX_STEPS = 500  # max length of line
NUM_TESTS = 30
TEST_EVERY = 10

WIN_EPISODES = 10
LOSE_EPISODES = 10

EPSILON_GREEDY = 0.1

class ConstantsIndices:
    def __init__(self):
        self.observations = None
        self.actions = None
        self.goal = None
        self.ctx = set()


def make_environment(desired_reward):
    return gym.make(
        "gymnasium_playground/FakeIroning-v0",
        render_mode=None,
        inFileStr="map1-ironing.csv",
        initX=2,
        initY=2,
        desired_reward=desired_reward,
    )


def generate_examples(model, pBatchSize, nBatchSize):
    win_examples = []
    lose_examples = []

    while len(win_examples) < pBatchSize or len(lose_examples) < nBatchSize:
        line = observations, actions, rewards = model.run_episode()

        if rewards[-1] >= model.env.desired_reward:
            if len(win_examples) < pBatchSize:
                win_examples.append(line)
        else:
            if len(lose_examples) < nBatchSize:
                lose_examples.append(line)

    return win_examples, lose_examples


def batchLearning(model, params):
    cOrange = "\u001b[33m"
    cGreen = "\u001b[36m"
    cReset = "\u001b[0m"

    for epoch in range(NUM_EPOCHS):
        model.env = make_environment(epoch + 1)
        print("<Generating training set", end="", flush=True)

        # generate games
        win_batch, lose_batch = generate_examples(
            model,
            params.win_batchSize,
            params.lose_batchSize,
        )

        # turn games into aml relations
        pbatch = []
        nbatch = []
        for ex in win_batch:
            prels, nrels = model.train(*ex) # (states, actions, rewards)
            pbatch.extend(prels)
            nbatch.extend(nrels)
        print(">")

        model.batchLearner.enforce(pbatch, nbatch)

        print(
            f"{cOrange}EPOCH#: {epoch}{cReset}",
            f"seen ({model.batchLearner.pcount}, {model.batchLearner.ncount})",
            f"Generation: {model.alg.generation}",
            f"Reserve size: {len(model.batchLearner.reserve)}",
        )

        # Test
        if (epoch + 1) % TEST_EVERY == 0:
            count_win = 0
            count_lose = 0

            for _ in range(NUM_TESTS):
                states, actions, rewards = model.run_episode()

                if rewards[-1] >= model.env.desired_reward:
                    count_win += 1
                else:
                    count_lose += 1

                print(f"{cGreen}Wins: {count_win} / Loses: {count_lose} / Reward: {rewards[-1]} / Steps: {len(actions)}{cReset}")
                print(actions)

        # Reserve Update
        print("<Updating reserve...", end="", flush=True)
        model.alg.cmanager.updateConstantsTo(
            model.alg.atomization, model.batchLearner.reserve, model.alg.exampleSet
        )
        print(">")


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


class AmlModel:
    def __init__(self, batchLearner, alg):
        self.batchLearner = batchLearner
        self.alg = alg
        self.env = make_environment(0)

        self._create_constants()

    def _create_constants(self):
        self.alg.cmanager.constants_indices = ConstantsIndices()

        c_actions = []
        if isinstance(self.env.action_space, gym.spaces.discrete.Discrete):
            for ac in range(self.env.action_space.n):
                c = self.alg.cmanager.setNewConstantIndexWithName("A[{ac}]")
                c_actions.append(c)

        c_observations = []
        if isinstance(self.env.observation_space, gym.spaces.box.Box):
            for _ in range(len(self.env.observation_space.low)):
                c1 = self.alg.cmanager.setNewChainIndex()  # up
                c2 = self.alg.cmanager.setNewChainIndex()  # down
                c_observations.append([c1, c2])

        c1 = self.alg.cmanager.setNewConstantIndexWithName("win")
        c2 = self.alg.cmanager.setNewConstantIndexWithName("lose")
        c_goal = {"win": c1, "lose": c2}

        self.alg.cmanager.constants_indices.observations = c_observations
        self.alg.cmanager.constants_indices.actions = c_actions
        self.alg.cmanager.constants_indices.goal = c_goal

    def predict(self, state):
        if np.random.random() < EPSILON_GREEDY:
            next_move = self.env.action_space.sample()
        else:
            constants_observations = self.alg.cmanager.constants_indices.observations
            target = self.batchLearner.reserve

            allConstants = sc.CSegment(
                self.alg.cmanager.getConstantSet().constants - self.alg.cmanager.constants_indices.ctx
            )

            las = ql.calculateLowerAtomicSegment(target, allConstants, True)
            bTerm = set()

            try:
                for ch, ob in enumerate(state):
                    bTerm.add(
                        self.alg.cmanager.getConstantInChain(constants_observations[ch][0], ob)
                    )
                    bTerm.add(
                        self.alg.cmanager.getConstantInChain(constants_observations[ch][1], -ob)
                    )

                    bTermAtoms = set()

                    for c in bTerm:
                        bTermAtoms |= las[c]

                    actions_alg = self.alg.cmanager.constants_indices.actions
                    actions_dis = []

                    for a in actions_alg:
                        actions_dis.append([a, las[a] - bTermAtoms])

                    random.shuffle(actions_dis)
                    actions_dis.sort(key=lambda pair: len(pair[1]))
                    next_move = actions_dis[0][0]
            except ValueError:
                print('ValueError!')
                next_move = self.env.action_space.sample()

        return next_move

    def run_episode(self):
        state, _ = self.env.reset()

        observations = []
        actions = []
        rewards = []

        for _ in range(MAX_STEPS):
            observations.append(state)

            action = model.predict(state)
            actions.append(action)

            statePrime, reward, terminated, _, _ = self.env.step(action)
            rewards.append(reward)

            if terminated:
                break

            state = statePrime

        return observations, actions, rewards

    def LCS(param, cmanager):
        if sc.LCSegment == sc.LCSegment_impl_wChains:
            return sc.LCSegment(param, cmanager)
        else:
            return sc.LCSegment(param)

    def train(self, states, actions, rewards):
        pos_rels = []
        neg_rels = []

        constants_observations = self.alg.cmanager.constants_indices.observations
        constants_actions = self.alg.cmanager.constants_indices.actions
        constants_goal = self.alg.cmanager.constants_indices.goal

        ctx_game = self.alg.cmanager.setNewConstantIndex()
        self.alg.cmanager.constants_indices.ctx.add(ctx_game)

        for state, action in zip(states, actions):
            ctx_move = self.alg.cmanager.setNewConstantIndex()
            self.alg.cmanager.constants_indices.ctx.add(ctx_move)

            # action < move + ctx_move
            term_left = [(constants_actions[action])]
            term_right = [(ctx_move)]
            for ch, ob in enumerate(state):
                term_right.append((constants_observations[ch][0], ob))
                term_right.append((constants_observations[ch][1], -ob))

            pos_rels.append(
                sc.relation(
                    AmlModel.LCS(term_left, self.alg.cmanager),
                    AmlModel.LCS(term_right, self.alg.cmanager),
                    True,
                    model.alg.generation,
                    region=1,
                )
            )

            # !action !< move + ctx_move
            constants_not_actions = constants_actions.copy()
            constants_not_actions.remove(constants_actions[action])
            for not_action in constants_not_actions:
                term_left = [(not_action)]
                neg_rels.append(
                    sc.relation(
                        AmlModel.LCS(term_left, self.alg.cmanager),
                        AmlModel.LCS(term_right, self.alg.cmanager),
                        False,
                        model.alg.generation,
                        region=1,
                    )
                )

            # ctx_game < ctx_move
            pos_rels.append(
                sc.relation(
                    AmlModel.LCS([(ctx_game)], self.alg.cmanager),
                    AmlModel.LCS([(ctx_move)], self.alg.cmanager),
                    True,
                    model.alg.generation,
                    region=1,
                )
            )

        # goal < ctx_game
        if rewards[-1] >= self.env.desired_reward:
            c_goal = constants_goal["win"]
            c_not_goal = constants_goal["lose"]
        else:
            c_goal = constants_goal["lose"]
            c_not_goal = constants_goal["win"]

        pos_rels.append(
            sc.relation(
                AmlModel.LCS([(c_goal)], self.alg.cmanager),
                AmlModel.LCS([(ctx_game)], self.alg.cmanager),
                True,
                model.alg.generation,
                region=1,
            )
        )
        # !goal !< ctx_game
        neg_rels.append(
            sc.relation(
                AmlModel.LCS([(c_not_goal)], self.alg.cmanager),
                AmlModel.LCS([(ctx_game)], self.alg.cmanager),
                False,
                model.alg.generation,
                region=1,
            )
        )

        return pos_rels, neg_rels


class TrainingParameters:
    def __init__(self):
        self.win_batchSize = 0
        self.lose_batchSize = 0


params = TrainingParameters()
params.win_batchSize = WIN_EPISODES
params.lose_batchSize = LOSE_EPISODES

alg = sc.embedder()
batchLearner = ql.batchLearner(alg)

batchLearner.useReduceIndicators = True
batchLearner.enforceTraceConstraints = True
batchLearner.byQuotient = False
batchLearner.storePositives = True
batchLearner.alg.verbose = False
batchLearner.verbose = False

model = AmlModel(batchLearner, alg)

batchLearning(model, params)
