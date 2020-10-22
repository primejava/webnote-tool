# -*- coding: utf-8 -*-
import sys,os,time
import json
import webbrowser
from webnote.db_helper import Recorder
from webnote.note_widget import *
from webnote.image_viewer import *
from webnote.ui_drawer import CDrawer
import shutil
from PyQt5 import QtWidgets,QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import pyperclip
import re

path="D:\下载\mx-wc\default"


class Ui_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()
    def get_data(self):
        items=self.listWidget.selectedItems()
        if items:
            return int(items[0].whatsThis())
    def setupUi(self):
        self.setWindowTitle("移动笔记")
        self.setObjectName("Dialog")
        self.resize(400, 327)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.record=Recorder()
        bookList=self.record.readBook()
        self.listWidget = QListWidget(self)
        for book in bookList:
            item = QListWidgetItem(book.get("title"))
            item.setWhatsThis(str(book.get("id")))
            self.listWidget.addItem(item)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

class SortUi_Dialog(QDialog):
    def __init__(self,id):
        super().__init__()
        self.bookId=id
        self.setupUi()
    def get_data(self):
        dirs=[]
        for i in range(self.listWidget.count()):
            item=self.listWidget.item(i)
            dirs.append(item.whatsThis())
        return dirs
    def loadBookWithTitle(self,dirs):
        books = {}
        for dir in dirs:
            json_file = os.path.join(path, dir, "index.json")
            with open(json_file, 'r', encoding='UTF-8') as f:
                load_dict = json.load(f)
                dt = {}
                dt["title"] = load_dict["title"]
                dt["link"] = load_dict["link"]
                dt["created_at"] = load_dict["created_at"]
                books[dir] = dt
        return books

    def up(self):
        index = self.listWidget.currentRow()
        if index > 0:
            index_new = index - 1
            self.listWidget.insertItem(index_new, self.listWidget.takeItem(self.listWidget.currentRow()))
            self.listWidget.setCurrentRow(index_new)

    def down(self):
        index = self.listWidget.currentRow()
        if index < self.listWidget.count():
            index_new = index + 1
            self.listWidget.insertItem(index_new, self.listWidget.takeItem(self.listWidget.currentRow()))
            self.listWidget.setCurrentRow(index_new)

    def setupUi(self):
        self.setWindowTitle("笔记排序")
        self.setObjectName("SortDialog")
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("SortbuttonBox")
        record=Recorder()
        onebook = record.findBook(self.bookId)
        self.listWidget = QListWidget(self)
        dirs=onebook.get("books")
        books=self.loadBookWithTitle(dirs)
        for dir in dirs:
            book = books.get(dir)
            item = QListWidgetItem(book.get("title"))
            item.setWhatsThis(dir)
            self.listWidget.addItem(item)
        v_box = QVBoxLayout()
        btn_up = QPushButton('&Up')
        btn_down = QPushButton('&Down')
        btn_up.clicked.connect(self.up)
        btn_down.clicked.connect(self.down)
        v_box.addWidget(btn_up)
        v_box.addWidget(btn_down)
        h_box = QHBoxLayout()
        h_box.addWidget(self.listWidget)
        h_box.addLayout(v_box)
        v_box.addWidget(self.buttonBox)
        self.setLayout(h_box)
        self.resize(400, 300)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

