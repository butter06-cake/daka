import streamlit as st
import pandas as pd
from datetime import datetime
import io
from PIL import Image, ImageDraw
import math

# ================== 配置参数 ==================
FACTORY_LAT = 31.3040
FACTORY_LON = 120.6280
ALLOW_RADIUS = 500
SIGN_IN_START = "07:30"
SIGN_IN_END = "08:30"
SIGN_OUT_START = "17:00"
SIGN_OUT_END = "18:00"
ADMIN_PASSWORD = "admin123"

# 初始化 session_state
if "daka_data" not in st.session_state:
    st.session_state.daka_data = pd.DataFrame()
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
if "user_lon" not in st.session_state:
    st.session_state.user_lon = None
if "location_verified" not in st.session_state:
    st.session_state.location_verified = False

st.set_page_config(page_title="荣基打卡", layout="wide")
st.title("🏭 荣基精密｜现场打卡")

# ================== 定位UI ==================
st.subheader("📍 位置验证")

col1, col2 = st.columns(2)
with col1:
    lat_input = st.number_input(
        "纬度", 
        value=float(st.session_state.user_lat) if st.session_state.user_lat else FACTORY_LAT,
        format="%.6f",
        step=0.000001,
        key="lat_input"
    )
with col2:
    lon_input = st.number_input(
        "经度", 
        value=float(st.session_state.user_lon) if st.session_state.user_lon else FACTORY_LON,
        format="%.6f",
        step=0.000001,
        key="lon_input"
    )

# 两个按钮
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📍 使用厂区坐标", use_container_width=True):
        st.session_state.user_lat = FACTORY_LAT
        st.session_state.user_lon = FACTORY_LON
        st.session_state.location_verified = True
        st.success(f"✅ 已设置为厂区坐标：{FACTORY_LAT}, {FACTORY_LON}")
        st.rerun()

with col_btn2:
    if st.button("✅ 确认使用当前坐标", use_container_width=True):
        if lat_input and lon_input:
            st.session_state.user_lat = lat_input
            st.session_state.user_lon = lon_input
            st.session_state.location_verified = True
            st.success(f"✅ 已确认坐标：{lat_input:.6f}, {lon_input:.6f}")
            st.rerun()
        else:
            st.error("请先输入坐标")

# 显示当前定位状态
if st.session_state.location_verified:
    st.success(f"✅ 当前定位：纬度 {st.session_state.user_lat:.6f}，经度 {st.session_state.user_lon:.6f}")
else:
    st.info("💡 请点击「使用厂区坐标」按钮，或手动输入坐标后点击「确认使用当前坐标」")

# ================== 距离计算与厂区判断 ==================
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

if st.session_state.location_verified:
    distance = get_distance(
        st.session_state.user_lat, 
        st.session_state.user_lon, 
        FACTORY_LAT, 
        FACTORY_LON
    )
    in_factory = distance <= ALLOW_RADIUS
    
    if in_factory:
        st.success(f"✅ 厂区范围内｜距离厂区 {distance:.0f} 米")
        disabled = False
    else:
        st.error(f"❌ 不在厂区｜距离厂区 {distance:.0f} 米（需在 {ALLOW_RADIUS} 米内）")
        st.warning("💡 点击「使用厂区坐标」按钮")
        disabled = True
else:
    in_factory = False
    disabled = True

# ================== 打卡表单 ==================
st.divider()
st.subheader("📝 打卡信息")

if not st.session_state.location_verified:
    st.info("🔒 请先完成位置验证")
elif not in_factory:
    st.error("🔒 您不在厂区范围内，无法打卡")
else:
    st.success("✅ 位置验证通过，请填写打卡信息")

# 基本信息
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("姓名 *", disabled=disabled)
    id_card = st.text_input("身份证号 *", disabled=disabled)
    workshop = st.selectbox(
        "车间 *",
        ["冲压车间", "注塑车间", "装配车间", "质检车间", "仓储物料区", "办公区"],
        disabled=disabled
    )
with col2:
    phone = st.text_input("手机号 *", disabled=disabled)
    job = st.selectbox(
        "工种 *",
        ["冲压操作工", "注塑操作工", "装配工", "质检QC", "物料", "普工"],
        disabled=disabled
    )
    clock_type = st.radio("打卡类型 *", ["签到", "签退"], horizontal=True, disabled=disabled)

