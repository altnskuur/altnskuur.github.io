---
technical: true
personal: false
date: 2026-07-20
notion: 3a3945c9dc438001a49fcd66938b025b
---
# CPU Burn Operation

CPU hızını maksimize ederek CPU’nun maksimum sınırlarını zorlamak için yapılır.

# Technical Details

- **Stress Workload (Matrix Multiplication):**  `matrixprod` metodu, CPU üzerinde yoğun matris çarpımı işlemleri gerçekleştirir. Bu işlem hem tam sayı (integer) hem de kayan nokta (floating-point) birimlerini aynı anda kullanarak işlemci mimarisini en üst seviyede zorlar ve ısıl yayılımı (heat dissipation) maksimize eder.
- **CPU Governor & Frequency:** Test sırasında işlemci hızı, Linux `performance` governor ayarı ile en yüksek frekansta (Maximum Turbo Frequency) tutulmaya zorlanır. Bu durum, anlık akım çekişinin (I-peak) en yüksek seviyeye ulaşmasını sağlar.
- **Thermal Throttling Observation:** Testin ana teknik amacı, işlemcinin **Tjunction** (kritik sıcaklık eşiği) değerine ulaşıp ulaşmadığını ve ulaştığında frekans düşürerek (throttling) kendini korumaya alıp almadığını gözlemlemektir.
- **Data Acquisition (RAPL & Sensors):** Sıcaklık verileri, CPU içerisindeki dijital termal sensörlerden (DTS) `lm-sensors` aracılığıyla okunur. Bu sensörler doğrudan silikon üzerindeki en sıcak noktaları (hotspots) raporlar.
- **Power Consumption:** Yüksek yük altında CPU'nun çektiği güç (Watt), **RAPL (Running Average Power Limit)** arayüzü üzerinden takip edilebilir. Bu, güç kaynağının (PSU) veya voltaj regülatörlerinin (VRM) kararlılığını test etmek için kritiktir.

# Application Area

## How to use?

Linux terminal üzerinden en progesyonel araç `stress-ng` veya `stress` paketleridir. Bu paketlerin kurulumu aşağıdaki gibidir.

```bash
sudo apt install stress-ng
```

Bu paket ile çekirdekleri sonuna kadar zorlamak için:

```bash
stress-ng --cpu 0 --cpu-method matrixprod
```

CPU yüklemesi yaparak CPU’nun anlık sıcaklık değerlerini takip etmek istenmektedir. Bu amaç için bir Bash script dosyası yazılmıştır. Bu scriptin çalışması için gerekli olan paketler de aşağıdaki gibi yüklenmelidir.

```bash
sudo apt install lm-sensors
sudo sensors-detect  # (Gelen sorulara YES diyerek sensörleri taratın)
```

İlgili Bash dosyasını yazmak için aşağıdaki gibi dosya oluşturulmalıdır.

```bash
nano core_temp.sh
```

İlgili dosya yukarıdaki gibi `nano` ile açıldıktan sonra aşağıdaki kod `CTRL+Shift+V` kısayolu ile yapıştırılmalıdır ve `CTRL+X`, `Y`, `Enter` ile kaydedilmelidir.

```bash
#!/bin/bash

LOG_FILE="cpu_log.txt"

while true; do
    # Terminali temizle (sadece anlık veriyi görmek için)
    clear
    
    # Zaman damgası
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    
    # Sadece çekirdek (Core) satırlarını al
    CORE_DATA=$(sensors | grep "Core")

    # 1. Ekrana bas
    echo "Zaman: $TIMESTAMP"
    echo "$CORE_DATA"

    # 2. Dosyaya timestamp ile birlikte ekle
    echo "--- $TIMESTAMP ---" >> "$LOG_FILE"
    echo "$CORE_DATA" >> "$LOG_FILE"

    sleep 1
done
```

İlgili dosyaya aşağıdaki şekilde yetki verilmelidir.

```bash
chmod +x core_temp.sh
```

Dosya aşağıdaki gibi çalıştırılır.

```bash
./core_temp.sh
```

CPU’nun anlık frekans değerini gözlemlemek için aşağıdaki komut çalıştırılmalıdır. Eğer `linux-tools` kurulu değilse kurulmalıdır.

```bash
sudo watch cpupower monitor
```

Daha görsel bir arayüz ile anlık frekans, utility, temperature değerlerini gözlemlek için aşağıdaki komut kullanılmalıdır

```bash
s-tui
# Eger yuklu degilse -> sudo apt install s-tui
```

## Where to use?

CPU’nun sınırlarının zorlanmak istendiği test setup’larında kullanılabilir
