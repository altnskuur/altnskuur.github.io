---
technical: true
personal: false
date: 2026-07-20
edited: 2026-10-17T19:22:00.000Z
notion: 3a3945c9dc4380a49b5dd303ee879ae1
---
# Ubuntu Black Screen Fault - OpenGL Fault

# Symptoms

Harici bir diske Ubuntu Desktop Image kurulduktan sonra ilgili “carrier” üzerinde çalıştırıldığında sistemin siyah ekran vermiştir. 

# Analysis

Yazının **Solutions** başlığı altında geçici ve kalıcı olmak üzere iki adet başlık verilmiştir. Bu kapsamda analizler **Geçici Çözüm Yolu** başlığına bağlı olarak yapılmıştır.

Sistem **Geçici Çözüm Yolu** ile ekrana görüntü verdiği varsayılmaktadır. Bu kapsamda ilk olarak parametreleri silerek, ekran gelmeyecek konfigürasyonda sistem çalıştırılmalıdır. Sistem çalıştırıldıktan sonra gücü kesilmeli ve ilgili parametre güncellemeleri ile ekran gelecek şekilde tekrar açılmalıdır. Ekranın açılmasının ardından aşağıdaki komut ile bir önceki boot’un log’ları incelenmelidir. 

```bash
journalctl -b -1 -r
```

İlgili loglar incelenmesinin ardından `kernel: i915 0000:00:02.0: *ERROR* CPU pipe A FIFO underrun`  şeklinde bir error logu gözlemlendi. Araştırmalar sonucu bu log aşağıdaki soruna yol açtığı gözlemlendi.

> İşlemcinin içindeki yeni nesil **Intel Arc** grafik kartı ile ekran sürücüsü (`i915`) arasındaki veri akışı senkronizasyonu kopuyordu. Ekran kartı, görüntüyü basacak veriyi zamanında alamadığı için kilitlenip siyah ekrana düşüyordu. `nomodeset` yazdığında ise bu gelişmiş sürücüyü tamamen kapattığın için sistem o hataya düşmüyor ama ekran kartının gücünü de kullanamıyordu.

- Kernel Driver 
```bash
lspci -k | grep -EA3 'VGA|3D|Display'
```

- Kernel Version 
```bash
uname -r
```

- 
```bash
glxinfo | grep "OpenGL version string"
```

- Örnek çıktılar:
```bash
# Calisan Image icin
VGA:
kernel modules: i915,xe
kernel driver in use: i195
kernel version: 6.8.0-124-generic

OpenGL version: 4.6

#Calismayan Image icin
VGA:
kernel modules: i915,xe
kernel version: 6.8.0-124-generic

OpenGL version: 4.5
```

# Solutions

## Geçici Çözüm Yolu

### Making Disable to the Wayland

Adım 1: Sistemi Recovery Mode ile Açmak

1. Carrier Board'un gücünü kesip yeniden ver.
2. Sistem tetiklendiği anda, Ubuntu logosu gelmeden hemen önce klavyeden sürekli `Shift` tuşuna basarak **GRUB ekranını yakala**.
3. GRUB menüsünde `Advanced options for Ubuntu` seçeneğine gel ve Enter'a bas.
4. Gelen listeden yanında `(recovery mode)` yazan satırı seç.
5. Birkaç saniye sonra karşına mavi/gri bir menü gelecek. Oradan yön tuşlarıyla `root` **(Drop to root shell prompt)** seçeneğinin üzerine gelip Enter'a bas. Ekranın altında komut satırı açılacak.

Adım 2: Diski Yazılabilir Yapmak ve Wayland'i Devre Dışı Bırakmak

Root satırına ulaştığında şu komutları sırasıyla gir:

1. Önce diski yazma moduna al:
```bash
mount -o remount,rw /
```

2. Ubuntu'nun ekran yöneticisi (GDM3) ayar dosyasını düzenlemek için aç:
```bash
nano /etc/gdm3/custom.conf
```

  *(Eğer dosya boş çıkarsa veya bulunamadı derse* `nano /etc/gdm3/daemon.conf` *dosyasını dene).*

3. Dosyanın içinde şu satırı bul:
```bash
# WaylandEnable=false
```

4. Bu satırın başındaki `#` **(diyez) işaretini sil**. Satır aynen şu hale gelmeli (böylece Wayland'i tamamen kapatıp Xorg'u zorunlu kılıyoruz):
```bash
WaylandEnable=false
```

5. Kaydet ve Çık: `Ctrl + O` ardından `Enter` ile kaydet, `Ctrl + X` ile editörden çık.

Adım 3: Sistemi Yeniden Başlatma

