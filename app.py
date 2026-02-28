import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KẾT NỐI (Dán trực tiếp để triệt tiêu lỗi Secrets) ---
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nK8ZcjV3qb3M9HBm93hUNQ_03TKqBNf"
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi kết nối: {e}")

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 ĐĂNG NHẬP QUẢN TRỊ")
    pw = st.text_input("Nhập mật khẩu", type="password")
    if st.button("Truy cập hệ thống"):
        if pw == "admin123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Sai mật khẩu!")
    st.stop()

# --- 3. THANH MENU & THAY ẢNH ADMIN ---
with st.sidebar:
    # Lấy ảnh đại diện Admin từ bảng settings
    try:
        res_av = supabase.table("settings").select("gh_chu").eq("key", "admin_avatar").single().execute()
        av_url = res_av.data.get('gh_chu') if res_av.data else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    except: av_url = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    
    st.markdown(f'<div style="text-align:center"><img src="{av_url}" style="border-radius:50%; width:100px; height:100px; object-fit:cover; border:3px solid #f0f2f6"></div>', unsafe_allow_html=True)
    
    # Tác vụ: Thay ảnh Admin
    new_admin_img = st.file_uploader("Thay ảnh đại diện", type=['jpg','png'])
    if new_admin_img:
        path = "admin_avatar.png"
        supabase.storage.from_("images").upload(path, new_admin_img.getvalue(), {"upsert": "true"})
        new_url = supabase.storage.from_("images").get_public_url(path)
        supabase.table("settings").upsert({"key": "admin_avatar", "gh_chu": new_url}).execute()
        st.success("Đã cập nhật ảnh!")
        st.rerun()

    st.divider()
    selected = option_menu("DANH MỤC", ["Tổng quan", "Nhân sự", "Lịch công tác"], 
                           icons=['house', 'people', 'calendar-event'], default_index=0)
    if st.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- 4. CÁC TÁC VỤ CHI TIẾT ---

if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh hệ thống")
    col1, col2 = st.columns(2)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        col1.metric("Tổng nhân viên", res_nv.count if res_nv.count else 0)
        col2.metric("Sự kiện lịch", res_lc.count if res_lc.count else 0)
        
        # Biểu đồ cơ cấu chức vụ
        df_all = pd.DataFrame(supabase.table("employees").select("chu_vu").execute().data)
        if not df_all.empty:
            st.subheader("📈 Thống kê chức vụ")
            st.bar_chart(df_all['chu_vu'].value_counts())
    except: st.info("Chưa có dữ liệu để hiển thị biểu đồ.")

elif selected == "Nhân sự":
    st.header("👥 Quản lý lý lịch nhân viên")
    tab1, tab2 = st.tabs(["➕ Thêm mới", "📑 Danh sách"])
    
    with tab1:
        with st.form("add_nv", clear_on_submit=True):
            ten = st.text_input("Họ tên")
            ms = st.text_input("Mã nhân viên")
            cv = st.selectbox("Chức vụ", ["Trưởng phòng", "Kế toán", "Nhân viên", "Kỹ thuật"])
            f_nv = st.file_uploader("Tải ảnh thẻ", type=['jpg','png'])
            if st.form_submit_button("Lưu vào hệ thống"):
                link_nv = ""
                if f_nv:
                    path_nv = f"nv_{ms}.png"
                    supabase.storage.from_("images").upload(path_nv, f_nv.getvalue(), {"upsert": "true"})
                    link_nv = supabase.storage.from_("images").get_public_url(path_nv)
                supabase.table("employees").insert({"Ho_Ten": ten, "ma_vn": ms, "chu_vu": cv, "gh_chu": link_nv}).execute()
                st.success("Đã thêm thành công!")
                st.rerun()

    with tab2:
        res_list = supabase.table("employees").select("*").execute()
        if res_list.data:
            for item in res_list.data:
                with st.expander(f"👤 {item['Ho_Ten']} - {item['ma_vn']}"):
                    c1, c2 = st.columns([1, 4])
                    if item.get('gh_chu'): c1.image(item['gh_chu'], width=120)
                    c2.write(f"**Chức vụ:** {item['chu_vu']}")
                    c2.write(f"**Mã số:** {item['ma_vn']}")

elif selected == "Lịch công tác":
    st.header("📅 Hệ thống lịch công ty")
    col_f, col_c = st.columns([1, 2])
    with col_f:
        with st.form("cal_form"):
            nd = st.text_input("Nội dung")
            ngay = st.date_input("Chọn ngày")
            if st.form_submit_button("Xác nhận"):
                supabase.table("work_schedule").insert({"title": nd, "start": str(ngay), "end": str(ngay)}).execute()
                st.rerun()
    with col_c:
        data_cal = supabase.table("work_schedule").select("*").execute().data
        calendar(events=data_cal if data_cal else [])
