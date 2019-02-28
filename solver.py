from config import Config
from __future__ import print_function
from ortools.linear_solver import pywraplp

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

def createDecisionVars(conf, solver):
    decVars = []
    nSlides = conf.N
    for slide in range(0, nSlides):
        decVars[slide] = []
        for photoIdx in range(0,len(conf.data)):
            decVars[slide].append(solver.IntVar(0, 1, str(slide)+'_'+str(photoIdx)))
    return decVars

def createObjectiveVars(conf, solver):
    objVars = []
    nSlides = conf.N
    for slide in range(0, nSlides):
        objVars[slide] = []
        for photoIdx in range(0,len(conf.data)):
            objVars[slide].append(solver.IntVar(0, solver.infinity(), str(slide)+'_'+str(photoIdx)+'_trans'))
    return objVars

def createRestrictions(conf, solver, decVars, objVars):
    # In each slide there is only 1 h photo or 2 vertical photos
    for slide in range(0, conf.N):
        constraint1 = solver.Constraint(2, 2)
        for photoIdx in range(0,len(conf.data)):
            decVar = decVars[slide][photoIdx]
            if conf.data[0]=='H':
                constraint1.SetCoefficient(decVar, 2)
            else:
                constraint1.SetCoefficient(decVar, 1)

    # Each photo is 0 or 1 times in a slide            
    for photoIdx in range(0,len(conf.data)):
        constraint2 = solver.Constraint(0,1)
        for slide in range(0, conf.N):
            decVar = decVars[slide][photoIdx]
            constraint2.setCoefficient(decVar, 1)

    # Transition between slides
    for slide in range(0, conf.N):
        transConstraint = solver.Constraint(0, solver.Infinity())



def calculate_interest(tags1, tags2):
    commontagsLen = len([value for value in tags1 if value in tags2]) 
    tagsin1NotIn2 = len([value for value in tags1 if value not in tags2])
    tagsIn2NotIn1 = len([value for value in tags2 if value not in tags1])
    return min(commontagsLen, min(tagsin1NotIn2, tagsIn2NotIn1))

def createObjectiveFunction(conf, solver, decVars, objVars):
      # Minimize c1 + c2 + c3 + c4
    objective = solver.Objective()
    for objVar in objVars:
        objective.SetCoefficient(objVar, 1)
    objective.SetMaximization()


def main():
    conf = readFile('a_example.in')
    solver = pywraplp.Solver('SolveIntegerProblem',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    decVars = createDecisionVars(conf, solver)
    objVars = createObjectiveVars(conf, solver)
    createRestrictions(conf, solver, decVars, objVars)
    createObjectiveFunction(conf, solver, decVars, objVars)
    solver.Solve()

main()

