import sys
import sqlite3
import pypinyin
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QApplication, QLineEdit, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSizePolicy, QListWidget, QListWidgetItem, QTextEdit, QMessageBox
from PySide6.QtGui import QIcon

import ApplescriptGenerator
import Chinese

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.con = sqlite3.connect("songs.sqlite3")
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS song(id integer primary key autoincrement, title, lyrics)")

        self.col1 = QVBoxLayout() # search
        self.col2 = QVBoxLayout() # edit
        self.col3 = QVBoxLayout() # arrow
        self.col4 = QVBoxLayout() # list

        self.layout = QHBoxLayout()
        self.layout.addLayout(self.col1)
        self.layout.addLayout(self.col2)
        self.layout.addLayout(self.col3)
        self.layout.addLayout(self.col4)

        self.setLayout(self.layout)

        # Column 1
        self.col1.addWidget(QLabel('搜索(标题汉字、拼音、首字母/歌词汉字)'))
        self.search = QLineEdit()
        self.col1.addWidget(self.search)

        self.col1.addWidget(QLabel('（双击/选中后按右边箭头→加入投影片）'))
        self.results = QListWidget()
        self.col1.addWidget(self.results)

        self.search.textChanged.connect(self.onSearch)
        self.search.returnPressed.connect(self.results.setFocus)
        
        self.results.currentItemChanged.connect(self.onCurrentItemChanged)
        self.results.itemDoubleClicked.connect(self.onSelect)
        
        # Column 2
        self.col2.addWidget(QLabel('标题'))
        self.title = QLineEdit()
        self.col2.addWidget(self.title)

        self.col2.addWidget(QLabel('歌词（空一行来分页，自动转简体）'))
        self.lyrics = QTextEdit()
        self.lyrics.setAcceptRichText(False)
        self.col2.addWidget(self.lyrics)

        self.toolbar = QHBoxLayout()
        self.save = QPushButton('保存')
        self.delete = QPushButton('删除')
        self.add = QPushButton('添加歌曲')
        self.toolbar.addWidget(self.save)
        self.toolbar.addWidget(self.delete)
        self.toolbar.addWidget(self.add)
        self.col2.addLayout(self.toolbar)

        self.save.clicked.connect(self.onSave)
        self.delete.clicked.connect(self.onDelete)
        self.add.clicked.connect(self.onAdd)

        # Column 3
        self.select = QPushButton('→')
        self.col3.addWidget(self.select)
        self.select.clicked.connect(self.onSelect)

        # Column 4
        self.col4.addWidget(QLabel('文件名'))
        self.filename = QLineEdit(date.today().strftime("%Y%m%d"))
        self.col4.addWidget(self.filename)

        self.selectedLabel = QLabel('已选择：\n')
        self.selectedLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.selectedLabel.setAlignment(Qt.AlignTop)
        self.col4.addWidget(self.selectedLabel)

        self.selected = []
        
        self.generate = QPushButton('生成投影片')
        self.col4.addWidget(self.generate)
        self.generate.clicked.connect(self.onGenerate)

        self.initList()

    def onSearch(self):
        searchString = self.search.text()
        if searchString == '':
            for i in range(self.results.count() - 1):
                self.results.item(i).setHidden(False)
            return

        for i in range(self.results.count()):
            item = self.results.item(i)
            title = item.data(Qt.UserRole)[1]
            lyrics = item.data(Qt.UserRole)[2]
            if searchString in title\
                or searchString in ''.join(pypinyin.lazy_pinyin(title))\
                or searchString in ''.join(pypinyin.lazy_pinyin(title, style=pypinyin.Style.FIRST_LETTER))\
                or searchString in lyrics:
                    item.setHidden(False)
            else:
                item.setHidden(True)

    def initList(self):
        self.results.clear()
        self.currentSong = None
        self.title.setText('')
        self.lyrics.setText('')

        self.songs = self.cur.execute("SELECT * FROM song").fetchall()
        for song in self.songs:
            newItem = QListWidgetItem()
            newItem.setText(song[1])
            newItem.setData(Qt.UserRole, song)
            self.results.insertItem(0, newItem)
        self.onSearch()
    
    def onCurrentItemChanged(self, item):
        if item is not None:
            self.currentSong = item.data(Qt.UserRole)
            self.title.setText(self.currentSong[1])
            self.lyrics.setText(self.currentSong[2])

    def onSave(self):
        if self.title.text().strip() == '':
            QMessageBox.critical(self, '错误', '标题不能为空')
            return
        if self.lyrics.toPlainText().strip() == '':
            QMessageBox.critical(self, '错误', '歌词不能为空')
            return
        
        # new song
        if self.currentSong is None:
            confirmation = QMessageBox.question(self, '确认', '你确认要添加这首歌吗？', QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                self.cur.execute("INSERT INTO song VALUES (NULL, ?, ?)", (Chinese.format(self.title.text()), Chinese.format(self.lyrics.toPlainText())))
                self.con.commit()
                self.initList()
            return

        # update song
        confirmation = QMessageBox.question(self, '确认', '你确认要修改这首歌吗？', QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.cur.execute("UPDATE song SET title = ?, lyrics = ? WHERE id = ?", (Chinese.format(self.title.text()), Chinese.format(self.lyrics.toPlainText()), self.currentSong[0]))
            self.con.commit()
            self.initList()
        else:
            self.title.setText(self.currentSong[1])
            self.lyrics.setText(self.currentSong[2])

    def onDelete(self):
        if self.currentSong is None:
            self.title.setText('')
            self.lyrics.setText('')
            return
        confirmation = QMessageBox.question(self, '确认', '你确认要删除这首歌吗？', QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            self.cur.execute("DELETE FROM song WHERE id = ?", (self.currentSong[0],))
            self.con.commit()
            self.initList()
        else:
            self.title.setText(self.currentSong[1])
            self.lyrics.setText(self.currentSong[2])

    def onAdd(self):
        self.currentSong = None
        self.results.setCurrentItem(None)
        self.title.setText('')
        self.lyrics.setText('')
    
    def onSelect(self):
        if self.currentSong is None:
            return
        self.selectedLabel.setText(self.selectedLabel.text() + self.currentSong[1] + '\n')
        self.selected.append(self.currentSong)

    def onGenerate(self):
        if len(self.selected) == 0:
            QMessageBox.critical(self, '错误', '请选择歌曲')
            return
        if self.filename.text().strip() == '':
            QMessageBox.critical(self, '错误', '文件名不能为空')
            return
        
        ApplescriptGenerator.generate(self.filename.text(), self.selected)
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.svg'))
    app.setStyle('Fusion')

    window = Window()
    window.setWindowTitle('诗歌投影片')
    window.setFixedSize(window.sizeHint())
    window.show()
    sys.exit(app.exec())
