---
technical: true
personal: false
date: 2026-10-18
edited: 2026-10-18T15:41:00.000Z
notion: 3fd945c9dc4380cb861ce5bb115b0802
---
# Intel Heterogeneous Multicore Architecture General Info

Eski geleneksel işlemcilerde (Homojen mimari), işlemcinin içindeki tüm çekirdekler birbirinin tıpatıp aynısıydı. Hızları, boyutları, güçleri eşitti. Heterojen (Hibrit) Mimari ise; aynı işlemci zarının (silikonunun) üzerine farklı boyutlarda, farklı güçlerde ve farklı uzmanlık alanlarına sahip çekirdek tiplerini bir arada yerleştirme felsefesidir. Amaç işlemciye hafif bir iş geldiğinde güçlü olan çekirdekleri çalıştırıp enerjiyi boşa harcamamak; ağır bir iş geldiğinde ise küçük çekirdeklerle vakit kaybetmeyip kas gücünü devreye sokmak. yani **maksimum performans ile minimum güç tüketimini** aynı anda yakalamak.

Eski geleneksel işlemcilerde (Homojen mimari), işlemcinin içindeki tüm çekirdekler birbirinin tıpatıp aynısıydı. Hızları, boyutları, güçleri eşitti. Heterojen (Hibrit) Mimari ise; aynı işlemci zarının (silikonunun) üzerine farklı boyutlarda, farklı güçlerde ve farklı uzmanlık alanlarına sahip çekirdek tiplerini bir arada yerleştirme felsefesidir. Amaç işlemciye hafif bir iş geldiğinde güçlü olan çekirdekleri çalıştırıp enerjiyi boşa harcamamak; ağır bir iş geldiğinde ise küçük çekirdeklerle vakit kaybetmeyip kas gücünü devreye sokmak. yani **maksimum performans ile minimum güç tüketimini** aynı anda yakalamak.

Bu mimari aslında yıllardır akıllı telefonlarımızdaki ARM işlemcilerde (Apple silicon, Snapdragon vb.) kullanılıyordu. Ancak bilgisayar (x86) dünyasına ana akım olarak gelişi şu şekilde oldu:

- **İlk Deneme (Lakefield - 2020):** Intel bunu ilk kez hibrit tasarımlı prototip bir mobil çipte denedi ama piyasada pek ses getirmedi.
- **Asıl Devrim (12. Nesil "Alder Lake" - 2021):** Intel, bu mimariyi masaüstü ve laptop pazarına kitlesel olarak **12. Nesil "Alder Lake"** mimarisiyle getirdi.

---

Modern bir Intel hibrit işlemcisinin içine bakıldığında 3 farklı çekirdek tipini (veya jenerasyonuna göre ilk ikisini) yan yana görmek mümkün.

P-Core (Performance Core)

- **Görevi:** Ağır, anlık, yüksek hesaplama gücü ve düşük gecikme gerektiren işleri sırtlamak.
- **Özellikleri:** Fiziksel olarak iridirler. Saat frekansları çok yüksektir. Hyper-Threading desteklerler (yani 1 fiziksel P-core, işletim sistemine 2 sanal çekirdek/thread olarak görünür). Çok güç tüketirler.
- **Neye Bakar?** Oyunlar, kod derleme (compilation), 3D modelleme, video render gibi kas gücü isteyen işler.
- **Kesme Yönetimi (Interrupt Handlers / HardIRQ)** $\rightarrow$ **P-Core (Zorunlu)** CAN-bus'tan anlık bir telemetri paketi geldiğinde veya RS-422 hattından kritik bir konum verisi düştüğünde, işlemcinin donanımsal kesme hattı (IRQ) tetiklenir. **Neden P-Core?** Gecikme (latency) ve jitter (gecikmedeki sapma) embedded sistemlerin düşmanıdır. Bir P-core, daha yüksek saat hızına ve daha derin işlem hatlarına (pipeline) sahip olduğu için gelen interrupt'ı nanosaniyeler içinde yakalar ve işler. Eğer bu kesme bir E-core'un insafına bırakılırsa, çekirdeğin uykudan uyanma gecikmesi yüzünden hat üzerinden gelen paketleri kaçırmak olasıdır(packet drop / buffer overflow).

