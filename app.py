import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Hệ thống Quản trị Nội bộ", layout="wide")

url = "https://hbjlexconqjstongvxef.supabase.co"
key = "sb_publishable_nK8ZcjV3qb3M9HBm93hUNQ_03TKqBNf"
supabase: Client = create_client(url, key)

# --- 2. ĐĂNG NHẬP ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    pw = st.text_input("Mật khẩu", type="password")
    if st.button("Vào quản trị"):
        if pw == "admin123":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. MENU ---
with st.sidebar:
    st.title("🏢 QUẢN TRỊ")
    selected = option_menu(
        menu_title=None,
        options=["Tổng quan", "Nhân sự", "Lịch công tác", "Kho hình ảnh"],
        icons=["house", "people", "calendar", "image"],
        default_index=0,
    )
    if st.button("Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- 4. XỬ LÝ CÁC TRANG ---

if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh")
    c1, c2 = st.columns(2)
    res_nv = supabase.table("employees").select("id", count="exact").execute()
    c1.metric("Tổng nhân sự", f"{res_nv.count} người")
    c2.metric("Trạng thái", "Ổn định")

elif selected == "Nhân sự":
    st.header("👥 Quản lý nhân sự")
    tab1, tab2 = st.tabs(["Thêm mới", "Danh sách"])
    
    with tab1:
        with st.form("form_nv"):
            ten = st.text_input("Họ tên")
            ms = st.text_input("Mã nhân viên")
            file_anh = st.file_uploader("Tải lên ảnh thẻ", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("Lưu nhân sự"):
                img_url = ""
                if file_anh:
                    # Tự động đẩy ảnh lên Supabase Storage
                    path = f"avatar/{ms}.png"
                    supabase.storage.from_("images").upload(path, file_anh.getvalue())
                    img_url = supabase.storage.from_("images").get_public_url(path)
                
                supabase.table("employees").insert({
                    "Ho_Ten": ten, "ma_vn": ms, "gh_chu": img_url
                }).execute()
                st.success("Đã thêm nhân sự và lưu ảnh!")

    with tab2:
        data = supabase.table("employees").select("*").execute()
        st.dataframe(pd.DataFrame(data.data))

elif selected == "Kho hình ảnh":
    st.header("🖼️ Thư mục lưu trữ hình ảnh")
    # Liệt kê ảnh từ Supabase Storage
    files = supabase.storage.from_("images").list("avatar")
    if files:
        cols = st.columns(4)
        for i, f in enumerate(files):
            url_img = supabase.storage.from_("images").get_public_url(f"avatar/{f['name']}")
            cols[i % 4].image(url_img, caption=f['name'])
    else:
        st.info("Chưa có hình ảnh nào trong kho.")

elif selected == "Lịch công tác":
    # Giữ nguyên phần lịch của bạn
    st.header("📅 Lịch công tác")
    res_cal = supabase.table("work_schedule").select("*").execute()
    calendar(events=res_cal.data if res_cal.data else [])
