import streamlit as st
from streamlit_option_menu import option_menu
from supabase import create_client, Client
import pandas as pd
from streamlit_calendar import calendar

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Hệ thống Quản trị Nội bộ", layout="wide")

url = "https://hbjlexconqjstongvxef.supabase.co"
key = "sb_publishable_nK8ZcjV3qb3M9HBm93hUNQ_03TKqBNf"
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Lỗi kết nối: {e}")
    st.stop()

# --- 2. HỆ THỐNG ĐĂNG NHẬP ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 ĐĂNG NHẬP")
    p = st.text_input("Mật khẩu truy cập", type="password")
    if st.button("Vào quản trị", use_container_width=True):
        if p == "admin123":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Sai mật khẩu!")
    st.stop()

# --- 3. MENU SIDEBAR (NÂNG CẤP THAY ẢNH) ---
with st.sidebar:
    st.markdown("<h3 style='text-align: center;'>HỆ THỐNG QUẢN TRỊ</h3>", unsafe_allow_html=True)
    
    # === [PHẦN MỚI: HIỂN THỊ VÀ CHỨC NĂNG THAY ẢNH ADMIN] ===
    # A. Lấy link ảnh hiện tại từ cột 'gh_chu' của bảng 'settings'
    try:
        data_admin = supabase.table("settings").select("gh_chu").eq("key", "admin_avatar").single().execute()
        current_avatar = data_admin.data.get('gh_chu')
    except:
        current_avatar = None # Nếu chưa có, sẽ dùng mặc định

    # B. Ảnh mặc định nếu chưa có ảnh thay
    default_avatar = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    
    # C. Hiển thị ảnh tròn
    st.markdown(f"""
    <div style="display: flex; justify-content: center; margin-bottom: 10px;">
        <img src="{current_avatar if current_avatar else default_avatar}" 
             style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 3px solid #f0f2f6;">
    </div>
    """, unsafe_allow_html=True)
    
    # D. Nút thay ảnh (bằng file_uploader nhỏ)
    new_avatar_file = st.file_uploader("Thay ảnh đại diện", type=['png', 'jpg', 'jpeg'], key="upload_avatar")
    
    if new_avatar_file:
        try:
            st.warning("Đang tải ảnh lên...")
            
            # 1. Tải ảnh lên Supabase Storage (Bucket: images)
            file_path = f"admin_avatar.png"
            # Cần thêm lệnh upsert=True để ghi đè file cũ
            supabase.storage.from_("images").upload(file_path, new_avatar_file.getvalue(), {"content-type": "image/png", "upsert": "true"})
            
            # 2. Lấy link công khai
            url_moi = supabase.storage.from_("images").get_public_url(file_path)
            
            # 3. Cập nhật link vào bảng 'settings' (Cần tạo bảng này trên Supabase)
            # Dùng 'upsert' để tự thêm nếu chưa có, hoặc cập nhật nếu đã có
            supabase.table("settings").upsert({"key": "admin_avatar", "gh_chu": url_moi}).execute()
            
            st.success("✅ Đã cập nhật ảnh Admin! Vui lòng F5 lại trang.")
            st.rerun() # Khởi động lại app để nhận ảnh mới
        except Exception as e:
            st.error(f"Lỗi: {e}")
    # === [HẾT PHẦN MỚI] ===
    
    st.divider()
    selected = option_menu(
        menu_title=None,
        options=["Tổng quan", "Nhân sự", "Lịch công tác"],
        icons=["house", "people", "calendar-event"],
        default_index=0,
    )
    st.divider()
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

# --- 4. XỬ LÝ CHI TIẾT ---
# (Phần này giữ nguyên từ bộ code chuẩn của bạn)

if selected == "Tổng quan":
    st.header("📊 Báo cáo nhanh hệ thống")
    col1, col2 = st.columns(2)
    try:
        res_nv = supabase.table("employees").select("id", count="exact").execute()
        res_lc = supabase.table("work_schedule").select("id", count="exact").execute()
        col1.metric("Tổng nhân viên", f"{res_nv.count if res_nv.count else 0}")
        col2.metric("Lịch công tác", f"{res_lc.count if res_lc.count else 0}")
    except:
        st.info("💡 Mẹo: Nhập dữ liệu để biểu đồ hiện lên.")

elif selected == "Quản lý Nhân sự":
    st.header("👥 Quản lý lý lịch nhân viên")
    tab1, tab2 = st.tabs(["➕ Thêm mới", "📑 Danh sách"])
    
    with tab1:
        with st.form("add_nv"):
            c1, c2 = st.columns(2)
            ten = c1.text_input("Họ tên")
            ms = c2.text_input("Mã nhân viên")
            cv = st.selectbox("Chức vụ", ["Nhân viên", "Trưởng phòng", "Kế toán", "Quản lý"])
            # (Bạn có thể thêm nút upload ảnh cho từng nhân viên tại đây sau)
            if st.form_submit_button("Lưu"):
                if ten and ms:
                    supabase.table("employees").insert({"Ho_Ten": ten, "ma_vn": ms, "chuc_vu": cv}).execute()
                    st.success("Thành công!")
                    st.rerun()

    with tab2:
        res = supabase.table("employees").select("*").execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        else:
            st.info("Danh sách trống.")

elif selected == "Lịch công tác":
    st.header("📅 Hệ thống Lịch công tác")
    # (Phần tờ lịch FullCalendar của bạn giữ nguyên)
    try:
        res_cal = supabase.table("work_schedule").select("*").execute()
        calendar(events=res_cal.data if res_cal.data else [])
    except Exception:
        st.error("Lỗi: Kiểm tra lại bảng 'work_schedule' trên Supabase!")
