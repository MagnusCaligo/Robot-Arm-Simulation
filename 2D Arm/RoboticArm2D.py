'''
Things I need:
    1. Implement driver for NEAT
    2. Arm output should return end effector position
    3. Drawing Widget should draw the most successful organism
'''
import math
from PyQt4 import QtGui

        
        
class RobotArm:
    
    def __init__(self, dof, distances):
    
        assert(dof == len(distances))
        self.dof = dof
        self.xPos = 0
        self.yPos = 0
        
        self.endEffectorPos = (0,0)
        
        self.distances = distances  
        self.thetas = [0] * self.dof       
        self.armEndEffectors = [(0,0)] * self.dof
        
    def update(self, thetas):
        self.thetas = thetas
        
        armXPos = math.cos(math.radians(thetas[0])) * self.distances[0]
        armYPos = math.sin(math.radians(thetas[0])) * self.distances[0]
        self.armEndEffectors[0] = (armXPos, armYPos)
        
        for i in range(1, self.dof):
            thetas[i] += thetas[i-1]
            armXPos = math.cos(math.radians(thetas[i])) * self.distances[i] + self.armEndEffectors[i - 1][0]
            armYPos = math.sin(math.radians(thetas[i])) * self.distances[i] + self.armEndEffectors[i - 1][1]
            self.armEndEffectors[i] = (armXPos, armYPos)
            self.endEffectorPos = self.armEndEffectors[i]
        
        return self.endEffectorPos
        
    def draw(self, qp):
        qp.setPen(QtGui.QPen(QtGui.QColor(255,0,0,128)))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0,128)) )
        
        qp.drawLine(self.xPos, self.yPos, self.armEndEffectors[0][0], self.armEndEffectors[0][1])
        for i in range(1, self.dof):
            qp.drawLine(self.armEndEffectors[i-1][0], self.armEndEffectors[i-1][1], self.armEndEffectors[i][0], self.armEndEffectors[i][1])
        
    @staticmethod
    def calculatePosition(distances, thetas):
        assert(len(distances)>0)
        assert(len(thetas) >0)
        assert(len(distances) == len(thetas))
        
        positions = []
        
        armXPos = math.cos(math.radians(thetas[0])) * distances[0]
        armYPos = math.sin(math.radians(thetas[0])) * distances[0]
        positions.append((armXPos, armYPos))
        
        for i in range(1, len(distances)):
            thetas[i] += thetas[i -1]
            armXPos = math.cos(math.radians(thetas[i])) * distances[i] + positions[i-1][0]
            armYPos = math.sin(math.radians(thetas[i])) * distances[i] + positions[i-1][1]
            positions.append((armXPos, armYPos))
        
        return positions
        #Positions = [(x,y), (x,y)]
