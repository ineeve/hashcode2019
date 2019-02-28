from __future__ import print_function
from config import Config
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
    for slide in range(0, conf.getNumSlides()):
        decVars.append([])
        for photoIdx in range(0,len(conf.data)):
            decVars[slide].append(solver.IntVar(0, 1, str(slide)+'_'+str(photoIdx)))
    return decVars

def createObjectiveVars(conf, solver):
    objVars = []
    for slide in range(1, conf.getNumSlides()):
        objVars.append([])
        for photoIdx in range(0,len(conf.data)):
            objVars[slide-1].append(solver.IntVar(0, solver.infinity(), str(slide)+'_'+str(photoIdx)+'_trans'))
    return objVars

def createRestrictions(conf, solver, decVars, objVars):
    # In each slide there is only 1 h photo or 2 vertical photos
    for slide in range(0, conf.getNumSlides()):
        constraint1 = solver.Constraint(2, 2)
        for photoIdx in range(0,len(conf.data)):
            decVar = decVars[slide][photoIdx]
            if conf.getOrientation(photoIdx)=='H':
                constraint1.SetCoefficient(decVar, 2)
            else:
                constraint1.SetCoefficient(decVar, 1)

    # Each photo is 0 or 1 times in a slide            
    for photoIdx in range(0,len(conf.data)):
        constraint2 = solver.Constraint(0,1)
        for slide in range(0, conf.getNumSlides()):
            decVar = decVars[slide][photoIdx]
            constraint2.SetCoefficient(decVar, 1)

    # Transition between slides
    for slide in range(1, conf.getNumSlides()):
        for photoIdx in range(0, len(conf.data)):
            transConstraint = solver.Constraint(0, 0)
            transConstraint.SetCoefficient(objVars[slide-1][photoIdx], 1)
            for prevPhotoIdx in range(0, len(conf.data)):
                prevSlideDecVar = decVars[slide-1][prevPhotoIdx]
                interest = calculateInterestTags(conf.getTags(photoIdx), conf.getTags(prevPhotoIdx))
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

def output(filename, conf, decVars):
    file = open(filename,'w')
    file.write(str(conf.getNumSlides()) + '\n')
    for slide in decVars:
        for decVar in slide:
            slideInd, photoInd = decVar.name().split('_')
            if decVar.solution_value() == 1:
                file.write(photoInd + ' ')
        file.write('\n')

def main():
    filename = 'c_memorable_moments.txt'
    conf = readFile(filename)
    solver = pywraplp.Solver('SolveIntegerProblem',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    decVars = createDecisionVars(conf, solver)
    objVars = createObjectiveVars(conf, solver)
    createRestrictions(conf, solver, decVars, objVars)
    createObjectiveFunction(conf, solver, decVars, objVars)

    """Solve the problem and print the solution."""
    result_status = solver.Solve()
    print(result_status)

    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())

    # The objective value of the solution.
    print('Optimal objective value = %d' % solver.Objective().Value())
    print()
    # The value of each variable in the solution.

    for slide in decVars:
        for decVar in slide:
            print('%s = %d' % (decVar.name(), decVar.solution_value()))

    output(filename + '_out', conf, decVars)

main()

