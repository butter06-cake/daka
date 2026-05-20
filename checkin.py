import streamlit as st
import pandas as pd
from datetime import datetime
import os

# -------------------------- 配置区（你只要改这里） --------------------------
# 厂区中心点经纬度（苏州荣基精密电子，可精准修改）
FACTORY_LAT = 31.3040    # 纬度
FACTORY_LON = 120.6280   # 经度
ALLOW_RADIUS = 500       # 允许打卡半径：500米，超出禁止打卡

# 打卡时间
SIGN_IN_START = "07:30"
SIGN_IN_END = "08:30"
SIGN_OUT_START = "17:00"
SIGN_OUT_END = "18:00"
EXCEL_FILE = "荣基打卡记录.xlsx"
FIXED_LOCATION = "苏州荣基精密电子厂区（GPS打卡）"
# --------------------------------------------------------------------------

st.set_page_config(page_title="荣基临时工打卡", layout="wide")
st.title("🏭 苏州荣基精密电子｜临时工打卡系统")

# 1. GPS定位组件（浏览器获取真实位置）
location_data = st.components.v1.html('''
<script>
navigator.geolocation.getCurrentPosition(
    pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        document.getElementById("lat").value = lat;
        document.getElementById("lon").value = lon;
    },
    err => {
        document.getElementById("err").value = err.message;
    }
);
</script>
<input type="hidden" id="lat" value="">
<input type="hidden" id="lon" value="">
<input type="hidden" id="err" value="">
''', height=0)

# 2. 计算两点距离（米）
import math
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

# 模拟前端获取（streamlit无法直接拿JS值，改用用户手动获取GPS经纬度输入，简单可用）
st.info("📍 请打开手机定位，获取当前经纬度，不在厂区500米内禁止打卡")
user_lat = st.number_input("当前纬度", value=FACTORY_LAT, format="%.4f")
user_lon = st.number_input("当前经度", value=FACTORY_LON, format="%.4f")

distance = get_distance(user_lat, user_lon, FACTORY_LAT, FACTORY_LON)
is_in_factory = distance <= ALLOW_RADIUS

if is_in_factory:
    st.success(f"✅ 已在打卡范围内｜距离厂区：{distance:.0f}米")
else:
    st.error(f"❌ 不在打卡范围内，禁止打卡｜距离厂区：{distance:.0f}米")

# 3. 基础信息
name = st.text_input("姓名", placeholder="请输入真实姓名", disabled=not is_in_factory)
phone = st.text_input("手机号码", placeholder="请输入11位手机号", disabled=not is_in_factory)
id_card = st.text_input("身份证号", placeholder="请输入18位身份证号", disabled=not is_in_factory)

# 4. 劳务派遣公司（选其他可手写）
company_options = [
    "苏州众达人力",
    "苏州博仁劳务",
    "苏州汇思人力",
    "苏州优才派遣",
    "其他"
]
selected_company = st.selectbox("劳务派遣公司", company_options, disabled=not is_in_factory)
custom_company = ""
if selected_company == "其他" and is_in_factory:
    custom_company = st.text_input("请输入劳务派遣公司全称", placeholder="例如：XX劳务公司")

# 5. 车间、工种
workshop = st.selectbox("车间/楼层", [
    "冲压车间",
    "注塑车间",
    "装配车间",
    "质检车间",
    "仓储物料区",
    "办公区"
], disabled=not is_in_factory)

job = st.selectbox("工种", [
    "冲压操作工",
    "注塑操作工",
    "装配工",
    "质检QC",
    "物料分拣",
    "普工/辅助工",
    "其他工种"
], disabled=not is_in_factory)

# 6. 打卡地点：强制固定，不可修改
st.text_input("打卡地点", value=FIXED_LOCATION, disabled=True)

# 7. 打卡类型
clock_type = st.radio("打卡类型", ["签到", "签退"], disabled=not is_in_factory)

# 8. 时间校验
now = datetime.now()
current_time = now.strftime("%H:%M")
weekday = now.weekday()
is_workday = weekday < 5

allow_time = False
msg = ""
if clock_type == "签到":
    allow_time = is_workday and SIGN_IN_START <= current_time <= SIGN_IN_END
    msg = "签到仅允许 07:30–08:30"
else:
    allow_time = is_workday and SIGN_OUT_START <= current_time <= SIGN_OUT_END
    msg = "签退仅允许 17:00–18:00"

st.info(f"🕒 当前时间：{current_time}｜{msg}")

# 9. 提交打卡
if st.button("✅ 确认打卡", disabled=not is_in_factory or not allow_time):
    final_company = custom_company if selected_company == "其他" else selected_company
    if not name:
        st.error("请填写姓名！")
    elif not phone or len(phone)!=11:
        st.error("请填写正确11位手机号！")
    elif not id_card or len(id_card)!=18:
        st.error("请填写正确18位身份证号！")
    elif not final_company.strip():
        st.error("请填写劳务派遣公司！")
    else:
        record = {
            "日期": now.strftime("%Y-%m-%d"),
            "打卡时间": current_time,
            "姓名": name,
            "手机号": phone,
            "身份证号": id_card,
            "派遣公司": final_company,
            "车间": workshop,
            "工种": job,
            "打卡类型": clock_type,
            "打卡地点": FIXED_LOCATION,
            "打卡经纬度": f"{user_lat},{user_lon}",
            "距离厂区(米)": round(distance)
        }
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
        else:
            df = pd.DataFrame([record])
        df.to_excel(EXCEL_FILE, index=False)
        st.success(f"🎉 {clock_type}成功！记录已保存")

# 10. 查看今日记录
if st.button("📊 查看今日打卡", disabled=not is_in_factory):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        today = now.strftime("%Y-%m-%d")
        st.dataframe(df[df["日期"] == today], use_container_width=True)
    else:
        st.info("暂无打卡记录")