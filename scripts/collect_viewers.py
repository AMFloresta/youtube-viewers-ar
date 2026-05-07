import os
import csv
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

BUE = ZoneInfo('America/Argentina/Buenos_Aires')

API_KEY = os.environ['YOUTUBE_API_KEY']
BASE_URL = 'https://www.googleapis.com/youtube/v3'

def get_concurrent_viewers(video_ids):
    """
    Obtiene viewers simultáneos para una lista de video IDs.
    Cuesta solo 1 unidad por llamada (sin importar cuántos IDs).
    """
    if not video_ids:
        return {}

    params = {
        'part': 'liveStreamingDetails',
        'id':   ','.join(video_ids),
        'key':  API_KEY
    }
    r = requests.get(f"{BASE_URL}/videos", params=params)
    data = r.json()

    result = {}
    for item in data.get('items', []):
        video_id = item['id']
        raw = item.get('liveStreamingDetails', {}).get('concurrentViewers')
        result[video_id] = int(raw) if raw else 0

    return result

def main():
    if not os.path.exists('data/current_streams.json'):
        print("❌ No existe data/current_streams.json. Ejecutá refresh_streams.py primero.")
        return

    with open('data/current_streams.json') as f:
        streams = json.load(f)

    # Reunir todos los video IDs válidos
    video_ids = [info['video_id'] for info in streams.values() if info.get('video_id')]

    viewers_map = get_concurrent_viewers(video_ids)

    # Armar la fila con timestamp + viewers por canal
    timestamp = datetime.now(BUE).strftime('%Y-%m-%d %H:%M:%S')
    channel_names = list(streams.keys())
    row = {'timestamp': timestamp}

    for name, info in streams.items():
        vid = info.get('video_id')
        viewers = viewers_map.get(vid, 0) if vid else None
        row[name] = viewers
        status = f"{viewers:,}" if viewers is not None else "sin stream"
        print(f"  {name}: {status} viewers")

    # Guardar en CSV (append)
    os.makedirs('data', exist_ok=True)
    csv_path = 'data/viewers.csv'
    file_exists = os.path.exists(csv_path)
    fieldnames = ['timestamp'] + channel_names

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"\n✅ Datos guardados — {timestamp}")

if __name__ == '__main__':
    main()
