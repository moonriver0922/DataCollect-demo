# LocGPT 2.0

## 数据采集

1. 基站部署

   将三台基站分散布置在场景中，接着将基站连接的电池“I”端摁下，开机准备时间约一分钟。以基站1为世界坐标系原点，即坐标为（0，0，0），记录下另外两台基站的位置。

2. 启动程序

   克隆仓库：

   ```shell
   git clone git@github.com:moonriver0922/DataCollect-demo.git
   ```

   执行命令：

   ```shell
   pip install -r requirements.txt
   ```

   安装成功后执行：

   ```python
   python main.py
   ```
