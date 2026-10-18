# UART Haberleşme Protokolü

## Temel Özellikler

Haberleşme protokollerini birkaç özellik çatısında ayrıştırmak mümkündür. Bu özellikler ve açıklamaları aşağıdaki gibidir:

- **Full-Duplex, Half-Duplex Yapısı:** Bir haberleşme protokolünün iki ucu arasında (alıcı ve verici uçları) aynı anda veri gönderimi ve alımı yapma durumudur. Yani A ve B adlı iki cihaz birbirleri ile haberleşirken A ucu, B ucuna veri gönderirken aynı anda A ucu, B ucundan veri de alabilme durumu varsa bu durum (aynı anda) iki yönlü haberleşmeye olanak sağladığını gösterir. Sistem iki yönlü haberleşmeye uygunsa **Full-Duplex**’tir, değilse **Half-Duplex**’tir.
- **Senkronizasyon:** Veri iletiminin iki (veya daha fazla) cihaz arasında bir saat sinyali eşliğinde (senkronizasyonunda) yapılması durumudur. Eğer veri iletimi saat sinyali eşliğindeyse sistem **Senkron**, değilse **Asenkron** sistemdir.

![](knowledge/assets/3e4945c9dc43801dade6ca3a315b2ff4/01.png)

UART bağlantı şeması yukarıda verilmiştir. Şemada da görüleceği üzere cihazlar arasında iletim (TX) ve alım (RX) hatları iki ayrı yoldan sağlanmaktadır. Dolayısı ile aynı anda veri gönderimi ve alımı için fiziksel şartlar ortadan kaldırılmıştır, yani UART için **Full-Duplex** bir yapıya sahiptir diyebiliriz. Buna ek olarak bağlantı şemasından görüleceği üzere iki cihaz arasında senkronizasyonu sağlayacak herhangi bir saat sinyali bağlantısı da bulunmamaktadır. Bu sebepten UART için **Asenkron** bir yapıya sahiptir diyebiliriz.

### Baudrate Kavramı

Baudrate tanım olarak saniyede iletilen bir miktarını ifade etmektedir. Yani bir cihazın 9600 baudrate olarak çalıştığını biliyorsak bu saniyede 9600 bit veri ile iş yaptığını belirtir. Sistemde UART haberleşme kullanılacağında baudrate, bir cihazın karşısındaki cihazdan ne hızda veri alacağını ve cihaza ne hızda veri göndermesi gerektiğini bilmesi açısından kritik öneme sahiptir. Bu sebepten ötürü UART haberleşme penceresi iki cihazda da açılmadan önce bu baudrate değerleri ayarlanır, ardından cihazlar birbirleri ile haberleşmeye başlar. 

Baudrate değerleri cihazdan cihaza ve sistemden sisteme farklılık gösterebilmekle birlikte cihazlarda genel olarak tercih edilen değerler 9600, 19200, 28800, 38400, 57600, 76800, 115200’dür.

### Baudrate Kavramının Donanımdaki Karşılığı

Donanımda bu UART Baudrate değerini tutması için bir register bulunmaktadır. (Bu register adı ve kullanılacak hesaplamalar karttan karta göre değişkenlik göstermekte olup bu yazıda kullanılacak register ve hesaplamalar STM32 kartlar için geçerlidir) STM32 için bu register’ın adı **USART Baudrate Register (BRR)**’dir. 

Kullanılan haberleşmede her ne kadar haberleşme için bir saat sinyaline gerek duyulmuyor olsa da verileri almak ve göndermek için bir saat sinyali eşliğinde bunu yapmak gerekmektedir. Yani haberleşme hattına bir saat sinyali eşlik etmese dahi cihazlar kendi içerisinde bir saat sinyali çalıştırırlar. Bu saat sinyalleri de Baudrate ile hesaplanır. Kullanılan donanımın saat frekansı fclk olmak üzere, aşağıdaki formül ile bu saat sinyalinin ne sıklıkla takip edileceği aşağıdaki formül ile hesaplanır;

$$
USARTDIV=fclk/Baudrate
$$