class BookTree(QTreeWidget):

    def add_bookgroup(self):
        maxId=-1
        for i in range(self.topLevelItemCount()):
            item=self.topLevelItem(i)
            id=item.data(Qt.UserRole, 0)
            if id is not None and maxId<id:
                maxId=id
        parent = QTreeWidgetItem()
        parent.setText(0, "新笔记本")
        parent.setData(Qt.UserRole, 0,maxId+1)
        self.addTopLevelItem(parent)
        self.record.writeBook(maxId+1, "新笔记本")
        return parent

    def findItemById(self,findId):
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            id = item.data(Qt.UserRole, 0)
            if findId==id:
                return item

    def sortByItem(self,childItems,dirs):
        newChilds=[None] * len(childItems)
        for item in childItems:
            dir = item.data(Qt.UserRole, 1)
            idx=dirs.index(dir)
            newChilds[idx]=item
        return newChilds

    def sort_book(self):
        items = self.selectedItems()
        if items:
            item = items[0]
            id = item.data(Qt.UserRole, 0)
            # 是父目录
            if id is not None:
                self.sortdi = SortUi_Dialog(id)
                if self.sortdi.exec_():
                    dirs = self.sortdi.get_data()
                    self.record.reWriteBook(dirs)
                    childItems=item.takeChildren()
                    for child in childItems:
                        item.removeChild(child)
                    newChilds=self.sortByItem(childItems,dirs)
                    for child in newChilds:
                        item.addChild(child)

    def move_book(self):
        items = self.selectedItems()
        if items:
            self.di = Ui_Dialog()
            if self.di.exec_():
                for item in items:
                    id = item.data(Qt.UserRole, 0)
                    # 是子目录
                    if id is None:
                            dir = item.data(Qt.UserRole, 1)
                            bookId = self.di.get_data()
                            if bookId:
                                item.parent().removeChild(item)
                                new_parent=self.findItemById(bookId)
                                new_parent.addChild(item)
                                self.record.addToBook(bookId, dir)

    def create_actions(self):
        action = QtWidgets.QAction("创建笔记本", self.view_menu)
        action2 = QtWidgets.QAction("移动笔记", self.view_menu)
        action3 = QtWidgets.QAction("笔记排序", self.view_menu)
        action.triggered.connect(self.add_bookgroup)
        action2.triggered.connect(self.move_book)
        action3.triggered.connect(self.sort_book)
        self.view_menu.addAction(action)
        self.view_menu.addAction(action2)
        self.view_menu.addAction(action3)
        self.addActions(self.view_menu.actions())

    def contextMenuEvent(self, ce):
        super().contextMenuEvent(ce)
        self.view_menu.exec(QCursor.pos())
    def __init__(self,_record,_func, parent=None):
        super().__init__(parent)
        self.record=_record
        self.refresh=_func
        self.header().hide()
        self.view_menu = QMenu(self)
        self.create_actions()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)


# 修复鼠标滚动失灵问题
class BugFixListView(QListWidget):
    def updateGeometries(self):
        super(BugFixListView, self).updateGeometries()
        self.verticalScrollBar().setSingleStep(15)

class FloatWidget(QtWidgets.QWidget):
    def bigger(self):
        self.browser.setZoomFactor(self.browser.zoomFactor()+0.1)
    def smaller(self):
        self.browser.setZoomFactor(self.browser.zoomFactor()-0.1)
    def toTop(self):
        command = '\n window.scrollTo(0, 0);'
        self.browser.page().runJavaScript(command)
    def slideMenu(self):
        if not hasattr(self, 'rightDrawer'):
            self.rightDrawer = CDrawer(self, widget=self.rightLayout)
            self.rightDrawer.setDirection(CDrawer.RIGHT)
        self.rightDrawer.show()

    def __init__(self, parent=None):
        super(FloatWidget, self).__init__(parent)
        self.width=80
        self.height=200
        self.setGeometry(0, 0, 80, 200)
        self.browser=parent.browser
        self.rightLayout = parent.tabs
        hbox = QtWidgets.QVBoxLayout()
        self._popup = QtWidgets.QPushButton(self)
        self._popup.setText("放大")
        self._popup.clicked.connect(self.bigger)
        self._popup.setFixedSize(self.width,self.height/3)
        hbox.addWidget(self._popup)
        self._popup2 = QtWidgets.QPushButton(self)
        self._popup2.setText("缩小")
        self._popup2.clicked.connect(self.smaller)
        self._popup2.setFixedSize(self.width,self.height/3)
        hbox.addWidget(self._popup2)
        # self._popup3 = QtWidgets.QPushButton(self)
        # self._popup3.setText("侧边栏")
        # self._popup3.clicked.connect(self.slideMenu)
        # self._popup3.setFixedSize(self.width,self.height/3)
        # hbox.addWidget(self._popup3)
        self._popup4 = QtWidgets.QPushButton(self)
        self._popup4.setText("回到顶部")
        self._popup4.clicked.connect(self.toTop)
        self._popup4.setFixedSize(self.width,self.height/3)
        hbox.addWidget(self._popup4)
        self.setLayout(hbox)


