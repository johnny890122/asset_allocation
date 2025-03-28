import pandas as pd
from pathlib import Path
import numpy as np

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
    def __init__(self, monthly_input, fgi_index, usd_twd, df):
        self.monthly_input = monthly_input
        self.fgi_index = fgi_index
        self.usd_twd = usd_twd
        self.df = df
    
    def calculate(self):
        self.df = self.df[["代號"]]
        self.df["投入金額(USD)"] = self.monthly_input
        self.df["投入金額"] = self.monthly_input
        self.df["成本"] = 0
        self.df["調整後佔比"] = 0
        return self.df