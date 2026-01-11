import socket
import threading
import time
import grpc

import member_pb2
import member_pb2_grpc

MEMBERS = [6001,6002,6003,6004,6005,6006]

with open("tolerance.conf") as f:
    TOLERANCE = int(f.read().strip())

print("Tolerance =", TOLERANCE)

stubs = {}
for p in MEMBERS:
    channel = grpc.insecure_channel(f"localhost:{p}")
    stubs[p] = member_pb2_grpc.MemberServiceStub(channel)

rr = 0
locations = {}

def choose():
    global rr
    res = []
    for _ in range(TOLERANCE):
        res.append(MEMBERS[rr % len(MEMBERS)])
        rr += 1
    return res

def handle_client(conn):
    data = conn.recv(4096).decode().strip()
    if not data:
        conn.close()
        return

    parts = data.split(" ", 2)
    cmd = parts[0]

    if cmd == "SET":
        mid = parts[1]
        msg = parts[2]

        targets = choose()
        ok = 0
        saved = []

        for p in targets:
            try:
                resp = stubs[p].Store(member_pb2.StoreRequest(id=mid, message=msg))
                if resp.ok:
                    ok += 1
                    saved.append(p)
            except:
                pass

        if ok == TOLERANCE:
            locations[mid] = saved
            conn.send(b"OK\n")
        else:
            conn.send(b"ERROR\n")

    elif cmd == "GET":
        mid = parts[1]
        if mid not in locations:
            conn.send(b"NOT_FOUND\n")
        else:
            for p in locations[mid]:
                try:
                    r = stubs[p].Get(member_pb2.GetRequest(id=mid))
                    if r.found:
                        conn.send((r.message + "\n").encode())
                        break
                except:
                    pass
            else:
                conn.send(b"NOT_FOUND\n")

    conn.close()

def status():
    while True:
        time.sleep(5)
        print("=== STATUS ===")
        print("Total messages:", len(locations))
        for m in MEMBERS:
            print("Member", m)
        print("=============")

s = socket.socket()
s.bind(("localhost", 5000))
s.listen()

print("Leader on 5000")
threading.Thread(target=status, daemon=True).start()

while True:
    c, a = s.accept()
    threading.Thread(target=handle_client, args=(c,), daemon=True).start()
