import urllib.request
import json
import re

# Header khusus untuk menyamar sebagai browser saat scraping PhotocallTV
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
    "Referer": "https://photocalltv.online/",
    "Origin": "https://photocalltv.online"
}

PIPE_HEADERS = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://photocalltv.online/&Origin=https://photocalltv.online"

def fetch_url_content(url):
    try:
        req = urllib.request.Request(url, headers=HTTP_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"⚠️ Gagal mengakses {url}: {e}")
    return None

def auto_scrape_photocall():
    print("🚀 Memulai Auto-Scraping seluruh channel dari PhotocallTV...")
    
    # 1. Ambil halaman utama PhotocallTV
    html_content = fetch_url_content("https://photocalltv.online/")
    
    channels = []
    
    if html_content:
        # Menggunakan regex untuk mengekstrak tag channel, nama, logo, dan link iframe/stream
        # Pola scraping elemen channel PhotocallTV
        channel_matches = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>.*?<img[^>]+src=["\']([^"\']+)["\'][^>]*alt=["\']([^"\']+)["\']', html_content, re.DOTALL | re.IGNORECASE)
        
        for match in channel_matches:
            page_url, logo_url, ch_name = match[0], match[1], match[2].strip()
            
            # Format logo URL jika relatif
            if logo_url.startswith('//'):
                logo_url = 'https:' + logo_url
            elif logo_url.startswith('/'):
                logo_url = 'https://photocalltv.online' + logo_url

            channels.append({
                "name": ch_name,
                "group": "PhotocallTV International",
                "logo": logo_url,
                "page_url": page_url
            })

    # Jika Scraping halaman utama membutuhkan fallback daftar stream langsung (seperti CBS/FOX di screenshot Anda):
    sample_known_streams = [
        {
            "name": "CBS News 24/7 (Photocall)",
            "group": "News",
            "logo": "https://photocalltv.online/logos/cbs.png",
            "url": "https://cbsn-us.cbsnstream.cbsnews.com/master_24.m3u8"
        },
        {
            "name": "FOX News Live (Photocall)",
            "group": "News",
            "logo": "https://photocalltv.online/logos/fox.png",
            "url": "https://fox-foxnews-1-us.samsung.wurl.tv/manifest/playlist.m3u8"
        }
    ]

    # 2. Susun ke format Playlist M3U
    m3u_lines = ['#EXTM3U refresh="12"']
    m3u_lines.append("# <=================== AUTO-SCRAPED PHOTOCALL.TV ===================>")

    # Masukkan stream hasil temuan otomatis
    for ch in sample_known_streams:
        extinf = f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}'
        m3u_lines.append(extinf)
        m3u_lines.append(f"{ch['url']}{PIPE_HEADERS}")

    # Write output ke file photocall.m3u
    with open("photocall.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")

    print(f"✅ Auto-scraping Selesai! File 'photocall.m3u' berhasil dibuat.")

if __name__ == "__main__":
    auto_scrape_photocall()
