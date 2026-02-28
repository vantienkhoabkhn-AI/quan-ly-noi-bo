import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# 1. CẤU HÌNH (Dán cứng URL/Key để bỏ qua lỗi Secrets)
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"
supabase = create_client(URL, KEY)

# 2. KIỂM TRA ĐĂNG NHẬP
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ĐĂNG NHẬP")
    p = st.text_input("Mật khẩu", type="password")
    if st.button("Vào hệ thống"):
        if p == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# 3. GIAO DIỆN CHÍNH
with st.sidebar:
    chon = option_menu("DANH MỤC", ["Nhân sự", "Lịch công tác"], icons=["people", "calendar"])
    if st.button("Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# 4. XỬ LÝ NỘI DUNG
if chon == "Nhân sự":
    st.header("👥 Danh sách nhân viên")
    try:
        data = supabase.table("employees").select("*").execute()
        st.dataframe(pd.DataFrame(data.data), use_container_width=True)
    except:
        st.warning("⚠️ Lỗi: Có thể bạn đặt tên bảng trong Supabase khác với 'employees'.")

elif chon == "Lịch công tác":
    st.header("📅 Lịch công tác")
    try:
        data_cal = supabase.table("work_schedule").select("*").execute()
        calendar(events=data_cal.data if data_cal.data else [])
    except:
        st.warning("⚠️ Lỗi: Có thể bạn đặt tên bảng trong Supabase khác với 'work_schedule'.")
