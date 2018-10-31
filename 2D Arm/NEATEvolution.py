import neat
import numpy as np
import random

config_file = "feedForward.config"
def Evolve():
    config = neat.Config(neat.defaultGeneome, neat.DefaultReproduction, neat.DefaultSpeciestSet, neat.DefualtStagnation, config_file)
    pop = neat.Population(config)
    
    winner = pop.run(__calculateFitness, 300)
    
    winnerOrganism = neat.nn.FeedForwardNetwork.create(winner, config)
    
    return winnerOrganism
    
    


def __calculateFitness(geneomes, config):
    rand = random.Random()
    seed = 2
    for geneomeID, genome in geneomes:
        rand.seed(seed)
    
        