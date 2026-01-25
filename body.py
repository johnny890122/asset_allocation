import streamlit as st
import pandas as pd
import utils

class Body():
    def __init__(self):
        self.__df = None

    @property
    def df(self):
        return self.__df
    
    @df.setter
    def df(self, df: pd.DataFrame):
        assert isinstance(df, pd.DataFrame), "df must be a pandas DataFrame"
        self.__df = df

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
            label="當月投入資金", 
            min_value=0, 
            value=st.session_state.default_monthly_capital, 
            step=1000,
        )

    @property
    def current_portfolio(self):
        return st.number_input(
            label="當前投資組合", 
            min_value=0, 
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

    def compute_dynamic_df(self, editable_table: pd.DataFrame) -> pd.DataFrame:
        desired_columns = ["佔比(%)", "行動"]
        dynamic_df = editable_table.copy()
        dynamic_df["ratio"] = dynamic_df["庫存金額"] / dynamic_df["庫存金額"].sum() * 100
        dynamic_df["行動"] = dynamic_df.apply(lambda x: utils.action_required(x), axis=1)
        dynamic_df["佔比(%)"] = dynamic_df["ratio"]


        return dynamic_df[desired_columns]
    
    def colored_dynamic_table(self, editable_table: pd.DataFrame):
        dynamic_table = self.compute_dynamic_df(editable_table)

        # set main df
        self.df = editable_table.join(dynamic_table)
        
        return st.dataframe(
            data=dynamic_table.style.map(utils.action_color, subset=["行動"]), 
            use_container_width=True,
            column_config={
                "佔比(%)": st.column_config.NumberColumn(format="%.2f")
            }
        )
