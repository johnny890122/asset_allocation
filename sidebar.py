import streamlit as st
import requests
from datetime import datetime, timedelta, timezone
from db import DBClient

class Sidebar():
    def __init__(self):
        self.db_client = DBClient()
        self._get_exchange_rate()

    def _get_exchange_rate(self):
        """
        Fetches the exchange rate, prioritizing today's rate from the DB,
        then falling back to an API call, and finally to the latest in DB.
        """
        today_str = datetime.now(timezone.utc).strftime("%Y/%m/%d")

        # 1. Check for today's rate in the database
        rate_data = self.db_client.get_currency_rate_by_date(today_str)

        if rate_data:
            st.session_state.USD_TWD = rate_data['rate']
            st.session_state.USD_TWD_DATE = rate_data['date']
            return

        # 2. If not found, call the API
        try:
            response = requests.get("https://open.er-api.com/v6/latest/USD")
            print("Fetching exchange rate from API...")
            response.raise_for_status()  # Raise an exception for bad status codes
            api_data = response.json()

            if api_data.get("result") == "success":
                rate = api_data['rates']['TWD']
                timestamp = api_data['time_last_update_unix']
                date_str = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y/%m/%d")
                
                # Save to database
                self.db_client.insert_currency_rate("USD", "TWD", date_str, rate)
                
                st.session_state.USD_TWD = rate
                st.session_state.USD_TWD_DATE = date_str
                return

        except requests.exceptions.RequestException as e:
            st.sidebar.warning(f"API call failed: {e}. Using latest available rate.")

        # 3. If API fails or returns an error, use the latest rate from the DB
        latest_rate_data = self.db_client.get_latest_currency_rate()
        if latest_rate_data:
            st.session_state.USD_TWD = latest_rate_data['rate']
            st.session_state.USD_TWD_DATE = latest_rate_data['date']
        else:
            # Fallback if DB is also empty
            st.sidebar.error("Could not retrieve exchange rate from any source.")
            st.session_state.USD_TWD = 30.0  # Default fallback
            st.session_state.USD_TWD_DATE = None

    @property
    def header(self):
        label = "💡 Info."
        return st.sidebar.header(label)
    
    @property
    def fgi_status(self):
        return st.sidebar.selectbox(
            label="當月市場情緒", 
            options=st.session_state.all_fgi_status,
            index=st.session_state.FGI_INDEX,
            key="fgi_status",
        )
    
    @property
    def conti_exterme_fear(self):
        label = "連續三個月皆極度恐懼"
        return st.sidebar.checkbox(label, key="conti_exterme_fear")
    
    @property 
    def conti_exterme_greed(self):
        label = "連續三個月皆極度貪婪"
        return st.sidebar.checkbox(label, key="conti_exterme_greed")

    @property
    def fgi_info(self):
        info = "[More about the FGI Index](https://edition.cnn.com/markets/fear-and-greed?utm_source=hp)"
        return st.sidebar.markdown(info)
    
    @staticmethod
    def validate_fgi(
        fgi_status: str, conti_exterme_fear: bool, conti_exterme_greed: bool
    ) -> bool:
        if fgi_status not in ["極度恐懼", "恐懼", "中性", "貪婪", "極度貪婪"]:
            st.sidebar.error("無效的市場情緒選擇，請重新選擇。")
            return False
        if conti_exterme_fear and conti_exterme_greed:
            st.sidebar.error("連續極度恐懼和極度貪婪不能同時選擇。")
            return False
        if conti_exterme_fear and fgi_status != "極度恐懼":
            st.sidebar.error("當前市場情緒必須為極度恐懼。")
            return False
        if conti_exterme_greed and fgi_status != "極度貪婪":
            st.sidebar.error("當前市場情緒必須為極度貪婪。")
            return False
        return True

    @property
    def usd_twd(self):
        return st.sidebar.number_input(
            label="美金匯率", min_value=0.0, max_value=100.0, 
            step=0.01, value=st.session_state.USD_TWD, key="usd_twd"
        )

    @property
    def usd_twd_info(self):

        if st.session_state.USD_TWD_DATE:
            label = f"(Date: {st.session_state.USD_TWD_DATE})"
        else:
            label = f"(Date: N/A)"

        return st.sidebar.markdown(label)