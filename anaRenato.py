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
    verticalPhotos = []
    horPhotos = []
    for idx, photo in enumerate(photos):
        if photo[0]=='V':
            verticalPhotos.append((photo, idx))
        else:
            horPhotos.append((photo, idx))
    newPhotos = []
    newPhotos = newPhotos + horPhotos
    idx=0
    while idx < (len(verticalPhotos) - 1):
        prevPhoto = verticalPhotos[idx]
        nxtPhoto = verticalPhotos[idx+1]
        prevTags = prevPhoto[0][2:]
        nextTags = nxtPhoto[0][2:]
        setOfTags = set(prevTags+nextTags)
        newPhoto = (['', '']+list(setOfTags),prevPhoto[1], nxtPhoto[1])
        newPhotos.append(newPhoto)
        idx+=2
    c.setData(newPhotos)
    return c


def createDecisionVars(conf, solver):
    objVars = [[]]
    nSlides = conf.nPhotos
    photos = conf.data
    for idx1,photo in enumerate(photos):
        objVars.append([])
        for idx2,photo2 in enumerate(photos):
            objVars[idx1].append(solver.IntVar(0, 1, str(idx1)+'_'+str(idx2)+'_trans'))
    return objVars

def createRestrictions(conf, solver, decVars):
    photos = conf.data
    for idx1, photo1 in enumerate(photos):
        constraint1 = solver.Constraint(0, 1)
        constraint2 = solver.Constraint(0, 1)
        constraint3 = solver.Constraint(0, 0)
        constraint3.SetCoefficient(decVars[idx1][idx1], 1)
        
        constraint4= solver.Constraint(0, 1)
        for idx2, photo2 in enumerate(photos):
            decVar1 = decVars[idx1][idx2]
            decVar2 = decVars[idx2][idx1]
            constraint1.SetCoefficient(decVar1, 1)
            constraint2.SetCoefficient(decVar2, 1)
            
            constraint4.SetCoefficient(decVars[idx1][idx2], 1)
            constraint4.SetCoefficient(decVars[idx2][idx1], 1)
    

def calculate_interest(tags1, tags2):
    commontagsLen = len([value for value in tags1 if value in tags2]) 
    tagsin1NotIn2 = len([value for value in tags1 if value not in tags2])
    tagsIn2NotIn1 = len([value for value in tags2 if value not in tags1])
    return min(commontagsLen, min(tagsin1NotIn2, tagsIn2NotIn1))

def createObjectiveFunction(conf, solver, decVars):
    photos = conf.data
    objective = solver.Objective()
    for idx1, photo1 in enumerate(photos):
        for idx2, photo2 in enumerate(photos):
            aux = calculate_interest(photo1[0][2:], photo2[0][2:])
            decVar1 = decVars[idx1][idx2]
            decVar2 = decVars[idx2][idx1]
            objective.SetCoefficient(decVar1, aux)
            objective.SetCoefficient(decVar2, aux)

    objective.SetMaximization()


def main():
    conf = readFile('c_memorable_moments.txt')
    solver = pywraplp.Solver('SolveIntegerProblem',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    decVars = createDecisionVars(conf, solver)
    createRestrictions(conf, solver, decVars)
    createObjectiveFunction(conf, solver, decVars)
    result_status = solver.Solve()
    # The problem has an optimal solution.
    assert result_status == pywraplp.Solver.OPTIMAL

    # The solution looks legit (when using solvers other than
    # GLOP_LINEAR_PROGRAMMING, verifying the solution is highly recommended!).
    assert solver.VerifySolution(1e-7, True)

    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())

    # The objective value of the solution.
    print('Optimal objective value = %d' % solver.Objective().Value())
    print()
    photos = conf.data
    for line in decVars:
        for var in line:
            if (var.solution_value == 1):
                print('%s = %d' % (var.name(), var.solution_value()))
                photo_begin, photo_end = var.name().split('_')
                prevPhoto = photos[photo_begin]
                nextPhoto = photos[photo_end]
                


main()

