from PyQt4 import QtCore, QtGui
import sys
import math
import numpy as np
from RoboticArm2D import RobotArm
from NEATEvolution import *

UPDATE_TIME = 100 #Time between drawing events
DOF = 1 #Degrees of freedom of the arm, can be increased but the networks will not converge on a good result
DISTANCES = [200] * DOF #Lengths of the arm segments

#This class draws the arms and the tests to the screen. We can also use the mouse to fake input
class DrawingWidget(QtGui.QWidget):

    def __init__(self, organism, trainingThread):
        super(DrawingWidget, self).__init__()
        self.setGeometry(150,150,640,480)
        self.setMouseTracking(True)
        self.show()
        
        #The GUI needs to know when the training is finished so it can start drawing, so it connects an event with the training stuff
        self.trainingThread = trainingThread
        self.connect(self.trainingThread, QtCore.SIGNAL("finished"), self.startTimer)
        
        #Timer for updating the GUI, however this is not initiated until after training is finished
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        
        self.trainedArm = RobotArm(DOF, DISTANCES) #Create a new instance of the arm, this will be used to mimic the trained network
        
        self.mousePos = (0,0)
        self.unmodifiedMousePos = (0,0)
        self.organism = organism #Trained organism that performed the best
        
        self.calculatedEF = (0,0) #Location of the last segment of the arm
        
        self.thetas = [0] * DOF #angles between the segments of the arm
        
    #Function used to update the gui, it is not called until training is done
    def startTimer(self):
        self.organism = self.trainingThread.bestOrganism #Update organism
        self.timer.start(UPDATE_TIME)
        
    #If you hit q the gui will close
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            sys.exit()
    
    #Main loop that updates the gui and the organism
    def update(self):
        outputAngles = self.organism.activate(self.unmodifiedMousePos) #Pass in the mouse position into the network
        outputAngles = [360 * t for t in outputAngles] #Parse the data into degrees
        self.trainedArm.update(outputAngles) #Update the arm position based on the angles
        self.calculatedEF = RobotArm.calculatePosition(DISTANCES, outputAngles)[-1] #Update the end-effector based on the arm
        
        self.repaint() #Repaint the screen and restart the loop
        self.timer.start(UPDATE_TIME)
        
    #Shit ton of paint events to draw everything to the screen, this can be ignored. 
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.translate(320, 240)
        qp.scale(1, -1)
        self.trainedArm.draw(qp)
        
        rand = random.Random()
        seed = 3
        rand.seed(seed)
        numOfTests = 5
        maxRange = sum(DISTANCES)
        for i in range(numOfTests):
        
            angle = rand.uniform(0,1) * math.pi * 2
            radius = maxRange #rand.uniform(0, 1) * maxRange
            targetX = radius * math.sin(angle)
            targetY = radius * math.cos(angle)
            qp.setPen(QtGui.QPen(QtGui.QColor(255,0,0,128)))
            qp.setBrush(QtGui.QBrush(QtGui.QColor(255,0,0,128)) )
            qp.drawEllipse(targetX-5, targetY-5, 10, 10)
            qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,255)))
            qp.scale(1,-1)
            qp.drawText(QtCore.QPointF(targetX-2, -targetY+5), str(i))
            qp.scale(1,-1)
        
        
        
        
        qp.setPen(QtGui.QPen(QtGui.QColor(0,255,0,128)))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0,128)) )
        qp.drawEllipse(self.calculatedEF[0]-5, self.calculatedEF[1]-5, 10, 10)
        
        qp.setPen(QtGui.QPen(QtGui.QColor(0,0,255,128)))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(0,0,255,128)) )
        qp.drawEllipse(self.unmodifiedMousePos[0]-5, self.unmodifiedMousePos[1]-5, 10, 10)
        
        qp.end()
        
    #If the mouse moves we need to pass the data to the arm
    #I have to do some transformation stuff here because I want 0,0 to be in the center of the screen
    #And I want Y to increase upwards not downwards
    def mouseMoveEvent(self,e):
        point =  e.pos()
        transform = QtGui.QTransform()
        transform.translate(-320,240)
        transform.scale(1,-1)
        point = transform.map(point)
        targetX = np.interp(point.x(), (-200, 200), (-1,1))
        targetY = np.interp(point.y(), (-200, 200), (-1,1))
        self.unmodifiedMousePos = (point.x(), point.y())
        self.mousePos = (targetX, targetY)
        
