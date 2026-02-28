import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Quản Lý Nội Bộ", layout="wide")

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login():
    st.markdown("<h2 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        password = st.text_input("Mật khẩu truy cập", type="password")
        if st.button("Xác nhận Đăng nhập", use_container_width=True):
            if password == "admin123":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Mật khẩu không chính xác!")

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --- 3. KẾT NỐI TRỰC TIẾP (Bỏ qua Secrets) ---
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi: {e}")
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
with st.sidebar:
    selected = option_menu("Menu", ["Tổng quan", "Nhân sự", "Lịch"], icons=["house", "people", "calendar"])
    if st.button("Đăng xuất"):
        st.session_state["logged_in"] = False
        st.rerun()

if selected == "Tổng quan":
    st.title("📊 Tổng quan")
    st.write("Chào mừng bạn quay lại!")
elif selected == "Nhân sự":
    st.title("👥 Nhân sự")
    res = supabase.table("employees").select("*").execute()
    st.dataframe(pd.DataFrame(res.data))
elif selected == "Lịch":
    st.title("📅 Lịch công tác")
    res_cal = supabase.table("work_schedule").select("*").execute()
    calendar(events=res_cal.data if res_cal.data else [])
