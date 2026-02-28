import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. KẾT NỐI (Dán trực tiếp để bỏ qua lỗi Secrets) ---
URL = "https://hbjlexconqjstongvxef.supabase.co"
KEY = "sb_publishable_nK8ZcjV3qb3M9HBm93hUNQ_03TKqBNf"
try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"Lỗi kết nối Supabase: {e}")

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    pw = st.text_input("Mật khẩu quản trị", type="password")
    if st.button("Truy cập"):
        if pw == "admin123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Sai mật khẩu!")
    st.stop()

# --- 3. GIAO DIỆN CHÍNH (SIDEBAR) ---
with st.sidebar:
    # Hiển thị Ảnh Admin (lấy từ bảng settings)
    try:
        res_avatar = supabase.table("settings").select("gh_chu").eq("key", "admin_avatar").single().execute()
        avatar_url = res_avatar.data.get('gh_chu') if res_avatar.data else None
    except: avatar_url = None
    
    st.markdown(f'<div style="text-align:center"><img src="{avatar_url if avatar_url else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"}" style="border-radius:50%; width:100px; height:100px; object-fit:cover"></div>', unsafe_allow_html=True)
    
    # Nút thay ảnh Admin ngay tại Sidebar
    new_admin_img = st.file_uploader("Thay ảnh đại diện", type=['jpg','png'], key="admin_up")
    if new_admin_img:
        path = "admin_avatar.png"
        supabase.storage.from_("images").upload(path, new_admin_img.getvalue(), {"upsert": "true"})
        new_url = supabase.storage.from_("images").get_public_url(path)
        supabase.table("settings").upsert({"key": "admin_avatar", "gh_chu": new_url}).execute()
        st.success("Đã thay ảnh!")
        st.rerun()

    st.divider()
    selected = option_menu("DANH MỤC", ["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"], 
                           icons=['house', 'people', 'calendar-event'], default_index=0)
    if st.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- 4. CÁC TÁC VỤ CHI TIẾT ---

if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh hệ thống")
    c1, c2, c3 = st.columns(3)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        c1.metric("Tổng nhân viên", res_nv.count if res_nv.count else 0)
        c2.metric("Sự kiện lịch", res_lc.count if res_lc.count else 0)
        c3.metric("Hệ thống", "Online")
        
        # Biểu đồ chức vụ
        df_all = pd.DataFrame(supabase.table("employees").select("chu_vu").execute().data)
        if not df_all.empty:
            st.bar_chart(df_all['chu_vu'].value_counts())
    except: st.info("Hãy thêm dữ liệu để hiển thị biểu đồ.")

elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý nhân sự")
    t1, t2 = st.tabs(["➕ Thêm nhân viên", "📑 Danh sách"])
    
    with t1:
        with st.form("add_nv", clear_on_submit=True):
            ten = st.text_input("Họ và tên")
            ms = st.text_input("Mã nhân viên")
            cv = st.selectbox("Chức vụ", ["Trưởng phòng", "Kế toán", "Kỹ thuật", "Nhân viên"])
            file_nv = st.file_uploader("Tải ảnh thẻ", type=['jpg','png'])
            if st.form_submit_button("Lưu vào hệ thống"):
                img_link = ""
                if file_nv:
                    path_nv = f"nv_{ms}.png"
                    supabase.storage.from_("images").upload(path_nv, file_nv.getvalue(), {"upsert": "true"})
                    img_link = supabase.storage.from_("images").get_public_url(path_nv)
                supabase.table("employees").insert({"Ho_Ten": ten, "ma_vn": ms, "chu_vu": cv, "gh_chu": img_link}).execute()
                st.success("Đã thêm thành công!")
                st.rerun()

    with t2:
        res_list = supabase.table("employees").select("*").execute()
        if res_list.data:
            df = pd.DataFrame(res_list.data)
            st.dataframe(df, use_container_width=True)
            for item in res_list.data:
                with st.expander(f"Xem chi tiết: {item['Ho_Ten']}"):
                    col_i, col_t = st.columns([1, 4])
                    if item.get('gh_chu'): col_i.image(item['gh_chu'], width=120)
                    col_t.write(f"Mã NV: {item['ma_vn']} | Chức vụ: {item['chu_vu']}")

elif selected == "Lịch công tác":
    st.header("📅 Lịch công tác")
    col_form, col_cal = st.columns([1, 2])
    with col_form:
        with st.form("cal_form"):
            t = st.text_input("Công việc")
            d = st.date_input("Ngày")
            if st.form_submit_button("Đăng lịch"):
                supabase.table("work_schedule").insert({"title": t, "start": str(d), "end": str(d)}).execute()
                st.rerun()
    with col_cal:
        events = supabase.table("work_schedule").select("*").execute().data
        calendar(events=events if events else [])
