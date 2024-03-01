<img src="C:\Users\lijin\AppData\Roaming\Typora\typora-user-images\image-20240229163321079.png" alt="image-20240229163321079" style="zoom: 67%;" />

# Rescrawler (资源爬取及DNS解析程序)

## 一、项目简介

### 1.1 开发背景

Rescrawler是专门服务于下行程序Concdownloader的存在，其主要功能是实时抓取互联网上最新的动态资源，并将其提供给Concdownloader，以支持高并发的下载需求，从而实现机器带宽的高负载率。

Rescrawler的抓取范围广泛，覆盖了国内众多软件市场、媒体平台以及各大镜像资源站，确保了下载资源的实时性和多样性。抓取的资源会被有效地分发给各个节点服务器，为Concdownloader提供了充足的下载素材。此外，考虑到后续打下行程序需要考虑省份和运营商的特殊性，在优化后的Rescrawler还支持从国内众多节点获取下载URL域名的DNS解析结果，同时还提供了自定义选择目标省份和运营商的功能，以生成更为精准和有效的下载流量。

通过Rescrawler成功构建了一个强大的资源获取及DNS解析引擎，为下行业务提供了源源不断的有效流量。

> *注意：以上所述功能并未完全实现，目前主要还是用于dns分省解析，后续优化提升空间很大*

### 1.2 环境要求

- 系统：centos 7
- python版本：3.6+
- 依赖库：psutil、pysnmp

### 1.3 项目目录结构

```shell
|-- crawler.py              # 主程序入口
|-- modules/                # 功能模块文件夹，包含主模块依赖的子模块
|   |-- __init__.py
|   |-- resolver.py         # dns分省解析
|   |-- xdbSearcher.py      # ip数据库检索
|   |-- logger.py           # 日志
|   |-- get_download_url_byPlaywright.py     # 使用playwright爬取js动态页面的下载url
|-- config/                 # 配置文件目录
|   |-- id.rsa              # 本机ssh登陆验证密钥
|   |-- our_node.json       # 现有业务节点信息
|   |-- resolve_node.json   # 解析主机信息
|   |-- server_login_info.json   # 中转存储服务器登陆信息
|-- info/                    
|   |-- dns_info.json    	# dns分省解析的输出结果
|   |-- page_url.txt    	# 下载页面url
|-- res/                    
|   |-- china.xdb			# ip数据库文件
|   |-- hosts		    	# dns分省解析后生成对应的hosts文件
|   |-- download_url.txt    # 原有下载url
|   |-- download_url_new.txt    # dns分省解析后筛选剩余的下载url
|-- tests/                  # 测试文件夹，包含所有的测试用例
|   |-- test.py
|-- log/                    # 存放分片日志 
|   |-- crawler.log
|-- requirements.txt        # 项目所有依赖的库
|-- README.md               # 项目的README文件，描述项目信息、安装步骤和用法等
```

### 1.4 执行流程

- 提供用户交互界面，询问是否开始爬取URL。
- 检查并处理命令行参数，根据参数指定运营商。
- 根据dns解析结果创建对应的hosts文件。

- 通过SSH协议将生成的hosts文件和下载URL文件上传至指定服务器。

## 二、部署流程

1. 临时配置linux系统dns

   ```bash
   sudo bash -c 'echo -e "nameserver 114.114.114.114\nnameserver 8.8.8.8\nnameserver 223.5.5.5" > /etc/resolv.conf'
   ```

2. 配置阿里云yum源

   ```bash
   sudo mv -f /etc/yum.repos.d /etc/yum.repos.d.backup
   sudo mkdir /etc/yum.repos.d
   curl -o /etc/yum.repos.d/CentOS-Base.repo -L http://mirrors.163.com/.help/CentOS7-Base-163.repo
   sudo yum clean all
   ```

3. 校准系统时间

   ```bash
   sudo yum install -y ntpdate
   sudo ntpdate time.windows.com
   sudo timedatectl set-timezone Asia/Shanghai
   sudo hwclock --systohc
   ```

4. 安装python3

   ```bash
   sudo yum install -y python3
   ```

5. 安装gcc

   ```bash
   sudo yum install -y gcc python3-devel
   ```

6. 安装python所需的外置库

   ```bash
   pip3 install paramiko -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com
   ```

7. 将项目打包文件`rescrawler.tar.gz`拷贝至/opt/目录下

   ```bash
   cd /opt/
   tar -zxvf  rescrawler.tar.gz
   ```

8. 运行程序

   ```bash
   python3 crawler.py 
   ```

## 三、功能详解

