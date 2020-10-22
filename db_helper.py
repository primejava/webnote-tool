# coding=utf-8
import sqlite3

# 数据表排序：book-》article-》section——》note

class Recorder:
    def __init__(self):
        self.conn = sqlite3.connect('D:\software\python_tools\html-note\\book.db')
        print("Opened database successfully")

    # 读取所有笔记本
    def readBook(self):
        c = self.conn.cursor()
        sql="SELECT id, title from notebook"
        cursor = c.execute(sql)
        books_data = cursor.fetchall()
        books = []
        for row in books_data:
            book = {}
            book["id"]=row[0]
            book["title"] = row[1]
            sql = "SELECT id from article where book_id= {} order by art_idx".format(book["id"])
            cursor = c.execute(sql)
            datas = cursor.fetchall()
            # 这里好像是id的集合
            articles=[]
            for data in datas:
                article={}
                article["id"]=data[0]
                article["marked"] = False
                cursor2 = c.execute("SELECT id from section where article_id= '{}' limit 1".format(data[0]))
                sectionId=cursor2.fetchone()
                if sectionId is not None:
                    article["marked"] = True
                articles.append(article)
            book["books"] = articles
            books.append(book)
        return books

    #读取一个笔记本
    def findBook(self,bookId):
        c = self.conn.cursor()
        sql = "SELECT id, title from notebook where id= {}".format(bookId)
        cursor = c.execute(sql)
        data = cursor.fetchall()
        sql = "SELECT id from article where book_id= {} order by art_idx".format(bookId)
        cursor = c.execute(sql)
        articles = cursor.fetchall()
        book = {}
        book["id"] = data[0][0]
        book["title"] = data[0][1]
        books = []
        for article in articles:
            books.append(article[0])
        book["books"] = books
        return book

    def removeFromBook(self,article_id):
        c = self.conn.cursor()
        sql = "delete  from article where id= '{}'".format(article_id)
        cursor = c.execute(sql)
        self.conn.commit()

    def addToBook(self,bookId,id):
        c = self.conn.cursor()
        sql = "SELECT id from article where id= '{}'".format(id)
        cursor = c.execute(sql)
        data = cursor.fetchall()
        if len(data)>0:
            sql="UPDATE article set book_id = {} where id='{}'".format(bookId, id)
        else:
            sql = "INSERT INTO article (id,book_id) VALUES ('{}',{})".format(id,bookId)
        c.execute(sql)
        self.conn.commit()

    #笔记本内部笔记重排序
    def reWriteBook(self,articles):
        c = self.conn.cursor()
        for idx,article in enumerate(articles):
            print(idx,article)
            c.execute("UPDATE article set art_idx = {} where id='{}'".format(idx,article))
        self.conn.commit()

    #创建笔记本
    def writeBook(self,id,title):
        c = self.conn.cursor()
        sql = "INSERT INTO notebook (id,title) VALUES ({},'{}')".format(id, title)
        c.execute(sql)
        self.conn.commit()


    #重命名笔记本
    def reNameBook(self,id,title):
        c = self.conn.cursor()
        c.execute("UPDATE notebook set title = '{}' where id={}".format(title,id))
        self.conn.commit()


    # 删除一个标注
    def delSection(self,section_id):
        c = self.conn.cursor()
        sql = "delete  from section where id= {}".format(section_id)
        cursor = c.execute(sql)
        sql = "delete  from node where id= {}".format(section_id)
        cursor = c.execute(sql)
        sql = "delete  from note where id= {}".format(section_id)
        cursor = c.execute(sql)
        self.conn.commit()

    # 写标注
    def writeSection(self, id,article_id,type, title, offset_start,offset_end,scroll_height,nodes):
        c = self.conn.cursor()
        sql = "INSERT INTO section (id,type,article_id,title,offset_start,offset_end,scroll_height) VALUES ({},{},'{}','{}',{},{},{})".format(id,type,article_id,title,offset_start,offset_end,scroll_height)
        c.execute(sql)
        for node in nodes:
            sql = "INSERT INTO node (section_id,node_offset,tagName,node_idx) VALUES ({},{},'{}',{})".format(
                id, node["offset"], node["tagName"],node["index"])
            c.execute(sql)
        self.conn.commit()



    # 读取标注
    def readSection(self,article_id):
        sections = []
        c = self.conn.cursor()
        sql = "SELECT id,type,title, offset_start, offset_end, scroll_height from section where article_id= '{}' order by scroll_height".format(article_id)
        cursor = c.execute(sql)
        datas = cursor.fetchall()
        for item in datas:
            section={}
            section["id"]=item[0]
            section["type"] = item[1]
            section["title"] = item[2]
            section["offset_start"] = item[3]
            section["offset_end"] = item[4]
            section["scroll_height"] = item[5]
            nodes=[]
            sql = "SELECT id,node_idx, node_offset, tagName from node where section_id= {}".format(section["id"])
            cursor = c.execute(sql)
            nodes_data = cursor.fetchall()
            for data in nodes_data:
                node={}
                node["id"] = data[0]
                node["index"]=data[1]
                node["offset"] = data[2]
                node["tagName"] = data[3]
                nodes.append(node)
            section["nodes"]=nodes
            notes=[]
            sql = "SELECT id,content, lineNums from note where section_id= {}".format(section["id"])
            cursor = c.execute(sql)
            notes_data = cursor.fetchall()
            for data in notes_data:
                note={}
                note["noteId"] = data[0]
                note["text"]=data[1]
                note["lineNums"] = data[2]
                notes.append(note)
            section["notes"]=notes
            sections.append(section)
        return sections

    def findNote(self,sectionId):
        c = self.conn.cursor()
        notes = []
        sql = "SELECT id,content, lineNums from note where section_id= {}".format(sectionId)
        cursor = c.execute(sql)
        notes_data = cursor.fetchall()
        for data in notes_data:
            note = {}
            note["noteId"] = data[0]
            note["text"] = data[1]
            note["lineNums"] = data[2]
            notes.append(note)
        return notes

    def editNote(self,noteId,text,lineNums):
        text = text.replace("'", "\"")
        c = self.conn.cursor()
        c.execute("UPDATE note set lineNums={},content = '{}' where id={}".format(lineNums,text, noteId))
        self.conn.commit()

    def delNote(self,noteId):
        c = self.conn.cursor()
        sql = "delete  from note where id= {}".format(noteId)
        cursor = c.execute(sql)
        self.conn.commit()

    # 增加一个标注上的笔记
    def addNote(self,sectionId,text,lineNums):
        text=text.replace("'","\"")
        c = self.conn.cursor()
        sql = "INSERT INTO note (section_id,content,lineNums,note_idx) VALUES ({},'{}',{},{})".format(
            sectionId, text, lineNums,0)
        result=c.execute(sql)
        self.conn.commit()
        return result.lastrowid


