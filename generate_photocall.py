import urllib.request
import re
import json

BASE_URL = "https://photocalltv.online"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Referer": "https://photocalltv.online/",
    "Origin": "https://photocalltv.online"
}

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
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return resp.read().decode('utf-8', errors='ignore')
    except Exception:
        pass
    return None

def extract_all_sources(page_url):
    """Mengekstrak SEMUA opsi server (m3u8) dan iframe alternatif dari halaman channel"""
    html = fetch_html(page_url)
    if not html:
        return []

    found_sources = []
    
    # 1. Cari semua URL m3u8 langsung di halaman
    m3u8_matches = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', html)
    for url in m3u8_matches:
        if "google" not in url and "analytics" not in url and url not in found_sources:
            found_sources.append(url)

    # 2. Cari link iframe / player alternatif jika ada (Sumber 2 / Fuente 2)
    iframe_matches = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    for iframe_url in iframe_matches:
        if iframe_url.startswith("//"):
            iframe_url = "https:" + iframe_url
        elif iframe_url.startswith("/"):
            iframe_url = BASE_URL + iframe_url
            
        # Buka iframe untuk mengambil m3u8 di dalamnya
        if "photocall" in iframe_url or "stream" in iframe_url or "player" in iframe_url:
            sub_html = fetch_html(iframe_url)
            if sub_html:
                sub_m3u8 = re.findall(r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*', sub_html)
                for sm in sub_m3u8:
                    if "google" not in sm and sm not in found_sources:
                        found_sources.append(sm)

    return found_sources

def build_referer_header(stream_url):
    """Menentukan header referer secara presisi sesuai domain server video"""
    if "futlive" in stream_url or "streamx" in stream_url or "khala" in stream_url:
        return "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://streamxhd.com/"
    elif "cbsnews" in stream_url:
        return "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://photocalltv.online/&Origin=https://photocalltv.online"
    elif "wurl.tv" in stream_url or "samsung" in stream_url:
        return "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    else:
        return "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://photocalltv.online/&Origin=https://photocalltv.online"

def auto_scrape_all_photocall():
    print("🚀 Memulai Auto-Scraping Multi-Fuente PhotocallTV...")
    
    all_pages = []
    seen_pages = set()

    # TAHAP 1: Ambil seluruh link halaman channel dari semua kategori
    for cat in CATEGORY_URLS:
        print(f"📡 Mengambil kategori: {cat['group']}...")
        html = fetch_html(cat["url"])
        if not html:
            continue
        
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

            all_pages.append({
                "name": clean_name,
                "logo": logo_url,
                "page_url": page_url,
                "group": cat["group"]
            })

    print(f"✅ Ditemukan {len(all_pages)} channel unik dari semua tab. Memulai ekstraksi stream & alternatif...")

    # TAHAP 2: Ekstrak stream video m3u8 asli & alternatif
    m3u_lines = ['#EXTM3U refresh="12"']
    m3u_lines.append("# <=================== PHOTOCALL.TV MULTI-SOURCE PLAYLIST ===================>")

    valid_count = 0
    for ch in all_pages:
        sources = extract_all_sources(ch["page_url"])
        
        # JIKA TIDAK DITEMUKAN STREAM M3U8, ABAIKAN (Mencegah error HTML)
        if not sources:
            continue

        for idx, stream_url in enumerate(sources):
            # Beri label server alternatif jika ada lebih dari 1 sumber
            source_label = f" (Fuente {idx+1})" if len(sources) > 1 else ""
            ch_display_name = f"{ch['name']}{source_label}"
            
            header_pipe = build_referer_header(stream_url)

            extinf = f'#EXTINF:-1 tvg-name="{ch_display_name}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch_display_name}'
            m3u_lines.append(extinf)
            m3u_lines.append(f"{stream_url}{header_pipe}")
            valid_count += 1

    with open("photocall.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")

    print(f"🎉 Selesai! Berhasil membuat 'photocall.m3u' berisi {valid_count} stream m3u8 valid!")

if __name__ == "__main__":
    auto_scrape_all_photocall()
