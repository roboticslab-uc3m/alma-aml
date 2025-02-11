import aml_engine as aml

import random
import math
import sys
import os
import pickle

import pygame
import numpy as np
from os import path

DATASET_DIR = "dataset"

NUM_OUTPUT_SAMPLES = 10

IMAGE_SIZE = (100, 100)  # (300, 300)
CLOTH_SIZE = (70, 56)   # (250, 150)
CLOTH_TL = (15, 22) # (25, 75)
# make sure the paper is folded at least with FOLD_MARGIN pixels inside
FOLD_MARGIN = 5 # original 1

RANDOM_SCALE_MAX = 0.25 # Shrinking variation. Set to 0 for False
RANDOM_ROTATE = True

# rounds the vaues while training (does not have an effect at test time)
ROUND = True
# minimal distance from pick point to consider an output incorrect (does not have an effect at test time)
RADIO = 2

RANSEED = 123456789
MAX_ITER = 100000000
INITIAL_ZERO_CONST = -1

# ------------------------------------------------------------------------------
labels = np.loadtxt(path.join(DATASET_DIR,"labels.txt"), delimiter=',', usecols=range(1,5))
# ------------------------------------------------------------------------------

def scale(origin, point, scale):
    ox, oy = origin
    px, py = point
    qx = ox + (px - ox) * scale
    qy = oy + (py - oy) * scale
    return qx, qy

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    Modified from [Mark Dickinson](https://stackoverflow.com/users/270986):
    - <https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python>
    """
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def reflect(p1, p2, pin):
    """
    Modified from [MBo](https://stackoverflow.com/users/844416):
    - <https://stackoverflow.com/questions/65252818/quickly-compute-reflection-of-point-about-line-described-by-two-points>
    """
    x12 = p2[0] - p1[0]
    y12 = p2[1] - p1[1]
    xxp = pin[0] - p1[0]
    yyp = pin[1] - p1[1]
    dotp = x12 * xxp + y12 * yyp
    dot12 = x12 * x12 + y12 * y12
    coeff = dotp / dot12
    lx = p1[0] + x12 * coeff
    ly = p1[1] + y12 * coeff
    return (2*lx-pin[0], 2*ly-pin[1])



def imageFileToMatrix(image_name):
    # load image and transform into array
    surface = pygame.image.load(image_name)
    pixel_array = pygame.PixelArray(surface)
    retMatrix = []
    for y in range(surface.get_height()):
        row = []
        for x in range(surface.get_width()):
            color = surface.unmap_rgb(pixel_array[x, y])
            # row.append(color[:3])  # Only take RGB values, exclude alpha
            row.append(int(color[1]/100))  # Only take RGB values, exclude alpha
        # print(row)
        retMatrix.append(row)

    return retMatrix


def imageWindowToMatrix(window):
    pixel_array = pygame.PixelArray(window)
    retMatrix = []
    for y in range(window.get_height()):
        row = []
        for x in range(window.get_width()):
            color = window.unmap_rgb(pixel_array[x, y])
            # row.append(color[:3])  # Only take RGB values, exclude alpha
            row.append(int(color[1]/100))  # Only take RGB values, exclude alpha
        # print(row)
        retMatrix.append(row)

    return retMatrix

def createExample(window):
    # note: offset 1 to avoid dot12 ZeroDivisionError: division by zero
    fold_x = random.randint(FOLD_MARGIN, CLOTH_SIZE[0]-FOLD_MARGIN) # (CLOTH_SIZE[0]/2, CLOTH_SIZE[0])
    fold_y = random.randint(FOLD_MARGIN, CLOTH_SIZE[1]-FOLD_MARGIN) # (CLOTH_SIZE[1]/2, CLOTH_SIZE[1])

    p = [CLOTH_TL,
        (CLOTH_TL[0]+CLOTH_SIZE[0], CLOTH_TL[1]),
        (CLOTH_TL[0]+CLOTH_SIZE[0], CLOTH_TL[1]+fold_y),
        (CLOTH_TL[0]+fold_x,        CLOTH_TL[1]+CLOTH_SIZE[1]),
        (CLOTH_TL[0],               CLOTH_TL[1]+CLOTH_SIZE[1])]
    p_place = (CLOTH_TL[0]+CLOTH_SIZE[0], CLOTH_TL[1]+CLOTH_SIZE[1])
    p_pick = reflect(p[2], p[3], p_place)

    image_center = (IMAGE_SIZE[0]/2,IMAGE_SIZE[1]/2)

    if RANDOM_ROTATE:
        angle = random.uniform(0, 6.28)
        p = [rotate(image_center, item, angle) for item in p]
        p_place = rotate(image_center, p_place, angle)
        p_pick = rotate(image_center, p_pick, angle)

    if RANDOM_SCALE_MAX != 0:
        scale_value = random.uniform(1-RANDOM_SCALE_MAX, 1) # 1+RANDOM_SCALE_MAX
        p = [scale(image_center, item, scale_value) for item in p]
        p_place = scale(image_center, p_place, scale_value)
        p_pick = scale(image_center, p_pick, scale_value)

    window.fill((0, 0, 0))

    pygame.draw.polygon(window, (100, 100, 100), (p[0], p[1], p[2], p[3], p[4]))
    pygame.draw.polygon(window, (200, 200, 200), (p[2], p[3], p_pick))

    if ROUND:
        p_pick = (round(p_pick[0]), round(p_pick[1]))
        p_place = (round(p_place[0]), round(p_place[1]))

    return window, p_pick, p_place

# encode an image as a set of constants
def exampleToConstants(intensityMatrix):
    ss = IMAGE_SIZE[0] * IMAGE_SIZE[1]
    j = 0
    ret = [-1]*ss
    for x in range(IMAGE_SIZE[0]):
        for y in range(IMAGE_SIZE[1]):
            if intensityMatrix[x][y] == 0:
                ret[j] = INITIAL_ZERO_CONST + j
            elif intensityMatrix[x][y] == 1:
                ret[j] = INITIAL_ZERO_CONST + j + ss
            elif intensityMatrix[x][y] == 2:
                ret[j] = INITIAL_ZERO_CONST + j + 2*ss
            else:
                print(intensityMatrix[x][y])
                raise ValueError
            j += 1
    return set(ret)

# ------------------------------------------------------------------------------

def LCS(param, cmanager):
    if aml.LCSegment == aml.LCSegment_impl_wChains:
        return aml.LCSegment(param, cmanager)
    else:
        return aml.LCSegment(param)

# construnct the output term with the 2 value4s for pick and the 2 values for place
def getOTerm(eid):
    ret = []
    ret.append((0, eid.pick[0]))
    ret.append((1, -eid.pick[0]))

    ret.append((2, eid.pick[1]))
    ret.append((3, -eid.pick[1]))

    ret.append((4, eid.place[0]))
    ret.append((5, -eid.place[0]))

    ret.append((6, eid.place[1]))
    ret.append((7, -eid.place[1]))

    return set(ret)

# construct an example
def getFoldExample(eid, idx):
    #j#window = eid.window
    #j#window, p_pick, p_place = createExample(window)
    #j#retMatrix = imageWindowToMatrix(window)
    image_name = path.join(DATASET_DIR,"image"+str(idx)+".png")
    retMatrix = imageFileToMatrix(image_name)
    term = exampleToConstants(retMatrix)
    print("labels[idx]",labels[idx])

    eid.pick = (0, 0) #j#tmp
    eid.place = (0, 0) #j#tmp

    return set(term), getOTerm(eid)

# generate a new dataset
def generateDataset(
    eid,
    idx_init,
    pSize,
    nSize,
    generation,
    region,
):
    print("<Generating set", end="", flush=True)
    pDataSet = []
    nDataSet = []
    oTermList = []
    cmanager = eid.cmanager

    RADIO = 2

    exampleTerm, oTerm = getFoldExample(eid, idx_init)
    exampleTerm = LCS(exampleTerm, cmanager)
    oTerm = LCS(oTerm, cmanager)

    pick = eid.pick
    place = eid.place
    oTermList.append([oTerm, pick, place, exampleTerm])

    pRel = aml.duple(oTerm, exampleTerm, True, generation, region)
    pRel.pick = pick
    pRel.place = place
    pDataSet.append(pRel)

    oterm1, pick1, place1, exampleTerm1 = oTermList[
        random.randint(0, len(oTermList)) - 1
    ]
    oterm2, pick2, place2, exampleTerm2 = oTermList[
        random.randint(0, len(oTermList)) - 1
    ]
    if abs((pick1[0] - pick2[0])**2 + (pick1[1] - pick2[1])**2) > RADIO**2:
        nRel = aml.duple(oterm2, exampleTerm1, False, generation, region)
        nDataSet.append(nRel)

    print(">")
    return pDataSet, nDataSet

# generate a test dataset
def generateTestSet(
    eid,
    idx_init,
    size,
    generation,
    region,
):
    pTest, nTest = generateDataset(
            eid,
            idx_init,
            size,
            size,
            generation,
            region,
    )

    pTest.extend(nTest)
    return pTest

# Obtaines the output for a given image
def testOutputField(cmanager, las, wH, up, down, maxval):
    verbose = False
    # up: number idnetfying the up chain of the output field
    # down: number idnetfying the down chain of the output field

    minval = math.inf
    select = []

    # scan the chains and select the point with fewr atom misses
    #  if there are more than one point with the same number of misses report all
    for value in range(0, maxval):
        c_up = cmanager.constOfChains[up].get(value, -1)
        c_down = cmanager.constOfChains[down].get(-value, -1)
        if c_up == -1 or c_down == -1:
            if (verbose): print(value, ": none")
        elif (c_up in las) and (c_down in las):
            fieldLas = las[c_up] | las[c_down]
            # disc: number of misses
            disc = len(fieldLas - wH.las)
            if (verbose): print(value, ":", disc)
            if minval > disc:
                minval = disc
                select = [value]
            elif minval == disc:
                select.append(value)
        else:
            if (verbose): print(value, ": none")
    print("result: ", select, "misses", minval)



def testModel(window,  name, constants, idx_init):
    #Load the model`

    print("WARNING: Loading is slow")
    cmanager, atomization = aml.loadAtomizationFromFileUsingBitarrays(name)  #
    print("atomization", len(atomization))

    # preprocessing (can be slow)
    # filter out size one (optional)
    atomization = [at for at in atomization if not at.isSizeOne()]
    print("atomization:", len(atomization), "atoms.")

    print("preprocessing can take a few minutes...")

    # obtain or create an output constant for every pixel value at each point of the 4x2 chains
    fields = [None]*4
    for s in [0, 1, 2, 3]:
        up = 2*s
        down = 2*s +1
        cFromVal = []
        for value in range(0, IMAGE_SIZE[s % 2]):
            cu = cmanager.getOrSetConstantIndexFromChainAndValue(up, value)
            cd = cmanager.getOrSetConstantIndexFromChainAndValue(down, -value)
            constants.add(cu)
            constants.add(cd)
            cFromVal.append([cu, cd])
        fields[s] = cFromVal
    testConsts = aml.CSegment(constants)

    # associate atoms to constents
    las = aml.calculateLowerAtomicSegment(atomization, testConsts, True)

    # start testing
    # generate a test set
    eid = aml.exampleInterpretationData()
    eid.window = window
    eid.cmanager = cmanager
    sizeOfTest =  1 #j# 10
    generation = 0
    region = 1
    testSet = generateTestSet(
                eid,
                idx_init,
                sizeOfTest,
                generation,
                region,
            )
    print("len(testSet)", len(testSet))
    testSet = [r for r in testSet if r.positive]

    # associate atoms to each term mentioned in the test set
    testSpace = aml.termSpace()
    for rel in testSet:
        rel.wL = testSpace.add(rel.L)
        rel.wH = testSpace.add(rel.R)
    print("len(cmanager.getConstantSet())", len(cmanager.getConstantSet()))
    testSpace.calculateLowerAtomicSegments(atomization, las)

    # print ressults for eahc item of the test set
    for r in testSet:
        print("Correct val pick[0]:", r.pick[0])
        testOutputField(cmanager, las, r.wH, 0, 1, IMAGE_SIZE[0])

        print("Correct val pick[1]:", r.pick[1])
        testOutputField(cmanager, las, r.wH, 2, 3, IMAGE_SIZE[1])

        print("Correct val place[0]:", r.place[0])
        testOutputField(cmanager, las, r.wH, 4, 5, IMAGE_SIZE[0])

        print("Correct val place[0]:", r.place[1])
        testOutputField(cmanager, las, r.wH, 6, 7, IMAGE_SIZE[1])

        input("next?")

# ------------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(RANSEED)
    sys.setrecursionlimit(100000000)

    pygame.init()
    window = pygame.display.set_mode(IMAGE_SIZE)

    # input constants. 3 colors.
    constants = set([c for c in range(0, 3 * IMAGE_SIZE[0] * IMAGE_SIZE[1])])
    # test a model
    # name = "ATOMIZATIONS/PAPERFOLD_R_2NOROUND_50"
    name = "PAPERFOLD_200"
    # name = "ATOMIZATIONS/PAPERFOLD_NOTROUND_100"
    testModel(window, name, constants, 10000)

    pygame.quit()
