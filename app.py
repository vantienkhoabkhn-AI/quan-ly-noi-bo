import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản trị Nội bộ", layout="wide")

# --- 2. KẾT NỐI SUPABASE ---
# Lưu ý: Nếu sau này bạn đổi dự án, hãy cập nhật lại 2 dòng dưới này
url = "https://hbjlexconqjstongvxef.supabase.co"
key = "sb_publishable_nK8ZcjV3qb3M9HBm93hUNQ_03TKqBNf" # Key của bạn
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Lỗi kết nối Supabase: {e}")

# --- 3. THANH MENU BÊN TRÁI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Phần mềm Quản lý")
    selected = option_menu(
        menu_title="Danh mục chính",
        options=["Tổng quan", "Quản lý Nhân sự", "Lịch công tác"],
        icons=["house", "people", "calendar-event"],
        menu_icon="cast",
        default_index=0,
    )

# --- 4. XỬ LÝ CHI TIẾT TỪNG TRANG ---

# --- TRANG 1: TỔNG QUAN ---
if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh hệ thống")
    col1, col2, col3 = st.columns(3)
    
    try:
        # Lấy dữ liệu đếm số lượng
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        
        col1.metric("Tổng nhân viên", f"{res_nv.count if res_nv.count else 0} người")
        col2.metric("Lịch công tác", f"{res_lc.count if res_lc.count else 0} sự kiện")
        col3.metric("Trạng thái", "Trực tuyến", "100%")
        
        st.divider()
        # Biểu đồ thống kê
        res_all = supabase.table("employees").select("chuc_vu").execute()
        if res_all.data:
            st.subheader("📈 Cơ cấu chức vụ nhân sự")
            df_chart = pd.DataFrame(res_all.data)
            st.bar_chart(df_chart['chuc_vu'].value_counts())
    except Exception:
        st.info("💡 Mẹo: Hãy nhập dữ liệu ở các mục khác để biểu đồ hiện lên nhé!")
# --- 1.5. HỆ THỐNG ĐĂNG NHẬP ĐƠN GIẢN ---
def login():
    st.title("🔐 Đăng nhập hệ thống")
    password = st.text_input("Nhập mật khẩu truy cập", type="password")
    if st.button("Đăng nhập"):
        # Bạn hãy đổi 'admin123' thành mật khẩu bạn muốn
        if password == "admin123":
            st.session_state["logged_in"] = True
            st.success("Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("Sai mật khẩu, vui lòng thử lại!")

# Kiểm tra trạng thái đăng nhập
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop() # Dừng toàn bộ code phía dưới nếu chưa đăng nhập thành công

# Nút Đăng xuất ở cuối Sidebar
with st.sidebar:
    if st.button("🚪 Đăng xuất"):
        st.session_state["logged_in"] = False
        st.rerun()
# --- TRANG 2: QUẢN LÝ NHÂN SỰ ---
elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý lý lịch nhân viên")
    tab1, tab2 = st.tabs(["➕ Thêm mới", "📑 Danh sách"])
    
    with tab1:
        with st.form("add_nv", clear_on_submit=True):
            c1, c2 = st.columns(2)
            ten = c1.text_input("Họ và tên")
            ms = c2.text_input("Mã nhân viên")
            cv = st.selectbox("Chức vụ", ["Nhân viên", "Trưởng phòng", "Kế toán", "Kỹ thuật", "Quản lý"])
            if st.form_submit_button("Lưu vào hệ thống"):
                if ten and ms:
                    supabase.table("employees").insert({"ho_ten": ten, "ma_nv": ms, "chuc_vu": cv}).execute()
                    st.success(f"Đã thêm thành công nhân viên {ten}")
                    st.rerun()

    with tab2:
        res = supabase.table("employees").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
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
                    # Chỉnh dữ liệu khớp với định dạng FullCalendar
                    new_event = {
                        "title": f"{staff}: {content} ({place})",
                        "start": str(date_val),
                        "end": str(date_val)
                    }
                    supabase.table("work_schedule").insert(new_event).execute()
                    st.success("Đã cập nhật tờ lịch!")
                    st.rerun()

    with col_cal:
        st.subheader("🗓️ Tờ lịch công ty")
        try:
            res_cal = supabase.table("work_schedule").select("*").execute()
            events = res_cal.data if res_cal.data else []
            
            cal_options = {
                "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth"},
                "initialView": "dayGridMonth",
            }
            calendar(events=events, options=cal_options)
        except Exception:

            st.error("⚠️ Lỗi: Bạn cần tạo bảng 'work_schedule' trên Supabase trước!")
