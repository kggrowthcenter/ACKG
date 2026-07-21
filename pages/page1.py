import altair as alt
from datetime import datetime
import pandas as pd
from data_processing import finalize_data
from navigation import make_sidebar
import streamlit as st

st.set_page_config(page_title="User Growth", page_icon="📈")
make_sidebar()

df_ackg, df_creds = finalize_data()
indo_months = {
    "Januari": "1",
    "Februari": "2",
    "Maret": "3",
    "April": "4",
    "Mei": "5",
    "Juni": "6",
    "Juli": "7",
    "Agustus": "8",
    "September": "9",
    "Oktober": "10",
    "November": "11",
    "Desember": "12",
}
df_ackg["Tanggal Pelaksanaan"] = (
    df_ackg["Tanggal Pelaksanaan"]
    .replace(indo_months, regex=True)
    .pipe(pd.to_datetime, format="%d %m %Y", errors="coerce")
)

st.sidebar.header("Filter Options")
selected_subunit = st.sidebar.multiselect(
    "Select SubUnit SAP", options=df_ackg["SubUnit_SAP"].dropna().unique()
)
selected_layer = st.sidebar.multiselect(
    "Select Layer", options=df_ackg["Layer"].dropna().unique()
)

filtered_df = df_ackg.copy()
if selected_subunit:
  filtered_df = filtered_df[
      filtered_df["SubUnit_SAP"].isin(selected_subunit)
  ]
if selected_layer:
  filtered_df = filtered_df[filtered_df["Layer"].isin(selected_layer)]

st.markdown("# 📈 User Growth\n---")

min_value = (
    df_ackg["Tanggal Pelaksanaan"].min().date()
    if not df_ackg["Tanggal Pelaksanaan"].empty
    else datetime.now().date()
)
max_value = (
    df_ackg["Tanggal Pelaksanaan"].max().date()
    if not df_ackg["Tanggal Pelaksanaan"].empty
    else datetime.now().date()
)
if "from_date" not in st.session_state:
  st.session_state.from_date = min_value
if "to_date" not in st.session_state:
  st.session_state.to_date = max_value

st.write("**Choose the data period:**")
col1, col2, col3 = st.columns(3)
if col1.button("Lifetime"):
  st.session_state.from_date, st.session_state.to_date = min_value, max_value
if col2.button("This Year"):
  st.session_state.from_date, st.session_state.to_date = (
      datetime(datetime.now().year, 1, 1).date(),
      min(datetime.now().date(), max_value),
  )
if col3.button("This Month"):
  st.session_state.from_date, st.session_state.to_date = (
      datetime(datetime.now().year, datetime.now().month, 1).date(),
      min(datetime.now().date(), max_value),
  )

from_date, to_date = st.date_input(
    "**Or pick the date manually:**",
    value=[
        max(st.session_state.from_date, min_value),
        min(st.session_state.to_date, max_value),
    ],
    min_value=min_value,
    max_value=max_value,
)
st.session_state.from_date, st.session_state.to_date = from_date, to_date

filtered_df = filtered_df[
    (filtered_df["Tanggal Pelaksanaan"].dt.date >= from_date)
    & (filtered_df["Tanggal Pelaksanaan"].dt.date <= to_date)
]

st.header("Participant Engagement Overview", divider="gray")
st.markdown(
    f"<p style='font-size: 20px;'><strong>Total Evaluated Profiles: <span"
    f" style='color:"
    f" #0056b3;'>{filtered_df['Alamat email'].nunique():,}</span></strong></p>",
    unsafe_allow_html=True,
)

st.subheader("Test Execution Distribution Timeline", divider="gray")
view_granularity = st.radio(
    "View Frequency:",
    ["Daily", "Weekly", "Monthly", "Yearly"],
    horizontal=True,
)
freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME", "Yearly": "YE"}

timeline_counts = (
    filtered_df.groupby(
        pd.Grouper(key="Tanggal Pelaksanaan", freq=freq_map[view_granularity])
    )
    .agg(participants=("Alamat email", "nunique"))
    .reset_index()
)

line_chart = (
    alt.Chart(timeline_counts)
    .mark_line(stroke="steelblue", strokeWidth=2, point=True)
    .encode(
        x=alt.X(
            "Tanggal Pelaksanaan:T",
            title="Assessment Date",
            axis=alt.Axis(format="%Y-%m-%d", labelAngle=-45),
        ),
        y=alt.Y("participants:Q", title="Volume of Unique Profiles"),
        tooltip=[
            alt.Tooltip(
                "Tanggal Pelaksanaan:T", title="Date", format="%Y-%m-%d"
            ),
            alt.Tooltip("participants:Q", title="Participants"),
        ],
    )
    .properties(width=600, height=350)
)
st.altair_chart(line_chart, use_container_width=True)
if st.button("Show Timeline Data"):
  st.dataframe(timeline_counts)

st.subheader("Layer Organizational Distribution", divider="gray")
layer_breakdown = (
    filtered_df.groupby("Layer")
    .agg(participants=("Alamat email", "nunique"))
    .reset_index()
)
layer_chart = (
    alt.Chart(layer_breakdown)
    .mark_bar()
    .encode(
        x=alt.X(
            "Layer:O",
            title="Layer Level",
            axis=alt.Axis(labelAngle=0, labelLimit=0, labelOverlap=False),
        ),
        y=alt.Y("participants:Q", title="Profiles Count"),
        color=alt.Color(
            "Layer:N", title="Layer Level", scale=alt.Scale(scheme="tableau10")
        ),
        tooltip=[
            alt.Tooltip("Layer:N", title="Layer"),
            alt.Tooltip("participants:Q", title="Total"),
        ],
    )
    .properties(width=600, height=350)
)
layered_chart = layer_chart + layer_chart.mark_text(
    align="center", baseline="bottom", fontSize=12, dy=-5, fontWeight="bold"
).encode(text=alt.Text("participants:Q"), color=alt.value("black"))
st.altair_chart(layered_chart, use_container_width=True)
if st.button("Show Layer Data"):
  st.dataframe(layer_breakdown)

st.subheader("SubUnit Organizational Distribution", divider="gray")
subunit_breakdown = (
    filtered_df.groupby("SubUnit_SAP")
    .agg(participants=("Alamat email", "nunique"))
    .reset_index()
)
subunit_chart = (
    alt.Chart(subunit_breakdown)
    .mark_bar()
    .encode(
        x=alt.X(
            "SubUnit_SAP:O",
            title="SubUnit SAP",
            axis=alt.Axis(labelAngle=-45, labelLimit=0, labelOverlap=False),
        ),
        y=alt.Y("participants:Q", title="Profiles Count"),
        color=alt.value("steelblue"),
        tooltip=[
            alt.Tooltip("SubUnit_SAP:O", title="SubUnit SAP"),
            alt.Tooltip("participants:Q", title="Total"),
        ],
    )
    .properties(width=600, height=350)
)
layered_subunit_chart = subunit_chart + subunit_chart.mark_text(
    align="center", baseline="bottom", fontSize=12, dy=-5, fontWeight="bold"
).encode(text=alt.Text("participants:Q"), color=alt.value("black"))
st.altair_chart(layered_subunit_chart, use_container_width=True)
if st.button("Show SubUnit Data"):
  st.dataframe(subunit_breakdown)