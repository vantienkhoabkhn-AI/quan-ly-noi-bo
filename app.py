import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản lý Nội bộ", layout="wide")

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login():
    st.markdown("<h2 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("Mật khẩu truy cập", type="password")
        if st.button("Xác nhận Đăng nhập", use_container_width=True):
            if password == "admin123":
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Mật khẩu sai!")

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --- 3. KẾT NỐI TRỰC TIẾP (BỎ QUA SECRETS) ---
# Dán trực tiếp để dứt điểm lỗi "Thiếu cấu hình Secrets"
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi kết nối Supabase: {e}")
    st.stop()

# --- 4. GIAO DIỆN CHÍNH ---
with st.sidebar:
    selected = option_menu("DANH MỤC", ["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"], 
                         icons=['house', 'people', 'calendar-event'], menu_icon="cast", default_index=0)
    if st.button("🚪 Đăng xuất"):
        st.session_state["logged_in"] = False
        st.rerun()

if selected == "Tổng quan":
    st.title("📊 Báo cáo chung")
    st.info("Hệ thống đã kết nối thành công!")
    
elif selected == "Quản lý Nhân sự":
    st.title("👥 Quản lý Nhân sự")
    res = supabase.table("employees").select("*").execute()
    st.dataframe(pd.DataFrame(res.data), use_container_width=True)

elif selected == "Lịch công tác":
    st.title("📅 Lịch công ty")
    res_cal = supabase.table("work_schedule").select("*").execute()
    calendar(events=res_cal.data if res_cal.data else [])
