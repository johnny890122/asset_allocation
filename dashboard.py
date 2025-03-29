import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import utils
from sidebar import Sidebar
from body import Body

# Initialize session state
utils.initialize_session_state()
sidebar = Sidebar()
body = Body()

# Page layout
st.set_page_config(layout="wide")

# Sidebar
sidebar_header = sidebar.header

# Sidebar FGI
with st.container():
    fgi_status = sidebar.fgi_status
    conti_exterme_fear = sidebar.conti_exterme_fear
    conti_exterme_greed = sidebar.conti_exterme_greed
    fig_info = sidebar.fgi_info
    fgi_validation = sidebar.validate_fgi(fgi_status, conti_exterme_fear, conti_exterme_greed)

# Sidebar USD/TWD
with st.sidebar:
    usd_twd = sidebar.usd_twd
    usd_twd_info = sidebar.usd_twd_info

# Main content
body_header = body.header
with st.expander("Details"):
    st.write(st.session_state.fgi_mapping)
    threshold_df = utils.threshold_bound()
    st.dataframe(threshold_df)

with st.container():
    portfolio_header = body.portfolio_header
    monthly_capital = body.monthly_capital
    available_cash = body.available_cash

with st.container():
    col1, col2 = body.columns
    with col1:
        editable_table = body.editable_table
    with col2:
        dynamic_table = body.compute_dynamic_df(editable_table)

if fgi_validation:
    cal_button = st.button("Calculate")
    if cal_button:
        st.sidebar.header("⚠️ 重要資訊")
        Caculator = utils.Caculator(
            editable_table.join(dynamic_table),
            monthly_capital, available_cash,
            fgi_status, conti_exterme_fear, conti_exterme_greed
        )

        st.sidebar.write(f"投入比例: {Caculator.input_ratio}%")
        st.sidebar.write(f"當月總投入金額: {Caculator.input_money:,.0f} TWD")
        st.sidebar.write(f"存入現金池金額: {Caculator.cash_pool:,.0f} TWD")

        st.header("Step 2: Portfolio Adjustment")
        st.dataframe(Caculator.output_df)