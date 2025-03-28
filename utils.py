import pandas as pd
from pathlib import Path
import numpy as np


def get_fgi_mapping():
    df = pd.read_csv("static/fgi_mapping.csv")
    return df

def get_target_data(dir: Path) -> pd.DataFrame:
    df = pd.read_csv(dir)
    df["庫存金額"] = 0
    return df

# Add color formatting
def color_percentage(val):
    if val > 50:
        return "background-color: red"
    elif val > 20:
        return "background-color: green"

    return "background-color: black"

class Caculator():
    def __init__(self, 
        monthly_input: int, liquid_money: int, fgi_status: str, 
        conti_exterme_fear: bool, conti_exterme_greed: bool, 
    ):
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
    def input_money(self):
        ratio = self.input_ratio
        expected_input_money = self.monthly_input * ratio / 100

        return min(expected_input_money, self.monthly_input+self.liquid_money)

    @property
    def cash_pool(self):
        return self.monthly_input - self.input_money
    
    def calculate(self):
        self.df = self.df[["代號"]]
        self.df["投入金額(USD)"] = self.monthly_input
        self.df["投入金額"] = self.monthly_input
        self.df["成本"] = 0
        self.df["調整後佔比"] = 0
        return self.df