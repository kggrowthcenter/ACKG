import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data
from datetime import datetime
from navigation import make_sidebar

st.set_page_config(page_title='User Growth', page_icon='📈')
make_sidebar()

df_ackg, df_creds = finalize_data()
indo_months = {'Januari': '1', 'Februari': '2', 'Maret': '3', 'April': '4', 'Mei': '5', 'Juni': '6', 'Juli': '7', 'Agustus': '8', 'September': '9', 'Oktober': '10', 'November': '11', 'Desember': '12'}
df_ackg['Tanggal Pelaksanaan'] = df_ackg['Tanggal Pelaksanaan'].replace(indo_months, regex=True)
df_ackg['Tanggal Pelaksanaan'] = pd.to_datetime(df_ackg['Tanggal Pelaksanaan'], format='%d %m %Y', errors='coerce').dt.date

st.sidebar.header("Filter Options")
selected_subunit = st.sidebar.multiselect("Select SubUnit SAP", options=df_ackg['SubUnit_SAP'].dropna().unique(), default=[])
selected_layer = st.sidebar.multiselect("Select Layer", options=df_ackg['Layer'].dropna().unique(), default=[])

filtered_df = df_ackg.copy()
if selected_subunit:
    filtered_df = filtered_df[filtered_df['SubUnit_SAP'].isin(selected_subunit)]
if selected_layer:
    filtered_df = filtered_df[filtered_df['Layer'].isin(selected_layer)]

st.markdown('# 📈 User Growth\n\nMetrics dashboard broken down by operational hierarchy.')
st.markdown('---')

min_value = df_ackg['Tanggal Pelaksanaan'].min() or datetime.now().date()
max_value = df_ackg['Tanggal Pelaksanaan'].max() or datetime.now().date()

if 'from_date' not in st.session_state: st.session_state.from_date = min_value
if 'to_date' not in st.session_state: st.session_state.to_date = max_value

st.write("**Choose the data period:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Lifetime'):
        st.session_state.from_date, st.session_state.to_date = min_value, max_value
with col2:
    if st.button('This Year'):
        st.session_state.from_date = datetime(datetime.now().year, 1, 1).date()
        st.session_state.to_date = min(datetime.now().date(), max_value)
with col3:
    if st.button('This Month'):
        st.session_state.from_date = datetime(datetime.now().year, datetime.now().month, 1).date()
        st.session_state.to_date = min(datetime.now().date(), max_value)

from_date, to_date = st.date_input('**Or pick the date manually:**', value=[max(st.session_state.from_date, min_value), min(st.session_state.to_date, max_value)], min_value=min_value, max_value=max_value)
st.session_state.from_date, st.session_state.to_date = from_date, to_date

filtered_df = filtered_df[(filtered_df['Tanggal Pelaksanaan'] >= from_date) & (filtered_df['Tanggal Pelaksanaan'] <= to_date)]

st.header('Participant Engagement Overview', divider='gray')
st.markdown(f"<p style='font-size: 20px;'><strong>Total Evaluated Profiles: <span style='color: #0056b3;'>{filtered_df['Alamat email'].nunique():,}</span></strong></p>", unsafe_allow_html=True)

st.subheader('Test Execution Distribution Timeline', divider='gray')
timeline_counts = filtered_df.groupby('Tanggal Pelaksanaan').agg(participants=('Alamat email', 'nunique')).reset_index()
line_chart = alt.Chart(timeline_counts).mark_line(stroke='steelblue', strokeWidth=2).encode(
    x=alt.X('Tanggal Pelaksanaan:T', title='Assessment Date', axis=alt.Axis(format='%Y-%m-%d', labelAngle=-45)),
    y=alt.Y('participants:Q', title='Volume of Unique Profiles'),
    tooltip=[alt.Tooltip('Tanggal Pelaksanaan:T', title='Date', format='%Y-%m-%d'), alt.Tooltip('participants:Q', title='Participants')]
).properties(width=600, height=350)
st.altair_chart(line_chart, use_container_width=True)

st.subheader('SubUnit Organizational Distribution', divider='gray')
subunit_breakdown = filtered_df.groupby(['SubUnit_SAP', 'Layer']).agg(participants=('Alamat email', 'nunique')).reset_index()
bar_chart = alt.Chart(subunit_breakdown).mark_bar().encode(
    x=alt.X('SubUnit_SAP:O', title='SubUnit SAP', axis=alt.Axis(labelAngle=-45)),
    y=alt.Y('participants:Q', title='Profiles Count'),
    color=alt.Color('Layer:N', title='Layer Level', scale=alt.Scale(scheme='tableau10')),
    tooltip=[alt.Tooltip('SubUnit_SAP:O', title='SubUnit SAP'), alt.Tooltip('Layer:N', title='Layer'), alt.Tooltip('participants:Q', title='Total')]
).properties(width=600, height=400)

layered_chart = bar_chart + bar_chart.mark_text(align='center', baseline='middle', fontSize=12, dy=4, fontWeight='bold').encode(text=alt.Text('participants:Q'), color=alt.value('black'))
st.altair_chart(layered_chart, use_container_width=True)

with st.expander("View Table Breakdown"):
    st.dataframe(timeline_counts)
    st.dataframe(subunit_breakdown)