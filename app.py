import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản trị Nội bộ", layout="wide")

# --- 2. KẾT NỐI SUPABASE ---
url = "https://hbjlexconqjstongvxef.supabase.co"
key = "sb_publishable_nK8ZcjV3qb3M9HBm93hUNQ_03TKqBNf"
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Lỗi kết nối Supabase: {e}")

# --- 3. KIỂM TRA ĐĂNG NHẬP (Bảo mật cho Admin) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    pw = st.text_input("Mật khẩu quản trị", type="password")
    if st.button("Truy cập"):
        if pw == "admin123": # Mật khẩu của bạn
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# --- 4. THANH MENU BÊN TRÁI (Tích hợp thay ảnh Admin) ---
with st.sidebar:
    # Lấy ảnh đại diện Admin từ bảng 'settings'
    try:
        res_av = supabase.table("settings").select("gh_chu").eq("key", "admin_avatar").single().execute()
        av_url = res_av.data.get('gh_chu') if res_av.data else "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    except:
        av_url = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

    # Hiển thị ảnh tròn đẹp mắt
    st.markdown(f'<div style="text-align:center"><img src="{av_url}" style="border-radius:50%; width:100px; height:100px; object-fit:cover; border:3px solid #f0f2f6"></div>', unsafe_allow_html=True)
    
    # Nút thay ảnh Admin
    up_admin = st.file_uploader("Thay ảnh đại diện", type=['jpg','png'], key="admin_up")
    if up_admin:
        path = "admin_avatar.png"
        supabase.storage.from_("images").upload(path, up_admin.getvalue(), {"upsert": "true"})
        new_url = supabase.storage.from_("images").get_public_url(path)
        supabase.table("settings").upsert({"key": "admin_avatar", "gh_chu": new_url}).execute()
        st.success("Đã thay ảnh!")
        st.rerun()

    st.title("Phần mềm Quản lý")
    selected = option_menu(
        menu_title="Danh mục chính",
        options=["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"],
        icons=["house", "people", "calendar-event"],
        menu_icon="cast",
        default_index=0,
    )
    if st.button("🚪 Đăng xuất"):
        st.session_state.auth = False
        st.rerun()

# --- 5. XỬ LÝ CHI TIẾT TỪNG TRANG ---

# --- TRANG 1: TỔNG QUAN ---
if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh hệ thống")
    col1, col2, col3 = st.columns(3)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        col1.metric("Tổng nhân viên", f"{res_nv.count if res_nv.count else 0} người")
        col2.metric("Lịch công tác", f"{res_lc.count if res_lc.count else 0} sự kiện")
        col3.metric("Trạng thái", "Trực tuyến", "100%")
        st.divider()
        res_all = supabase.table("employees").select("chuc_vu").execute()
        if res_all.data:
            st.subheader("📈 Cơ cấu chức vụ nhân sự")
            df_chart = pd.DataFrame(res_all.data)
            st.bar_chart(df_chart['chuc_vu'].value_counts())
    except Exception:
        st.info("💡 Mẹo: Hãy nhập dữ liệu để biểu đồ hiện lên nhé!")

# --- TRANG 2: QUẢN LÝ NHÂN SỰ (Tích hợp thêm ảnh thẻ) ---
elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý lý lịch nhân viên")
    tab1, tab2 = st.tabs(["➕ Thêm mới", "📑 Danh sách"])
    
    with tab1:
        with st.form("add_nv", clear_on_submit=True):
            c1, c2 = st.columns(2)
            ten = c1.text_input("Họ và tên")
            ms = c2.text_input("Mã nhân viên")
            cv = st.selectbox("Chức vụ", ["Nhân viên", "Trưởng phòng", "Kế toán", "Kỹ thuật", "Quản lý"])
            f_nv = st.file_uploader("Tải ảnh thẻ nhân viên", type=['jpg','png'])
            
            if st.form_submit_button("Lưu vào hệ thống"):
                if ten and ms:
                    link_nv = ""
                    if f_nv:
                        path_nv = f"nv_{ms}.png"
                        supabase.storage.from_("images").upload(path_nv, f_nv.getvalue(), {"upsert": "true"})
                        link_nv = supabase.storage.from_("images").get_public_url(path_nv)
                    
                    # Lưu vào database (Cột gh_chu dùng để chứa link ảnh)
                    supabase.table("employees").insert({"ho_ten": ten, "ma_nv": ms, "chuc_vu": cv, "gh_chu": link_nv}).execute()
                    st.success(f"Đã thêm thành công nhân viên {ten}")
                    st.rerun()

    with tab2:
        res = supabase.table("employees").select("*").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"👤 {item['ho_ten']} - {item['ma_nv']}"):
                    col_img, col_info = st.columns([1, 4])
                    if item.get('gh_chu'):
                        col_img.image(item['gh_chu'], width=120)
                    col_info.write(f"**Chức vụ:** {item['chuc_vu']}")
                    col_info.write(f"**Mã số:** {item['ma_nv']}")
        else:
            st.info("Chưa có dữ liệu nhân viên.")

# --- TRANG 3: LỊCH CÔNG TÁC ---
elif selected == "Lịch công tác":
    st.header("📅 Hệ thống Lịch công tác")
    col_form, col_cal = st.columns([1, 2])
    with col_form:
        st.subheader("📌 Đăng ký lịch")
        with st.form("work_form", clear_on_submit=True):
            content = st.text_input("Nội dung công việc")
            staff = st.text_input("Người thực hiện")
            place = st.text_input("Địa điểm")
            date_val = st.date_input("Chọn ngày")
            if st.form_submit_button("Xác nhận đăng lịch"):
                if content and staff:
                    new_event = {"title": f"{staff}: {content} ({place})", "start": str(date_val), "end": str(date_val)}
                    supabase.table("work_schedule").insert(new_event).execute()
                    st.success("Đã cập nhật tờ lịch!")
                    st.rerun()
    with col_cal:
        st.subheader("🗓️ Tờ lịch công ty")
        try:
            res_cal = supabase.table("work_schedule").select("*").execute()
            calendar(events=res_cal.data if res_cal.data else [])
        except Exception:
            st.error("⚠️ Lỗi: Kiểm tra lại bảng 'work_schedule' trên Supabase!")
