import socket

def is_ip_reachable(ip_address, port):
    try:
        s = socket.create_connection((ip_address, port), timeout=2)
        s.close()
        return True
    except socket.error:
        return False

# 示例用法
ip_to_check = "192.168.1.1"
port_to_check = 80

if is_ip_reachable(ip_to_check, port_to_check):
    print(f"The IP address {ip_to_check} is reachable on port {port_to_check}.")
else:
    print(f"The IP address {ip_to_check} is not reachable on port {port_to_check}.")


