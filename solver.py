from config import Config

def readFile(filename):
    file = open(filename,'r')
    firstLine = file.readline().split(' ')
    
    R = int(firstLine[0])
    C = int(firstLine[1])
    c = Config(R,C)
    data = []

    for line in file.readlines():
        data.append(list(map(int, line.replace('\n','').split(' '))))
    c.setData(data)
    return c

def main():
    conf = readFile('a_example.in')
    print(conf.data)

main()

