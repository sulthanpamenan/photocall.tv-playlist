import urllib.request
import re
import json

BASE_URL = "https://photocalltv.online"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Referer": "https://photocalltv.online/",
    "Origin": "https://photocalltv.online"
}

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status == 200:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
    return None

def auto_scrape_photocall():
    print("🚀 Memulai Auto-Scraping RATUSAN channel dari PhotocallTV...")
    
    html = fetch_html(BASE_URL)
    if not html:
        print("❌ Gagal mengambil halaman utama PhotocallTV.")
        return

    # Regex untuk mengekstrak semua elemen channel (Link, Logo, Nama) secara otomatis
    # Pola: <a href="..."><img src="..." alt="...">...<span>Nama Channel</span></a>
    pattern = re.compile(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', 
        re.DOTALL | re.IGNORECASE
    )
    
    matches = pattern.findall(html)
    print(f"📦 Ditemukan {len(matches)} elemen channel kasar di website.")

    extracted_channels = []
    seen_urls = set()

    for href, logo_src, raw_name in matches:
        # 1. Bersihkan Nama Channel
        clean_name = raw_name.strip()
        clean_name = re.sub(r'\s*\([^)]*\)', '', clean_name) # Hapus teks dalam kurung seperti (Photocall)
        clean_name = re.sub(r'\s+24/7', '', clean_name)     # Hapus imbuhan 24/7 jika ada
        
        if not clean_name or len(clean_name) < 2:
            continue

        # 2. Rapikan Link Logo
        logo_url = logo_src
        if logo_url.startswith("//"):
            logo_url = "https:" + logo_url
        elif logo_url.startswith("/"):
            logo_url = BASE_URL + logo_url

        # 3. Format URL Detail Channel
        detail_url = href
        if detail_url.startswith("/"):
            detail_url = BASE_URL + detail_url

        if detail_url in seen_urls:
            continue
        seen_urls.add(detail_url)

        # Tentukan Kategori Group
        group_title = "Photocall TV"
        if "deportes" in detail_url.lower() or "sport" in detail_url.lower():
            group_title = "Sports"
        elif "news" in detail_url.lower() or "24h" in detail_url.lower():
            group_title = "News"

        extracted_channels.append({
            "name": clean_name,
            "logo": logo_url,
            "detail_url": detail_url,
            "group": group_title
        })

    print(f"🔍 Memproses {len(extracted_channels)} channel unik...")

    # 4. Buat File M3U
    m3u_lines = ['#EXTM3U refresh="12"']
    m3u_lines.append(f"# <=================== PHOTOCALL.TV AUTO-SCRAPED ({len(extracted_channels)} CHANNELS) ===================>")

    count = 0
    for ch in extracted_channels:
        # Cek apakah server channel mengarah ke server Olahraga (khala.futlivehd / streamxhd)
        if "futlive" in ch["detail_url"] or "streamx" in ch["detail_url"] or ch["group"] == "Sports":
            header_pipe = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://streamxhd.com/"
        else:
            header_pipe = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://photocalltv.online/&Origin=https://photocalltv.online"

        extinf = f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}'
        m3u_lines.append(extinf)
        m3u_lines.append(f"{ch['detail_url']}{header_pipe}")
        count += 1

    # Simpan ke file photocall.m3u
    with open("photocall.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")

    print(f"✅ Selesai! Berhasil mengekstrak {count} channel secara otomatis ke 'photocall.m3u'.")

if __name__ == "__main__":
    auto_scrape_photocall()
