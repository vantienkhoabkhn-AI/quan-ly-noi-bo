import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. KẾT NỐI (Dán trực tiếp URL/Key)
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"
supabase = create_client(URL, KEY)

st.title("📂 KIỂM TRA DỮ LIỆU HỆ THỐNG")

# 2. ĐĂNG NHẬP ĐƠN GIẢN
if "ok" not in st.session_state:
    st.session_state.ok = False
if not st.session_state.ok:
    p = st.text_input("Mật khẩu", type="password")
    if st.button("Xác nhận"):
        if p == "admin123":
            st.session_state.ok = True
            st.rerun()
    st.stop()

# 3. TỰ ĐỘNG DÒ TÌM BẢNG (Để không bị lỗi "Không tìm thấy bảng")
st.info("Đang kiểm tra các bảng có sẵn trong Supabase của bạn...")

# Bạn hãy thay tên bảng thực tế vào 2 dòng dưới đây nếu bạn biết tên đúng
ten_bang_nhan_vien = "employees" 
ten_bang_lich = "work_schedule"

col1, col2 = st.columns(2)

with col1:
    st.subheader("👥 Dữ liệu Nhân sự")
    try:
        res = supabase.table(ten_bang_nhan_vien).select("*").execute()
        st.dataframe(pd.DataFrame(res.data))
    except Exception as e:
        st.error(f"Không tìm thấy bảng '{ten_bang_nhan_vien}'. Hãy kiểm tra lại tên bảng trên Supabase!")

with col2:
    st.subheader("📅 Lịch công tác")
    try:
        res_cal = supabase.table(ten_bang_lich).select("*").execute()
        st.write(res_cal.data)
    except:
        st.error(f"Không tìm thấy bảng '{ten_bang_lich}'")
