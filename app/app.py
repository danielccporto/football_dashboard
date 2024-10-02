# app.py
import streamlit as st
import pandas as pd
from utils.data_loader import carregar_dados_competicoes, carregar_dados_temporadas, carregar_dados_partidas, carregar_eventos_partida
from utils.visualizations import gerar_mapa_passes, gerar_mapa_chutes, gerar_mapa_calor_passes

st.set_page_config(layout="wide")

@st.cache_data
def carregar_dados_competicoes_cache():
    return carregar_dados_competicoes()

@st.cache_data
def carregar_dados_temporadas_cache(competition_id):
    return carregar_dados_temporadas(competition_id)

@st.cache_data
def carregar_dados_partidas_cache(competition_id, season_id):
    return carregar_dados_partidas(competition_id, season_id)

@st.cache_data
def carregar_eventos_partida_cache(match_id):
    return carregar_eventos_partida(match_id)

if 'competicao_selecionada' not in st.session_state:
    st.session_state['competicao_selecionada'] = None
if 'temporada_selecionada' not in st.session_state:
    st.session_state['temporada_selecionada'] = None
if 'partida_selecionada' not in st.session_state:
    st.session_state['partida_selecionada'] = None

competicoes = carregar_dados_competicoes_cache()
competicao_selecionada = st.sidebar.selectbox(
    "Selecione a Competição",
    competicoes['competition_name'].unique(),
    index=0 if st.session_state['competicao_selecionada'] is None else
    list(competicoes['competition_name'].unique()).index(st.session_state['competicao_selecionada']) if st.session_state['competicao_selecionada'] in list(competicoes['competition_name'].unique()) else 0
)

st.session_state['competicao_selecionada'] = competicao_selecionada

competition_id = competicoes[competicoes['competition_name'] == competicao_selecionada]['competition_id'].values[0]
temporadas = carregar_dados_temporadas_cache(competition_id)
temporada_selecionada = st.sidebar.selectbox(
    "Selecione a Temporada",
    temporadas['season_name'].unique(),
    index=0 if st.session_state['temporada_selecionada'] is None else
    list(temporadas['season_name'].unique()).index(st.session_state['temporada_selecionada']) if st.session_state['temporada_selecionada'] in list(temporadas['season_name'].unique()) else 0
)

st.session_state['temporada_selecionada'] = temporada_selecionada

season_id = temporadas[temporadas['season_name'] == temporada_selecionada]['season_id'].values[0]
partidas = carregar_dados_partidas_cache(competition_id, season_id)
partida_selecionada = st.sidebar.selectbox(
    "Selecione a Partida",
    partidas['match_id'].astype(str) + " - " + partidas['home_team'] + " vs " + partidas['away_team'],
    index=0 if st.session_state['partida_selecionada'] is None else
    list(partidas['match_id'].astype(str) + " - " + partidas['home_team'] + " vs " + partidas['away_team']).index(st.session_state['partida_selecionada']) if st.session_state['partida_selecionada'] in list(partidas['match_id'].astype(str) + " - " + partidas['home_team'] + " vs " + partidas['away_team']) else 0
)

st.session_state['partida_selecionada'] = partida_selecionada

match_id = int(partida_selecionada.split(" - ")[0])
eventos_partida = carregar_eventos_partida_cache(match_id)

st.write(f"### Competição: {competicao_selecionada}")
st.write(f"### Temporada: {temporada_selecionada}")
st.write(f"### Partida: {partida_selecionada}")

st.write("### Estrutura do DataFrame de eventos:")
st.dataframe(eventos_partida.head())  

total_gols = len(eventos_partida[eventos_partida['type'] == 'Goal'])
total_passes = len(eventos_partida[eventos_partida['type'] == 'Pass'])
total_chutes = len(eventos_partida[eventos_partida['type'] == 'Shot'])

col1, col2, col3 = st.columns(3)
col1.metric("Total de Gols", total_gols)
col2.metric("Total de Passes", total_passes)
col3.metric("Total de Chutes", total_chutes)


jogadores = eventos_partida['player'].dropna().unique()
jogador_selecionado = st.sidebar.selectbox("Selecione um Jogador para Análise", jogadores)

tipos_de_eventos = eventos_partida['type'].dropna().unique()
evento_selecionado = st.sidebar.multiselect("Filtrar Eventos por Tipo", tipos_de_eventos, default=tipos_de_eventos)

eventos_filtrados = eventos_partida[
    (eventos_partida['player'] == jogador_selecionado) & 
    (eventos_partida['type'].isin(evento_selecionado))
]

st.write("### Eventos Filtrados do Jogador Selecionado:")
st.dataframe(eventos_filtrados)


csv_data = eventos_filtrados.to_csv(index=False)

st.download_button(
    label="Baixar eventos filtrados como CSV",
    data=csv_data,
    file_name='eventos_filtrados.csv',
    mime='text/csv'
)


passes_sucessos = eventos_filtrados[
    (eventos_filtrados['type'] == 'Pass') & 
    (eventos_filtrados['pass_outcome'].isnull())
]

st.write(f"Total de passes bem-sucedidos encontrados para {jogador_selecionado}: {len(passes_sucessos)}")

st.header("Mapa de Calor dos Passes (Jogador Selecionado)")
fig_calor, _ = gerar_mapa_calor_passes(eventos_filtrados)
st.pyplot(fig_calor)

st.header(f"Mapa de Passes (Jogador: {jogador_selecionado})")
fig_passes, _ = gerar_mapa_passes(passes_sucessos)
st.pyplot(fig_passes)

st.header(f"Mapa de Chutes (Jogador: {jogador_selecionado})")
fig_chutes, _ = gerar_mapa_chutes(eventos_filtrados)
st.pyplot(fig_chutes)
