from PyQt4 import QtCore, QtGui
import sys
import math
import numpy as np
from RoboticArm2D import RobotArm
from NEATEvolution import *

UPDATE_TIME = 100
DOF = 2
DISTANCES = [100] * DOF
class DrawingWidget(QtGui.QWidget):

    def __init__(self, organism):
        super(DrawingWidget, self).__init__()
        self.setGeometry(150,150,640,480)
        self.setMouseTracking(True)
        self.show()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(UPDATE_TIME)
        self.arm1 = RobotArm(DOF, DISTANCES)
        
        self.arm2 = RobotArm(DOF, DISTANCES)
        self.mousePos = (0,0)
        self.unmodifiedMousePos = (0,0)
        self.organism = organism
        
        self.calculatedEF = (0,0)
        
        self.thetas = [0] * DOF
        self.thetasRates = np.random.normal(0, 1, DOF)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            sys.exit()
            
    def update(self):
        
        thetas = RobotArm.calculateInverseKinematics(DISTANCES, self.unmodifiedMousePos)
        self.arm1.update(thetas)
        
        
        '''
        transform = QtGui.QTransform()
        transform.translate(320,240)
        transform.scale(1,-1)
        self.calculatedEF = transform.map(self.calculatedEF[0], self.calculatedEF[1])
        '''
        
        outputAngles = self.organism.activate(self.unmodifiedMousePos)
        outputAngles = [360 * t for t in outputAngles]
        self.arm2.update(outputAngles)
        self.calculatedEF = RobotArm.calculatePosition(DISTANCES, outputAngles)[1]
        
        print calculateDistanceBetween2D(self.unmodifiedMousePos, self.calculatedEF)
        
        self.repaint()
        self.timer.start(UPDATE_TIME)
        
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.translate(320, 240)
        qp.scale(1, -1)
        #self.arm1.draw(qp)
        self.arm2.draw(qp)
        
        rand = random.Random()
        seed = 3
        rand.seed(seed)
        numOfTests = 2
        maxRange = 200
        for i in range(numOfTests):
        
            angle = rand.uniform(0,1) * math.pi * 2
            radius = rand.uniform(0, 1) * maxRange
            targetX = radius * math.sin(angle)
            targetY = radius * math.cos(angle)
            #targetX = rand.uniform(-maxRange, maxRange)
            #targetY = rand.uniform(-maxRange, maxRange)
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
        
        
        
print RobotArm.calculatePosition([100,100],[120,240])
print calculateDistanceBetween2D((100,100), (200, 200))
winningOrganism = Evolve_Different_Paramters(DISTANCES)
        
app = QtGui.QApplication(sys.argv)
widget = DrawingWidget(winningOrganism)
sys.exit(app.exec_())
