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
    
    
    winner = pop.run(lambda geneomes, config: __calculateFitnessMovingPoint(geneomes, config, distances), 10)
    
    winnerOrganism = neat.nn.FeedForwardNetwork.create(winner, config)
    
    return winnerOrganism
    
    


def __calculateFitnessFixedPoint(geneomes, config, distances):
    xPos = 100
    yPos = 100
    for geneomeID, genome in geneomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = net.activate([xPos, yPos])
        output = [360 * t for t in output]
        positions = RobotArm.calculatePosition(distances, output)
        endEffectorPosition = positions[-1]
        
        distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (xPos, yPos))
        genome.fitness = -distanceBetween
        
def __calculateFitnessMovingPoint(geneomes, config, distances):
    
    for geneomeID, genome in geneomes:
        genome.fitness = 0
        
        rand = random.Random()
        seed = 2
        rand.seed(seed)
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        xDifferences = []
        yDifferences = []
        numberOfTest = 2
        for i in range(numberOfTest):
            targetX = rand.uniform(-100, 100)
            targetY = rand.uniform(-100, 100)
            modifiedTargetX = np.interp(targetX, (-100, 100), (-1,1))
            modifiedTargetY = np.interp(targetY, (-100, 100), (-1,1))
            output = net.activate([modifiedTargetX, modifiedTargetY])
            output = [360 * t for t in output]
            positions = RobotArm.calculatePosition(distances, output)
            endEffectorPosition = positions[-1]
            distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY))
            genome.fitness += math.pow(math.e, -((10 * (distanceBetween/200) ) ** 2)/float(10)) / float(numberOfTest)
            xDifferences.append(abs(targetX - endEffectorPosition[0]))
            yDifferences.append(abs(targetY - endEffectorPosition[1]))
        #genome.fitness/= 20
        genome.fitness = (.5 * 1/float(sum(xDifferences))) + (.5 * 1/float(sum(yDifferences)))
        genome.fitness = 1/float(sum(xDifferences) + sum(yDifferences))
        
    
        
def calculateDistanceBetween2D(v1, v2):
    unSquare = ((v1[0] - v2[0]) ** 2 ) + ((v1[1] - v2[1]) **2)
    return unSquare ** .5
