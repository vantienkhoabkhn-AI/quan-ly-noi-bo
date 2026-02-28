import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KẾT NỐI TRỰC TIẾP (Bỏ qua ô Secrets lỗi) ---
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi: {e}")
    st.stop()

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 ĐĂNG NHẬP")
    pwd = st.text_input("Mật khẩu", type="password")
    if st.button("Vào hệ thống"):
        if pwd == "admin123":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# --- 3. GIAO DIỆN SAU ĐĂNG NHẬP ---
with st.sidebar:
    selected = option_menu("Menu", ["Tổng quan", "Nhân sự", "Lịch"])

if selected == "Tổng quan":
    st.header("📊 Hệ thống đã sẵn sàng!")
elif selected == "Nhân sự":
    res = supabase.table("employees").select("*").execute()
    st.table(pd.DataFrame(res.data))
elif selected == "Lịch":
    res_cal = supabase.table("work_schedule").select("*").execute()
    calendar(events=res_cal.data)