### 3.1 主程序（crawler.py）

1. **程序启动及初始化**：
   - 输出程序启动时的Logo信息。
   - 打印当前程序版本、更新时间和路径信息。

2. **资源爬取及处理**：
   - 执行资源爬取和处理的相关操作，包括爬取URL、获取下载URL、解析URL、生成本地hosts文件、上传至服务器等。
   - 调用`modules.qihu_crawler`模块中的函数实现资源爬取功能。
   - 调用`modules.sync`和`modules.resolver`模块中的函数实现文件同步和域名解析功能。

3. **用户交互及检查**：
   - 提供用户交互界面，询问是否开始爬取URL。
   - 接受用户输入的指定运营商信息。
   - 检查并处理命令行参数，根据参数指定运营商。
   - 根据解析结果创建对应的hosts文件。

4. **上传至服务器**：
   - 使用`subprocess.run`函数通过SSH协议将生成的hosts文件和下载URL文件上传至指定服务器。

5. **日志记录**：
   - 使用`modules.logger`模块中的`logging`对象记录程序运行过程中的重要信息，包括警告、错误和一般信息。

### 3.2 resolver模块

1. **提取域名** (`extract_domains`函数)：
   - 从指定文件中提取出URL中的域名。
   - 使用正则表达式匹配URL中的域名信息，并将匹配到的域名添加到集合中返回。

2. **获取其他地域远程主机的域名解析结果** (`resolve_domain`函数)：
   - 使用Paramiko库建立SSH连接到远程服务器。
   - 在远程主机上执行`dig`命令进行域名解析。
   - 将解析结果存储在字典中，并写入本地临时存储文件。

3. **查询IP归属地** (`ip_region_search`函数)：
   - 使用XdbSearcher库查询IP地址的归属地。
   - 根据IP地址查询结果提取出省份、城市、地区和运营商信息，并存储在字典中返回。

4. **获取匹配的IP地址** (`get_match_region_ip`函数)：
   - 从配置文件中读取指定的解析节点信息。
   - 调用`extract_domains`函数提取下载URL中的域名。
   - 调用`resolve_domain`函数通过SSH连接到远程服务器解析域名。
   - 调用`ip_region_search`函数查询解析得到的IP地址的归属地。
   - 将解析结果写入本地文件。

## 四、配置维护

### 4.1 项目ssh密钥配置

- 使用下面命令将本机的ssh密钥复制到项目指定目录

  ```bash
  cp /root/.ssh/id_rsa /opt/crwaler/config/id_rsa
  ```

### 4.1 Dns解析节点服务器配置

- **添加**

  1. 首先通过ssh终端登陆到需要添加的解析主机上，安装解析所需工具

     ```bash
     sudo yum install bind-utils -y
     ```

  2. 在解析主机添加ssh密钥（如果该机器已存在skytonops则无需此操作）

     ```bash
     mkdir -p ~/.ssh/ && vi ~/.ssh/authorized_keys
     ```

  3. 另提一行，复制项目中config目录下的id_rsa中的密钥到当前文件中，并保存（如果该机器已存在skytonops则无需此操作）
  4. 接着回到crawler部署的主机上，试着使用ssh+ip连接解析主机，验证是否免密登录成功（如果该机器已存在skytonops则无需此操作）

  4. 进入项目config目录，使用vi编辑器打开`resolve_node.json`文件进行编辑

     - 在对应运营商的大括号下面填入，解析节点名（自定义）和IP

       > **注意**：格式一定要符合json格式规范要求，否则会报错

     ```bash
     {"中国电信": {
       "赤壁电信": "221.233.216.114",
       "鄂州电信": "58.53.47.234"
     },
     "中国联通": {
       "西安联通": "221.11.96.5",
       "荆州联通": "58.19.152.26"
     },
     "中国移动": {
       "银川移动": "111.51.144.233"
     }}
     ```

- **删除**

  - 进入项目config目录，使用vi编辑器打开`resolve_node.json`文件进行编辑
    - 删除对应主机的行

### 4.2 IP数据库更新

- 进入项目的res目录，替换其中的`china.xdb`文件即可

### 4.3 默认下载url库更新

- 默认下载url库存储在项目res目录，替换其中的download_url.txt文件即可

### 4.4 文件中转服务器修改

- 进入项目config目录，使用vi编辑器打开`server_login_info.json`文件进行编辑

  - 主机ip+ssh端口号

    > **注意：**这台机器需要已经加入skytonops管理或者已经拥有本机密钥

  ```bash
  {
      "host": "118.182.250.151",
      "port": 4222
  }
  ```

  






