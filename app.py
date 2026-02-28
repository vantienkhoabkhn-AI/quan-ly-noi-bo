import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản trị Nội bộ", layout="wide")

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

def login():
    st.markdown("<h2 style='text-align: center;'>🔐 ĐĂNG NHẬP HỆ THỐNG</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("Mật khẩu truy cập", type="password")
        if st.button("Xác nhận Đăng nhập", use_container_width=True):
            if password == "admin123": # Bạn có thể đổi mật khẩu tại đây
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Mật khẩu không chính xác!")

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --- 3. KẾT NỐI SUPABASE (Dán trực tiếp để tránh lỗi Secrets) ---
url = "https://hbjlexconqjstongvxef.supabase.co"
key = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf" 

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Lỗi kết nối: {e}")
    st.stop()

# --- 4. THANH MENU SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    selected = option_menu(
        menu_title="DANH MỤC CHÍNH",
        options=["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"],
        icons=["grid-1x2", "people", "calendar3"],
        default_index=0,
    )
    st.divider()
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# --- 5. XỬ LÝ NỘI DUNG ---
if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh hệ thống")
    c1, c2, c3 = st.columns(3)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        c1.metric("Tổng nhân viên", f"{res_nv.count if res_nv.count else 0}")
        c2.metric("Lịch tuần này", f"{res_lc.count if res_lc.count else 0}")
        c3.metric("Kết nối", "Ổn định", "100%")
    except:
        st.info("Chưa có dữ liệu báo cáo.")

elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý lý lịch nhân viên")
    with st.form("add_nv", clear_on_submit=True):
        name = st.text_input("Họ và tên")
        code = st.text_input("Mã nhân viên")
        if st.form_submit_button("Thêm mới"):
            if name and code:
                supabase.table("employees").insert({"ho_ten": name, "ma_nv": code}).execute()
                st.success("Đã thêm thành công!")
                st.rerun()
    
    res = supabase.table("employees").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

elif selected == "Lịch công tác":
    st.header("📅 Lịch công tác công ty")
    col_f, col_c = st.columns([1, 2])
    with col_f:
        with st.form("add_event", clear_on_submit=True):
            t = st.text_input("Nội dung công việc")
            d = st.date_input("Chọn ngày")
            if st.form_submit_button("Đăng lịch"):
                if t:
                    supabase.table("work_schedule").insert({"title": t, "start": str(d), "end": str(d)}).execute()
                    st.success("Đã lưu!")
                    st.rerun()
    with col_c:
        try:
            res_cal = supabase.table("work_schedule").select("*").execute()
            calendar(events=res_cal.data if res_cal.data else [])
        except:
            st.error("Lỗi hiển thị lịch.")
