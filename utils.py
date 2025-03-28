import pandas as pd
from pathlib import Path
import numpy as np
import streamlit as st

def initialize_session_state():
    st.session_state.FGI_INDEX = 1
    st.session_state.USD_TWD = 33.125
    st.session_state.DIR = Path("static")

    data = get_target_data(st.session_state.DIR/"target.csv")
    st.session_state.df = data
    st.session_state.fgi_mapping = get_fgi_mapping()
    st.session_state.all_fgi_status = st.session_state.fgi_mapping["市場情緒"].unique()

    st.session_state.threshold_bound = threshold_bound()

def get_fgi_mapping():
    df = pd.read_csv("static/fgi_mapping.csv")
    return df

def get_target_data(dir: Path) -> pd.DataFrame:
    df = pd.read_csv(dir)
    df["庫存金額"] = 0
    return df

# Add color formatting
def action_color(action: str) -> str:
    assert action in ["加碼", "減碼", "持平"], f"Invalid action: {action}"
    
    if action == "加碼":
        return "background-color: green"
    elif action == "減碼":
        return "background-color: red"

    return "background-color: black"

def action_required(row) -> str:
    lower_bound = st.session_state.threshold_bound[row["代號"]]["lower_bound"]
    upper_bound = st.session_state.threshold_bound[row["代號"]]["upper_bound"]
    if row["佔比"] < lower_bound:
        return "加碼"
    elif row["佔比"] > upper_bound:
        return "減碼"
    else:
        return "持平"

def threshold_bound() -> dict:
    df = st.session_state.df.copy()
    df["upper_bound"] = df["目標權重(%)"] + df["閾值(%)"] * df["目標權重(%)"] / 100
    df["lower_bound"] = df["目標權重(%)"] - df["閾值(%)"] * df["目標權重(%)"] / 100

    bounds_dict = {
        row["代號"]: {"lower_bound": row["lower_bound"], "upper_bound": row["upper_bound"]}
        for _, row in df.iterrows()
    }

    return bounds_dict

def compute_dynamic_df(input_df: pd.DataFrame) -> pd.DataFrame:
    dynamic_df = input_df.copy()
    dynamic_df["佔比"] = dynamic_df["庫存金額"] / dynamic_df["庫存金額"].sum() * 100
    dynamic_df["行動"] = dynamic_df.apply(lambda x: action_required(x), axis=1)
    dynamic_df["佔比(%)"] = dynamic_df["佔比"].apply(lambda x: f"{x:.2f}%" if x >= 0 else "-")
    dynamic_df = dynamic_df.set_index("代號")[["佔比(%)", "行動"]]

    return dynamic_df


# TODO:
def error_message(message: str):
    pass

class Caculator():
    def __init__(self,
        df: pd.DataFrame, monthly_input: int, liquid_money: int, fgi_status: str, 
        conti_exterme_fear: bool, conti_exterme_greed: bool, 
    ):
        self.df = df
        self.monthly_input = monthly_input
        self.liquid_money = liquid_money
        self.fgi_status = fgi_status
        self.conti_exterme_fear = conti_exterme_fear
        self.conti_exterme_greed = conti_exterme_greed

    @property
    def input_ratio(self):
        assert self.fgi_status in ["極度恐懼", "恐懼", "中性", "貪婪", "極度貪婪"]
        assert not (self.conti_exterme_fear and self.conti_exterme_greed), "Both conti_exterme_fear and conti_exterme_greed cannot be True at the same time."
        assert not (self.conti_exterme_fear and self.fgi_status != "極度恐懼"), "conti_exterme_fear can only be True when fgi_status is 極度恐懼."
        assert not (self.conti_exterme_greed and self.fgi_status != "極度貪婪"), "conti_exterme_greed can only be True when fgi_status is 極度貪婪."

        fgi_mapping = get_fgi_mapping()
        
        if self.conti_exterme_fear or self.conti_exterme_greed:
            columns = "連續極端的投入比例"
        else:
            columns = "投入比例"

        return fgi_mapping.loc[fgi_mapping["市場情緒"] == self.fgi_status, columns].values[0]

    @property
    def input_money(self) -> int:
        ratio = self.input_ratio
        expected_input_money = self.monthly_input * ratio / 100

        return min(expected_input_money, self.monthly_input+self.liquid_money)

    @property
    def cash_pool(self) -> int:
        return self.monthly_input - self.input_money
    
    @property
    def output_df(self):
        # TODO: Implement the logic to calculate the output DataFrame
        output_df = self.df.copy()
        output_df["投入金額(USD)"] = self.monthly_input
        output_df["投入金額"] = self.monthly_input
        output_df["成本"] = 0
        output_df["調整後佔比"] = 0
        return output_df