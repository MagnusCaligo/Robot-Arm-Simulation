import neat
import numpy as np
import random
from RoboticArm2D import RobotArm
import math
import os
from PyQt4 import QtCore
import sys
import time
import copy


'''
Location of config files for evolution parameters
When training, I would originally have multiple config files. That would allow me to test various 
configurations against each other to see what evolved the best. This was the overall winner.
'''
config_files = ["configurations/lowAddition_lowSubtraction_weights1000_hypertangent_1dof.txt"] 
        
#Used to calculate the distance between two 2D points
def calculateDistanceBetween2D(v1, v2):
    unSquare = ((v1[0] - v2[0]) ** 2 ) + ((v1[1] - v2[1]) **2)
    return unSquare ** .5
    
    
#Main threading class, initializes all of the threads and keeps track of learning
class EvolveThreadingMain(QtCore.QObject):
    def __init__(self,distances):
        QtCore.QObject.__init__(self)
        '''
        Distances is a set of distances of the arm components.
        The length of distances corresponds to the degrees of freedom.
        Originally, I had planned to train higher degrees of freedom arms, but I ended up resorting to one degree.
        '''
        self.distances = distances
        self.configs = [] #Different config files
        self.threads = [] #Different threads, each running a config file
        
        self.numConfigs = len(config_files)
        
        '''
        This is how many tests are run for each config file.
        Since evolution is random, there might be times where a better network is evolved
        just by chance, so we need to run evolution multiple times with the same configuration.
        Each test is ran on its own thread, and reports back to this class
        '''
        self.numTests = 5 
        
        #Keeps track of time
        self.timeSinceLastUpdate = time.time()
        
        #Stores information for printing to terminal
        self.printData = []
        self.winnerData = []
        
        #Keep track of the best running organism and fitness to return later
        self.bestOrganism = None
        self.highestFitness = None
        
        self.complete = False #Completes when all threads have finished
        
        for i in range(self.numConfigs): #Initalize the printing data
            self.printData.append([])
            self.winnerData.append([])
            for p in range(self.numTests): #Printing data is a list, where each index is a list of data for that configuration
                self.printData[i].append(None)
                self.winnerData[i].append(None)
                
         
            
    #This function initalizes the threads and sets them off
    def evolveWithThreads(self):
        #Update configs based on config files
        for con in config_files:
            self.configs.append(neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, con))
            
        #Create numTests amount of threads for each config file
        for con_id, con in enumerate(self.configs):
            for sub_id in range(self.numTests):
                self.threads.append(EvolveConfiguration(con,self.distances, con_id, sub_id))
          
        #Initalize and start the threads
        for thread in self.threads:
            #Connect the threads so that when they finish we recieve the data
            self.connect(thread, QtCore.SIGNAL("winner_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.getWinnerData) 
            self.connect(thread, QtCore.SIGNAL("update_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.returnData)
            thread.start() #Start the thread
            
    #Function for getting winner data and determinig if we all threads are finished or not
    def getWinnerData(self, con_id, sub_id, data):
        self.winnerData[con_id][sub_id] = data
        if self.highestFitness == None or data[1] > self.highestFitness:
            self.bestOrganism = neat.nn.FeedForwardNetwork.create(data[2], data[3])
            self.highestFitness = data[1]
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
            self.complete = True
            self.emit(QtCore.SIGNAL("finished"))
        
    #Function for getting data after each itteration
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
            timeLeft = (EvolveConfiguration.NUMBER_OF_ITERATIONS-self.printData[0][0][0])/float(1/float(deltaTime))
            print "Delta Time:", deltaTime, "\tApproximate Time Left:", timeLeft, "seconds\t", timeLeft/float(60), "minutes\t", timeLeft/float(60)/float(60), "hours"
            self.timeSinceLastUpdate = time.time()
            for i in range(self.numConfigs):
                print "\nConfiguration", i, ":"
                for p in range(self.numTests):
                    print "\tRun", p, "- Generaton:", self.printData[i][p][0], "\t Fitness:", self.printData[i][p][1]
                    
            self.printData = copy.deepcopy(self.winnerData)
                    
    #Once we have all the threads finished, write the data so we can see the highest fitness     
    def writeData(self, dataString):
        outputId = 0
        while "output" + str(outputId) + ".data" in os.listdir('.'):
            outputId += 1
            
        file = open("output" + str(outputId) + ".data", "w")
        file.write(dataString)
        file.close()
        print "Wrote to file:", "output" + str(outputId) + ".data"
        #sys.exit(1)
                    
    
#Threading object
class EvolveConfiguration(QtCore.QThread):

    #Number of iterations to run per thread, i.e. 1000 generations
    NUMBER_OF_ITERATIONS = 1000

    def __init__(self, config, distances, config_id, sub_id):
        QtCore.QThread.__init__(self)
        self.config = config
        self.distances = distances
        self.config_id = config_id
        self.sub_id = sub_id
        self.generation = -1
        self.dataFile = open("generationData.txt", "w")
        
    def run(self):
        pop = neat.Population(self.config) #Create the population
        
        #Calculate the winner withe the fitness function
        winner = pop.run(lambda geneomes, config: self.__calculateFitnessMovingPoint(geneomes, config, self.distances), EvolveConfiguration.NUMBER_OF_ITERATIONS)
        #Announce that you are finished and send data to master
        self.emit(QtCore.SIGNAL("winner_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.config_id, self.sub_id, [self.generation, winner.fitness, winner, self.config])
        self.dataFile.close()
        
    #Calculate fitness of the network
    def __calculateFitnessMovingPoint(self, geneomes, config, distances):
        self.generation += 1 #Increment which generation you are on for the master and printing
        maximumDistance = sum(distances)
        numberOfTest = 3 #Number of points in space to test the organism on
        highestFitness = None #Used for determining the highest fitness of this generation
        for geneomeID, genome in geneomes: #For each organism
            genome.fitness = 0
            
            rand = random.Random()
            seed = 3 #Unfortunately the networks haven't been able to learn on random seeds, they just barely learn on a set seed
            rand.seed(seed)
            
            net = neat.nn.FeedForwardNetwork.create(genome, config) #Create the network from the geneome

            
            for i in range(numberOfTest):
                #Calculate the target location using random and a bit of polar math
                angle = rand.uniform(0,1) * math.pi * 2
                radius = maximumDistance 
                targetX = radius * math.sin(angle)
                targetY = radius * math.cos(angle)
                
                #Test the network given the location of the target
                output = net.activate([targetX, targetY])
                output = [360 * t for t in output] #Parse the data into degrees
                positions = RobotArm.calculatePosition(distances, output) #Calculate the end-effector of the arm given the degrees returned by the network
                endEffectorPosition = positions[-1] #Get the last joint in the arm i.e. the end effector
                
                
                distanceBetween = calculateDistanceBetween2D(endEffectorPosition, (targetX, targetY)) #Calculate the difference between the target and actual
                genome.fitness -= distanceBetween ** 2 #Use mean squared error to set the geneomes fitness
                
            if highestFitness == None or genome.fitness > highestFitness: #Check if we have a higher fitness
                highestFitness = genome.fitness 
        
        #Once a generation has finished, announce it to the master
        self.emit(QtCore.SIGNAL("update_data(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.config_id, self.sub_id, [self.generation, highestFitness])
        self.dataFile.write(str(highestFitness) + "\n")