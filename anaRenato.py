from __future__ import print_function
from config import Config
from ortools.linear_solver import pywraplp

chunkSize = 50

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
        newPhoto = (['', '']+list(setOfTags),str(prevPhoto[1]) + " " + str(nxtPhoto[1]))
        newPhotos.append(newPhoto)
        idx+=2
    c.setData(newPhotos)
    return c


def createDecisionVars(photos, solver):
    objVars = [[]]
    for idx1 in range(len(photos)):
        objVars.append([])
        for idx2 in range(len(photos)):
            objVars[idx1].append(solver.IntVar(0, 1, str(idx1)+'_'+str(idx2)+'_trans'))
    return objVars

def createRestrictions(photos, solver, decVars):
    for idx1 in range(len(photos)):
        constraint1 = solver.Constraint(0, 1)
        constraint2 = solver.Constraint(0, 1)
        constraint3 = solver.Constraint(0, 0)
        constraint3.SetCoefficient(decVars[idx1][idx1], 1) #can't have a transition to himself
        
        constraint4= solver.Constraint(0, 1)
        for idx2 in range(len(photos)):
            decVar1 = decVars[idx1][idx2]
            decVar2 = decVars[idx2][idx1]
            constraint1.SetCoefficient(decVar1, 1) # There can be at most one transition from idx1 to idx2
            constraint2.SetCoefficient(decVar2, 1) # There can be at most one transition from idx2 to idx1
            # if there is a transition from 1 to 2, there cannot be a transition from 2 to 1
            constraint4.SetCoefficient(decVar1, 1)
            constraint4.SetCoefficient(decVar2, 1)
    

def calculate_interest(tags1, tags2):
    commontagsLen = len([value for value in tags1 if value in tags2]) 
    tagsin1NotIn2 = len([value for value in tags1 if value not in tags2])
    tagsIn2NotIn1 = len([value for value in tags2 if value not in tags1])
    return min(commontagsLen, min(tagsin1NotIn2, tagsIn2NotIn1))

def createObjectiveFunction(photos, solver, decVars):
    objective = solver.Objective()
    for idx1, photo1 in enumerate(photos):
        for idx2, photo2 in enumerate(photos):
            aux = calculate_interest(photo1[0][2:], photo2[0][2:])
            decVar1 = decVars[idx1][idx2]
            #decVar2 = decVars[idx2][idx1]
            objective.SetCoefficient(decVar1, aux)
            #objective.SetCoefficient(decVar2, aux)

    objective.SetMaximization()

# receives [(2,3), (3,10), (10,15)] which means there's a transition from photo 2 to 3 and from 3 to 10
def buildSlideshow(transitions, photos, chunkIdx):
    print("building slideshow:" + str(chunkIdx))
    slideshow = []
    print(transitions)
    lastElements = [last for (_,last) in transitions]
    firstElements = [first for (first, _) in transitions]
    # the first photo is the only element that exist in the first elements but not on the last elements
    print(set(firstElements).intersection(lastElements))
    nextPhoto = (set(firstElements)-set(lastElements)).pop()
    lastPhoto = (set(lastElements)-set(firstElements)).pop()
    while(nextPhoto != lastPhoto):
        realNextPhoto = photos[nextPhoto][1]
        slideshow.append(realNextPhoto)
        for first,last in transitions:
            if first == nextPhoto:
                nextPhoto = last
                break
    slideshow.append(photos[lastPhoto][1])
    print("finished slideshow:" + str(chunkIdx))
    return slideshow

def buildSlideshowNoob(transitions, photos, chunkIdx):
    slideshow = []
    for first,second in transitions:
        realFirstPhoto = photos[first][1]
        realSecondPhoto = photos[second][1]
        slideshow.append(realFirstPhoto)
        slideshow.append(realSecondPhoto)
    return slideshow
    
def outputSlides(filename, slideshow):
    file = open(filename + ".out","w")
    file.write(str(len(slideshow))+ "\n")
    for slide in slideshow:
        file.write(str(slide) + "\n")
    file.close()
def main():
    filename = 'b_lovely_landscapes.txt'
    conf = readFile(filename)
    chunks = splitDataInChunks(conf.data)
    fullSlideshow = []
    for chunkIdx, chunk in enumerate(chunks):

        solver = pywraplp.Solver('SolveIntegerProblem',
                           pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        decVars = createDecisionVars(chunk, solver)
        createRestrictions(chunk, solver, decVars)
        createObjectiveFunction(chunk, solver, decVars)
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
        
        transitions=[]
        for line in decVars:
            for var in line:
                if (var.solution_value() == 1):
                    photo_begin, photo_end, _ = var.name().split('_')
                    transitions.append((int(photo_begin), int(photo_end)))
        fullSlideshow += buildSlideshowNoob(transitions, chunk, chunkIdx+1)
    outputSlides(filename, fullSlideshow)
                


main()

