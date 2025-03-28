import streamlit as st
import pandas as pd
import numpy as np

st.title("📊 Sample Dashboard")

st.sidebar.header("Filters")
num_points = st.sidebar.slider("Number of Data Points", 10, 1000, 200)

# Generate random data
data = pd.DataFrame({
    'x': np.random.randn(num_points),
    'y': np.random.randn(num_points)
})

st.write("### Scatter Plot")
st.scatter_chart(data)

st.write("### Raw Data")
st.dataframe(data)

