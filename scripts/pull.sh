#!/bin/bash
#===============================================================================
# Date：Jan. 26th, 2024
# Author : yuanzi
# Description: 更新url及hosts
#===============================================================================

# 定义日志函数
get_current_time() {
    echo "$(date "+%Y-%m-%d %H:%M:%S")"
}
log_info() {
    echo -e "$(get_current_time) \e[32mINFO\e[0m: $1"
}

log_error() {
    echo -e "$(get_current_time) \e[31mERROR\e[0m: $1"
}

log_warning() {
    echo -e "$(get_current_time) \e[33mWARNING\e[0m: $1"
}

log_info "正在从中转服务器进行拉取，请稍后..."
# 检查是否以root用户身份运行
if [[ $EUID -ne 0 ]]; then
    log_error "请以root用户身份运行此脚本"
    exit 1
fi

sshpass -p '!Lijinyuan20' scp -o StrictHostKeyChecking=no root@8.222.161.51:/root/temp/hosts /root/
sshpass -p '!Lijinyuan20' scp -o StrictHostKeyChecking=no root@8.222.161.51:/root/temp/download_url.txt /root/
mv -f /root/hosts /etc/hosts
mv -f /root/download_url.txt /opt/concdownloader/res/

log_info "download_url及host已成功拉取到本地目录"


