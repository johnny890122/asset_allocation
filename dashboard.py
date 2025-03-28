import streamlit as st
import pandas as pd
from pathlib import Path
import utils

# Page layout
st.set_page_config(layout="wide")
st.title("📊 每月投入金額計算機")
st.session_state.FGI_INDEX = 1
st.session_state.USD_TWD = 33.125
st.session_state.DIR = Path("static")

# Initial data setup
data = utils.get_target_data(st.session_state.DIR/"target.csv")
if "df" not in st.session_state:
    st.session_state.df = data
if "fgi" not in st.session_state:
    st.session_state.fgi = utils.get_fgi_mapping()

with st.expander("Details"):
    st.write(st.session_state.fgi)

# Sidebar
st.sidebar.header("💡 Info.")
fgi_status = st.sidebar.selectbox(
    label="當月市場情緒", options=st.session_state.fgi["市場情緒"].unique(),
    index=st.session_state.FGI_INDEX, key="fgi_status"
)
conti_exterme_fear = st.sidebar.checkbox("連續三個月皆極度恐懼")
conti_exterme_greed = st.sidebar.checkbox("連續三個月皆極度貪婪")

st.sidebar.markdown(
    "[More about the FGI Index](https://edition.cnn.com/markets/fear-and-greed?utm_source=hp)"
)
usd_twd = st.sidebar.number_input(
    label="美金匯率", min_value=0.0, max_value=100.0, 
    step=0.01, value=st.session_state.USD_TWD, key="usd_twd"
)
st.sidebar.markdown(
    "[More about the USD/TWD](https://www.bloomberg.com/quote/USDTWD:CUR)"
)

# Main content
st.header("Input")
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
    dynamic_df = input_df.copy()
    dynamic_df["佔比"] = dynamic_df.apply(
            lambda x: x["庫存金額"] / dynamic_df["庫存金額"].sum() * 100, axis=1
        )
    dynamic_df = dynamic_df[["佔比"]]
    dynamic_df["Notes"] = "123"
    dynamic_df = dynamic_df.style.applymap(utils.color_percentage, subset=["佔比"])

    st.dataframe(
        dynamic_df, 
        hide_index=True,
        use_container_width=True
    )

cal_button = st.button("Calculate")

if cal_button:
    st.sidebar.header("⚠️ 重要資訊")
    Caculator = utils.Caculator(
        monthly_input, liquid_money,
        fgi_status, conti_exterme_fear, conti_exterme_greed
    )

    st.sidebar.write(f"投入比例: {Caculator.input_ratio}%")
    st.sidebar.write(f"當月總投入金額: {Caculator.input_money:,.0f} TWD")
    st.sidebar.write(f"存入現金池金額: {Caculator.cash_pool:,.0f} TWD")
