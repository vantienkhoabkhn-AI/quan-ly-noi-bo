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
            if password == "admin123": # Mật khẩu của bạn
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Mật khẩu không chính xác!")

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --- 3. KẾT NỐI SUPABASE (Dán trực tiếp để chắc chắn chạy được) ---
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi kết nối cơ sở dữ liệu: {e}")
    st.stop()

# --- 4. THANH MENU SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛠 QUẢN TRỊ")
    selected = option_menu(
        menu_title="Menu Chính",
        options=["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"],
        icons=["house", "people", "calendar-event"],
        menu_icon="cast",
        default_index=0,
    )
    st.divider()
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# --- 5. XỬ LÝ NỘI DUNG ---

# TRANG 1: TỔNG QUAN
if selected == "Tổng quan":
    st.title("📊 Báo cáo hệ thống")
    c1, c2 = st.columns(2)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        c1.metric("Tổng nhân sự", f"{res_nv.count if res_nv.count else 0}")
        c2.metric("Số lịch công tác", f"{res_lc.count if res_lc.count else 0}")
    except:
        st.info("Đang cập nhật dữ liệu...")

# TRANG 2: NHÂN SỰ
elif selected == "Quản lý Nhân sự":
    st.title("👥 Danh sách nhân viên")
    with st.expander("➕ Thêm nhân viên mới"):
        with st.form("nv_form", clear_on_submit=True):
            n = st.text_input("Họ tên")
            m = st.text_input("Mã số")
            if st.form_submit_button("Lưu"):
                if n and m:
                    supabase.table("employees").insert({"ho_ten": n, "ma_nv": m}).execute()
                    st.success("Đã thêm!")
                    st.rerun()
    
    res = supabase.table("employees").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

# TRANG 3: LỊCH CÔNG TÁC
elif selected == "Lịch công tác":
    st.title("📅 Lịch công tác công ty")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        with st.form("lc_form", clear_on_submit=True):
            job = st.text_input("Nội dung/Người đi")
            date = st.date_input("Ngày thực hiện")
            if st.form_submit_button("Đăng ký lịch"):
                if job:
                    supabase.table("work_schedule").insert({"title": job, "start": str(date), "end": str(date)}).execute()
                    st.success("Đã lưu lịch!")
                    st.rerun()
    with col_b:
        try:
            res_cal = supabase.table("work_schedule").select("*").execute()
            calendar(events=res_cal.data if res_cal.data else [])
        except:
            st.error("Không thể hiển thị lịch.")
