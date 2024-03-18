# LocGPT 2.0

## 数据采集

1. 基站部署

   将三台基站分散水平放置在场景中，接着将基站连接的电池“I”端摁下，开机准备时间约一分钟。以基站1中心点为世界坐标系原点，即坐标为(0., 0., 0.)，记录下另外两台基站的位置。为简化测量，省去方位角度的计算，三台基站的摆放朝向应一致。基站的x, y, z参考坐标轴如下：

   ![851710772844_.pic](https://img.xwyue.com/i/2024/03/18/65f852d70f15b.jpg)

2. 启动程序

   如果没有python，先安装python：

   - 执行命令安装HomeBrew（已经安装可以跳过）：

     ```shell
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```

   - 安装成功后执行命令：

     ```shell
     brew install python@3.11.5
     ```

   克隆仓库：

   ```shell
   git clone git@github.com:moonriver0922/DataCollect-demo.git
   ```

   文件结构如下：

   .
   ├── README.md
   ├── conf.yaml
   ├── logger.py
   ├── main.py
   └── requirements.txt

   执行命令：

   ```shell
   pip install -r requirements.txt
   ```

   安装成功后执行：

   ```python
   python main.py
   ```
