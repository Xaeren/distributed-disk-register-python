import socket
import threading
import time
import grpc
import member_pb2
import member_pb2_grpc

# 1. Sabit liste yerine geniş bir potansiyel aralık belirliyoruz
POTENTIAL_PORTS = range(6001, 6011) 

with open("tolerance.conf") as f:
    TOLERANCE = int(f.read().strip())

print("Sistem Tolerance =", TOLERANCE)

locations = {}
rr = 0

def get_active_members():
    """Dinamik Keşif: O an açık olan üyeleri portları tarayarak bulur."""
    active_stubs = {}
    for p in POTENTIAL_PORTS:
        try:
            # Kanala çok kısa bir zaman aşımı (0.1 sn) veriyoruz ki tarama hızlı bitsin
            channel = grpc.insecure_channel(f"localhost:{p}")
            stub = member_pb2_grpc.MemberServiceStub(channel)
            # Üyenin gerçekten orada olup olmadığını anlamak için boş bir Get isteği atıyoruz
            stub.Get(member_pb2.GetRequest(id="health_check"), timeout=0.1)
            active_stubs[p] = stub
        except:
            continue # Port kapalıysa listeye ekleme
    return active_stubs

def choose(active_stubs):
    global rr
    res = []
    active_ports = list(active_stubs.keys())
    
    if len(active_ports) < TOLERANCE:
        return None # Yeterli üye yoksa SET işlemi yapılamaz

    for _ in range(TOLERANCE):
        res.append(active_ports[rr % len(active_ports)])
        rr += 1
    return res

def handle_client(conn):
    try:
        data = conn.recv(4096).decode().strip()
        if not data: return

        parts = data.split(" ", 2)
        cmd = parts[0]
        
        # Dinamik olarak o anki aktif üyeleri al
        current_active = get_active_members()

        if cmd == "SET":
            mid, msg = parts[1], parts[2]
            targets = choose(current_active)
            
            if not targets:
                conn.send(b"ERROR: Not enough active members\n")
                return

            saved = []
            for p in targets:
                try:
                    resp = current_active[p].Store(member_pb2.StoreRequest(id=mid, message=msg), timeout=1)
                    if resp.ok: saved.append(p)
                except: continue

            if len(saved) >= TOLERANCE:
                locations[mid] = saved
                conn.send(b"OK\n")
            else:
                conn.send(b"ERROR: Replication failed\n")

        elif cmd == "GET":
            mid = parts[1]
            if mid not in locations:
                conn.send(b"NOT_FOUND\n")
            else:
                success = False
                for p in locations[mid]:
                    try:
                        # Hata Toleransı: Üye kapalıysa listedeki diğer kopyayı dene
                        channel = grpc.insecure_channel(f"localhost:{p}")
                        stub = member_pb2_grpc.MemberServiceStub(channel)
                        r = stub.Get(member_pb2.GetRequest(id=mid), timeout=1)
                        if r.found:
                            conn.send((r.message + "\n").encode())
                            success = True
                            break
                    except: continue
                if not success: conn.send(b"NOT_FOUND\n")

    finally:
        conn.close()

def status():
    while True:
        time.sleep(10)
        active_now = list(get_active_members().keys())
        print(f"\n--- DURUM: {len(active_now)} Aktif Üye | {len(locations)} Mesaj ---")
        print(f"Aktif Portlar: {active_now}")

s = socket.socket()
s.bind(("localhost", 5000))
s.listen()

print("Leader 5000 portunda hazır...")
threading.Thread(target=status, daemon=True).start()

while True:
    c, a = s.accept()
    threading.Thread(target=handle_client, args=(c,), daemon=True).start()
