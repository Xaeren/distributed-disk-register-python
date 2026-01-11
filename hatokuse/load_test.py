import socket

TOTAL = 9000

for i in range(1, TOTAL+1):
    s = socket.socket()
    s.connect(("localhost", 5000))
    msg = f"SET {i} hello_{i}"
    s.send((msg + "\n").encode())
    resp = s.recv(1024).decode().strip()
    s.close()

    if resp != "OK":
        print("ERROR on", i)
        break

    if i % 500 == 0:
        print("Sent", i)

print("DONE")
