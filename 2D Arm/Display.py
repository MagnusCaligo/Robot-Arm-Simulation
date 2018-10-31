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

    def __init__(self):
        super(DrawingWidget, self).__init__()
        self.setGeometry(150,150,640,480)
        self.show()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(UPDATE_TIME)
        self.arm1 = RobotArm(DOF, DISTANCES)
        
        self.thetas = [0] * DOF
        self.thetasRates = np.random.normal(0, 1, DOF)
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            sys.exit()
            
    def update(self):
        self.arm1.update(self.thetas)
        self.thetas += self.thetasRates
        self.repaint()
        self.timer.start(UPDATE_TIME)
        
    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.translate(320, 240)
        qp.scale(1, -1)
        self.arm1.draw(qp)
        qp.end()
        
        
        
print RobotArm.calculatePosition([100,100],[180,90])
winningOrganism = Evolve(DISTANCES)
        
app = QtGui.QApplication(sys.argv)
widget = DrawingWidget()
sys.exit(app.exec_())