import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import utils
from sidebar import Sidebar
from body import Body
from db import DBClient

# Page layout
st.set_page_config(layout="wide")

# Initialize session state
utils.initialize_session_state()

# Check MongoDB connection
db_client = DBClient()

sidebar = Sidebar()
body = Body()

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
    col1, col2 = st.columns(2)
    with col1:
        current_portfolio = body.current_portfolio
    with col2:
        monthly_capital = body.monthly_capital
    available_cash = body.available_cash

with st.container():
    col1, col2 = body.columns
    with col1:
        editable_table = body.editable_table
    with col2:
        colored_dynamic_table = body.colored_dynamic_table(editable_table)

if fgi_validation:
    cal_button = st.button("Calculate")
    if cal_button:
        Caculator = utils.Caculator(
            body.df, monthly_capital, available_cash, current_portfolio,
            fgi_status, conti_exterme_fear, conti_exterme_greed
        )

        st.header("Step 2: Portfolio Adjustment")
        st.write("⚠️ 重要資訊")

        if conti_exterme_fear:
            diplay_text = "連續極度恐懼"
        elif conti_exterme_greed:
            diplay_text = "連續極度貪婪"
        else:
            diplay_text = fgi_status

        with st.container():
            st.write(
                f"- 當前市場情緒: {diplay_text}\n"
                f"- 當前美元匯率: {st.session_state.usd_twd}\n"
                f"- 投入比例: {Caculator.input_ratio}%\n"
                f"- 當月總投入金額: {Caculator.money_input + Caculator.to_vgsh:,.0f} TWD\n"
                f"- 存入現金池金額: {Caculator.cash_pool - Caculator.to_vgsh:,.0f} TWD"
            )
            if Caculator.to_vgsh > 0:
                st.write(
                    f"p.s. 原本投入 {Caculator.money_input:,.0f} TWD，其餘 {Caculator.to_vgsh:,.0f} TWD 為機會金溢出至 VGSH"
                )

        st.dataframe(
            data=Caculator.output_df.style.map(utils.action_color, subset=["行動"]), 
            use_container_width=True,
            column_config={
                "投入金額": st.column_config.NumberColumn(format="%.0f"),
                "調整後庫存": st.column_config.NumberColumn(format="%.0f"),
                "調整後佔比(%)": st.column_config.NumberColumn(format="%.2f"),
                "美金計價": st.column_config.NumberColumn(format="%.0f"),
            }
        )