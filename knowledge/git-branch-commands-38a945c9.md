> Local’ime bir git reposu clone’ladım. Bu repo üzerinde değişiklikler yapacağım ama ilk olarak ayrı bir branch açmak istiyorum. Branch nasıl açarım?

### 1. Terminal veya Komut Satırını Aç

Projenin kopyalandığı (clone edildiği) klasörün içinde olduğundan emin ol. Değilsen terminalden projenin içine gir:

```bash
cd <proje-klasörünün-adı>
```

### 2. Yeni Bir Branch Oluştur ve Ona Geç

Bunu yapmanın iki popüler yolu var. İkisi de aynı kapıya çıkar, hangisi kolayına gelirse onu kullanabilirsin:

**Modern ve Önerilen Yöntem (Git 2.23+):**

```bash
git switch -c <yeni-branch-adı>
```

*Buradaki* `-c` *(create) yeni bir branch oluşturup doğrudan ona geçmeni sağlar.*

**Klasik Yöntem:**

```bash
git checkout -b <yeni-branch-adı>
```

*Buradaki* `-b` *de yine aynı şekilde branch'i oluşturur ve seni o branch'e taşır.*

> **Küçük bir ipucu:** Branch isminde Türkçe karakter ve boşluk kullanmamaya özen göster. Kelimeleri ayırmak için `-` (tire) veya `/` (bölü) işareti kullanabilirsin (Örn: `feature/new-login-page` veya `fix-memory-leak`).

### 4. Geliştirme Sonrası Uzak Sunucuya (Remote) Pushlamak

Kodunda değişiklikleri yaptın, `git add` ve `git commit` adımlarını tamamladın. Bu yeni branch'i localinden Github/Gitlab gibi uzak sunucuya ilk kez göndereceğin zaman şu komutu kullanman gerekir:

```bash
git push -u origin <yeni-branch-adı>
```

*Buradaki* `-u` *(set-upstream) bayrağı, localindeki bu branch ile uzak sunucudaki branch'i birbirine bağlar. Bundan sonraki push'larında sadece* `git push` *yazman yeterli olur.*

### 5. Ana Branch’e Geçme

```bash
git switch main
```

### 6. Branchleri Birleştirme - merge

```bash
git merge <kapatmak-istedigin-branch-adi>
```

### 7. Branch’i Sil

```bash
git branch -d <silmek-istedigin-branch-adi>
```

### 8. Uzak Sunucudaki (Remote) Branch'i Silme

```bash
git push origin --delete <branch-adi>
```
