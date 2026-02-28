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
    st.error(f"Lỗi kết nối: {e}")

# --- 3. KIỂM TRA ĐĂNG NHẬP ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 ĐĂNG NHẬP")
    p = st.text_input("Mật khẩu", type="password")
    if st.button("Vào hệ thống"):
        if p == "admin123":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# --- 4. MENU BÊN TRÁI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    selected = option_menu(
        menu_title="DANH MỤC",
        options=["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"],
        icons=["house", "people", "calendar-event"],
        default_index=0,
    )
    if st.button("Đăng xuất"):
        st.session_state["authenticated"] = False
        st.rerun()

# --- 5. XỬ LÝ CHI TIẾT ---

if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh")
    col1, col2 = st.columns(2)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        col1.metric("Tổng nhân viên", f"{res_nv.count if res_nv.count else 0}")
        col2.metric("Lịch sắp tới", f"{res_lc.count if res_lc.count else 0}")
        
        # Biểu đồ chức vụ
        res_all = supabase.table("employees").select("chu_vu").execute()
        if res_all.data:
            df_chart = pd.DataFrame(res_all.data)
            st.bar_chart(df_chart['chu_vu'].value_counts())
    except:
        st.info("Chưa có dữ liệu để hiển thị báo cáo.")

elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý lý lịch nhân viên")
    t1, t2 = st.tabs(["➕ Thêm mới", "📑 Danh sách"])
    
    with t1:
        with st.form("add_nv", clear_on_submit=True):
            c1, c2 = st.columns(2)
            ten = c1.text_input("Họ và tên")
            ms = c2.text_input("Mã nhân viên")
            cv = st.selectbox("Chức vụ", ["Nhân viên", "Trưởng phòng", "Kế toán", "Kỹ thuật", "Quản lý"])
            anh = st.file_uploader("Chọn ảnh thẻ", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("Lưu vào hệ thống"):
                if ten and ms:
                    url_anh = ""
                    if anh:
                        # Tải ảnh lên Supabase Storage (Bucket: images)
                        path = f"nhan_vien/{ms}.png"
                        supabase.storage.from_("images").upload(path, anh.getvalue(), {"content-type": "image/png"})
                        url_anh = supabase.storage.from_("images").get_public_url(path)
                    
                    # Lưu dữ liệu vào bảng (Cột gh_chu dùng lưu link ảnh)
                    supabase.table("employees").insert({
                        "Ho_Ten": ten, "ma_vn": ms, "chu_vu": cv, "gh_chu": url_anh
                    }).execute()
                    st.success("Đã thêm thành công!")
                    st.rerun()

    with t2:
        res = supabase.table("employees").select("*").execute()
        if res.data:
            for item in res.data:
                with st.expander(f"{item['Ho_Ten']} - {item['ma_vn']}"):
                    col_a, col_b = st.columns([1, 4])
                    if item.get('gh_chu'):
                        col_a.image(item['gh_chu'], width=100)
                    col_b.write(f"Chức vụ: {item['chu_vu']}")
                    col_b.write(f"Ghi chú: {item.get('gh_chu', 'Không có ảnh')}")
        else:
            st.info("Danh sách trống.")

elif selected == "Lịch công tác":
    st.header("📅 Hệ thống Lịch công tác")
    col_f, col_c = st.columns([1, 2])
    
    with col_f:
        with st.form("work_form", clear_on_submit=True):
            content = st.text_input("Nội dung")
            staff = st.text_input("Người thực hiện")
            date_val = st.date_input("Ngày")
            if st.form_submit_button("Xác nhận"):
                new_event = {"title": f"{staff}: {content}", "start": str(date_val), "end": str(date_val)}
                supabase.table("work_schedule").insert(new_event).execute()
                st.success("Đã thêm lịch!")
                st.rerun()

    with col_c:
        res_cal = supabase.table("work_schedule").select("*").execute()
        calendar(events=res_cal.data if res_cal.data else [], options={"initialView": "dayGridMonth"})
