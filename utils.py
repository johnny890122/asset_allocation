import pandas as pd
from pathlib import Path
import numpy as np
import streamlit as st

def initialize_session_state():
    st.session_state.FGI_INDEX = 1
    st.session_state.USD_TWD = 33.125
    st.session_state.DIR = Path("static")

    data = get_target_data(st.session_state.DIR/"target.csv").set_index("代號")
    st.session_state.df = data
    st.session_state.fgi_mapping = get_fgi_mapping()
    st.session_state.all_fgi_status = st.session_state.fgi_mapping["市場情緒"].unique()

    st.session_state.threshold_bound = threshold_bound()
    st.session_state.default_monthly_capital = 40000
    st.session_state.BONDS = ["VGSH"]

def get_fgi_mapping():
    df = pd.read_csv("static/fgi_mapping.csv")
    return df

def get_target_data(dir: Path) -> pd.DataFrame:
    df = pd.read_csv(dir)
    df["庫存金額"] = 0
    return df

# Add color formatting
def action_color(action: str) -> str:
    # assert action in ["加碼", "減碼", "持平"], f"Invalid action: {action}"
    
    if action == "加碼":
        return "background-color: green"
    elif action == "減碼":
        return "background-color: red"

    return "background-color: black"

def action_required(row) -> str:
    bound = st.session_state.threshold_bound[row.name]
    if row["ratio"] < bound["lower"]:
        return "加碼"
    elif row["ratio"] > bound["upper"]:
        return "減碼"
    else:
        return "持平"

def threshold_bound() -> dict:
    df = st.session_state.df.copy()
    df["upper"] = df["目標權重(%)"] + df["閾值(%)"] * df["目標權重(%)"] / 100
    df["lower"] = df["目標權重(%)"] - df["閾值(%)"] * df["目標權重(%)"] / 100

    bounds_dict = {
        index: {"lower": row["lower"], "upper": row["upper"]}
        for index, row in df.iterrows()
    }
    return bounds_dict
class Caculator():
    def __init__(self,
        df: pd.DataFrame, monthly_capital: int, available_cash: int, fgi_status: str, 
        conti_exterme_fear: bool, conti_exterme_greed: bool, 
    ):
        self.df = df
        self.monthly_capital = monthly_capital
        self.available_cash = available_cash
        self.fgi_status = fgi_status
        self.conti_exterme_fear = conti_exterme_fear
        self.conti_exterme_greed = conti_exterme_greed

    @property
    def input_ratio(self):
        fgi_mapping = get_fgi_mapping()
        
        if self.conti_exterme_fear or self.conti_exterme_greed:
            columns = "連續極端的投入比例"
        else:
            columns = "投入比例"

        return fgi_mapping.loc[fgi_mapping["市場情緒"] == self.fgi_status, columns].values[0]

    @property
    def money_input(self) -> int:
        ratio = self.input_ratio
        expected_input_money = self.monthly_capital * ratio / 100

        return min(expected_input_money, self.monthly_capital+self.available_cash)

    @property
    def cash_pool(self) -> int:
        return self.monthly_capital - self.money_input
    
    @property
    def output_df(self):
        assert set(self.df["行動"].unique()) <= {"加碼", "減碼", "持平"}, "行動欄位必須為加碼、減碼或持平"
        df = self.df.copy()

        df["調整前投入金額"] = self.money_input * df["目標權重(%)"] / 100

        df.loc[df["行動"] != "持平", "偏離程度"] = df["佔比(%)"] - df["目標權重(%)"]
        df.loc[df["行動"] == "持平", "偏離程度"] = 0

        df.loc[df["行動"] == "持平", "調整額度"] = 0
        df.loc[df["行動"] != "持平", "調整額度"] = df["庫存金額"].sum() * df["目標權重(%)"] / 100 - df["庫存金額"]
        df.loc[(df["調整額度"].apply(np.abs) > df["調整前投入金額"]) & (df["調整額度"] < 0), "調整額度"] = -df["調整前投入金額"]


        excessive_quota = df["調整額度"].sum()

        df["投入金額"] = df["調整前投入金額"] + df["調整額度"]

        df["投入金額"] -= excessive_quota * df["投入金額"] / df["投入金額"].sum()

        df["調整後庫存金額"] = df["庫存金額"] + df["投入金額"]
        df["ratio"] = df["調整後庫存金額"] / df["調整後庫存金額"].sum() * 100
        df["調整後佔比(%)"] = df["ratio"]
        df["行動"] = df.apply(lambda x: action_required(x), axis=1)

        df["投入金額(USD)"] = df["投入金額"] / st.session_state.USD_TWD

        # Add a row to sum up the columns
        sum_row = df.select_dtypes(include=[np.number]).sum()

        sum_row["行動"] = "-"
        df = pd.concat([df, sum_row.to_frame().T])

        columns = ['投入金額', '投入金額(USD)', '調整後庫存金額', '調整後佔比(%)', '行動']
        return df[columns]
            