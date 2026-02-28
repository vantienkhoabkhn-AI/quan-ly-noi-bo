import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. KẾT NỐI (Dán trực tiếp URL và Key của bạn)
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"
supabase = create_client(URL, KEY)

st.title("🚀 HỆ THỐNG QUẢN LÝ")

# 2. KIỂM TRA DỮ LIỆU NHÂN VIÊN
st.subheader("👥 Danh sách nhân viên")
try:
    # Thử gọi bảng 'employees', nếu lỗi sẽ báo để bạn sửa tên bảng
    res = supabase.table("employees").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    else:
        st.info("Bảng nhân viên hiện đang trống.")
except Exception as e:
    st.warning(f"Cần kiểm tra lại tên bảng 'employees' trong Supabase. Lỗi: {e}")

# 3. KIỂM TRA DỮ LIỆU LỊCH
st.subheader("📅 Lịch công tác")
try:
    res_cal = supabase.table("work_schedule").select("*").execute()
    st.write(res_cal.data)
except Exception as e:
    st.warning(f"Cần kiểm tra lại tên bảng 'work_schedule' trong Supabase. Lỗi: {e}")
