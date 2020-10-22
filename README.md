# webnote-tool
网页笔记标注工具

# 功能介绍

有时候在网络上浏览一些好的博客文章总想剪藏下来备份到本地，这样就不怕网络上的文章因为各种原因导致无法访问。

其实印象笔记和有道笔记都有剪藏的功能，但是只阅读不输出是无法真正加深记忆吸收知识的，因此我结合这款开源的[剪藏](https://github.com/mika-cn/maoxian-web-clipper)工具实现了这款笔记标注工具。

我们通过剪藏工具备份的各种网页都以html的格式存储在本地磁盘上，默认是D:\下载\mx-wc\default。

本工具加载此目录下所有已剪藏网页，在左侧目录树上默认是挂载到默认笔记本目录下，大家可以创建其他目录进行分类。点击标题就可以在左侧显示文章。显示效果和原始网站显示效果是完全一致的。目录上方可以进行**模糊搜索**，下方的**纠正**按钮，用于自动纠正显示失败的图片，**跳转到**按钮，用于自动在浏览器打开文章的原始站点。如图所示：

![image](https://github.com/primejava/webnote-tool/blob/master/doc/pic1.png)

主要功能是标注功能，如图所示：

在文章中选择一段文字后，单击右键选择**标注**，即可标注一段文字并可以在左侧书写笔记。单击左侧的笔记，右侧同时也会迅速滑动定位到相关位置。

![image](https://github.com/primejava/webnote-tool/blob/master/doc/pic2.png)

# 使用方法

- 请先安装谷歌浏览器扩展工具[剪藏](https://github.com/mika-cn/maoxian-web-clipper)，剪藏的网页保存地址需要默认是在D:\下载\mx-wc\default目录
- 在windows系统中安装python3的环境
- 下载本项目，`pip install -r requirements.txt`安装依赖包
- `python html_noter.py`启动项目
- 可能存在目录问题,请自行重命名
