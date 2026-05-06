# 📺 YouTube Viewers — Noticias Argentina

Recolecta automáticamente los viewers en vivo de 5 canales de noticias argentinos cada 15 minutos y los guarda en un CSV para análisis posterior.

## Canales monitoreados
- Todo Noticias (@todonoticias)
- C5N (@c5n)
- Crónica TV (@cronicatv)
- La Nación (@lanacion)
- A24 (@A24com)

## Arquitectura

```
GitHub Actions (cada 6h)  →  refresh_streams.py  →  data/current_streams.json
GitHub Actions (cada 15m) →  collect_viewers.py  →  data/viewers.csv
```

## Setup inicial

### 1. Agregar el secret de YouTube

En GitHub: Settings → Secrets and variables → Actions → New repository secret

- Nombre: `YOUTUBE_API_KEY`
- Valor: tu clave de YouTube Data API v3

### 2. Correr el refresh manualmente la primera vez

Actions → "Refrescar streams en vivo" → Run workflow

Esto crea el archivo `data/current_streams.json` con los IDs de video actuales.

### 3. Verificar que el collect funciona

Actions → "Recolectar viewers cada 15 minutos" → Run workflow

Si todo va bien, verás `data/viewers.csv` en el repo con la primera fila de datos.

A partir de ahí, todo corre solo automáticamente.

## Análisis local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Bajar los datos
git pull

# Ver últimos 7 días
python scripts/analyze.py

# Ver últimas 2 semanas
python scripts/analyze.py --dias 14

# Ver último mes
python scripts/analyze.py --dias 30
```

## Cuota YouTube API (10.000 unidades/día)
- Refresh cada 6h: 5 canales × 100 unidades × 4 = 2.000 unidades/día
- Collect cada 15m: 5 canales × 1 unidad × 96 = 480 unidades/día
- **Total: ~2.500 unidades/día** ✅ (muy por debajo del límite)
