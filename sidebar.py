import streamlit as st

class Sidebar():
    def __init__(self):
        pass

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
        info = "[More about the USD/TWD](https://www.bloomberg.com/quote/USDTWD:CUR)"
        return st.sidebar.markdown(info)