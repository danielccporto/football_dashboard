# utils/data_loader.py
from statsbombpy import sb
import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados_competicoes():
    try:
        competicoes = sb.competitions()
        return competicoes
    except Exception as e:
        st.error(f"Erro ao carregar as competições: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_temporadas(competition_id):
    try:
        # Carregar todas as temporadas disponíveis para a competição
        temporadas = sb.competitions()
        temporadas_filtradas = temporadas[temporadas['competition_id'] == competition_id]
        return temporadas_filtradas[['season_name', 'season_id']].drop_duplicates()
    except Exception as e:
        st.error(f"Erro ao carregar as temporadas para a competição {competition_id}: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_partidas(competition_id, season_id):
    try:
        # A função sb.matches() requer competition_id e season_id
        partidas = sb.matches(competition_id=competition_id, season_id=season_id)
        return partidas[['match_id', 'home_team', 'away_team']]
    except Exception as e:
        st.error(f"Erro ao carregar as partidas para a competição {competition_id} e temporada {season_id}: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_eventos_partida(match_id):
    try:
        eventos = sb.events(match_id=match_id)
        return eventos
    except Exception as e:
        st.error(f"Erro ao carregar eventos da partida {match_id}: {e}")
        return pd.DataFrame()
