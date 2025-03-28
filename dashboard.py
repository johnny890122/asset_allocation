import streamlit as st
import pandas as pd
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt
import utils

# Page layout
st.set_page_config(layout="wide")
st.title("📊 每月投入金額計算機")

# Initial data setup
DIR = Path("static")
data = utils.get_target_data(DIR/"target.csv")
if "df" not in st.session_state:
    st.session_state.df = data

# Sidebar
st.sidebar.header("資訊")
fgi_index = st.sidebar.number_input(
        label="FGI Index", min_value=0, max_value=100, value=0, key="fgi_index"
    )
usd_twd = st.sidebar.number_input(
        label="USD/TWD", min_value=0, max_value=100, value=0, key="usd_twd"
    )

# Main content
st.header("Input")
monthly_input = st.number_input(
    label="每月投入金額", min_value=0, value=40000, key="monthly_input"
)
col1, col2 = st.columns([1, 1])

with col1:
    input_df = st.data_editor(
            st.session_state.df[["代號", "標的", "目標權重(%)", "庫存金額"]], 
            column_config={
                "庫存金額": st.column_config.NumberColumn("庫存金額", min_value=0)
            },
            disabled=["代號", "標的", "目標權重(%)"],
            use_container_width=True,
            hide_index=True
        )

with col2:
    dynamic_df = input_df.copy()
    dynamic_df["佔比"] = dynamic_df.apply(
            lambda x: x["庫存金額"] / dynamic_df["庫存金額"].sum() * 100, axis=1
        )
    dynamic_df = dynamic_df[["佔比"]]
    dynamic_df["Notes"] = "123"
    dynamic_df = dynamic_df.style.applymap(utils.color_percentage, subset=["佔比"])

    # st.write(dynamic_df)
    st.dataframe(
        dynamic_df, 
        hide_index=True,
        use_container_width=True
    )



cal_button = st.button("Calculate")

if cal_button:
    st.header("Output")

    calculated_df = utils.Caculator(
        monthly_input, fgi_index, usd_twd, input_df
    ).calculate()
    
    st.dataframe(calculated_df, hide_index=True)
    
