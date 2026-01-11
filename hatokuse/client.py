import socket
import sys

if len(sys.argv) < 3:
    print("Usage:")
    print("  python client.py SET <id> <message>")
    print("  python client.py GET <id>")
    exit(1)

HOST = "localhost"
PORT = 5000   # leader

cmd = sys.argv[1]

if cmd == "SET":
    if len(sys.argv) < 4:
        print("SET needs id and message")
        exit(1)
    mid = sys.argv[2]
    msg = " ".join(sys.argv[3:])
    data = f"SET {mid} {msg}"

elif cmd == "GET":
    mid = sys.argv[2]
    data = f"GET {mid}"

else:
    print("Unknown command")
    exit(1)

s = socket.socket()
s.connect((HOST, PORT))
s.send((data + "\n").encode())

resp = s.recv(4096).decode().strip()
s.close()

print(resp)
