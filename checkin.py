import streamlit as st
import pandas as pd
from datetime import datetime
import io
from PIL import Image, ImageDraw
import math
from streamlit_geolocation import st_geolocation

# ================== 配置参数 ==================
FACTORY_LAT = 31.3040
FACTORY_LON = 120.6280
ALLOW_RADIUS = 500                     # 米
SIGN_IN_START = "07:30"
SIGN_IN_END = "08:30"
SIGN_OUT_START = "17:00"
SIGN_OUT_END = "18:00"
ADMIN_PASSWORD = "admin123"

# 数据存储
if "daka_data" not in st.session_state:
    st.session_state.daka_data = pd.DataFrame()

# 定位存储
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
if "user_lon" not in st.session_state:
    st.session_state.user_lon = None

st.set_page_config(page_title="荣基打卡", layout="wide")
st.title("🏭 荣基精密｜现场打卡")

# ================== 自动定位（使用专业组件，用户不可手动修改） ==================
st.subheader("📍 自动定位（系统获取，不可修改）")

col1, col2 = st.columns(2)
with col1:
    lat_display = st.text_input("纬度", value=str(st.session_state.user_lat) if st.session_state.user_lat else "未获取", disabled=True)
with col2:
    lon_display = st.text_input("经度", value=str(st.session_state.user_lon) if st.session_state.user_lon else "未获取", disabled=True)

# 定位组件（会自动处理权限请求和 HTTPS 要求）
location = st_geolocation()

if location and "latitude" in location:
    st.session_state.user_lat = location["latitude"]
    st.session_state.user_lon = location["longitude"]
    st.success(f"✅ 定位成功：纬度 {st.session_state.user_lat:.6f}，经度 {st.session_state.user_lon:.6f}")
else:
    if st.session_state.user_lat is None:
        st.warning("⚠️ 请点击地图上的「获取位置」按钮，并允许位置权限")

has_location = st.session_state.user_lat is not None and st.session_state.user_lon is not None

# ================== 距离与厂区判断 ==================
def get_dist(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    return R * 2 * math.atan2(
        math.sqrt(math.sin((lat2 - lat1) / 2) ** 2 +
                  math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2),
        math.sqrt(1 - (math.sin((lat2 - lat1) / 2) ** 2 +
                       math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2))
    )

if has_location:
    distance = get_dist(st.session_state.user_lat, st.session_state.user_lon, FACTORY_LAT, FACTORY_LON)
    in_factory = distance <= ALLOW_RADIUS
    if in_factory:
        st.success(f"✅ 厂区范围内｜距离{distance:.0f}米")
    else:
        st.error(f"❌ 不在厂区（当前距离{distance:.0f}米），禁止打卡")
else:
    in_factory = False
    distance = None

disabled = not (has_location and in_factory)

# ================== 基本信息录入（仅在厂区内且定位成功后可填） ==================
name = st.text_input("姓名 *", disabled=disabled)
phone = st.text_input("手机号 *", disabled=disabled)
id_card = st.text_input("身份证 *", disabled=disabled)

company = st.radio(
    "劳务公司",
    ["苏州众达人力","苏州博仁劳务","苏州汇思人力","苏州优才派遣","其它"],
    horizontal=True,
    disabled=disabled
)
other_company = st.text_input("劳务全称", disabled=disabled) if company == "其它" else ""

workshop = st.selectbox(
    "车间",
    ["冲压车间","注塑车间","装配车间","质检车间","仓储物料区","办公区"],
    disabled=disabled
)
job = st.selectbox(
    "工种",
    ["冲压操作工","注塑操作工","装配工","质检QC","物料","普工"],
    disabled=disabled
)
clock_type = st.radio("打卡类型", ["签到","签退"], horizontal=True, disabled=disabled)

# ================== 强制现场拍照（只能当场拍摄） ==================
st.subheader("📷 现场实时拍照（只能当场拍摄，禁止旧照片）")
camera_image = st.camera_input("请拍摄人脸+厂区背景", disabled=disabled, label_visibility="collapsed")

# ================== 水印函数 ==================
def add_watermark(img, name, lat, lon):
    draw = ImageDraw.Draw(img)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, img.height - 40), f"{name}｜{now}｜{lat},{lon}", fill="red")
    return img

# ================== 时间校验 ==================
now = datetime.now()
current_time = now.strftime("%H:%M")
today = now.strftime("%Y-%m-%d")
is_workday = now.weekday() < 5
allow_time = False
if clock_type == "签到":
    allow_time = is_workday and SIGN_IN_START <= current_time <= SIGN_IN_END
else:
    allow_time = is_workday and SIGN_OUT_START <= current_time <= SIGN_OUT_END
st.info(f"🕒 当前时间 {current_time}，{'允许打卡' if allow_time else '不在打卡时段内'}")

# ================== 提交打卡 ==================
if st.button("✅ 确认打卡", disabled=not (allow_time and in_factory and camera_image is not None and has_location)):
    if not name or len(phone) != 11 or len(id_card) != 18:
        st.error("请完整填写姓名、11位手机号、18位身份证号")
    else:
        img = Image.open(camera_image)
        img = add_watermark(img, name, st.session_state.user_lat, st.session_state.user_lon)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")

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
            "照片": img_bytes.getvalue()
        }])
        st.session_state.daka_data = pd.concat([st.session_state.daka_data, new_row], ignore_index=True)
        st.success(f"✅ {clock_type}成功，工时：{work_h if work_h else '无'}")

# ================== 个人当日记录查看 ==================
st.divider()
st.subheader("👤 我的今日记录")
if st.button("查看我的记录", disabled=not (has_location and in_factory and name)):
    my_records = st.session_state.daka_data[
        (st.session_state.daka_data["日期"] == today) &
        (st.session_state.daka_data["姓名"] == name)
    ]
    if my_records.empty:
        st.info("今日暂无打卡记录")
    else:
        st.dataframe(my_records)

# ================== 管理员后台 ==================
st.divider()
st.subheader("🔐 管理员后台")
pwd = st.text_input("管理员密码", type="password")
if pwd == ADMIN_PASSWORD:
    st.success("登录成功")
    st.dataframe(st.session_state.daka_data)
    if not st.session_state.daka_data.empty:
        excel_buffer = io.BytesIO()
        st.session_state.daka_data.to_excel(excel_buffer, index=False)
        st.download_button(
            label="📥 导出全部打卡记录（Excel）",
            data=excel_buffer.getvalue(),
            file_name="daka_records.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