Ayarı başarıyla kaydettiysen sistemi normal modda açılmak üzere uğurla:

```bash
reboot
```

Sistem bu sefer Wayland yerine doğrudan Xorg (X11) grafik sunucusunu tetikleyecek.

---

### `nomodeset` Setting

Adım 1: Sistemi Grub Shell ile Açmak

1. Carrier Board'un gücünü kesip yeniden ver.
2. Sistem tetiklendiği anda, Ubuntu logosu gelmeden hemen önce klavyeden sürekli `ESC` tuşuna basarak **GRUB shell ekranını yakala**.

Adım 2: Diskleri Listele

Önce diski ve partition'ları teyit edelim. Komut satırına şunu yaz ve Enter'a bas:

```bash
ls
```

Ekranda `(hd0)`, `(hd0,gpt1)`, `(hd0,gpt2)` gibi ibareler göreceksin. Bizim Ubuntu root partition'ımız muhtemelen `(hd0,gpt2)` olan.

Adım 2: Manuel Boot Komutları

Sırasıyla tam olarak şunları yazıp her satırdan sonra Enter'a bas (Burada `hd0,gpt2` senin büyük partition'ın, `hd0,gpt1` ise EFI partition'ındır. Sistemden sisteme farklılık gösterebilir. Bu sebepten `ls` ile ilgili alanlar kontrol edilmelidir):

1. Root partition'ı GRUB'a gösteriyoruz:
```bash
set root=(hd0,gpt2)
```

2. Çekirdeği (kernel) yüklüyoruz (Sonuna `nomodeset` ekliyoruz ki o kilitlenen grafik arayüzü Wayland falan bu sefer hiç devreye girmesin, direkt terminal olarak güvenle açılsın):
```bash
linux /boot/vmlinuz root=/dev/nvme0n1p2 nomodeset
```

3. Initrd imajını yüklüyoruz:
```bash
initrd /boot/initrd.img
```

4. Ve tetiği çekiyoruz:
```bash
boot
```

Bu yapılmış olan `nomodeset`  parametre eklentisi geçicidir. Bu parametreyi kalıcı hale getirmek için grup güncellenmelidir.

1. Grub ayarlarını açalım:
```bash
sudo nano /etc/default/grub
```

2. Gelen dosyada `GRUB_CMDLINE_LINUX_DEFAULT` satırını bul ve ilgili satırı aşağıdaki gibi düzenleyelim:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nomodeset"
```

3. Değişikliğin ardından `CTRL+X`,  `Y`  ve `Enter`  ile ilgili dosyadan çıkalım.
4. Konfigürasyon ayarlarını kaydetmek için aşağıdaki komutu uygulayalım:
```bash
sudo update-grub
```

Bu `nomodeset`  parametresi ayarı ile ekran kontrolünü dahili ekran kartından tamamiyle CPU’ya aktarılır. Sürdürülebilir bir çözüm değildir. Bu aşamadan sonraki kalıcı çözümü elde etmek için image ilk ayarsız çalıştırılmalı ve kapatılmalı, ardından ilgili parametre ayarları yapılarak ekran görüntüsü elde edilmeli ve `journalctl -b -1 -r` komutu ile soruna sebep olan hata logları incelenmelidir.

## Çözüm Tespiti ve Kalıcı Çözüm

**OpenGL (Open Graphics Library)**, işletim sistemindeki pencerelerin, grafik arayüzlerin (GDM, GNOME desktop vb.) ve 3D uygulamaların ekran kartının donanımsal gücünü (GPU ivmelendirmesini) kullanmasını sağlayan ortak bir grafik dilidir/API'sidir.

Linux dünyasında bu işi **Mesa** adı verilen açık kaynaklı bir sürücü kütüphanesi yürütür.

- **Çalışan Dahili Image (OpenGL 4.6):** İçerisinde güncel Mesa sürücüleri var. Kartın dilinden anlıyor, donanımsal zamanlamayı doğru yönetiyor.
- **Çöken Harici SSD (OpenGL 4.5 - nomodeset ile):**  `nomodeset` ile açtığın için sistem ekran kartını hiç görmüyor, doğrudan işlemciye yüklenip eski ve temel bir yazılımsal render (LLVMpipe/VESA) kullanıyor. Bu yüzden OpenGL sürümü 4.5'e düşüyor. Eğer `nomodeset` parametresini kaldırırsan, sistemdeki mevcut eski grafik kütüphaneleri Intel Arc'ı düzgün süremediği için zamanlamayı kaçırıp `FIFO underrun` hatasıyla ekranı karatıyor.
1. Güncel Grafik Deposunu (PPA) Sisteme Ekleme: Ubuntu'nun kendi resmi depolarındaki Mesa bazen eski kalabiliyor. Linux dünyasında Intel ve AMD kartlar için en güvenilir, kararlı ve güncel Mesa sürücülerini barındıran **Kisak-Mesa PPA** deposunu harici sisteme ekliyoruz.
```bash
sudo add-apt-repository ppa:kisak/kisak-mesa -y
```

  Ubuntu, stabilite adına resmi depolarındaki sürücüleri ve Mesa kütüphanelerini çok nadir günceller.

  **PPA (Personal Package Archive):** Ubuntu'da resmi depoların dışından, güvendiğin geliştiricilerin en güncel paketlerini sistemine çekebilmeni sağlayan özel depolardır.

  **Kisak-Mesa:** Linux dünyasında özellikle Intel ve AMD ekran kartları için en güncel, en kararlı ve performansı optimize edilmiş Mesa sürücülerini derleyip paketleyen, topluluğun en güvendiği ünlü bir PPA deposudur.

2. Paket Listesini Güncelleme ve Upgrade: Depoyu ekledikten sonra sistemi tamamen güncelliyoruz. Bu komut sistemdeki tüm eski OpenGL/Mesa kütüphanelerini Intel Arc destekleyen en güncel sürüme çekecek.
```bash
sudo apt update && sudo apt upgrade -y
```

3. Grub Ayarını Normale Döndürmek: Mesa güncellendikten sonra artık `nomodeset` prangasına ihtiyacımız kalmaması gerekiyor. `/etc/default/grub` dosyasına gidip eklediğimiz tüm parametreleri temizleyelim.
```bash
sudo nano /etc/default/grub
```

  `GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"` haline geri getir (i915'li veya nomodeset'li tüm ekleri sil). Kaydet (`Ctrl+O`, `Enter`, `Ctrl+X`). Ardından GRUB'ı güncelle

