import streamlit as st
import pandas as pd
import utils

class Body():
    def __init__(self):
        pass

    @property
    def header(self):
        label = "💰 投資組合計算器"
        return st.title(label)
    
    @property
    def portfolio_header(self):
        label = "步驟 1: 輸入當前投資組合"
        return st.subheader(label)
    
    @property
    def monthly_capital(self):
        return st.number_input(
            label="當月資金", 
            min_value=0, 
            value=st.session_state.default_monthly_capital, 
            step=1000,
        )
    
    @property
    def available_cash(self):
        return st.number_input(
            label="手頭現金", 
            min_value=0, 
            value=0, 
            step=1000
        )
    
    @property
    def columns(self):
        return st.columns(2)
    
    @property
    def editable_table(self):
        desired_columns = ["標的", "目標權重(%)", "庫存金額"]
        return st.data_editor(
            data=st.session_state.df[desired_columns], 
            column_config={
                "庫存金額": st.column_config.NumberColumn("庫存金額", min_value=0)
            },
            disabled=["代號", "標的", "目標權重(%)", ],
            use_container_width=True
        )

    @staticmethod
    def action_required(row) -> str:
        bound = st.session_state.threshold_bound[row.name]
        if row["ratio"] < bound["lower_bound"]:
            return "加碼"
        elif row["ratio"] > bound["upper_bound"]:
            return "減碼"
        else:
            return "持平"


    @staticmethod
    def compute_dynamic_df(df: pd.DataFrame):
        desired_columns = ["佔比(%)", "行動"]

        dynamic_df = df.copy()
        dynamic_df["ratio"] = dynamic_df["庫存金額"] / dynamic_df["庫存金額"].sum() * 100
        dynamic_df["行動"] = dynamic_df.apply(lambda x: utils.action_required(x), axis=1)
        dynamic_df["佔比(%)"] = dynamic_df["ratio"].apply(lambda x: f"{x:.2f}" if x >= 0 else "-")
        dynamic_df = dynamic_df[desired_columns]

        return st.dataframe(
            data=dynamic_df.style.map(utils.action_color, subset=["行動"]), 
            use_container_width=True
        )