Örnek verecek olursak 42 MHz bir donanım ile 9600 baudrate değeri (saniye başı işlenecek bit) elde edilmek istensin. Bu kapsamda her bir saat darbesi (1/42000000=) 23.8 nanosaniyede vurmaktadır ve 9600 baudrate değeri elde etmek için her (42000000/9600=) 4375 saat darbesinde bir örnek almak gerekmektedir. Bir başka deyişle saatin frekansı uygun USARTDIV değerine bölünerek istenen baudrate değeri elde edilir. USART Baudrate Register (BRR)’ında ise baudrate değeri değil, bu USARTDIV değeri tutulur ve bu değere göre saat sinyali seyrekleştirilerek haberleşmenin iki cihaz için de senkronizasyonu, haberleşme hattında bir saat sinyali eşlik etmeden sağlanır. Sonuç olarak sistemin gönderici tarafında *(1/baudrate)* saniyerde bir yeni bit çıkarması beklenir. Alıcı tarafındaysa bu süre oversampling ile daha küçük parçalara bölünebilir. 

![](knowledge/assets/3e4945c9dc43801dade6ca3a315b2ff4/02.png)

Yukarıdaki görsel RM0090 Reference Manuel kitapçığından alınmıştır. Bu görselde USART_BRR Register yapısı gösterilmiştir. Son 16 bit ayrılmıştır ve sürekli olarak reset (0) değerine ayarlı olmalıdır. 15 ile 4. bitler arası DIV_Mantissa bitleridir ve bu USARTDIV değerinin tam sayı kısmını tutar. İlk 4 bit ise DIV_Fraction bitleridir ve bu USARTDIV değerinin ondalık kısmını tutar. Bu iki alan “rw” olarak, yani hem okunabilir hem de yazılabilir olarak işaretlenmiştir. Not olarak ise baud sayacı eğer TE veya RE bitleri disable edilirse duracağını belirtmektedir. TE biti “Transmission Enable”, yani gönderim aktif flag’i, RE biti “Receive Enable” yani alım aktif flag’idir.

Kısacası istenilen baudrate değerinin elde edilmesi için gönderici ve alıcı kendi donanımlarındaki saatlerin hızlarını ayarlar. Saatin istenen hıza ayarlanması için bir divider devresi kullanılır ve bu divider değeri Baudrate Register içerisinde tutulur. Bu register ile saatin hızı bölünerek sistem istenilen hıza ulaştırılır. 

### Sistemin Alıcı Ucunda Oversampling

1 saat darbesinde gönderilen verinin değerini 1 saat darbesinde okumaya çalışmak gürültü, baudrate hassasiyeti vb sebeplerden ötürü fazlasıyla risk barındırmaktadır. Bu kapsamda bağlantının alıcı tarafında oversampling ile göndericinin 1 saat darbesi birden çok parçaya bölünmüştür. 8x oversampling bu bir saat darbesinin 8’e, 16x oversampling ise bu bir saat darbesinin 16’ya bölündüğünü ifade etmektedir. Yani gönderici tarafın saati 160 mikrosaniyede bir kez vurduğunu, yani 160 mikrosaniyede 1 bit veri gönderdiğini farzedelim. 8x oversampling durumunda alıcı taraf gelen veriyi (160/8=) 20 mikrosaniyede bir kez okurken 16x oversampling durumunda alıcı taraf gelen veriyi (160/16=) 10 mikrosaniyede bir kez okur. Dolayısı ile gürültü ile değişen değerler, baudrate hassasiyeti ile kaybedilebilecek değerlerin önüne geçilmek istenmektedir. Alıcının 1 bit veri gönderdiği sürede 8x oversampling için 8 veri, 16x oversampling için 16 veri toplandı. **Peki hangi veri alıcının gönderdiği doğru veri olarak kabul edilir?** Doğru verinin kabulü için tek bir çözüm/kabul vardır. **Tam ortada elde edilen veri her zaman doğru veri kabul edilir.** Dolayısı ile 8x oversampling için 4. veri, 16x oversampling için 8. veri doğru veri olarak kabul edilir. Bu ilgili örneği seçme sorunu donanımda çözülmüş bir sorundur. Donanım oversampling oranına göre bit süresi botunca belli aralıklarla ölçüm yapar ama CPU bundan haberdar olmaz. UART peripheral’inin içinde bu iş için özel bir sampling logic ve state machine vardır. Bu donanımdaki iki yapı ortadaki veriyi otomatik olarak alır ve yazılımın kullanacağı “Data Register - DR”a bırakır. 