```bash
sudo update-grub
```

4. Test zamanı. Sistemi yeniden başlat.
```bash
sudo reboot
```

**Not:** Sistemi reboot etmeden ilgili driver update’ler yapılmaz. Dolayısıyla reboot yapılmadıkça OpenGL versiyonu düzelmeyecektir.

# How to Prevent Next Time?

### 1. Kurulum Esnasında İnternet Bağlantısını Mecburi Kıl

ISO'dan kurulum yaparken bilgisayarın mutlaka aktif bir internet bağlantısı (mümkünse stabil bir Ethernet kablosu) olsun. Kurulum sihirbazındaki şu iki seçeneği kesinlikle tikle:

- **"Download updates while installing Ubuntu"** (Kurulum yaparken güncellemeleri indir)
- **"Install third-party software for graphics and Wi-Fi hardware"** (Grafik ve Wi-Fi donanımları için üçüncü parti yazılımları kur)

Bu iki seçenek, kurulum medyasındaki (ISO içindeki) eski paketlerin yerine, internetteki en güncel kernel ve Mesa sürücülerinin daha kurulum bitmeden diske yazılmasını sağlar.

### 2. İlk Bootu "Nomodeset" Olmadan Yapmaya Zorla (Donanım Haritalaması İçin)

Sistem kurulduktan sonra harici diskten yapacağın **ilk boot çok kritiktir**. Linux çekirdeği ilk düzgün açılışta donanımı tarar ve sürücü haritalarını oluşturur.

- Eğer sistem ilk açılışta siyah ekranda kalıyorsa, hemen kalıcı olarak `nomodeset` eklemek yerine ekran kartının güç yönetimini esnetecek geçici parametreleri (`i915.enable_dc=0` veya `i915.enable_fbc=0`) GRUB ekranından anlık vererek sistemi **ekran kartı sürücüsü aktifken** bir kez masaüstüne ulaştırmaya çalış.

### 3. Masaüstüne Ulaşır Ulaşmaz "Ramdisk"i (initramfs) Güncelle

Yeni donanımlarda, grafik sürücülerinin mikro kodları (firmware) diske yüklenir ama boot imajına (`initramfs`) otomatik olarak hemen işlenmeyebilir. Harici diske kurulum biter bitmez terminalde şu komutu çalıştırmak sistemi garantiye alır:

```bash
sudo update-initramfs -u -k all
```

Bu komut, kernel'a *"Bak harici diskte yeni grafik firmware'leri var, bunları boot esnasında hafızaya erken yükle"* talimatı verir.

# Sources

- [Gemini Sohbet Ekranı: OpenGL sorun tespiti ve çözümü](https://gemini.google.com/share/3f97489c284f)
- [Gemini Sohbet Ekranı: Genel çözüm uğraşı](https://gemini.google.com/share/134899c4fd56)
