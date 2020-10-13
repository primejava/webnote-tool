#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



# 图片按钮
class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed,parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed
        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return self.pixmap.size()


# 文本添加区
class AddWidget(QWidget):
    def tag(self):
        yellow = QColor(255, 255, 0)
        fmt = QTextCharFormat()
        fmt.setBackground(yellow)
        cursor = self.note_add.textCursor()
        cursor.mergeCharFormat(fmt)
        self.note_add.mergeCurrentCharFormat(fmt)

    def __init__(self, *args, **kwargs):
        super(AddWidget, self).__init__(*args, **kwargs)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        # 工具栏
        self.edit_tool_Layout = QHBoxLayout(self)
        self.edit_tool_Layout.setAlignment(Qt.AlignRight)
        self.note_tag_button = QPushButton("着重")
        self.note_tag_button.setFixedWidth(40)
        self.note_tag_button.setFixedHeight(20)
        self.note_tag_button.clicked.connect(self.tag)
        self.edit_tool_Layout.addWidget(self.note_tag_button)
        self.main_layout.addLayout(self.edit_tool_Layout)
        # 编辑区
        self.note_add = QTextEdit()
        self.main_layout.addWidget(self.note_add)
        self.note_cancel_button = QPushButton("取消")
        self.note_cancel_button.setFixedWidth(40)
        self.note_cancel_button.setFixedHeight(20)
        self.note_add_button = QPushButton("确定")
        self.note_add_button.setFixedWidth(40)
        self.note_add_button.setFixedHeight(20)
        self.edit_bottom_Layout = QHBoxLayout(self)
        self.edit_bottom_Layout.setAlignment(Qt.AlignRight)
        self.edit_bottom_Layout.addWidget(self.note_cancel_button)
        self.edit_bottom_Layout.addWidget(self.note_add_button)
        self.main_layout.addLayout(self.edit_bottom_Layout)


# 文本详情区
class DetailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super(DetailWidget, self).__init__(*args, **kwargs)
        self.main_layout = QVBoxLayout(self)
        # 详情区
        self.note_content = QLabel()
        self.note_content.setWordWrap(True)
        self.main_layout.addWidget(self.note_content)
        self.note_edit_button = QPushButton("编辑")
        self.note_edit_button.setFixedWidth(40)
        self.note_edit_button.setFixedHeight(20)
        self.note_del_button = QPushButton("删除")
        self.note_del_button.setFixedWidth(40)
        self.note_del_button.setFixedHeight(20)
        self.edit_bottom_Layout = QHBoxLayout(self)
        self.edit_bottom_Layout.setAlignment(Qt.AlignRight)
        self.edit_bottom_Layout.addWidget(self.note_edit_button)
        self.edit_bottom_Layout.addWidget(self.note_del_button)
        self.main_layout.addLayout(self.edit_bottom_Layout)

    def sizeHint(self):
        lineNums = self.parent().getTextLineNumbers()
        if lineNums>0:
            width = self.main_layout.sizeHint().width()
            fontHeight=17
            return QSize(width, lineNums* fontHeight+60)
        return self.main_layout.sizeHint()

# 文本块
class NoteWidget(QWidget):
    def setTextLineNumbers(self,lineNums):
        self.lineNums=lineNums
    # 获取编辑框文本行数,默认直接从编辑框取值
    def getTextLineNumbers(self,getByWidget=False):
        if (not getByWidget) and self.lineNums>0:
            return self.lineNums
        linenums = 0
        tb = self.addWidget.note_add.document().begin()
        while (tb.isValid()):
            layout = tb.layout()
            if layout:
                linenums = linenums + layout.lineCount()
            tb = tb.next()
        return linenums
    #删除自身
    def deleteSelf(self):
        self.main_layout.removeWidget(self.addWidget)
        self.main_layout.removeWidget(self.detailWidget)
        self.addWidget.deleteLater()
        self.detailWidget.deleteLater()
        self.parentWidget.delete_note(self)

    # 点击取消，编辑框消失，详情框出现，或者直接删除这个部件
    def cancel(self):
        self.addWidget.hide()
        self.detailWidget.show()
        self.parentWidget.parentWidget.setSizeHint(self.parentWidget.sizeHint())
        if str(self.id) == "-1":
            self.deleteSelf()

    # 点击添加,编辑框消失,详情框出现
    def add(self):
        text = self.addWidget.note_add.toHtml()
        if not text:
            QMessageBox.information(self, "提示", "内容不能为空")
            return
        listWidgetItem = self.parentWidget.parentWidget
        # info = listWidgetItem.whatsThis()
        maskId = listWidgetItem.data(Qt.UserRole + 1)
        # maskId=info.split("|")[0]

        self.detailWidget.note_content.setText(text)
        self.addWidget.hide()
        self.detailWidget.show()
        lineNums = self.getTextLineNumbers(True)
        self.setTextLineNumbers(lineNums)
        listWidgetItem.setSizeHint(self.parentWidget.sizeHint())
        if str(self.id)=="-1":
            self.id =self.parentWidget.record.addNote(maskId,text,lineNums)
        else:
            self.parentWidget.record.editNote(self.id , text,lineNums)


    # 点击编辑,详情框关闭,编辑框出现
    def edit(self):
        text=self.detailWidget.note_content.text()
        self.addWidget.note_add.setText(text)
        self.detailWidget.hide()
        self.addWidget.show()
        self.parentWidget.parentWidget.setSizeHint(self.parentWidget.sizeHint())

    def setId(self,_id):
        self.id=_id

    def __init__(self, _parentWidget,*args, **kwargs):
        super(NoteWidget, self).__init__(*args, **kwargs)
        self.parentWidget=_parentWidget
        self.id=-1
        self.lineNums=0
        self.main_layout = QVBoxLayout(self)
        self.addWidget=AddWidget()
        self.detailWidget=DetailWidget()
        self.addWidget.note_cancel_button.clicked.connect(self.cancel)
        self.addWidget.note_add_button.clicked.connect(self.add)
        self.detailWidget.note_edit_button.clicked.connect(self.edit)
        self.detailWidget.note_del_button.clicked.connect(self.deleteSelf)
        self.main_layout.addWidget(self.addWidget)
        self.main_layout.addWidget(self.detailWidget)
    def sizeHint(self):
        if self.lineNums==0:
            return self.main_layout.sizeHint()
        else:
            if self.detailWidget.isVisible():
                return self.detailWidget.sizeHint()
            return self.main_layout.sizeHint()

