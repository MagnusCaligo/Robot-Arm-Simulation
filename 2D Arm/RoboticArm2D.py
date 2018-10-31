'''
Things I need:
    1. Implement driver for NEAT
    2. Arm output should return end effector position
    3. Drawing Widget should draw the most successful organism
'''
import math
from PyQt4 import QtGui

        
        
class RobotArm:
    
    def __init__(self, dof):
    
        self.dof = dof
        self.xPos = 0
        self.yPos = 0
        
        self.endEffectorPos = (0,0)
        
        self.distances = [100] * self.dof        
        self.thetas = [0] * self.dof       
        self.armEndEffectors = [(0,0)] * self.dof
        
    def update(self, thetas):
        self.thetas = thetas
        
        armXPos = math.cos(math.radians(thetas[0])) * self.distances[0]
        armYPos = math.sin(math.radians(thetas[0])) * self.distances[0]
        self.armEndEffectors[0] = (armXPos, armYPos)
        
        for i in range(1, self.dof):
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
        
        
