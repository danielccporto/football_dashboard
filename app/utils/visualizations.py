# utils/visualizations.py
from mplsoccer import Pitch
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

def verificar_coordenadas_validas(coordenadas):
    if not isinstance(coordenadas, list) or len(coordenadas) < 2:
        return False
    if not all(isinstance(c, (int, float)) for c in coordenadas):
        return False
    return True

def gerar_mapa_passes(eventos_partida):
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    if 'location' not in eventos_partida.columns or 'pass_end_location' not in eventos_partida.columns:
        st.error("As colunas 'location' e 'pass_end_location' não estão presentes no DataFrame de eventos.")
        return fig, ax

    if eventos_partida[['location', 'pass_end_location']].dropna().empty:
        st.warning("Nenhum dado de passe encontrado. As colunas 'location' ou 'pass_end_location' estão vazias.")
        return fig, ax

    passes = eventos_partida.dropna(subset=['location', 'pass_end_location'])
    passes = passes[passes['location'].apply(verificar_coordenadas_validas) & passes['pass_end_location'].apply(verificar_coordenadas_validas)]

    if passes.empty:
        st.warning("Nenhum passe válido encontrado para visualização. Verifique os dados carregados.")
        return fig, ax

    pitch.arrows(
        passes['location'].apply(lambda x: x[0]), passes['location'].apply(lambda x: x[1]),
        passes['pass_end_location'].apply(lambda x: x[0]), passes['pass_end_location'].apply(lambda x: x[1]),
        ax=ax, color='blue', width=2, headwidth=10, headlength=10
    )

    return fig, ax


def gerar_mapa_chutes(eventos_partida):
    """Gera um mapa de chutes para uma partida específica."""
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    if 'location' not in eventos_partida.columns:
        st.error("A coluna 'location' não está presente no DataFrame de eventos.")
        return fig, ax

    chutes = eventos_partida[eventos_partida['type'] == 'Shot']
    chutes = chutes.dropna(subset=['location'])
    chutes = chutes[chutes['location'].apply(verificar_coordenadas_validas)]

    if chutes.empty:
        st.warning("Nenhum chute válido encontrado para visualização.")
        return fig, ax

    pitch.scatter(
        chutes['location'].apply(lambda x: x[0]), chutes['location'].apply(lambda x: x[1]),
        ax=ax, c='red', s=100, edgecolor='black', linewidth=1, label='Chutes'
    )

    return fig, ax

def gerar_mapa_calor_passes(eventos_partida):
    """Gera um mapa de calor para os passes."""
    pitch = Pitch(pitch_type='statsbomb', line_zorder=2)
    fig, ax = pitch.draw(figsize=(10, 7))

    if 'location' not in eventos_partida.columns:
        st.error("A coluna 'location' não está presente no DataFrame de eventos.")
        return fig, ax

    passes = eventos_partida[eventos_partida['type'] == 'Pass']
    passes = passes.dropna(subset=['location'])
    passes = passes[passes['location'].apply(verificar_coordenadas_validas)]

    st.write(f"Quantidade de passes válidos para o mapa de calor: {len(passes)}")

    if passes.empty:
        st.warning("Nenhum passe válido encontrado para visualização no mapa de calor.")
        return fig, ax

    x = passes['location'].apply(lambda loc: loc[0]).values
    y = passes['location'].apply(lambda loc: loc[1]).values

    heatmap_stats = pitch.bin_statistic(x, y, statistic='count', bins=(10, 10))  

    pitch.heatmap(heatmap_stats, ax=ax, cmap='coolwarm', alpha=0.6)  
    
    pitch.label_heatmap(heatmap_stats, ax=ax, fontsize=12, color='black', ha='center', va='center')

    return fig, ax

