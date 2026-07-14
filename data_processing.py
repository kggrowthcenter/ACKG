import streamlit as st
import pandas as pd
from fetch_data import fetch_data_ackg, fetch_data_creds

@st.cache_data(ttl=1800)
def fetch_sap_ackg():
    selected_columns = ['Nik', 'SubUnit_SAP', 'Layer', 'Jenis Kelamin_SAP', 'Tanggal lahir_SAP', 'Alamat email', 'Tanggal Pelaksanaan', 'Analytical Thinking', 'Agile Decision Making', 'Business Planning', 'Stakeholder Engagement', 'Culture Building', 'Mindset', 'Creativity Style', 'Humility', 'Grit', 'Curiosity', 'Meaning Making', 'Purpose in Life', 'Overall LEAN', 'Intellectual Curiosity', 'Unconventional Thinking', 'Cognitive Flexibility', 'Open-Mindedness', 'Social Astuteness', 'Social Flexibility', 'Personal Learner', 'Self-Reflection', 'Self-Regulation', 'Overall ELITE', 'Self-Awareness', 'Self- Regulation', 'Motivation', 'Empathy', 'Social Skills', 'Astaka top 1', 'Astaka top 2', 'Astaka top 3', 'Astaka top 4', 'Astaka top 5', 'Astaka top 6', 'Genuine top 1', 'Genuine top 2', 'Genuine top 3', 'Genuine top 4', 'Genuine top 5', 'Genuine top 6', 'Genuine top 7', 'Genuine top 8', 'Genuine top 9']
    df_ackg = fetch_data_ackg(selected_columns)
    return df_ackg

@st.cache_data(ttl=1800)
def finalize_data():
    df_ackg = fetch_sap_ackg()
    df_creds = fetch_data_creds()
    return df_ackg, df_creds