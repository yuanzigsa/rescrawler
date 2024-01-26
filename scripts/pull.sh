#!/bin/bash

# 如果没安装的话
#sudo yum install sshpass -y
sshpass -p '!Lijinyuan20' scp -o StrictHostKeyChecking=no root@8.222.161.51:/root/temp/hosts /root/
sshpass -p '!Lijinyuan20' scp -o StrictHostKeyChecking=no root@8.222.161.51:/root/temp/download_url.txt /root/
mv /root/hosts /etc/hosts
mv /root/download_url.txt /opt/concdownloader/res/

echo "download_url及host已成功拉取到本地目录"


