import grpc
from concurrent import futures
import time
import os
import sys
import threading  

import member_pb2
import member_pb2_grpc

if len(sys.argv) < 2:
    print("Usage: python member.py <port>")
    exit(1)

PORT = sys.argv[1]
STORAGE = f"storage_{PORT}"
os.makedirs(STORAGE, exist_ok=True)

class Member(member_pb2_grpc.MemberServiceServicer):

    def Store(self, request, context):
        try:
            with open(f"{STORAGE}/{request.id}.txt", "wb", buffering=0) as f:
                f.write(request.message.encode('utf-8'))
            return member_pb2.StoreReply(ok=True)
        except:
            return member_pb2.StoreReply(ok=False)

    def Get(self, request, context):
        try:
            with open(f"{STORAGE}/{request.id}.txt", "rb") as f:
                msg = f.read().decode('utf-8')
            return member_pb2.GetReply(found=True, message=msg)
        except:
            return member_pb2.GetReply(found=False, message="")

def report():
    while True:
        print(f"[Member {PORT}] Diskte {len(os.listdir(STORAGE))} mesaj var")
        time.sleep(10)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
member_pb2_grpc.add_MemberServiceServicer_to_server(Member(), server)
server.add_insecure_port(f"[::]:{PORT}")
server.start()

print("Member running on", PORT)
threading.Thread(target=report, daemon=True).start()
while True:
    time.sleep(1000)

