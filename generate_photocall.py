import urllib.request
import re
import json

# Headers Default
HEADERS_PHOTOCALL = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://photocalltv.online/&Origin=https://photocalltv.online"
HEADERS_STREAMXHD = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36&Referer=https://streamxhd.com/"

# Daftar Channel PhotocallTV Utama (Sesuai Layout Sidebar Screenshot Anda)
photocall_channels = [
    # --- NEWS CHANNELS ---
    {
        "name": "CBS News",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/CBSNews.png",
        "url": "https://cbsn-us.cbsnstream.cbsnews.com/out/v1/55a8648e8f134e82a470f83d562deeca/master.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "FOX Live",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/FOXLive.png",
        "url": "https://fox-foxnews-1-us.samsung.wurl.tv/manifest/playlist.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "ABC News",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/ABCNews.png",
        "url": "https://abcnews-lh.akamaihd.net/i/abc_live11@424858/master.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "NBC News",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/NBCNews.png",
        "url": "https://nbcnews-lh.akamaihd.net/i/nbc_live1@123456/master.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "Bloomberg TV",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/Bloomberg.png",
        "url": "https://liveproduseast.global.ssl.fastly.net/us/bbg/live.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "Newsmax TV",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/Newsmax.png",
        "url": "https://newsmax-lh.akamaihd.net/i/newsmax_1@328909/master.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    
    # --- ENTERTAINMENT & SCIENCE ---
    {
        "name": "NASA TV",
        "group": "Science",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/Science/NASATV.png",
        "url": "https://ntv1.akamaized.net/hls/live/2014075/NASA-NTV1-HLS/master.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "Court TV",
        "group": "Entertainment",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/Entertainment/CourtTV.png",
        "url": "https://courttv-us-east.wurl.tv/manifest/playlist.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    {
        "name": "Cheddar USA",
        "group": "News",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/News/Cheddar.png",
        "url": "https://cheddar-us.wurl.tv/manifest/playlist.m3u8",
        "headers": HEADERS_PHOTOCALL
    },
    
    # --- SPORTS (StreamXHD / FutLive Source) ---
    {
        "name": "DSports Argentina",
        "group": "Sports",
        "logo": "https://raw.githubusercontent.com/sulthanpamenan/IPTV/main/Logos/Sports/DSports.png",
        "url": "https://khala.futlivehd.com/global/dsportsar/index.m3u8",
        "headers": HEADERS_STREAMXHD
    }
]

def generate_photocall_m3u():
    print("🔄 Memproses playlist PhotocallTV...")
    
    lines = ['#EXTM3U refresh="12"']
    lines.append("# <=================== PHOTOCALL.TV CHANNELS ===================>")
    
    for ch in photocall_channels:
        extinf = f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}'
        lines.append(extinf)
        lines.append(f"{ch['url']}{ch['headers']}")
        
    content = "\n".join(lines) + "\n"
    
    with open("photocall.m3u", "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"✅ Berhasil membuat file photocall.m3u ({len(photocall_channels)} channel)")

if __name__ == "__main__":
    generate_photocall_m3u()
