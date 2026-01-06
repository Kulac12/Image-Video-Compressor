# Resim ve Video Boyut Küçültücü

Toplu resim ve video boyut küçültme araçları. Web siteleri için optimize edilmiş dosya boyutları elde edin.

## Özellikler

### Resim Boyut Küçült
- **Hedef Boyut Belirleme**: 100-300 KB arası web optimizasyonu
- **Toplu İşlem**: Birden fazla dosyayı aynı anda işleyin
- **Sürükle-Bırak**: Dosyaları doğrudan pencereye sürükleyin
- **Format Dönüştürme**: JPEG, PNG, WebP arası dönüşüm
- **Hız Ayarı**: Hızlı/Normal/Yavaş sıkıştırma seçenekleri
- **Boyut Sınırlama**: Maksimum genişlik/yükseklik belirleme
- **Çift Dil**: Türkçe ve İngilizce arayüz

### Video Boyut Küçült
- **Codec Desteği**: H.264, H.265 (HEVC), VP9
- **Kalite Kontrolü**: CRF değeri ile hassas ayar
- **Çözünürlük Seçimi**: 4K, 1080p, 720p, 480p, 360p
- **Preset Seçimi**: ultrafast'tan veryslow'a hız/kalite dengesi
- **Ses Ayarları**: Bit rate ve ses kaldırma seçenekleri
- **Çift Dil**: Türkçe ve İngilizce arayüz

## Kurulum

### Hazır Exe Kullanımı (Windows)
1. [Releases](../../releases) sayfasından son sürümü indirin
2. `Resim_Boyut_Kucult.exe` veya `Video_Boyut_Kucult.exe` dosyasını çalıştırın

### Kaynak Koddan Çalıştırma
```bash
# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Resim aracını çalıştırın
python resim_sikistirici.py

# Video aracını çalıştırın
python video_sikistirici.py
```

### Video Aracı İçin Ek Gereksinim
Video Boyut Küçült aracı için [FFmpeg](https://ffmpeg.org/download.html) kurulu olmalıdır.

## Gereksinimler

- Python 3.8+
- Pillow (resim işleme için)
- FFmpeg (video işleme için)
- windnd (sürükle-bırak desteği için, opsiyonel)

## Kullanım

### Resim Boyut Küçült
1. **Dosya Ekle** veya **Klasör Ekle** butonuyla resimleri seçin (veya sürükle-bırak)
2. **Hedef Boyut** özelliğini aktifleştirin ve KB aralığını belirleyin
3. İsterseniz çıktı formatını ve hız ayarını değiştirin
4. **BOYUT KÜÇÜLTMEYE BAŞLA** butonuna tıklayın

### Video Boyut Küçült
1. Video dosyasını seçin
2. Codec, çözünürlük ve kalite ayarlarını yapın
3. **BOYUT KÜÇÜLTMEYE BAŞLA** butonuna tıklayın

## Desteklenen Formatlar

### Resim
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- BMP (.bmp)
- TIFF (.tiff, .tif)

### Video
- MP4 (.mp4)
- AVI (.avi)
- MKV (.mkv)
- MOV (.mov)
- WebM (.webm)

## Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

## Geliştirici

**Edanur KULAÇ**

---

Sorularınız veya önerileriniz için [Issues](../../issues) sayfasını kullanabilirsiniz.
