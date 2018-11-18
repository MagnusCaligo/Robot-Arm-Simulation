import neat
import numpy as np
import random
from RoboticArm2D import RobotArm
import math
import os
from PyQt4 import QtCore
import sys
import time
config_file = "config-feedforward.txt"

config_files = ["configurations/lowAddition_lowSubtraction_weights30.txt","configurations/lowAddition_lowSubtraction_weights1000.txt","configurations/lowAddition_noSubtraction_weights30.txt","configurations/lowAddition_noSubtraction_weights1000.txt"]

generation = 0

def Evolve(distances):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    
    
    winner = pop.run(lambda geneomes, config: __calculateFitnessMovingPoint(geneomes, config, distances), 1500)
    
    winnerOrganism = neat.nn.FeedForwardNetwork.create(winner, config)
    print "Winner Organism Fitness:", winner.fitness
    
    fitness = 1
    numberOfTest = 2
    maximumDistance = 200
    rand = random.Random()
    seed = random.randint(0,10000)
    seed = 3
    rand.seed(seed)
    
    net = neat.nn.FeedForwardNetwork.create(winner, config)
    xDifferences = []
    yDifferences = []
    
    for i in range(numberOfTest):
        angle = rand.uniform(0,1) * math.pi * 2
        radius = rand.uniform(0, 1) * maximumDistance
        targetX = radius * math.sin(angle)
        targetY = radius * math.cos(angle)
        
        output = net.activate([targetX, targetY])
        output = [360 * t for t in output]
        positions = RobotArm.calculatePosition(distances, output)
        endEffectorPosition = positions[-1]
        print "Target was:", targetX, targetY, "Position was:", endEffectorPosition
        distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY))
        fitness -= distanceBetween
        
    print "Actual Fitnes:", fitness
    
    
    return winnerOrganism
    
def Evolve_Different_Paramters(distances):
    global generation
    config1 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "configurations/lowAddition_lowSubtraction_weights30.txt")
    config2 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "configurations/lowAddition_lowSubtraction_weights1000.txt")
    config3 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "configurations/lowAddition_noSubtraction_weights30.txt")
    config4 = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, "configurations/lowAddition_noSubtraction_weights1000.txt")
    
    configs = [config1, config2, config3, config4]
    data = []
    for index,con in enumerate(configs):
        print "Running Config Number:", index
        data.append([])
        for i in range(10):
            print "\n\nRunning Instance:", i
            generation = 0
            pop = neat.Population(con)
            #pop.add_reporter(neat.StdOutReporter(True))
            winner = pop.run(lambda geneomes, con: __calculateFitnessMovingPoint(geneomes, con, distances), 3000)
            data[-1].append(winner.fitness)
    
    print data
    sys.exit(0)


def __calculateFitnessFixedPoint(geneomes, config, distances):
    rand = random.Random()
    seed = 2
    maximumDistance = 200
    rand.seed(seed)
    angle = rand.uniform(0,1) * math.pi * 2
    radius = rand.uniform(0, 1) * maximumDistance
    targetX = radius * math.sin(angle)
    targetY = radius * math.cos(angle)
            
    xPos = 100
    yPos = 0
    for geneomeID, genome in geneomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = net.activate([xPos, yPos])
        output = [360 * t for t in output]
        positions = RobotArm.calculatePosition(distances, output)
        endEffectorPosition = positions[-1]
        
        distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (xPos, yPos))
        genome.fitness = -distanceBetween
        #genome.fitness = 1/ (float(abs(endEffectorPosition[0] - xPos) + abs(endEffectorPosition[1] - yPos)))
        
