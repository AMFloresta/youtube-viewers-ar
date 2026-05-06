import os
import json
import requests
from datetime import datetime, timezone

API_KEY = os.environ['YOUTUBE_API_KEY']
BASE_URL = 'https://www.googleapis.com/youtube/v3'

CHANNEL_HANDLES = {
    'TodoNoticias': '@todonoticias',
    'C5N':          '@c5n',
    'CronicaTV':    '@cronicatv',
    'LaNacion':     '@lanacion',
    'A24':          '@A24com'
}

def get_channel_id(handle):
    """Obtiene el ID del canal a partir del handle. Cuesta 1 unidad."""
    params = {'part': 'id', 'forHandle': handle, 'key': API_KEY}
    r = requests.get(f"{BASE_URL}/channels", params=params)
    data = r.json()
    if data.get('items'):
        return data['items'][0]['id']
    print(f"  [!] No se encontró canal para {handle}")
    return None

def get_live_video_id(channel_id):
    """Encuentra el video en vivo actual del canal. Cuesta 100 unidades."""
    params = {
        'part':      'id',
        'channelId': channel_id,
        'eventType': 'live',
        'type':      'video',
        'key':       API_KEY
    }
    r = requests.get(f"{BASE_URL}/search", params=params)
    data = r.json()
    if data.get('items'):
        return data['items'][0]['id']['videoId']
    print(f"  [!] No hay stream en vivo para canal {channel_id}")
    return None

def main():
    # Cargar datos existentes para reutilizar channel_ids
    existing = {}
    os.makedirs('data', exist_ok=True)
    if os.path.exists('data/current_streams.json'):
        with open('data/current_streams.json') as f:
            existing = json.load(f)

    streams = {}
    for name, handle in CHANNEL_HANDLES.items():
        print(f"Procesando {name}...")

        # Reutilizar channel_id si ya lo tenemos (ahorra cuota)
        channel_id = existing.get(name, {}).get('channel_id')
        if not channel_id:
            channel_id = get_channel_id(handle)

        video_id = get_live_video_id(channel_id) if channel_id else None

        streams[name] = {
            'handle':     handle,
            'channel_id': channel_id,
            'video_id':   video_id,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        print(f"  channel={channel_id}, video={video_id}")

    with open('data/current_streams.json', 'w') as f:
        json.dump(streams, f, indent=2, ensure_ascii=False)

    print("\n✅ Streams actualizados correctamente.")

if __name__ == '__main__':
    main()