Örnek bir UART donanım yapısı aşağıda verilmiştir. Detaylı inceleme başka bir başlık altında yapılacaktır.

![](knowledge/assets/3e4945c9dc43801dade6ca3a315b2ff4/03.png)

## UART Frame

Şu ana kadar iki cihazın haberleşmesindeki gerekli fiziksel bağlantıları ve veri hattına verinin bırakılması ve hattan alınması üzerine zamanlamayı konuştuk. Peki bu hat üzerinden gönderilen veri nasıl bir formattadır? Aynı baudrate ayarı gibi sistemin iki ucu için UART hattı açılırken tele bırakılacak verinin tipi seçilmelidir. Böylece gönderen uç göndereceği veriyi uygun formatta paketlerken alıcı taraf ise gelen veriyi uygun formatta açar. 

Gönderilecek verinin senkron olmaması sebebiyle bu veri paketleri bir başlangıç ve bitiş bitine sahip olmaları gerekmektedir. UART protokolü gereği başlangıç biti her zaman low (0), bitiş biti ise her zaman high (1) olmalıdır. Bu iki bit arası ise veri ve güvenlik biti/bitleri ile doldurulur. UART protokolünün olabilecek frameleri aşağıdaki gibidir;

- **8N1:** 1 start biti + 8 veri biti + 0 eşlik biti + 1 stop biti = 10 bit/frame
- **8E1:**  1 start biti + 8 veri biti + 1 çift eşlik biti + 1 stop biti = 11 bit/frame
- **7O2:** 1 start biti + 7 veri biti + 1 tek eşlik biti + 2 stop biti = 10 bit/frame

![](knowledge/assets/3e4945c9dc43801dade6ca3a315b2ff4/04.png)

### Start-Stop Bitleri

Start biti her zaman 1 bittir ve her zaman low (space-0) olarak başlar.

Stop biti/bitleri ise her zaman tek bitten oluşmak zorunda değildir. 1/2 bitlik stop biti en hızlı bit iken 2 stop biti ise en toleranslı stop bitidir. Stop bit sayısı kaç olursa olsun her zaman bu bit high (mark-1) olarak işaretlenir.

### Veri Bitleri

UART Frame’ine göre veri biti sayısı 5, 6, 7, 8 veya 9 olabilir. Fakat veriler paketlenirken en anlamsız bit (LSB - Least Significant Bit) her zaman ilk sırada, yani bit0 sırasında gönderilir. En anlamlı bit ise (MSB - Most Significant Bit) en son sırada, yani bit7 sırasında gönderilir. Örneğin göndereceğimiz veri “u” olsun. Bu verinin 7-bit ASCII karşılığı 1110101’dir. Bu veri UART paketine sokulacağında 1010111 formatına çevrilerek gönderilir. Protokolün bu LSB→MSB dönüşümü yazılımda değil donanımda çözümlenir. İlgili veri yazılım tarafından olduğu gibi (Örn 1110101) şeklinde DR’ye yazar. Donanımın shift register’ı ilgili sırayı tersine çevirerek veriyi paketler ve haberleşme hattına iletir. Dolayısı ile UART ile haberleşmede bütün paketleme işlemi, tersine çevirme işlemi gibi işlemler donanım tarafından halledilir, yazılımın sadece veriyi ilgili register olan DR’ye yazması yeterlidir.

**Peki neden LSB→MSB sırasında veri hatta yazılır?** Bu sorunun birden çok cevabı bulunmakta.

