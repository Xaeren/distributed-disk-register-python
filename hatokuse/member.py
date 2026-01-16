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
            file_path = f"{STORAGE}/{request.id}.txt"
            content = request.message.encode('utf-8')
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            with open(file_path, "r+b") as f:
                mm = mmap.mmap(f.fileno(), 0)
                mm.write(content)
                mm.close()
                
            return member_pb2.StoreReply(ok=True)
        except Exception as e:
            print(f"Hata: {e}")
            return member_pb2.StoreReply(ok=False)

    def Get(self, request, context):
        try:
            file_path = f"{STORAGE}/{request.id}.txt"
            if not os.path.exists(file_path):
                return member_pb2.GetReply(found=False)

            with open(file_path, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    msg = mm.read().decode('utf-8')
            return member_pb2.GetReply(found=True, message=msg)
        except Exception as e:
            return member_pb2.GetReply(found=False)

    
    def report_status():
        while True:
            file_count = len([name for name in os.listdir(STORAGE) if os.path.isfile(os.path.join(STORAGE, name))])
            print(f"\n[PORT {PORT}] Rapor: Şu an diskte {file_count} mesaj saklanıyor.")
            time.sleep(10)


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
member_pb2_grpc.add_MemberServiceServicer_to_server(Member(), server)
server.add_insecure_port(f"[::]:{PORT}")
server.start()

print("Member running on", PORT)
threading.Thread(target=report_status, daemon=True).start()
while True:
    time.sleep(1000)

