# Keynote 生成器
[English Version](https://github.com/jimmywengzj/Keynote-generator)

储存、查看、编辑歌词，生成主日敬拜投影片

<p align="center">
  <img src="https://github.com/user-attachments/assets/78b73933-bcf9-4f91-8b61-60fc0e247ed8">
  <img src="https://github.com/user-attachments/assets/20cf478c-77d8-46ea-af5c-ddafbfed3730" width="480">
</p>

## 使用方法
### 安装
先安装 `Python` 和 `pip` 
```
pip install PySide6 applescript pypinyin opencc-python-reimplemented
```

### Keynote主题
此生成器使用Keynote主题创建投影片，双击 `Worship.kth` ，将主题添加到主题选择器。保留默认名字 `Worship` ，欢迎自行修改主题，包括换背景、调整文本框大小、更换字体等。

### 从现有的Keynote文件中提取歌词（可选）
把Keynote文件复制到 `~/Desktop/slides` 文件夹，双击并运行 `parser.scpt` ，它会把歌词写到桌面上的 `out.txt` 中。手动检查一下文件的内容， `#Title` 后是每首歌的歌名， `#Page` 是每页投影片的歌词。

检查完后，把 `out.txt` 放到项目文件夹中，运行：
```
python database-init.py
```
启动程序后就能看到导入的歌词。

### 生成投影片！
```
python GUI.py
```
使用中间栏下面的三个按钮永久修改数据库中的歌曲。用拼音、拼音首字母或文字搜索后双击歌名即可加入生成队列，也可以选择歌曲后按 `→` 。输入文件名后只要点击 `生成投影片` ，Keynote就会自动做好投影片并保存在桌面上。

### 汉字格式
为了防止一行歌词过长导致的自动换行，在 `ApplescriptGenerator.py` 中直接计算了字体大小。如果修改了主题的文本框宽度、字体或默认字号，需要相应修改这部分代码。

另外程序默认使用 [OpenCC](https://github.com/yichen0831/opencc-python) 将繁体转换为简体，可以根据需要修改 `Chinese.py`。