class CustomWidget(QWidget):
    # 高度累加
    def addQsize(self,qsize_a,qsize_b):
        return QSize(qsize_a.width(),qsize_a.height()+qsize_b.height())
    # 删除自己的网页标注
    def delete_mask(self):
        command = '\n delete_mask({});'.format(self.mask_id)
        self.browser.page().runJavaScript(command)

    # 删除标注下的一个笔记
    def delete_note(self,noteWidget):
        noteId= noteWidget.id
        self.note_list.remove(noteWidget)
        self.main_layout.removeWidget(noteWidget)
        noteWidget.deleteLater()
        listWidgetItem = self.parentWidget
        listWidgetItem.setSizeHint(self.sizeHint())
        if str(noteId)!="-1":
            # info = listWidgetItem.whatsThis()
            maskId = listWidgetItem.data(Qt.UserRole + 1)
            # maskId=info.split("|")[0]
            self.record.delNote(noteId)

    # 手动点击添加
    def add_note(self):
        noteWidget = NoteWidget(self)
        noteWidget.detailWidget.hide()
        self.main_layout.addWidget(noteWidget)
        self.note_list.append(noteWidget)
        self.parentWidget.setSizeHint(self.sizeHint())

    # 自动load节点，从json文本中获取数据
    def load_note(self,text):
        noteWidget = NoteWidget(self)
        noteWidget.setId(text["noteId"])
        if "lineNums" in text.keys():
            noteWidget.setTextLineNumbers(int(text["lineNums"]))
        noteWidget.addWidget.hide()
        noteWidget.detailWidget.note_content.setText(text["text"])
        self.main_layout.addWidget(noteWidget)
        self.note_list.append(noteWidget)
        self.parentWidget.setSizeHint(self.sizeHint())
    # 删除自己
    def del_self(self):
        reply = QMessageBox.question(self, '询问', '这将删除此标注及其所有笔记，确定删除吗?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.delete_mask()
            for noteWidget in self.note_list:
                noteWidget.deleteSelf()
            self.deleteLater()
            listWid=self.parentWidget.listWidget()
            listWid.takeItem(listWid.row(self.parentWidget))
            self.record.delSection(self.mask_id)

    def edit_self(self):
        pass
    def set_maskId(self,maskId):
        self.mask_id=maskId


    def set_browser(self, _browser):
        self.browser = _browser

    def __init__(self, _parentWidget,type,_title, _record,*args, **kwargs):
        super(CustomWidget, self,).__init__(*args, **kwargs)
        self.mask_id=None
        self.browser=None
        self.main_layout = QVBoxLayout(self)
        self.note_list=list()
        self.parentWidget=_parentWidget
        self.record=_record
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        # 标题区域
        self.note_title=QLabel(_title)
        self.note_title.setContentsMargins(0,0,0,10)
        if type==1:
            self.note_title.setStyleSheet('QLabel { border:none; border-left:5px solid rgb(255,255,0);border-bottom:2px dashed gray;}')
        else:
            self.note_title.setStyleSheet(
                'QLabel { border:none; border-left:5px solid rgb(255,122,122);border-bottom:2px dashed gray;}')
        self.note_title.setWordWrap(True)
        self.main_layout.addWidget(self.note_title)
        # 工具按钮
        self.tool_Layout = QHBoxLayout(self)
        self.tool_Layout.setAlignment(Qt.AlignRight)
        addButton = PicButton(QPixmap("add.png"),QPixmap("add_hover.png"),QPixmap("add_hover.png"))
        addButton.setFixedWidth(25)
        addButton.setFixedHeight(25)
        addButton.clicked.connect(self.add_note)
        delButton = PicButton(QPixmap("del.png"),QPixmap("del_hover.png"),QPixmap("del_hover.png"))
        delButton.setFixedWidth(25)
        delButton.setFixedHeight(25)
        delButton.clicked.connect(self.del_self)
        editButton = PicButton(QPixmap("edit.png"),QPixmap("edit_hover.png"),QPixmap("edit_hover.png"))
        editButton.setFixedWidth(25)
        editButton.setFixedHeight(25)
        editButton.clicked.connect(self.edit_self)
        self.tool_Layout.addWidget(addButton)
        self.tool_Layout.addWidget(editButton)
        self.tool_Layout.addWidget(delButton)
        self.main_layout.addLayout(self.tool_Layout)

    def sizeHint(self):
        size_init = self.addQsize(self.note_title.sizeHint(),self.tool_Layout.sizeHint())
        # 对未计算到的高度进行补偿
        offset_size=QSize(0,30)
        size_init=self.addQsize(size_init,offset_size)
        for noteWidget in self.note_list:
            size_init=self.addQsize(size_init,noteWidget.sizeHint())
        return size_init