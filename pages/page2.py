import altair as alt
from datetime import datetime
import pandas as pd
from data_processing import finalize_data
from navigation import make_sidebar
import streamlit as st

st.set_page_config(page_title="Result Summary", page_icon="📊")
make_sidebar()

st.markdown("# 📊 Result Summary")

df_ackg, df_creds = finalize_data()
df_ackg["Tanggal Pelaksanaan"] = (
    df_ackg["Tanggal Pelaksanaan"]
    .pipe(pd.to_datetime, errors="coerce")
)

st.sidebar.header("Filter Options")
df_filtered = df_ackg.copy()

selected_subunits = st.sidebar.multiselect(
    "Select Subunit SAP", options=df_filtered["SubUnit_SAP"].dropna().unique()
)
if selected_subunits:
  df_filtered = df_filtered[df_filtered["SubUnit_SAP"].isin(selected_subunits)]

selected_layers = st.sidebar.multiselect(
    "Select Layer", options=df_filtered["Layer"].dropna().unique()
)
if selected_layers:
  df_filtered = df_filtered[df_filtered["Layer"].isin(selected_layers)]

selected_genders = st.sidebar.multiselect(
    "Select Gender", options=df_filtered["Jenis Kelamin_SAP"].dropna().unique()
)
if selected_genders:
  df_filtered = df_filtered[
      df_filtered["Jenis Kelamin_SAP"].isin(selected_genders)
  ]

min_value = (
    df_filtered["Tanggal Pelaksanaan"].min().date()
    if not df_filtered["Tanggal Pelaksanaan"].empty
    else datetime.now().date()
)
max_value = (
    df_filtered["Tanggal Pelaksanaan"].max().date()
    if not df_filtered["Tanggal Pelaksanaan"].empty
    else datetime.now().date()
)

if "from_date" not in st.session_state:
  st.session_state.from_date, st.session_state.to_date = min_value, max_value

st.write("**Choose the data period:**")
col1, col2, col3 = st.columns(3)
if col1.button("Lifetime"):
  st.session_state.from_date, st.session_state.to_date = min_value, max_value
if col2.button("This Year"):
  current_year = datetime.now().year
  st.session_state.from_date, st.session_state.to_date = (
      datetime(current_year, 1, 1).date(),
      min(datetime.now().date(), max_value),
  )
if col3.button("This Month"):
  current_year, current_month = datetime.now().year, datetime.now().month
  st.session_state.from_date, st.session_state.to_date = (
      datetime(current_year, current_month, 1).date(),
      min(datetime.now().date(), max_value),
  )

from_date, to_date = st.date_input(
    "**Or pick the date manually:**",
    value=(
        max(st.session_state.from_date, min_value),
        min(st.session_state.to_date, max_value),
    ),
    min_value=min_value,
    max_value=max_value,
)
st.session_state.from_date, st.session_state.to_date = from_date, to_date

df_filtered = df_filtered[
    (df_filtered["Tanggal Pelaksanaan"].dt.date >= from_date)
    & (df_filtered["Tanggal Pelaksanaan"].dt.date <= to_date)
]

st.header("Active Learners Overview", divider="gray")
total_participants = df_filtered["Alamat email"].nunique()
st.markdown(
    f"<p style='font-size: 20px; text-align: center;'><strong>Total Evaluated"
    f" Profiles: <span style='color:"
    f" red;'>{total_participants:,}</span></strong></p>",
    unsafe_allow_html=True,
)

test_columns = [
    "Analytical Thinking",
    "Agile Decision Making",
    "Business Planning",
    "Stakeholder Engagement",
    "Culture Building"
]

st.header("Assessment Summary", divider="gray")
selected_test = st.selectbox(
    "Choose Assessment Test",
    options=[col for col in test_columns if col in df_filtered.columns],
)

if selected_test:
  df_test = (
      df_filtered.dropna(subset=[selected_test])
      .groupby(selected_test)
      .agg(participants=("Alamat email", "nunique"))
      .reset_index()
  )

  total_test_users = df_test["participants"].sum()
  df_test["percentage"] = (
      (df_test["participants"] / total_test_users * 100).round(2)
      if total_test_users > 0
      else 0
  )

  chart = (
      alt.Chart(df_test)
      .mark_bar()
      .encode(
          x=alt.X(
              f"{selected_test}:O",
              title="Result Category",
              axis=alt.Axis(labelAngle=-45, labelLimit=0, labelOverlap=False),
          ),
          y=alt.Y("participants:Q", title="Participants"),
          tooltip=[
              alt.Tooltip(f"{selected_test}:O", title="Category"),
              alt.Tooltip("participants:Q", title="Participants"),
              alt.Tooltip("percentage:Q", title="Percentage (%)"),
          ],
      )
      .properties(width=600, height=400)
  )

  layered_chart = chart + chart.mark_text(
      align="center", baseline="bottom", fontSize=12, dy=-5, fontWeight="bold"
  ).encode(text=alt.Text("participants:Q"), color=alt.value("black"))

  st.altair_chart(layered_chart, use_container_width=True)
  if st.button("Show Assessment Data"):
    st.dataframe(df_test)

st.header("Demographic Comparison", divider="gray")
demographic_options = ["SubUnit_SAP", "Layer", "Jenis Kelamin_SAP"]
selected_demo_variable = st.selectbox(
    "Select Demographic Variable", options=demographic_options
)

if selected_test and selected_demo_variable:
  df_demo = (
      df_filtered.dropna(subset=[selected_test, selected_demo_variable])
      .groupby([selected_demo_variable, selected_test])["Alamat email"]
      .nunique()
      .reset_index(name="participants")
  )

  total_per_group = df_demo.groupby(selected_demo_variable)[
      "participants"
  ].transform("sum")
  df_demo["percentage"] = (
      (df_demo["participants"] / total_per_group * 100).round(2)
      if total_per_group.sum() > 0
      else 0
  )

  demo_chart = (
      alt.Chart(df_demo)
      .mark_bar()
      .encode(
          x=alt.X("percentage:Q", title="Percentage (%)"),
          y=alt.Y(
              f"{selected_demo_variable}:N",
              title=selected_demo_variable.replace("_", " "),
              axis=alt.Axis(labelLimit=0, labelOverlap=False),
          ),
          color=alt.Color(f"{selected_test}:N", title="Result Category"),
          tooltip=[
              selected_demo_variable,
              selected_test,
              "participants",
              "percentage",
          ],
      )
      .properties(width=700, height=400)
  )

  st.altair_chart(demo_chart, use_container_width=True)
  if st.button("Show Demographic Comparison Data"):
    st.dataframe(df_demo)