def __calculateFitnessMovingPoint(geneomes, config, distances):
    global generation
    print "\rGeneration:", generation,
    generation += 1
    maximumDistance = 200
    numberOfTest = 4
    
    for geneomeID, genome in geneomes:
        genome.fitness = 0
        
        rand = random.Random()
        seed = random.randint(0,10000)
        #seed = 3
        rand.seed(seed)
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        xDifferences = []
        yDifferences = []
        
        for i in range(numberOfTest):
            angle = rand.uniform(0,1) * math.pi * 2
            radius = rand.uniform(0, 1) * maximumDistance
            targetX = radius * math.sin(angle)
            targetY = radius * math.cos(angle)
        
            #targetX = rand.uniform(-maximumDistance, maximumDistance)
            #targetY = rand.uniform(-maximumDistance, maximumDistance)
            modifiedTargetX = np.interp(targetX, (-maximumDistance, maximumDistance), (-1,1))
            modifiedTargetY = np.interp(targetY, (-maximumDistance, maximumDistance), (-1,1))
            output = net.activate([targetX, targetY])
            output = [360 * t for t in output]
            positions = RobotArm.calculatePosition(distances, output)
            endEffectorPosition = positions[-1]
            distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY))
            genome.fitness -= distanceBetween ** 2
            #genome.fitness += math.pow(math.e, -((10 * (distanceBetween/20) ) ** 2)/float(10)) / float(numberOfTest)
            xDifferences.append(abs(targetX - endEffectorPosition[0]))
            yDifferences.append(abs(targetY - endEffectorPosition[1]))
            
        #genome.fitness/= 20
        #genome.fitness = (.5 * 1/float(sum(xDifferences))) + (.5 * 1/float(sum(yDifferences)))
        #genome.fitness = 10/float(sum(xDifferences) + sum(yDifferences))
        
    
        
def calculateDistanceBetween2D(v1, v2):
    unSquare = ((v1[0] - v2[0]) ** 2 ) + ((v1[1] - v2[1]) **2)
    return unSquare ** .5
    
