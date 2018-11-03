import neat
import numpy as np
import random
from RoboticArm2D import RobotArm
import math
import os

config_file = "config-feedforward.txt"
def Evolve(distances):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    
    
    winner = pop.run(lambda geneomes, config: __calculateFitnessMovingPoint(geneomes, config, distances), 1)
    
    winnerOrganism = neat.nn.FeedForwardNetwork.create(winner, config)
    
    return winnerOrganism
    
    


def __calculateFitnessFixedPoint(geneomes, config, distances):
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
    
    maximumDistance = 150
    numberOfTest = 15
    
    for geneomeID, genome in geneomes:
        genome.fitness = 1
        
        rand = random.Random()
        seed = 2
        rand.seed(seed)
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        xDifferences = []
        yDifferences = []
        
        for i in range(numberOfTest):
            targetX = rand.uniform(-maximumDistance, maximumDistance)
            targetY = rand.uniform(-maximumDistance, maximumDistance)
            modifiedTargetX = np.interp(targetX, (-maximumDistance, maximumDistance), (-1,1))
            modifiedTargetY = np.interp(targetY, (-maximumDistance, maximumDistance), (-1,1))
            output = net.activate([targetX, targetY])
            output = [360 * t for t in output]
            positions = RobotArm.calculatePosition(distances, output)
            endEffectorPosition = positions[-1]
            distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY))
            genome.fitness = -distanceBetween
            #genome.fitness += math.pow(math.e, -((10 * (distanceBetween/200) ) ** 2)/float(10)) / float(numberOfTest)
            xDifferences.append(abs(targetX - endEffectorPosition[0]))
            yDifferences.append(abs(targetY - endEffectorPosition[1]))
            
        #genome.fitness/= 20
        #genome.fitness = (.5 * 1/float(sum(xDifferences))) + (.5 * 1/float(sum(yDifferences)))
        #genome.fitness = 1/float(sum(xDifferences) + sum(yDifferences))
        
    
        
def calculateDistanceBetween2D(v1, v2):
    unSquare = ((v1[0] - v2[0]) ** 2 ) + ((v1[1] - v2[1]) **2)
    return unSquare ** .5
