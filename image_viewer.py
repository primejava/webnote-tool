# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QWidget,QDialog
from PyQt5.QtCore import QPoint,Qt
from PyQt5.QtGui import QPixmap,QPainter

class ImageWithMouseControl(QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Image with mouse control')
        self.parent = parent
        self.point = QPoint(0, 0)

    def setImg(self,src):
        self.img = QPixmap(src)
        self.scaled_img = self.img.scaledToWidth(400)

    def paintEvent(self, e):
        '''
        绘图
        :param e:
        :return:
        '''
        painter = QPainter()
        painter.begin(self)
        self.draw_img(painter)
        painter.end()

    def draw_img(self, painter):
        painter.drawPixmap(self.point, self.scaled_img)

    def mouseMoveEvent(self, e):  # 重写移动事件
        if self.left_click:
            self._endPos = e.pos() - self._startPos
            self.point = self.point + self._endPos
            self._startPos = e.pos()
            self.repaint()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = True
            self._startPos = e.pos()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.left_click = False
        elif e.button() == Qt.RightButton:
            self.point = QPoint(0, 0)
            self.scaled_img = self.img.scaledToWidth(self.size().width()-10)
            self.repaint()

    def wheelEvent(self, e):
        if e.angleDelta().y() > 0:
            # 放大图片
            self.scaled_img = self.img.scaledToWidth(self.scaled_img.width()-50)
            new_w = e.x() - (self.scaled_img.width() * (e.x() - self.point.x())) / (self.scaled_img.width() + 50)
            new_h = e.y() - (self.scaled_img.height() * (e.y() - self.point.y())) / (self.scaled_img.height() + 50)
            self.point = QPoint(new_w, new_h)
            self.repaint()
        elif e.angleDelta().y() < 0:
            # 缩小图片
            self.scaled_img = self.img.scaledToWidth(self.scaled_img.width()+50)
            new_w = e.x() - (self.scaled_img.width() * (e.x() - self.point.x())) / (self.scaled_img.width() - 50)
            new_h = e.y() - (self.scaled_img.height() * (e.y() - self.point.y())) / (self.scaled_img.height() - 50)
            self.point = QPoint(new_w, new_h)
            self.repaint()

    def resizeEvent(self, e):
        if self.parent is not None:
            self.scaled_img = self.img.scaledToWidth(self.size().width()-10)
            self.point = QPoint(0, 0)
            self.update()

class Img_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.widget = ImageWithMouseControl(self)
        self.widget.setGeometry(10, 10, 400, 400)
        self.setWindowTitle("图片查看器")
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint|Qt.WindowCloseButtonHint)
        self.setObjectName("ImgDialog")
    def setImg(self,src):
        self.widget.setImg(src)
    def resizeEvent(self, e):
        self.widget.setGeometry(10, 10, self.width() - 10, self.height() - 10)