import math
from PyQt4 import QtGui   
        
#This class implements the logic behind a 2D arm
#It does NOT account for physics or collision, just movement
class RobotArm:
    def __init__(self, dof, distances):
    
        #Just making sure
        assert(dof == len(distances))
        self.dof = dof
        
        #Location of the center of the arm
        self.xPos = 0
        self.yPos = 0
        
        #Location of the last segment of the arm
        self.endEffectorPos = (0,0)
        
        #initalizeing stuff
        self.distances = distances  
        self.thetas = [0] * self.dof       
        self.armEndEffectors = [(0,0)] * self.dof
        
    #Main update function, takes in a list of angles and will update the arm sequencially
    #The angles are RELATIVE angles from the previous arm, 
    #For example, if the values [37,0] are passed in, the arm will point straing at a 37 degree angle as there is no change in the second segment
    def update(self, thetas):
        self.thetas = thetas
        
        #Calculate the first one by hand, because there is always going to be at least one and we need one done before we can loop
        #This is all essentially forward kinematics
        armXPos = math.cos(math.radians(thetas[0])) * self.distances[0]
        armYPos = math.sin(math.radians(thetas[0])) * self.distances[0]
        self.armEndEffectors[0] = (armXPos, armYPos)
        sumTheta = thetas[0]
        
        #Keep calculating the rest using the same logic
        for i in range(1, self.dof):
            sumTheta += thetas[i]
            armXPos = math.cos(math.radians(sumTheta)) * self.distances[i] + (self.armEndEffectors[i - 1][0])
            armYPos = math.sin(math.radians(sumTheta)) * self.distances[i] + (self.armEndEffectors[i - 1][1])
            self.armEndEffectors[i] = (armXPos, armYPos)
            self.endEffectorPos = self.armEndEffectors[i]
        return self.endEffectorPos #return the positions of the segments, the last one being the end effector
        
    #Draw the arm to the screen
    def draw(self, qp):
        qp.setPen(QtGui.QPen(QtGui.QColor(255,0,0,128)))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0,128)) )
        qp.drawLine(self.xPos, self.yPos, self.armEndEffectors[0][0], self.armEndEffectors[0][1])
        for i in range(1, self.dof):
            qp.drawLine(self.armEndEffectors[i-1][0], self.armEndEffectors[i-1][1], self.armEndEffectors[i][0], self.armEndEffectors[i][1])
        
    #This is a static function that is capable of calculating the position of an arm in 2D space, no matter how many degrees of freedom
    #Essentially does the same thing as the update function, but for general purposes
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
            positions.append((armXPos, armYPos))
        
        return positions
        #Positions = [(x,y), (x,y)]
        
    #This function calculates the inverse kinematics for a 2 degree of freedom arm in 2d space
    #I was originally using this to compare the trained arm against the mathematical equivalent
    #This function is not used for anything, but I couldn't let myself erase it 
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
