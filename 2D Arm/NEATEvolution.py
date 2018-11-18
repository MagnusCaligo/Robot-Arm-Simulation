import neat
import numpy as np
import random
from RoboticArm2D import RobotArm
import math
import os
from PyQt4 import QtCore

config_file = "config-feedforward.txt"
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
    
    


def __calculateFitnessFixedPoint(geneomes, config, distances):
    rand = random.Random()
    seed = 2
    maximumDistance = 200
    rand.seed(seed)
    angle = rand.uniform(0,1) * math.pi * 2
    radius = rand.uniform(0, 1) * maximumDistance
    targetX = radius * math.sin(angle)
    targetY = radius * math.cos(angle)
            
    xPos = targetX
    yPos = targetY
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
    
    maximumDistance = 200
    numberOfTest = 4
    
    for geneomeID, genome in geneomes:
        genome.fitness = 0
        
        rand = random.Random()
        seed = random.randint(0,10000)
        seed = 3
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

    def evolveWithThreads(self):
        self.configs.append(neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file))
        
        self.threads = [EvolveConfiguration(c,self.distances, i) for i,c in enumerate(self.configs)]
        for thread in self.threads:
            self.connect(thread, QtCore.SIGNAL("data(PyQt_PyObject, PyQt_PyObject)"), self.printData)
            thread.start()
            
    def printData(self, id, data):
        print "Thread", id, "finished:", data
    
class EvolveConfiguration(QtCore.QThread):

    NUMBER_OF_ITERATIONS = 1500

    def __init__(self, config, distances, id):
        QtCore.QThread.__init__(self)
        self.config = config
        self.distances = distances
        self.id = id
        
    def run(self):
        pop = neat.Population(self.config)
        pop.add_reporter(neat.StdOutReporter(True))
        winner = pop.run(lambda geneomes, config: self.__calculateFitnessMovingPoint(geneomes, config, self.distances), EvolveConfiguration.NUMBER_OF_ITERATIONS)
        self.emit(QtCore.SIGNAL("data(PyQt_PyObject, PyQt_PyObject)"), self.id, winner.fitness)
        
    def __calculateFitnessMovingPoint(self, geneomes, config, distances):
        
        maximumDistance = 200
        numberOfTest = 4
        
        for geneomeID, genome in geneomes:
            genome.fitness = 0
            
            rand = random.Random()
            seed = random.randint(0,10000)
            seed = 3
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