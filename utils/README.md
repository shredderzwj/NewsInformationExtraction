# utils

### 此目录下存放相关的工具，主要有：

+ orm.py 用于连接数据库，获得数据库中的数据
+ handle.py 用于数据的处理，包括数据预处理、清洗、分词等操作
+ train.py 用于模型的训练
+ langconv 中文繁体简体互转。来自[https://github.com/skydark/nstools/tree/master/zhtools](https://github.com/skydark/nstools/tree/master/zhtools)
+ wikiextractor 目录下为维基百科数据包解压工具，来自 [https://github.com/attardi/wikiextractor](https://github.com/attardi/wikiextractor),修改 wikiextractor 的源代码，把不需要的信息滤掉，然后增加繁简转换、切词等功能，直接输出下一步做词向量需要的格式，并存入文件。这么做可以减少大量的IO操作，提高处理效率。（维基百科中文数据包[下载地址](https://dumps.wikimedia.org/zhwiki/)）