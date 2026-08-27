import urllib.request
import re
import json

BASE_URL = "https://photocalltv.online"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Referer": "https://photocalltv.online/",
    "Origin": "https://photocalltv.online"
}

# 1. Daftar seluruh Kategori & Tab Negara di PhotocallTV
CATEGORY_URLS = [
    {"group": "España", "url": "https://photocalltv.online/"},
    {"group": "Internacional", "url": "https://photocalltv.online/category/internacional/"},
    {"group": "Deportes", "url": "https://photocalltv.online/category/deportes/"},
    {"group": "Radio", "url": "https://photocalltv.online/category/radio/"},
    {"group": "Mexico", "url": "https://photocalltv.online/category/mexico/"},
    {"group": "Argentina", "url": "https://photocalltv.online/category/argentina/"},
    {"group": "America", "url": "https://photocalltv.online/category/america/"},
    {"group": "Brasil", "url": "https://photocalltv.online/category/brasil/"},
    {"group": "Chile", "url": "https://photocalltv.online/category/chile/"},
    {"group": "Colombia", "url": "https://photocalltv.online/category/colombia/"},
    {"group": "Ecuador", "url": "https://photocalltv.online/category/ecuador/"},
    {"group": "Peru", "url": "https://photocalltv.online/category/peru/"}
]

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        pass
    return None

def extract_stream_m3u8(page_url):
    """Membuka halaman web channel dan mengekstrak link .m3u8 asli dari player"""
    html = fetch_html(page_url)
    if not html:
        return None
    
    # Cari URL .m3u8 di dalam player JS / iframe
    m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html)
    if m3u8_matches:
        # Prioritaskan stream langsung bukan iklan
        for url in m3u8_matches:
            if "google" not in url and "analytics" not in url:
                return url
    return None

def auto_scrape_all_photocall():
    print("🚀 Memulai Deep Scraping SELURUH Tab Kategori & Negara PhotocallTV...")
    
    all_channels = []
    seen_pages = set()

    # TAHAP 1: Pindai semua tab kategori & negara
    for cat in CATEGORY_URLS:
        print(f"📡 Mengambil daftar channel dari kategori: {cat['group']}...")
        html = fetch_html(cat["url"])
        if not html:
            continue
        
        # Ekstrak semua link channel (<a href="..."><img src="..." alt="...">)
        pattern = re.compile(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', 
            re.DOTALL | re.IGNORECASE
        )
        
        matches = pattern.findall(html)
        
        for href, logo_src, raw_name in matches:
            clean_name = raw_name.strip()
            clean_name = re.sub(r'\s*\([^)]*\)', '', clean_name)
            clean_name = re.sub(r'\s+24/7', '', clean_name)
            
            if not clean_name or len(clean_name) < 2:
                continue

            logo_url = logo_src
            if logo_url.startswith("//"):
                logo_url = "https:" + logo_url
            elif logo_url.startswith("/"):
                logo_url = BASE_URL + logo_url

            page_url = href
            if page_url.startswith("/"):
                page_url = BASE_URL + page_url

            if page_url in seen_pages:
                continue
            seen_pages.add(page_url)

            all_channels.append({
                "name": clean_name,
                "logo": logo_url,
                "page_url": page_url,
                "group": cat["group"]
            })

    print(f"✅ Total {len(all_channels)} channel ditemukan dari seluruh tab!")

    # TAHAP 2: Ekstrak link .m3u8 dari player setiap channel
    print("🎥 Memproses ekstraksi link video .m3u8 asli dari player...")
    
    m3u_lines = ['#EXTM3U refresh="12"']
    m3u_lines.append(f"# <=================== PHOTOCALL.TV ALL CHANNELS ({len(all_channels)}) ===================>")

    valid_count = 0
    for ch in all_channels:
        # Ekstrak stream m3u8 asli dari halaman player
        stream_url = extract_stream_m3u8(ch["page_url"])
        
        if not stream_url:
            # Fallback jika stream di-embed via iframe khusus
            stream_url = ch["page_url"]

        # Tentukan Pipe Header berdasarkan tipe server
        if "futlive" in stream_url or "streamx" in stream_url or ch["group"] == "Deportes":
            pipe = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://streamxhd.com/"
        else:
            pipe = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://photocalltv.online/&Origin=https://photocalltv.online"

        extinf = f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}'
        m3u_lines.append(extinf)
        m3u_lines.append(f"{stream_url}{pipe}")
        valid_count += 1

    # Simpan ke file photocall.m3u
    with open("photocall.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")

    print(f"🎉 Selesai! File 'photocall.m3u' berisi {valid_count} channel berhasil dibuat!")

if __name__ == "__main__":
    auto_scrape_all_photocall()
