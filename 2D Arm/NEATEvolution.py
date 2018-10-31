import neat
import numpy as np
import random
from RoboticArm2D import RobotArm

config_file = "config-feedforward.txt"
def Evolve(distances):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file)
    pop = neat.Population(config)
    
    pop.add_reporter(neat.StdOutReporter(True))
    
    
    winner = pop.run(lambda geneomes, config: __calculateFitnessMovingPoint(geneomes, config, distances), 300)
    
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
        genome.fitness = 1
        
        rand = random.Random()
        seed = 2
        rand.seed(seed)
        
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        differences = []
        for i in range(10):
            targetX = rand.uniform(-100, 100)
            targetY = rand.uniform(-100, 100)
            output = net.activate([targetX, targetY])
            output = [360 * t for t in output]
            positions = RobotArm.calculatePosition(distances, output)
            endEffectorPosition = positions[-1]
            distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY))
            genome.fitness -= distanceBetween
        
    
        
def calculateDistanceBetween2D(v1, v2):
    unSquare = ((v1[0] - v2[0]) ** 2 ) + ((v1[1] - v2[1]) **2)
    return unSquare ** .5