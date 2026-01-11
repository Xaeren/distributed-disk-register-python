DAĞITIK MESAJ KAYIT SİSTEMİ (Python + gRPC)

Bu proje, Sistem Programlama ödevi kapsamında geliştirilen, hata toleranslı ve dağıtık bir mesaj abonelik sistemidir.

Amaç; istemciden gelen mesajların lider sunucu tarafından belirli sayıda üye (member) sunucuya dağıtılarak diske kaydedilmesi ve herhangi bir üye çökse bile mesajların sistemden geri alınabilmesidir.

1. SİSTEM MİMARİSİ

Sistemde üç ana bileşen vardır:

--- Client
    SET ve GET komutlarını text tabanlı olarak leader’a gönderir.

--- Leader
    İstemciden gelen mesajları alır.
    tolerance.conf dosyasından okuduğu hata toleransı kadar member’a mesajı gönderir.
    Hangi mesajın hangi member’larda tutulduğunu kaydeder.
    Üyelerin durumunu ve toplam mesaj sayısını periyodik olarak ekrana basar.

--- Member (Aile Üyesi)
    Leader’dan gelen mesajları gRPC üzerinden alır.
    Mesajları kendi diskine yazar.
    Periyodik olarak kaç mesaj sakladığını ekrana basar.

İstemci ↔ Leader: Text tabanlı TCP
Leader ↔ Member: gRPC (.proto ile tanımlı)

2. DOSYA YAPISI

Proje dizini şu şekildedir:

--- leader.py

--- member.py

--- client.py

--- load_test.py

--- member.proto

--- tolerance.conf

--- README.md

--- venv/

3. HATOKUSE PROTOKOLÜ

İstemci sadece iki komut gönderir:

SET <message_id> <message>
GET <message_id>

SET: Mesajı kaydeder
GET: Mesajı geri getirir

Leader, SET komutunda mesajın en az “tolerance” adet member tarafından başarıyla diske yazıldığını görmeden OK dönmez.

4. HATA TOLERANSI

Hata toleransı tolerance.conf dosyasında tanımlıdır.

Örnek:
tolerance.conf = 3

Bu durumda her mesaj en az 3 farklı member sunucuda tutulur.

Bir veya iki member çökse bile mesaj, hayatta kalan başka bir member’dan geri alınabilir.

5. YÜK DAĞITIMI

Leader, member’ları round-robin yöntemiyle seçer.
Bu sayede mesajlar member’lara dengeli şekilde dağılır.

Örnek:
9000 mesaj ve tolerance = 3 ise
Toplamda 3’erli gruplar halinde yaklaşık 4500 mesaj bir grup member’da, 4500 mesaj diğer grupta tutulur.

6. ÇALIŞTIRMA ADIMLARI

6.1) Sanal ortamı aktif et
     venv\Scripts\activate

6.2) tolerance.conf içine bir sayı yaz
     Örnek:
     3

6.3) Member’ları başlat (her biri ayrı terminalde)
     python member.py 6001
     python member.py 6002
     python member.py 6003
     python member.py 6004
     python member.py 6005
     python member.py 6006

6.4) Leader’ı başlat
     python leader.py

6.5) Yük testi gönder
     python load_test.py

6.6) Manuel test
     python client.py SET 5001 hello
     python client.py GET 5001

7. CRASH TESTİ

Örnek senaryo (tolerance = 3):

--- 4501 ID’li mesaj 6003, 6005 ve 6006 portlu      memberlarda tutuluyor olsun.

--- 6003 ve 6005 kapatılırsa (crash)

--- Leader, 6006’dan mesajı alıp istemciye dönebilir.

Bu sayede sistem hata toleranslıdır.

8. DİSK KAYIT YAPISI

Her member kendi klasöründe mesajları tutar:

storage_6001/
storage_6002/
storage_6003/
…

Her mesaj şu dosyada saklanır:
<message_id>.txt

Örnek:
storage_6003/4501.txt

9. SAĞLANAN ŞARTLAR

Bu proje şu gereksinimleri sağlar:

--- Hata toleransı 1’den n’e kadar çalışır

--- Mesajlar birden fazla member’a kaydedilir

--- Leader, hangi mesajın hangi member’da olduğunu  bilir

--- Member çökse bile mesajlar kaybolmaz

--- Yük dengeli dağıtılır

--- Leader ve member’lar periyodik durum bilgisi basar

10. SONUÇ

Bu sistem, Kafka ve RabbitMQ benzeri mantıkta çalışan, ancak eğitim amaçlı sadeleştirilmiş, gRPC tabanlı bir dağıtık mesaj kayıt servisidir.

Testlerde 9000 mesaj başarıyla dağıtılmış ve crash senaryolarında mesajların geri getirilebildiği doğrulanmıştır.
