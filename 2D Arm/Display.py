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
        self.organism = organism
        
        self.thetas = [0] * DOF
        self.thetasRates = np.random.normal(0, 1, DOF)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            sys.exit()
            
    def update(self):
        self.arm1.update(self.thetas)
        self.thetas += self.thetasRates
        
        outputAngles = self.organism.activate(self.mousePos)
        outputAngles = [360 * t for t in outputAngles]
        print "Output Angles:", outputAngles
        self.arm2.update(outputAngles)
        
        
        self.repaint()
        self.timer.start(UPDATE_TIME)
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.translate(320, 240)
        qp.scale(1, -1)
        self.arm1.draw(qp)
        self.arm2.draw(qp)
        
        rand = random.Random()
        seed = 2
        rand.seed(seed)
        numOfTests = 2
        for i in range(numOfTests):
            targetX = rand.uniform(-200, 200)
            targetY = rand.uniform(-200, 200)
            print targetX, targetY
            qp.setPen(QtGui.QPen(QtGui.QColor(0,0,0,128)))
            qp.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0,128)) )
            qp.drawEllipse(targetX-5, targetY-5, 10, 10)
        
        
        qp.end()
        
    def mouseMoveEvent(self,e):
        point =  e.pos()
        transform = QtGui.QTransform()
        transform.translate(-320,240)
        transform.scale(1,-1)
        point = transform.map(point)
        self.mousePos = (point.x(), point.y())
        
        
        
print RobotArm.calculatePosition([100,100],[180,90])
winningOrganism = Evolve(DISTANCES)
        
app = QtGui.QApplication(sys.argv)
widget = DrawingWidget(winningOrganism)
sys.exit(app.exec_())