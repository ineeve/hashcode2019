from __future__ import print_function
from config import Config
from ortools.linear_solver import pywraplp
import math
import copy

chunkSize = 20
sumVAR = []

def splitDataInChunks(data):
    chunks = []
    i = 0
    while i < len(data):
        chunks.append(data[i:i+chunkSize])
        i+=chunkSize
    return chunks

def readFile(filename):
    file = open(filename,'r')
    firstLine = file.readline().split(' ')
    N = int(firstLine[0])
    c = Config(N)
    photos = []
    for line in file.readlines():
        photos.append(line.replace('\n','').split(' '))

    c.setData(photos)
    return c

def createDecisionVars(chunk, solver, chunkId):
    global sumVAR
    decVars = []
    for slide in range(0, getNumSlides(chunk)):
        decVars.append([])
        for photoIdx in range(0,len(chunk)):
            decVars[slide].append(solver.IntVar(0, 1, str(slide + chunkId*chunkSize)+'_'+str(photoIdx + chunkId*chunkSize)))
    sumVAR += decVars
    return decVars

def createObjectiveVars(chunk, solver):
    objVars = []
    for slide in range(1, getNumSlides(chunk)):
        objVars.append([])
        for photoIdx in range(0,len(chunk)):
            objVars[slide-1].append(solver.IntVar(0, solver.infinity(), str(slide)+'_'+str(photoIdx)+'_trans'))
    return objVars

def createRestrictions(chunk, solver, decVars, objVars):
    slidesInChunk = getNumSlides(chunk)
    # In each slide there is only 1 h photo or 2 vertical photos
    for slide in range(0, slidesInChunk):
        constraint1 = solver.Constraint(2, 2)
        for photoIdx in range(0,len(chunk)):
            decVar = decVars[slide][photoIdx]
            if getOrientation(chunk, photoIdx)=='H':
                constraint1.SetCoefficient(decVar, 2)
            else:
                constraint1.SetCoefficient(decVar, 1)

    # Each photo is 0 or 1 times in a slide            
    for photoIdx in range(0,len(chunk)):
        constraint2 = solver.Constraint(0,1)
        for slide in range(0, slidesInChunk):
            decVar = decVars[slide][photoIdx]
            constraint2.SetCoefficient(decVar, 1)

    # Transition between slides
    for slide in range(1, slidesInChunk):
        for photoIdx in range(0, len(chunk)):
            transConstraint = solver.Constraint(0, 0)
            transConstraint.SetCoefficient(objVars[slide-1][photoIdx], 1)
            for prevPhotoIdx in range(0, len(chunk)):
                prevSlideDecVar = decVars[slide-1][prevPhotoIdx]
                interest = calculateInterestTags(getTags(chunk, photoIdx), getTags(chunk, prevPhotoIdx))
                transConstraint.SetCoefficient(prevSlideDecVar, -interest)


def calculateInterestTags(tags1, tags2):
    commontagsLen = len([value for value in tags1 if value in tags2]) 
    tagsin1NotIn2 = len([value for value in tags1 if value not in tags2])
    tagsIn2NotIn1 = len([value for value in tags2 if value not in tags1])
    return min(commontagsLen, min(tagsin1NotIn2, tagsIn2NotIn1))

def createObjectiveFunction(conf, solver, decVars, objVars):
    objective = solver.Objective()
    for slide in objVars:
        for objVar in slide:
            objective.SetCoefficient(objVar, 1)        
    objective.SetMaximization()

def output(filename):
    file = open(filename,'w')
    file.write(str(len(sumVAR)) + '\n')
    for slide in sumVAR:
        for decVar in slide:
            try:
                _, photoInd = decVar.name().split('_')
                if decVar.solution_value() == 1:
                    print(decVar.name())
                    file.write(photoInd + ' ')
            except Exception as e: 
                #I dont know why it happens, but I'm just ignoring it
                print(e)
        file.write('\n')
    file.close()

def getOrientation(chunk, photoIdx):
    return chunk[photoIdx][0]

def getTags(chunk, photoIdx):
    return chunk[photoIdx][2:]

def getNumSlides(chunk):
    nSlides = 0
    for photo in chunk:
        if photo[0] == 'H':
            nSlides += 1
        else:
            nSlides += 0.5
    
    return math.floor(nSlides)

def main():
    filename = 'c_memorable_moments.txt'
    conf = readFile(filename)
    chunks = splitDataInChunks(conf.data)
    for chunkId,chunk in enumerate(chunks):
    
        solver = pywraplp.Solver('SolveIntegerProblem',
                            pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        decVars = createDecisionVars(chunk, solver, chunkId)
        objVars = createObjectiveVars(chunk, solver)
        createRestrictions(chunk, solver, decVars, objVars)
        createObjectiveFunction(chunk, solver, decVars, objVars)

        """Solve the problem and print the solution."""
        result_status = solver.Solve()
        print(result_status)

        print('Number of variables =', solver.NumVariables())
        print('Number of constraints =', solver.NumConstraints())

        # The objective value of the solution.
        print('Optimal objective value = %d' % solver.Objective().Value())
        print()
        # The value of each variable in the solution.
        """
        for slide in decVars:
            for decVar in slide:
                print('%s = %d' % (decVar.name(), decVar.solution_value()))
        """
        
    output(filename + '_out')

main()

