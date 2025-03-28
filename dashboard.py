import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import utils

# Initialize session state
utils.initialize_session_state()

# Page layout
st.set_page_config(layout="wide")

# Sidebar
# FGI Index
st.sidebar.header("💡 Info.")
fgi_status = st.sidebar.selectbox(
    label="當月市場情緒", options=st.session_state.all_fgi_status,
    index=st.session_state.FGI_INDEX, key="fgi_status"
)
conti_exterme_fear = st.sidebar.checkbox("連續三個月皆極度恐懼")
conti_exterme_greed = st.sidebar.checkbox("連續三個月皆極度貪婪")
st.sidebar.markdown(
    "[More about the FGI Index](https://edition.cnn.com/markets/fear-and-greed?utm_source=hp)"
)

# USD/TWD
usd_twd = st.sidebar.number_input(
    label="美金匯率", min_value=0.0, max_value=100.0, 
    step=0.01, value=st.session_state.USD_TWD, key="usd_twd"
)
st.sidebar.markdown(
    "[More about the USD/TWD](https://www.bloomberg.com/quote/USDTWD:CUR)"
)

# Main content
st.title("💰 投資組合計算器")
with st.expander("Details"):
    st.write(st.session_state.fgi_mapping)

    threshold_df = utils.threshold_bound()
    st.dataframe(threshold_df)

st.header("Step 1: Input the portfolio")
monthly_input = st.number_input(
    label="當月資金", min_value=0, value=40000, 
    step=1000, key="monthly_input"
)

liquid_money = st.number_input(
    label="手頭現金", min_value=0, value=0, 
    step=1000, key="liquid_money"
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
    dynamic_df = utils.compute_dynamic_df(input_df)
    st.dataframe(
        dynamic_df.style.applymap(utils.action_color, subset=["行動"]), 
        use_container_width=True
    )

cal_button = st.button("Calculate")

if cal_button:
    st.sidebar.header("⚠️ 重要資訊")
    Caculator = utils.Caculator(
        input_df.set_index("代號").join(dynamic_df),
        monthly_input, liquid_money,
        fgi_status, conti_exterme_fear, conti_exterme_greed
    )

    st.sidebar.write(f"投入比例: {Caculator.input_ratio}%")
    st.sidebar.write(f"當月總投入金額: {Caculator.input_money:,.0f} TWD")
    st.sidebar.write(f"存入現金池金額: {Caculator.cash_pool:,.0f} TWD")

    st.header("Step 2: Portfolio Adjustment")
    st.dataframe(Caculator.output_df)