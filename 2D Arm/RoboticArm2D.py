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
        sumTheta = thetas[0]
        for i in range(1, self.dof):
            sumTheta += thetas[i]
            armXPos = math.cos(math.radians(sumTheta)) * self.distances[i] + (self.armEndEffectors[i - 1][0])
            armYPos = math.sin(math.radians(sumTheta)) * self.distances[i] + (self.armEndEffectors[i - 1][1])
            self.armEndEffectors[i] = (armXPos, armYPos)
            self.endEffectorPos = self.armEndEffectors[i]
        print "UPDATED END EFFECTOR:", self.endEffectorPos
        return self.endEffectorPos
        
    def draw(self, qp):
        qp.setPen(QtGui.QPen(QtGui.QColor(255,0,0,128)))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0,128)) )
        print "Drawing Line from", [self.xPos, self.yPos], self.armEndEffectors[0]
        qp.drawLine(self.xPos, self.yPos, self.armEndEffectors[0][0], self.armEndEffectors[0][1])
        for i in range(1, self.dof):
            print "Drawing Line from", self.armEndEffectors[i-1], self.armEndEffectors[i]
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
        sumTheta = thetas[0]
        for i in range(1, len(distances)):
            sumTheta += thetas[i]
            #newTheta = thetas[i] + thetas[i -1]
            armXPos = (math.cos(math.radians(sumTheta)) * distances[i]) + positions[i-1][0]
            armYPos = (math.sin(math.radians(sumTheta)) * distances[i]) + positions[i-1][1]
            print "Second CALCULATION:", armXPos, armYPos
            positions.append((armXPos, armYPos))
        
        print "OUTPUT:", positions
        return positions
        #Positions = [(x,y), (x,y)]
        
    @staticmethod
    def calculateInverseKinematics(distances, target):
        temp = ((target[0] ** 2) + (target[1] ** 2)) 
        if temp > (2*distances[0]*distances[1]) + (distances[0]**2 + distances[1]**2):
            temp = (2*distances[0]*distances[1]) + (distances[0]**2 + distances[1]**2)
            
        above = (temp - (distances[0]**2) - (distances[1]**2))
        below = (2 * distances[0] * distances[1])
        
        t2 = math.acos(above/float(below))
        
        temp = (float(distances[1]) * math.sin(t2)),float(distances[0] + (distances[1]*math.cos(t2)))
        t1 = math.atan2(target[1],float(target[0])) - math.atan2(temp[0], temp[1])
        return [math.degrees(t1), math.degrees(t2)]
