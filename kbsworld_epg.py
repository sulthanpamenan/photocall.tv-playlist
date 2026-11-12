from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup


def fetch_kbs_schedule(date_str, time_add="-2", language="e"):
  """Mengambil halaman jadwal KBS World berdasarkan tanggal, time_add, dan bahasa."""
  url = "https://kbsworld.kbs.co.kr/schedule/list.php"
  params = {"language": language, "time_add": time_add, "sdate": date_str}
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Referer": "https://kbsworld.kbs.co.kr/",
  }

  print(
      f"Mengambil data EPG untuk tanggal {date_str} (time_add={time_add})..."
  )
  response = requests.get(url, params=params, headers=headers)
  if response.status_code != 200:
    print(f"Gagal mengambil data, status code: {response.status_code}")
    return []

  soup = BeautifulSoup(response.text, "html.parser")
  schedule_items = []

  # Parsing elemen jadwal dari struktur HTML KBS World
  list_items = soup.select(".schedule-list > li.twice-tab")

  for item in list_items:
    time_elem = item.select_one(".time-wrap .time")
    title_elem = item.select_one(".title")
    desc_elem = item.select_one(".text")
    genre_elem = item.select_one(".genre")

    if time_elem and title_elem:
      time_str = time_elem.get_text(strip=True)  # Format "HH:MM"
      full_title = title_elem.get_text(strip=True)
      desc = desc_elem.get_text(strip=True) if desc_elem else ""
      genre = genre_elem.get_text(strip=True) if genre_elem else "General"

      schedule_items.append({
          "time": time_str,
          "title": full_title,
          "desc": desc,
          "genre": genre,
      })

  return schedule_items


def generate_xmltv(days_to_fetch=7):
  """Menghasilkan file XMLTV untuk beberapa hari kedepan."""
  root = ET.Element("tv")

  # Definisi Channel KBS World
  channel = ET.SubElement(root, "channel", id="KBSWorld.kr")
  display_name = ET.SubElement(channel, "display-name")
  display_name.text = "KBS World"

  base_date = datetime.now()

  for i in range(days_to_fetch):
    current_date = base_date + timedelta(days=i)
    date_str = current_date.strftime("%Y-%m-%d")

    # Ambil jadwal harian (default UTC+7, ubah time_add jika perlu)
    items = fetch_kbs_schedule(date_str, time_add="-2", language="e")

    for idx, item in enumerate(items):
      hour, minute = map(int, item["time"].split(":"))

      # Tentukan objek datetime acara
      start_dt = datetime(
          current_date.year,
          current_date.month,
          current_date.day,
          hour,
          minute,
      )

      # Jika waktu melompat ke hari berikutnya atau melewati tengah malam
      if idx > 0:
        prev_hour, prev_min = map(int, items[idx - 1]["time"].split(":"))
        if hour < prev_hour:  # Melewati tengah malam
          start_dt += timedelta(days=1)

      # Tentukan waktu selesai (stop time) menggunakan jadwal acara berikutnya atau +1 jam default
      if idx + 1 < len(items):
        next_hour, next_min = map(int, items[idx + 1]["time"].split(":"))
        stop_dt = datetime(
            start_dt.year, start_dt.month, start_dt.day, next_hour, next_min
        )
        if next_hour < hour:  # Lewat tengah malam
          stop_dt += timedelta(days=1)
      else:
        stop_dt = start_dt + timedelta(hours=1)

      # Format XMLTV waktu: YYYYMMDDHHMMSS +0700
      start_formatted = start_dt.strftime("%Y%m%d%H%M%S +0700")
      stop_formatted = stop_dt.strftime("%Y%m%d%H%M%S +0700")

      # Buat elemen <programme>
      programme = ET.SubElement(
          root,
          "programme",
          start=start_formatted,
          stop=stop_formatted,
          channel="KBSWorld.kr",
      )

      # Judul Acara
      title_el = ET.SubElement(programme, "title", lang="en")
      title_el.text = item["title"]

      # Deskripsi Acara
      if item["desc"]:
        desc_el = ET.SubElement(programme, "desc", lang="en")
        desc_el.text = item["desc"]

      # Genre Acara
      if item["genre"]:
        category_el = ET.SubElement(programme, "category", lang="en")
        category_el.text = item["genre"]

  # Simpan ke file XML
  filename = "kbsworld_epg.xml"
  tree = ET.ElementTree(root)

  # Tambahkan deklarasi XML manual agar rapi
  with open(filename, "wb") as f:
    f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    tree.write(f, encoding="utf-8", xml_declaration=False)

  print(f"\nBerhasil! File EPG XML disimpan sebagai '{filename}'")


if __name__ == "__main__":
  # Mengambil EPG untuk rentang 7 hari ke depan
  generate_xmltv(days_to_fetch=7)
