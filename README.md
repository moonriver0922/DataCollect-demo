# LocGPT 2.0

## 数据采集

1. 基站部署

   首先将标签的电源开关拨至"on"，然后将三台基站分散水平放置在场景中，接着将基站连接的电池“I”端摁下，开机准备时间约一分钟。

   以基站1中心点为世界坐标系原点，即坐标为(0., 0., 0.)，记录下另外两台基站中心点的位置。

   为简化测量，省去方位角度的计算，三台基站的摆放朝向应一致。

   基站的x, y, z参考坐标轴如下（右手螺旋）：

   ![851710772844_.pic](https://img.xwyue.com/i/2024/03/18/65f852d70f15b.jpg)

2. 启动程序

   macOS

   ------

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

   成功后在*DataCollect-demo*文件夹路径下执行命令：

   ```shell
   pip install -r requirements.txt
   ```

   安装成功后执行：

   将*your scenario's name*替换成采集场景即可

   ```python
   python main.py --collection "your scenario's name"
   ```