E-Core (Efficient Core)

- **Görevi:** Arka plan işlerini devralıp, P-core'ların rahat nefes almasını sağlamak ve enerji tasarrufu yapmak.
- **Özellikleri:** Fiziksel olarak çok küçüktürler. Bir P-core'un kapladığı alana tam 4 tane E-core sığdırılabilir. Hyper-Threading desteklemezler. Çok az elektrik harcarlar.
- **Neye Bakar?** Arka planda çalan Spotify, açık duran Discord, Windows'un kendi servisleri veya tarayıcıda boşta bekleyen sekmeler.
- **Veri İşleme ve Protokol Yığınları (SoftIRQ / Network Stack)** $\rightarrow$ **E-Core (Tercihen):** Interrupt yakalanıp veri buffer’a alındıktan sonra, o verinin anlamlandırılması (örneğin Ethernet'ten gelen TCP/IP paketinin çözülmesi veya CAN-bus verisinin parse edilmesi) daha üst katman bir iştir. **Neden E-Core?** Bu aşamada artık mikro saniyeler seviyesinde bir gecikme ölümcül değildir. Bu yüzden Linux çekirdeğindeki `ksoftirqd` (yazılımsal kesme thread'leri) veya ağ yığınları E-core'lara yönlendirilebilir. Böylece P-core'lar bir sonraki donanımsal interrupt'ı beklemek için boşa çıkar.
- **Ubuntu Servisleri ve Arka Plan Görevleri** $\rightarrow$ **E-Core:** Sistemin ayağa kalkarken çalıştırdığı `systemd` servisleri, `sshd` (SSH bağlantısı), günlük tutma mekanizmaları (`rsyslogd`, `journald`), `chrony` (zaman senkronizasyonu) veya varsa bir veritabanı/dosya yönetim servisi (Samba, NFS vb.). **Neden E-Core?** Bu servislerin hiçbirinin gerçek zamanlı (real-time) bir aciliyeti yoktur. Arka planda sakin sakin çalışabilirler. Bunları E-core'a kilitlemek, işlemcinin toplam güç tüketimini (TDP) ve dolayısıyla embedded kartının sıcaklığını ciddi oranda düşürür. Fan kullanmadığın, pasif soğutmalı endüstriyel bir kutu tasarlıyorsan bu altın değerindedir.

**LP-E Core (Low Power Efficient)**

- **Görevi:** Bilgisayar boştayken veya uyku moduna yakınken ana işlemci bloklarını tamamen kapatıp sistemi mikroskobik bir enerjiyle açık tutmak.
- **Özellikleri:** Bu çekirdekler işlemcinin ana bilgi işlem kısmında değil, giriş-çıkışların yönetildiği **SoC (System on Chip)** adasında yaşarlar. İlk kez Meteor Lake (Core Ultra 1. Nesil) ile geldiler.
- **Neye Bakar?** Laptop ekranı kapalıyken e-postaları kontrol etmek veya sadece ekranda hareketsiz bir video oynatmak.

Farklı güçteki bu çekirdeklerin düzgün çalışabilmesi için işletim sisteminin (Windows/Linux) çok zeki olması gerekir. Eğer Windows ağır bir oyunu yanlışlıkla güçsüz bir E-core'a atarsa oyun kasım kasım kasılır.

Bunun yaşanmaması için Intel, işlemcinin içine donanımsal bir kontrolör olan **Intel Thread Director (ITD)** mekanizmasını koydu.

                      [Çalıştırılan Program] ──> [Intel Thread Director (Anlık Takip)]
┌────────────────────────┴────────────────────────┐
(Ağır Hesaplama / Ağır Kod)                      (Arka Plan / Basit Görev)
                        ▼                                                                  ▼
     [P-CORE Devreye Girer]                           [E-CORE Devreye Girer]

ITD, işlemcide koşan kodları nanosaniyeler seviyesinde izler. Bir programın ağır matematiksel komutlar çalıştırdığını gördüğü an işletim sistemine fısıldar: *"Bunu hemen P-core'a taşı!"*. Eğer sen o programı alta simge durumuna küçültürsen, ITD programı P-core'dan alır, E-core'a fırlatır ve P-core'u uykuya yatırarak sistemin ısınmasını engeller.
