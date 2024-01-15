import paramiko


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


