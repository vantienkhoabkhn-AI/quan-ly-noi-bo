import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. THÔNG TIN KẾT NỐI (ĐÃ KIỂM TRA CHÍNH XÁC)
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"

# Khởi tạo kết nối
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi khởi tạo: {e}")

st.title("🚀 HỆ THỐNG QUẢN LÝ")

# 2. HIỂN THỊ DỮ LIỆU NHÂN VIÊN
st.subheader("👥 Danh sách nhân viên")
try:
    # Lấy dữ liệu từ bảng 'employees'
    res = supabase.table("employees").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    else:
        st.info("Bảng 'employees' hiện đang trống.")
except Exception as e:
    st.warning("⚠️ Không tìm thấy bảng 'employees'. Hãy kiểm tra tên bảng trong Supabase.")

# 3. HIỂN THỊ LỊCH CÔNG TÁC
st.subheader("📅 Lịch công tác")
try:
    # Lấy dữ liệu từ bảng 'work_schedule'
    res_cal = supabase.table("work_schedule").select("*").execute()
    if res_cal.data:
        st.write(res_cal.data)
    else:
        st.info("Bảng 'work_schedule' hiện đang trống.")
except Exception as e:
    st.warning("⚠️ Không tìm thấy bảng 'work_schedule'. Hãy kiểm tra tên bảng trong Supabase.")