- Tarihsel Neden: UART protokolü ilk kez mekanik teleprinter / teletype (TTY) cihazlarından türedi. O dönemde makineler ASCII tablosundaki düşük değerli karakterleri (ör. NUL=0x00, BEL=0x07) en sık kullanıyordu. LSB önce gönderilirse, cihaz karakteri daha erken tanıyabiliyordu yani pratikte daha hızlı tepki verebiliyordu. Bu sebepten bu standart haline geldi.
- Donanım Basitliği: UART’ın çıkışı/okuyucusu aslında bir shift register. Shift register, veriyi en düşük bitinden başlayarak kaydırmayı çok daha kolay yapıyor. Çünkü LSB zaten DR (data register)’ın en düşük ucunda duruyor, hat üzerinden birer birer çıkarmak için ek mantık gerekmez.

### Parity

Gönderilen veride hata olup olmadığını tespit etmek için kullanılan opsiyonel 1 bittir. Donanım veri bitlerindeki 1’leri sayar. Bunun sonucunda;

- **Even Parity:** Gönderilecek  verinin içerisindeki 1 bitlerinin sayısının çift olmasını amaçlar. 
  - Örneğin 1110101 verisinin içerisindeki 1 bitlerinin sayısı 5’tir. 5 adet 1 biti olması veride tek sayıda 1 biti olduğu anlamına gelir. Dolayısıyla parity biti “1” olarak verideki 1 biti sayısını çift yapar.
- **Odd Parity:** Gönderilecek verinin içerisindeki 1 bitlerinin sayısını tek olmasını amaçlar.
  - Örneğin 1110101 verisinin içerisindeki 1 bitlerinin sayısı 5’tir. 5 adet 1 biti olması veride tek sayıda 1 biti olduğu anlamına gelir. Dolayısıyla parity biti “0” olarak verideki 1 biti sayısının tek kalmasını sağlar.

Gönderici tarafındaki donanım bu hesaplamayı yaparak ilgili biti ayarlar, alıcı tarafındaki donanım ise bu hesaplamayı yaparak ilgili bitle karşılaştırır. Sonuç aynıysa gelen veri doğru kabul edilir. 

**Peki parity bit karşılaştırmasında sonuç aynı değilse ne olur?** Donanım bu sorunu gelen parity biti ile hesaplananın uyuşmadığını gösteren “PE” flag’ini 1 yaparak çözer. PE flag’ini kontrol eden, PE flag’i 1 olduğu durumda ne yapılması gerektiğine karar veren mekanizma ise yazılıma bırakılmıştır. Yani sorunun tespiti donanımdadır, sorunun çözümü ise yazılıma bırakılmıştır. **Bu kapsamda yazılımda bu sorun nasıl çözülebilir?** 

- Veri kaybını göze alarak hatalı paketi çöpe atarak devam edebilir.
- Yazılımcı eğer UART Frame’in üst katman yapısını **ACK/NACK** mekanizması ile inşa ettiyse ilgili pakete NACK gönderek tekrar aynı frame’in gönderimini isteyebilir.
- Yazılımcı eğer UART Frame’in üst katman yapısına **CRC veya checksum** mekanizması eklediyse bütün paketi geçersiz sayabilir ve tekrar aynı frame’in gönderimini isteyebilir.

## Hata Tespit Mekanizmaları

Gelen verilerin hatalarının tespiti için parity bit çözümünün üzerinden geçtik. Hatayı tespit etmek için başka methotların ve hatayı telafi etmek için başka yöntemlerin üzerinden geçelim.

### Donanım Katmanı Hata Tespitleri

**Parity Error:** Eğer gelen parity bit ile hesaplanan parity bit uyuşmuyorsa PE flag işaretlenir.

**Framing Error:** Eğer stop biti beklenen yerde 1 değilse FE flag işaretlenir. Genellikle baudrate uyuşmazlığı veya veri kayması sebebiyle oluşur.

**Noise Error:** Hat seviyesi sampling sırasında kararsızsa oversampling ile karar alınsa dahi eğer kararsızlık eşiği aşılırsa NE flag işaretlenir.

**Overrun Error:** Alıcı register DR boşaltılmadan yeni bayt gelirse ORE flag işaretlenir. Eski veri kaybolur sadece en son gelen bayt kalır.

