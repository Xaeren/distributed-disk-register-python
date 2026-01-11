import grpc
from concurrent import futures
import time
import os
import sys

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
            with open(f"{STORAGE}/{request.id}.txt", "w", encoding="utf-8") as f:
                f.write(request.message)
            return member_pb2.StoreReply(ok=True)
        except:
            return member_pb2.StoreReply(ok=False)

    def Get(self, request, context):
        try:
            with open(f"{STORAGE}/{request.id}.txt", "r", encoding="utf-8") as f:
                msg = f.read()
            return member_pb2.GetReply(found=True, message=msg)
        except:
            return member_pb2.GetReply(found=False, message="")

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
member_pb2_grpc.add_MemberServiceServicer_to_server(Member(), server)
server.add_insecure_port(f"[::]:{PORT}")
server.start()

print("Member running on", PORT)
while True:
    time.sleep(1000)
