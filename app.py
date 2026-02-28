import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Kết nối thẳng (Bỏ qua hoàn toàn ô Secrets)
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"
supabase = create_client(URL, KEY)

# 2. Giao diện
st.title("🚀 HỆ THỐNG ĐÃ CHẠY!")

tab1, tab2 = st.tabs(["Nhân sự", "Lịch công tác"])

with tab1:
    st.subheader("Danh sách nhân viên")
    res = supabase.table("employees").select("*").execute()
    st.dataframe(pd.DataFrame(res.data))

with tab2:
    st.subheader("Lịch công tác")
    res_cal = supabase.table("work_schedule").select("*").execute()
    st.write(res_cal.data)
