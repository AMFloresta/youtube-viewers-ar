"""
analyze.py — Análisis y visualización de viewers en vivo
Ejecutar localmente después de hacer git pull
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import argparse
from pathlib import Path

CHANNELS = ['TodoNoticias', 'C5N', 'CronicaTV', 'LaNacion', 'A24']
COLORS   = ['#e74c3c',      '#3498db', '#27ae60',  '#f39c12',  '#8e44ad']

def load_data(csv_path='data/viewers.csv'):
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.set_index('timestamp').sort_index()
    # Convertir a Buenos Aires (UTC-3)
    df.index = df.index.tz_convert('America/Argentina/Buenos_Aires')
    return df

def plot_series(df, title, output_path):
    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')

    for channel, color in zip(CHANNELS, COLORS):
        if channel in df.columns:
            ax.plot(df.index, df[channel],
                    label=channel, color=color,
                    linewidth=1.5, alpha=0.9)

    # Formato de ejes
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m\n%H:%M'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    ax.set_title(title, fontsize=16, color='white', pad=15)
    ax.set_xlabel('Fecha y hora (ARG)', color='#aaaaaa')
    ax.set_ylabel('Viewers simultáneos', color='#aaaaaa')
    ax.tick_params(colors='#aaaaaa')
    ax.grid(True, alpha=0.2, color='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333355')

    legend = ax.legend(facecolor='#1a1a2e', edgecolor='#333355', labelcolor='white')

    plt.tight_layout()
    Path(output_path).parent.mkdir(exist_ok=True)
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor())
    print(f"📊 Gráfico guardado en {output_path}")
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Análisis de viewers YouTube')
    parser.add_argument('--dias', type=int, default=7,
                        help='Cantidad de días a mostrar (default: 7)')
    parser.add_argument('--output', default='data/viewers_chart.png')
    args = parser.parse_args()

    df = load_data()
    print(f"📁 Total de registros: {len(df):,}")
    print(f"📅 Desde: {df.index.min()}")
    print(f"📅 Hasta: {df.index.max()}")

    # Filtrar por días solicitados
    cutoff = df.index.max() - pd.Timedelta(days=args.dias)
    df_filtered = df[df.index >= cutoff]

    title = f'Viewers en vivo — Noticias Argentina (últimos {args.dias} días)'
    plot_series(df_filtered, title, args.output)

    # Stats básicas
    print("\n📊 Pico máximo de viewers:")
    for channel in CHANNELS:
        if channel in df.columns:
            peak = df[channel].max()
            peak_time = df[channel].idxmax()
            print(f"  {channel}: {int(peak):,} viewers — {peak_time.strftime('%d/%m/%Y %H:%M')}")

if __name__ == '__main__':
    main()
