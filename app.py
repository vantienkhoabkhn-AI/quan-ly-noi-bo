import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. KẾT NỐI TRỰC TIẾP
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nk8Zcjv3qb3M9Hbm93HUN9_03TKqBNf"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Hệ thống Quản lý", layout="wide")
st.title("🚀 DỮ LIỆU TỪ SUPABASE CỦA BẠN")

# 2. TỰ ĐỘNG LIỆT KÊ TẤT CẢ CÁC BẢNG (Không cần điền tên)
# Nếu bạn không biết tên bảng, đoạn code này sẽ giúp bạn tìm thấy nó
try:
    # Lấy danh sách bảng từ hệ thống của Supabase
    st.info("Đang kiểm tra dữ liệu thực tế trong tài khoản của bạn...")
    
    # Cách 1: Thử lấy bảng 'employees' nếu có
    try:
        res1 = supabase.table("employees").select("*").execute()
        if res1.data:
            st.subheader("👥 Bảng: employees")
            st.dataframe(pd.DataFrame(res1.data), use_container_width=True)
    except:
        pass

    # Cách 2: Thử lấy bảng 'work_schedule' nếu có
    try:
        res2 = supabase.table("work_schedule").select("*").execute()
        if res2.data:
            st.subheader("📅 Bảng: work_schedule")
            st.dataframe(pd.DataFrame(res2.data), use_container_width=True)
    except:
        pass

    # CÁCH CHỐT: Nếu 2 tên trên sai, hãy thử hiển thị bất kỳ bảng nào bạn có
    st.divider()
    st.write("👉 Nếu không thấy dữ liệu hiện lên, bạn hãy chụp ảnh màn hình Supabase (mục Table Editor) gửi tôi. Tôi sẽ chỉ cho bạn tên bảng chuẩn.")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