class WebEngineView(QWebEngineView):
    def __init__(self, _record,*args, **kwargs):
        super(WebEngineView, self).__init__(*args, **kwargs)
        self.channel = QWebChannel(self)
        self.record=_record
        self.imgViewer = Img_Dialog()
        # 把自身对象传递进去
        self.channel.registerObject('Bridge', self)
        # 设置交互接口
        self.page().setWebChannel(self.channel)

    def view_img(self,result):
        if result:
            imgpath=result[8:]
            imgpath=imgpath.replace(imgpath.split("//")[1],"下载")
            self.imgViewer.setImg(imgpath)
            self.imgViewer.show()

    # 注意pyqtSlot用于把该函数暴露给js可以调用
    @pyqtSlot(str,str)
    def callFromJs(self,method, result):
        if method=="img":
            self.view_img(result)
        elif method=="tip":
            datas=result.split("|")
            lists=self.record.findNote(datas[2])
            response={}
            response["clientX"]=int(datas[0])
            response["clientY"] = int(datas[1])
            response["sectionId"] = datas[2]
            notes=[]
            for item in lists:
                notes.append(item["text"])
            response["notes"] = notes
            self.page().runJavaScript("\n showToolTip({});".format(response))

class MainWindow(QWidget):
    # 给笔记列表添加一项笔记 标注id，标题，标注所在文档高度
    def addNodeItem(self,maskId,type,title,scroll_height,texts=None):
            item = QListWidgetItem()
            item.setData(Qt.UserRole + 1,maskId)
            item.setData(Qt.UserRole + 2, scroll_height)
            widget = CustomWidget(item,type,title,self.record)
            widget.set_maskId(maskId)
            widget.set_browser(self.browser)
            item.setSizeHint(widget.sizeHint())
            self.noteListWidget.addItem(item)
            self.noteListWidget.setItemWidget(item, widget)
            if texts:
                for text in texts:
                    widget.load_note(text)

    # 加载所有网页
    def load_htmls(self):
        data = {}
        for dir in os.listdir(path):
            json_file = os.path.join(path, dir, "index.json")
            with open(json_file, 'r', encoding='UTF-8') as f:
                load_dict = json.load(f)
                dt = {}
                dt["title"] = load_dict["title"]
                dt["link"] = load_dict["link"]
                dt["created_at"] = load_dict["created_at"]
                data[dir] = dt
        return data

    def load_notes(self):
        self.noteListWidget.clear()
        # 为了加载右侧的笔记
        sections = self.record.readSection(self.currentHtml)
        for section in sections:
            title=section["title"]
            mask_id=section["id"]
            type = section["type"]
            scroll_height = section["scroll_height"]
            if "notes" in section.keys():
                texts=section["notes"]
                self.addNodeItem(mask_id,type,title,scroll_height,texts)
            else:
                self.addNodeItem(mask_id,type, title, scroll_height)


    def onTabChanged(self,idx):
        if not self.currentHtml:
            return
        if idx==1:
            currentTab = self.tabs.currentWidget()
            if self.currentHtml!=currentTab.whatsThis():
                currentTab.setWhatsThis(self.currentHtml)
                self.load_notes()


    def refresh(self):
        self.bookListWidget.clear()
        parent = QTreeWidgetItem()
        parent.setText(0, "默认笔记本")
        parent.setData(Qt.UserRole, 0, -1)
        self.bookListWidget.addTopLevelItem(parent)
        bookList=self.record.readBook()
        htmls = self.load_htmls()
        for book in bookList:
            item = QTreeWidgetItem()
            item.setText(0, book.get("title"))
            item.setData(Qt.UserRole, 0, book.get("id"))
            self.bookListWidget.addTopLevelItem(item)
            books=book.get("books")
            if books and len(books)>0:
                for one_book in books:
                    dir=one_book["id"]
                    dt = htmls.get(dir)
                    if dt:
                        son = QTreeWidgetItem(item)
                        marked=one_book["marked"]
                        if marked:
                            son.setBackground(0,QColor("#ff9"))
                        son.setText(0, dt.get("title"))
                        son.setData(Qt.UserRole, 1, dir)
                        son.setData(Qt.UserRole+1, 0, dt.get("link"))
                        son.setData(Qt.UserRole + 1, 1, book.get("id"))
                        self.bookListWidget.addTopLevelItem(son)
                        htmls.pop(dir)

        for dir in os.listdir(path):
            dt=htmls.get(dir)
            if dt:
                item = QTreeWidgetItem(parent)
                item.setText(0, dt.get("title"))
                item.setData(Qt.UserRole,1,dir)
                item.setData(Qt.UserRole+1,0, dt.get("link"))
                item.setData(Qt.UserRole + 1, 1, "-1")
                self.bookListWidget.addTopLevelItem(item)

    def edit_json(self,json_file,value):
        with open(json_file, 'r', encoding='UTF-8') as f:
            json_data = json.load(f)
            with open(json_file, 'w', encoding='UTF-8') as fw:
                json_data['title'] = value
                json.dump(json_data, fw)


        # 回调函数
    def js_callback(self, result):
        id = str(result["id"])
        scroll_height=str(result["top"])
        title=result["text"]
        offset_start = result["offset_start"]
        offset_end=result["offset_end"]
        nodes=result["serializeNodes"]
        type = result["type"]
        self.record.writeSection(id,self.currentHtml,type,title,offset_start,offset_end,scroll_height,nodes)
        if self.tabs.currentIndex()==0:
            # 将此标签置空，促使列表重新加载
            self.noteTab.setWhatsThis(None)
            self.tabs.setCurrentIndex(1)
        else:
            self.addNodeItem(id,type,title, scroll_height)
        self.contextMenu.hide()

    def copy_text_callbak(self,result):
        pyperclip.copy(result)
        self.contextMenu.hide()

    def copy_text(self):
        command = '\n getSelectionText();'
        self.browser.page().runJavaScript(command, self.copy_text_callbak)

    def confuse(self):
        id = str(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        command = '\n renderSelectionNodes({},{});'.format(id,2)
        self.browser.page().runJavaScript(command, self.js_callback)

    def mask(self):
        id= str(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())))
        command = '\n renderSelectionNodes({},{});'.format(id,1)
        self.browser.page().runJavaScript(command, self.js_callback)

    def open_url(self):
        webbrowser.open(self.url_hoverd)

    def delete_mask(self,mask_id):
        command = '\n delete_mask({});'.format(id)
        self.browser.page().runJavaScript(command)

    def renameImg(self, image):
        assets_dir=os.path.join(path, self.currentHtml, "assets")
        for file in os.listdir(assets_dir):
            old_file_name = os.path.splitext(file)[0]
            new_file_name = os.path.splitext(image)[0]
            if old_file_name == new_file_name:
                os.rename(os.path.join(assets_dir, file), os.path.join(assets_dir, image))
                break

    def doCorrect(self):
        if self.currentHtml:
            html_dir = os.path.join(path, self.currentHtml)
            html_file= os.path.join(html_dir,"index.html")
            with open(html_file, "r", encoding='utf-8') as html:
                content = html.read()
                p = r'(assets.[\S]*?.(jpg|jpeg|png|gif|bmp|webp))'
                # 返回正则表达式在字符串中所有匹配结果的列表
                imglist = re.findall(p, content)
                # 循环遍历列表的每一个值
                for img in imglist:
                    img_file = os.path.join(html_dir, img[0])
                    if not os.path.exists(img_file):
                        image_file = img[0][7:]
                        self.renameImg(image_file)
        QMessageBox.about(self, "提示", "已尝试纠正图片")


    def rename(self):
        for item in self.bookListWidget.selectedItems():
            parentId = item.data(Qt.UserRole, 0)
            # 是子目录
            if parentId is None:
                dir = item.data(Qt.UserRole,1)
                title=item.text(0)
                dlg = QInputDialog(self)
                text, ok = dlg.getText(self, '重命名标题', '标题',QLineEdit.Normal, title)
                if ok:
                    item.setText(0,text)
                    json_file = os.path.join(path, dir, "index.json")
                    self.edit_json(json_file,text)
            else:
                title = item.text(0)
                dlg = QInputDialog(self)
                text, ok = dlg.getText(self, '重命名标题', '标题', QLineEdit.Normal, title)
                if ok:
                    item.setText(0, text)
                    self.record.reNameBook(parentId, text)

    def gotoHTML(self):
        item=self.bookListWidget.selectedItems()[0]
        link=item.data(Qt.UserRole+1,0)
        if link:
            webbrowser.open(link)

    def del_checked(self):
        reply = QMessageBox.question(self, '询问', '这将删除网页及其所有笔记，确定删除吗?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for item in self.bookListWidget.selectedItems():
                id = item.data(Qt.UserRole, 0)
                # 是子目录
                if id is None:
                    dir = item.data(Qt.UserRole, 1)
                    html_dir = os.path.join(path, dir)
                    if os.path.exists(html_dir):
                        shutil.rmtree(html_dir)
                    parent = item.parent()
                    if parent:
                        self.record.removeFromBook(dir)
                    self.refresh()
                else:
                    QMessageBox.about(self,"提示","笔记本无法删除")

    def loadCss(self,css_path):
        path = QtCore.QFile(css_path)
        if not path.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return
        css = path.readAll().data().decode("utf-8")
        SCRIPT = """
           (function() {
           css = document.createElement('style');
           css.type = 'text/css';
           document.head.appendChild(css);
           css.innerText = `%s`;
           })()
           """ % (css)
        self.browser.page().runJavaScript(SCRIPT)

    def loadJs(self,js_path):
        path = QtCore.QFile(js_path)
        if not path.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            return
        js = path.readAll().data().decode("utf-8")
        self.browser.page().runJavaScript(js)

    def on_load_finished(self):
        if (self.isFirstLoadFinished):
            self.isFirstLoadFinished = False
            self.loadCss("note.css")
            self.loadJs("qwebchannel.js")
            self.loadJs("note.js")
            # 为了加载网页标签
            sections = self.record.readSection(self.currentHtml)
            for section in sections:
                id = section["id"]
                type = section["type"]
                text_nodes = section["nodes"]
                offset_start = section["offset_start"]
                offset_end = section["offset_end"]
                command = '\n load_mask({},{},{},{},{})'.format(id,type,text_nodes, offset_start,offset_end)
                self.browser.page().runJavaScript(command)
                # if "notes" in section.keys():
                #     texts = section["notes"]
                #     if len(texts) > 0:
                #         notes = []
                #         for item in texts:
                #             notes.append(item["text"])
                #         response = {}
                #         response["sectionId"] = id
                #         response["notes"] = notes
                #         self.browser.page().runJavaScript("\n showToolTip({});".format(response))

    # 需要加载笔记，然后再加载标注（包括列表标注，和网页的标注）
    def bookListClicked(self, qmodelindex):
        item = self.bookListWidget.currentItem()
        parentId=item.data(Qt.UserRole,0)
        if parentId is None:
            self.currentHtml = item.data(Qt.UserRole,1)
            self.browser.setZoomFactor(1.0)
            html=os.path.join(path, item.data(Qt.UserRole,1), "index.html").replace("\\","//")
            self.browser.load(QUrl('file:///'+html))
            self.isFirstLoadFinished=True

    def noteListClicked(self, item):
        mask_id=item.data(Qt.UserRole + 1)
        # scroll_top = int(item.data(Qt.UserRole + 2))
        command = '\n toggleMask({});'.format(mask_id)
        self.browser.page().runJavaScript(command)


    def showContextMenu(self, pos):
        '''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        self.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示
        self.contextMenu.show()


    def createContextMenu(self):
        self.browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.showContextMenu)
        self.contextMenu=QMenu(self)
        url_action = self.contextMenu.addAction(u'打开链接')
        url_action.triggered.connect(self.open_url)
        mask_action = self.contextMenu.addAction(u'标注')
        mask_action.triggered.connect(self.mask)
        confuse_action = self.contextMenu.addAction(u'疑惑')
        confuse_action.triggered.connect(self.confuse)
        copy_action = self.contextMenu.addAction(u'复制')
        copy_action.triggered.connect(self.copy_text)


    # 调整位置
    def adjustBtnPos(self):
        x = int(self.geometry().width()*4/5 - self.floatButton.width-70)
        y = int(self.geometry().height() - self.floatButton.height-20)
        self.floatButton.move(x, y)
    #
    def  changeEvent(self,event):
        if event.type() == QEvent.WindowStateChange:
            self.adjustBtnPos()

    def showEvent(self, e):
        self.adjustBtnPos()

    def searchBook(self):
        title=self.searchBox.text()
        cursor = QTreeWidgetItemIterator(self.bookListWidget)
        while cursor.value():
            item = cursor.value()
            if title.lower() in item.text(0).lower():
                item.setHidden(False)
                # 需要让父节点也显示,不然子节点显示不出来
                try:
                    item.parent().setHidden(False)
                except Exception:
                    pass
            else:
                item.setHidden(True)
            cursor = cursor.__iadd__(1)

    def on_url_changed(self, url):
        self.url_hoverd=url

    def __init__(self):
        super(QWidget, self).__init__()
        self.record=Recorder()
        self.currentHtml=None
        self.url_hoverd=None
        self.setGeometry(200, 50, 1500, 1000)
        self.mainLayout = QHBoxLayout()
        self.leftLayout = QHBoxLayout()
        self.rightLayout= QHBoxLayout()
        self.bookLayout = QFormLayout()
        self.browser = WebEngineView(self.record)
        self.browser.page().linkHovered.connect(self.on_url_changed)
        self.isFirstLoadFinished=True
        self.browser.loadFinished.connect(self.on_load_finished)
        self.leftLayout.addWidget(self.browser)
        self.mainLayout.addLayout(self.leftLayout,4)
        self.mainLayout.addLayout(self.rightLayout,1)

        self.searchBox = QLineEdit()
        self.searchBox.returnPressed.connect(self.searchBook)
        self.bookLayout.addRow(self.searchBox)
        self.bookListWidget = BookTree(self.record,self.refresh)
        self.bookListWidget.clicked.connect(self.bookListClicked)
        self.bookListWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.bookLayout.addRow(self.bookListWidget)

        self.gotoButton = QtWidgets.QPushButton()
        self.gotoButton.setFocusPolicy(0)
        self.gotoButton.setText("跳转到")
        self.gotoButton.clicked.connect(self.gotoHTML)
        self.delButton = QtWidgets.QPushButton()
        self.delButton.setFocusPolicy(0)
        self.delButton.setText("删除")
        self.delButton.clicked.connect(self.del_checked)
        self.refreshButton = QtWidgets.QPushButton()
        self.refreshButton.setFocusPolicy(0)
        self.refreshButton.setText("刷新")
        self.refreshButton.clicked.connect(self.refresh)
        self.correctButton = QtWidgets.QPushButton()
        self.correctButton.setFocusPolicy(0)
        self.correctButton.setText("纠正")
        self.correctButton.clicked.connect(self.doCorrect)
        self.renameButton = QtWidgets.QPushButton()
        self.renameButton.setFocusPolicy(0)
        self.renameButton.setText("重命名")
        self.renameButton.clicked.connect(self.rename)
        self.bookBox = QHBoxLayout()
        self.bookBox.addWidget(self.delButton)
        self.bookBox.addWidget(self.refreshButton)
        self.bookBox.addWidget(self.correctButton)
        self.bookBox.addWidget(self.renameButton)
        self.bookBox.addWidget(self.gotoButton)
        self.bookLayout.addRow(self.bookBox)
        self.noteLayout = QFormLayout()
        self.noteListWidget = BugFixListView()
        self.noteListWidget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.noteListWidget.itemClicked.connect(self.noteListClicked)
        self.noteListWidget.setStyleSheet("QListWidget::Item:hover{background:#ffffff;padding-top:0px; padding-bottom:0px; }"
                                            "QListWidget::item:selected{background:#ffffff; color:red; }"
                                            "QListWidget::item:selected:!active{active{border-width:0px;background:#ffffff; }")
        self.noteLayout.addRow(self.noteListWidget)
        self.tabs = QTabWidget()
        self.bookTab = QWidget()
        self.noteTab = QWidget()
        self.tabs.addTab(self.bookTab,"目录")
        self.tabs.addTab(self.noteTab,"笔记")
        self.tabs.currentChanged['int'].connect(self.onTabChanged)
        self.bookTab.setLayout(self.bookLayout)
        self.noteTab.setLayout(self.noteLayout)
        self.rightLayout.addWidget(self.tabs)
        self.setLayout(self.mainLayout)
        self.createContextMenu()
        self.floatButton = FloatWidget(self)
        self.refresh()


if __name__ == '__main__':
    app=QApplication(sys.argv)
    app.setApplicationName("笔记浏览")
    app.setFont(QFont("幼圆"))
    win=MainWindow()
    win.show()
    app.exit(app.exec_())