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
            if password == "admin123": # Mật khẩu của bạn
                st.session_state["logged_in"] = True
                st.rerun()
            else:
                st.error("Mật khẩu không chính xác!")

if not st.session_state["logged_in"]:
    login()
    st.stop()

# --- 3. KẾT NỐI SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("Thiếu cấu hình Secrets (URL/KEY) trên Streamlit Cloud!")
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
        c3.metric("Trạng thái", "Ổn định", "100%")
    except:
        st.info("Chưa có dữ liệu.")

elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý nhân sự")
    name = st.text_input("Họ tên")
    code = st.text_input("Mã NV")
    if st.button("Thêm nhân viên"):
        if name and code:
            supabase.table("employees").insert({"ho_ten": name, "ma_nv": code}).execute()
            st.success("Đã thêm!")
            st.rerun()
    
    res = supabase.table("employees").select("*").execute()
    if res.data:
        st.table(pd.DataFrame(res.data))

elif selected == "Lịch công tác":
    st.header("📅 Lịch công tác")
    col_f, col_c = st.columns([1, 2])
    with col_f:
        with st.form("f_l"):
            t = st.text_input("Nội dung")
            d = st.date_input("Ngày")
            if st.form_submit_button("Lưu"):
                supabase.table("work_schedule").insert({"title": t, "start": str(d), "end": str(d)}).execute()
                st.rerun()
    with col_c:
        res_cal = supabase.table("work_schedule").select("*").execute()
        calendar(events=res_cal.data if res_cal.data else [])