# 劳务公司
company = st.radio(
    "劳务公司 *",
    ["苏州众达人力", "苏州博仁劳务", "苏州汇思人力", "苏州优才派遣", "其它"],
    horizontal=True,
    disabled=disabled
)
other_company = st.text_input("请输入劳务公司全称", disabled=disabled) if company == "其它" else ""

# ================== 拍照 ==================
st.subheader("📷 现场拍照")
st.markdown("**必须当场拍摄，禁止使用相册旧照片**")
camera_image = st.camera_input("请拍摄人脸+厂区背景", disabled=disabled, label_visibility="collapsed")

# ================== 时间校验 ==================
now = datetime.now()
current_time = now.strftime("%H:%M")
today = now.strftime("%Y-%m-%d")
is_workday = now.weekday() < 5

if clock_type == "签到":
    allow_time = is_workday and SIGN_IN_START <= current_time <= SIGN_IN_END
else:
    allow_time = is_workday and SIGN_OUT_START <= current_time <= SIGN_OUT_END

if not disabled and in_factory:
    if allow_time:
        st.success(f"🕒 当前时间 {current_time}，可以打卡")
    else:
        st.error(f"🕒 当前时间 {current_time}，不在打卡时间内")

# ================== 水印函数 ==================
def add_watermark(img, name, lat, lon):
    draw = ImageDraw.Draw(img)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, img.height - 40), f"{name}｜{now_str}｜{lat:.6f},{lon:.6f}", fill="red")
    return img

# ================== 提交打卡 ==================
submit_disabled = disabled or not in_factory or not allow_time or camera_image is None

if st.button("✅ 确认打卡", disabled=submit_disabled):
    if not name or len(phone) != 11 or len(id_card) != 18:
        st.error("请完整填写姓名、11位手机号和18位身份证号")
    else:
        # 处理照片
        img = Image.open(camera_image)
        img = add_watermark(img, name, st.session_state.user_lat, st.session_state.user_lon)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        
        # 计算工时
        work_h = ""
        if clock_type == "签退":
            mask = (st.session_state.daka_data["姓名"] == name) & \
                   (st.session_state.daka_data["日期"] == today) & \
                   (st.session_state.daka_data["打卡类型"] == "签到")
            if not st.session_state.daka_data.empty and mask.any():
                t1 = pd.to_datetime(st.session_state.daka_data[mask].iloc[0]["打卡时间"], format="%H:%M")
                t2 = pd.to_datetime(current_time, format="%H:%M")
                mins = int((t2 - t1).total_seconds() / 60)
                work_h = f"{mins // 60}小时{mins % 60}分钟"
        
        # 保存记录
        new_row = pd.DataFrame([{
            "日期": today,
            "打卡时间": current_time,
            "姓名": name,
            "手机号": phone,
            "身份证": id_card,
            "劳务公司": other_company if company == "其它" else company,
            "车间": workshop,
            "工种": job,
            "打卡类型": clock_type,
            "工时": work_h,
            "纬度": st.session_state.user_lat,
            "经度": st.session_state.user_lon,
            "照片": img_bytes.getvalue()
        }])
        st.session_state.daka_data = pd.concat([st.session_state.daka_data, new_row], ignore_index=True)
        st.success(f"✅ {clock_type}成功！" + (f" 工时：{work_h}" if work_h else ""))
        st.balloons()

# ================== 查看记录 ==================
st.divider()
st.subheader("👤 我的打卡记录")

if st.button("查看今日记录", disabled=disabled or not name):
    my_records = st.session_state.daka_data[
        (st.session_state.daka_data["日期"] == today) &
        (st.session_state.daka_data["姓名"] == name)
    ]
    if my_records.empty:
        st.info("今日暂无打卡记录")
    else:
        display_cols = ["打卡时间", "打卡类型", "车间", "工种", "工时"]
        st.dataframe(my_records[display_cols])

# ================== 管理员后台 ==================
st.divider()
st.subheader("🔐 管理员后台")
pwd = st.text_input("管理员密码", type="password")

if pwd == ADMIN_PASSWORD:
    st.success("登录成功")
    st.dataframe(st.session_state.daka_data)
    if not st.session_state.daka_data.empty:
        excel_buffer = io.BytesIO()
        export_df = st.session_state.daka_data.drop(columns=["照片"], errors="ignore")
        export_df.to_excel(excel_buffer, index=False)
        st.download_button(
            label="📥 导出打卡记录",
            data=excel_buffer.getvalue(),
            file_name=f"打卡记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
