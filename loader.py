import sys
import socket
import pickle

def load(df, n):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('localhost', 12345))
        data = []
        sock.send((df + ' ' + n).encode())
        while True:
            packet = sock.recv(4096)
            if not packet:
                break
            data.append(packet)
    finally:
        sock.close()
    return pickle.loads(b"".join(data))


print(load(sys.argv[1], sys.argv[2]).to_json())
sys.stdout.flush()
