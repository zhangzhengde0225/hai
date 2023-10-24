import socket

def test_connection(ip, port, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
    except (socket.timeout, socket.error) as e:
        print(f"Unable to connect to {ip}:{port} - {e}")
        return False
    else:
        print(f"Successfully connected to {ip}:{port}")
        return True
    finally:
        sock.close()

ip = "172.16.17.19"
port = 42902
test_connection(ip, port)
