import re
import os
import json
import paramiko
import threading
from scp import SCPClient
from modules.logger import logging


# 读json文件
def read_from_json_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        value = json.load(file)
    return value


# 写json文件
def write_to_json_file(value, path):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(value, file, ensure_ascii=False, indent=2)


# 远程主机执行命令
def run_command_on_server(server, command, output_dict):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['host'], port=server['port'], username=server['username'], password=server['password'])

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        result = f"在 {server['host']} 上执行命令的输出：\n{output if output else error}"
        ssh.close()
        output_dict[server['host']] = result
    except Exception as e:
        result = f"在 {server['host']} 上执行命令失败: {e}"
        output_dict[server['host']] = result


# 推送文件到远程服务器
def put_file_to_server(local_file_path, remote_file_path):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(server['host'], port=server['port'], username=server['username'], password=server['password'])
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_file_path, remote_file_path)
        print(f"文件已成功传输到 {server['host']}")
    except Exception as e:
        print(f"传输到 {server['host']} 失败: {e}")
    finally:
        ssh.close()


if __name__ == '__main__':
    # JSON文件路径
    json_file_path = '../../res/server_login_info.json'
    with open(json_file_path, 'r') as file:
        servers = json.load(file)

    # 创建线程列表和输出字典
    threads = []
    outputs = {}

    # 传输文件到每个服务器并执行命令
    for server in servers:
        # 假设要执行的命令是 "bash env.sh"
        # command = "sudo nohup python3 download_multi-ip_rotate.py &"

        command = "ls"

        put_file_to_server("download_multi-ip_rotate.py")

        # 创建线程
        thread = threading.Thread(target=run_command_on_server, args=(server, command, outputs))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 打印每个服务器的输出
    for server, output in outputs.items():
        print(output)

    print("所有命令执行完成。")