class EvolveThreadingMain(QtCore.QObject):

    def __init__(self,distances):
        QtCore.QObject.__init__(self)
        self.distances = distances
        self.configs = []
        self.threads = []
        
        self.numConfigs = len(config_files)
        self.numTests = 10
        
        self.timeSinceLastUpdate = time.time()
        
        self.printData = []
        self.winnerData = []
        for i in range(self.numConfigs):
            self.printData.append([])
            self.winnerData.append([])
            for p in range(self.numTests):
                self.printData[i].append(None)
                self.winnerData[i].append(None)
                
         
            

    def evolveWithThreads(self):
        for con in config_files:
            self.configs.append(neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, con))
        
        #self.threads = [EvolveConfiguration(c,self.distances, i) for i,c in enumerate(self.configs)]
        for con_id, con in enumerate(self.configs):
            for sub_id in range(self.numTests):
                self.threads.append(EvolveConfiguration(con,self.distances, con_id, sub_id))
        for thread in self.threads:
            self.connect(thread, QtCore.SIGNAL("winner_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.getWinnerData)
            self.connect(thread, QtCore.SIGNAL("update_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.returnData)
            thread.start()
            
    def getWinnerData(self, con_id, sub_id, data):
        self.winnerData[con_id][sub_id] = data
        dataIsFull = True
        for i in range(self.numConfigs):
            for p in range(self.numTests):
                if self.winnerData[i][p] == None:
                    dataIsFull = False
                    break
        if dataIsFull == True:
            dataString = ""
            os.system('cls')
            print "All threads finished!"
            for i in range(self.numConfigs):
                print "\nConfiguration", i, ":"
                for p in range(self.numTests):
                    print "\tRun", p, "- Generaton:", self.winnerData[i][p][0], "\t Fitness:", self.winnerData[i][p][1]
                    dataString = dataString + str(i) + " " + str(p) + " " + str(self.winnerData[i][p][0]) + " " + str(self.winnerData[i][p][1]) + "\n"
            self.writeData(dataString)
        
        
    def returnData(self, con_id, sub_id, data):
        self.printData[con_id][sub_id] = data
        dataIsFull = True
        for i in range(self.numConfigs):
            for p in range(self.numTests):
                if self.printData[i][p] == None:
                    dataIsFull = False
                    break
        if dataIsFull == True:
            os.system('cls')
            deltaTime = time.time() - self.timeSinceLastUpdate
            timeLeft = (1500-self.printData[0][0][0])/float(1/float(deltaTime))
            print "Delta Time:", deltaTime, "\tApproximate Time Left:", timeLeft, "seconds\t", timeLeft/float(60), "minutes\t", timeLeft/float(60)/float(60), "hours"
            self.timeSinceLastUpdate = time.time()
            for i in range(self.numConfigs):
                print "\nConfiguration", i, ":"
                for p in range(self.numTests):
                    print "\tRun", p, "- Generaton:", self.printData[i][p][0], "\t Fitness:", self.printData[i][p][1]
                    
            self.printData = []
            for i in range(self.numConfigs):
                self.printData.append([])
                for p in range(self.numTests):
                    self.printData[i].append(None)
                    
                    
    def writeData(self, dataString):
        outputId = 0
        while "output" + str(outputId) + ".data" in os.listdir('.'):
            outputId += 1
            
        file = open("output" + str(outputId) + ".data", "w")
        file.write(dataString)
        file.close()
        sys.exit(1)
                    
    
class EvolveConfiguration(QtCore.QThread):

    NUMBER_OF_ITERATIONS = 1500

    def __init__(self, config, distances, config_id, sub_id):
        QtCore.QThread.__init__(self)
        self.config = config
        self.distances = distances
        self.config_id = config_id
        self.sub_id = sub_id
        self.generation = -1
        
    def run(self):
        pop = neat.Population(self.config)
        #pop.add_reporter(neat.StdOutReporter(True))
        winner = pop.run(lambda geneomes, config: self.__calculateFitnessMovingPoint(geneomes, config, self.distances), EvolveConfiguration.NUMBER_OF_ITERATIONS)
        self.emit(QtCore.SIGNAL("winner_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.config_id, self.sub_id, [self.generation, winner.fitness])
        
    def __calculateFitnessMovingPoint(self, geneomes, config, distances):
        self.generation += 1
        maximumDistance = 200
        numberOfTest = 4
        highestFitness = None
        for geneomeID, genome in geneomes:
            genome.fitness = 0
            
            rand = random.Random()
            seed = random.randint(0,10000)
            seed = 3
            #rand.seed(seed)
            
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            xDifferences = []
            yDifferences = []
            
            for i in range(numberOfTest):
                angle = rand.uniform(0,1) * math.pi * 2
                radius = rand.uniform(0, 1) * maximumDistance
                targetX = radius * math.sin(angle)
                targetY = radius * math.cos(angle)
            
                #targetX = rand.uniform(-maximumDistance, maximumDistance)
                #targetY = rand.uniform(-maximumDistance, maximumDistance)
                modifiedTargetX = np.interp(targetX, (-maximumDistance, maximumDistance), (-1,1))
                modifiedTargetY = np.interp(targetY, (-maximumDistance, maximumDistance), (-1,1))
                output = net.activate([targetX, targetY])
                output = [360 * t for t in output]
                positions = RobotArm.calculatePosition(distances, output)
                endEffectorPosition = positions[-1]
                distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY))
                genome.fitness -= distanceBetween ** 2
                #genome.fitness += math.pow(math.e, -((10 * (distanceBetween/20) ) ** 2)/float(10)) / float(numberOfTest)
                xDifferences.append(abs(targetX - endEffectorPosition[0]))
                yDifferences.append(abs(targetY - endEffectorPosition[1]))
                
            if highestFitness == None or genome.fitness > highestFitness:
                highestFitness = genome.fitness
            #genome.fitness/= 20
            #genome.fitness = (.5 * 1/float(sum(xDifferences))) + (.5 * 1/float(sum(yDifferences)))
            #genome.fitness = 10/float(sum(xDifferences) + sum(yDifferences)) 
        self.emit(QtCore.SIGNAL("update_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.config_id, self.sub_id, [self.generation, highestFitness])