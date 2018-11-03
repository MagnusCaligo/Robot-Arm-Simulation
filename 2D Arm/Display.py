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
        distances = 200
        temp = ((self.unmodifiedMousePos[0] ** 2) + (self.unmodifiedMousePos[1] ** 2)) 
        
        print "Above:", (temp -(((distances**2) + (distances**2))**.5)), "Below", (2*distances*distances), "Total:", (((temp -(((distances**2) + (distances**2))**.5))/(2*distances*distances)))
        
        t2 = math.acos(((temp -(((distances**2) + (distances**2))**.5))/(2*distances*distances)))
        
        temp = (distances * math.sin(t2)),float(distances + (distances*math.cos(t2)))
        t1 = math.atan2(self.unmodifiedMousePos[1],float(self.unmodifiedMousePos[0])) - math.atan2(temp[0], temp[1])
        self.arm1.update([math.degrees(t1), math.degrees(t2)])
        self.thetas += self.thetasRates
        
        self.calculatedEF = RobotArm.calculatePosition([distances, distances], [math.degrees(t1),math.degrees(t2)])[-1]
        
        outputAngles = self.organism.activate(self.mousePos)
        outputAngles = [360 * t for t in outputAngles]
        #print "Output Angles:", [math.degrees(t1), math.degrees(t2)], "Calculated Position:", RobotArm.calculatePosition([100,100],[math.degrees(t1), math.degrees(t2)])[-1], "Mouse Position:", self.unmodifiedMousePos
        self.arm2.update(outputAngles)
        
        
        self.repaint()
        self.timer.start(UPDATE_TIME)
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.translate(320, 240)
        qp.scale(1, -1)
        self.arm1.draw(qp)
        #self.arm2.draw(qp)
        
        rand = random.Random()
        seed = 2
        rand.seed(seed)
        numOfTests = 6
        for i in range(numOfTests):
            targetX = rand.uniform(-200, 200)
            targetY = rand.uniform(-200, 200)
            qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,128)))
            qp.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0,128)) )
            qp.drawEllipse(targetX-5, targetY-5, 10, 10)
        
        qp.setPen(QtGui.QPen(QtGui.QColor(0,255,0,128)))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(0,255,0,128)) )
        qp.drawEllipse(self.calculatedEF[0]-5, self.calculatedEF[1]-5, 10, 10)
        
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
winningOrganism = Evolve(DISTANCES)
        
app = QtGui.QApplication(sys.argv)
widget = DrawingWidget(winningOrganism)
sys.exit(app.exec_())