**Break Detection:** Hat uzun süre 0 seviyesinde kalırsa BK flag işaretlenir. 

**IDLE Line Detection:** Alıcı hattında belirli süre hiç bir gelmezse IDLE flag işaretlenir. Paket sonunun geldiği işareti olarak da kullanılabilir.

### Yazılım-Protokol Katmanı Hata Kontrolleri

Donanım katmanları çoğu zaman tek başına yetmez. Daha güvenilir protokoller için üst katmanda ek mekanizmalar yazılımcı tarafından kurulur. Gönderilecek UART frame’ler paketlenerek her paketin sonrasında ilgili hata kontrol mekanizmaları uygulanır. Paketlemeler ve kontrol mekanizmaları tamamen yazılımcının tercihine bağlıdır.

**Checksum:** Gönderilen paket içerisindeki verilerin (frame’lerin değil, paket içerisindeki framelerin içerisindeki verilerin) toplamının belirli bir sayıya modu alınarak o pakete dair checksum değeri hesaplanır. O paketin ardından yeni bir frame ile checksum değeri gönderilir. Gönderici nasıl hangi değerle modunun alınacağını, her paketin kaç frame’den oluşacağını ve chacksum değerinin hangi frame’de gönderileceğini biliyorsa alıcı da aynı şekilde bu üst katman protokolü bilmektedir ve ona göre işlemlerde bulunmaktadır.

**CRC:** Hata tespiti için kullanılan çok güçlü bir algoritmadır. Polinom bölme matematiği ile çalışır. 

- Veri matematiksel olarak bir ikili polinom gibi düşünülür. Ör. 1101=x^3+x^2+x^0
- Önceden tanımlı bir üretici polinom (generator polynomial) seçilir. Bu seçilen polinomun uzunluğuna göre CRC isimlendirmesi değişmektedir. 
  - en büyük terim x^8 ise→ CRC-8
  - en büyük terim x^16 ise→ CRC-16
  - en büyük terim x^32 ise→ CRC-32
- Gönderici veriyi bu polinoma böler, kalan değeri de paketin sonuna ek bir frame ile CRC değeri olarak gönderir.
- Alıcı ise tüm veri + CRC’yi aynı polinomla böler
  - Kalan=0 ise gelen veri doğrudur.
  - Kalan≠0 ise gelen veri bozulmuştur.
**Sequence Number (Paket Numarası):** Her pakete bir paket numarası vererek alıcının da bu paket sırasını takip etmesi ve eksik gelen veriyi tespit etmesi sağlanır. 

**ACK/NACK Mekanizması:** ACK onay, NACK ise olumsuz onay anlamına gelmektedir. Alıcı paketi doğru aldıysa vericiye ACK mesajı yollar, yanlış aldıysa NACK mesajı yollar. Bu mekanizma hata tespit mekanizması değil, geri bildirim mekanizmasıdır. Dolayısı ile hatalı geldiği tespit edilen paket alıcıya NACK gönderilerek alıcıdan tekrar istenir.

Sonuç olarak UART haberleşme protokolü, görünürde basit bir iki hat üzerinden veri iletimi sağlasa da, arka planda donanımın sunduğu baudrate üretim mekanizmaları, oversampling ile gürültüye karşı dayanıklılık, start–data–parity–stop yapısıyla çerçeveleme ve donanım seviyesinde hata bayrakları sayesinde güvenilir bir iletişim altyapısı oluşturur. Bununla birlikte, donanım katmanı tek başına mutlak güvenlik sağlamadığından, yazılım ve protokol katmanında geliştirilecek checksum, CRC, sequence number veya ACK/NACK gibi mekanizmalar ile eksik, hatalı veya kaybolan verilerin kontrol altına alınması mümkündür. Böylece UART, hem gömülü sistemlerde basit sensör–mikrodenetleyici haberleşmesinden endüstriyel cihazlar arası veri aktarımına kadar geniş bir kullanım alanı bulan, hem de donanım ve yazılım düzeyinde birlikte ele alındığında esnek, ölçeklenebilir ve güvenilir bir seri iletişim yöntemi olarak öne çıkmaktadır.
