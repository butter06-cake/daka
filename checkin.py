import streamlit as st
import pandas as pd
from datetime import datetime
import io
from PIL import Image, ImageDraw
import math

# 厂区定位
FACTORY_LAT = 31.3040
FACTORY_LON = 120.6280
ALLOW_RADIUS = 500
SIGN_IN_START = "07:30"
SIGN_IN_END = "08:30"
SIGN_OUT_START = "17:00"
SIGN_OUT_END = "18:00"
ADMIN_PASSWORD = "admin123"

# 云端永久保存数据
if "daka_data" not in st.session_state:
    st.session_state.daka_data = pd.DataFrame()

st.set_page_config(page_title="荣基打卡", layout="wide")
st.title("🏭 荣基精密｜现场打卡")

# 自动获取手机GPS定位
st.markdown("""
<script>
navigator.geolocation.getCurrentPosition(p=>{
    document.getElementById("lat").value = p.coords.latitude.toFixed(4);
    document.getElementById("lon").value = p.coords.longitude.toFixed(4);
})
</script>
""", unsafe_allow_html=True)

lat = st.text_input("", key="lat", label_visibility="hidden", value=str(FACTORY_LAT))
lon = st.text_input("", key="lon", label_visibility="hidden", value=str(FACTORY_LON))

# 距离计算
def get_dist(lat1,lon1,lat2,lon2):
    R=6371000
    lat1,lon1,lat2,lon2=map(math.radians,[float(lat1),float(lon1),float(lat2),float(lon2)])
    return R*2*math.atan2(math.sqrt(math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2),math.sqrt(1-(math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2)))

distance = get_dist(lat,lon,FACTORY_LAT,FACTORY_LON)
in_factory = distance <= ALLOW_RADIUS

if in_factory:
    st.success(f"✅ 厂区范围内｜距离{distance:.0f}米")
else:
    st.error("❌ 不在厂区，禁止打卡")

# 基础信息
name = st.text_input("姓名 *", disabled=not in_factory)
phone = st.text_input("手机号 *", disabled=not in_factory)
id_card = st.text_input("身份证 *", disabled=not in_factory)

company = st.radio("",["苏州众达人力","苏州博仁劳务","苏州汇思人力","苏州优才派遣","其它"], horizontal=True, disabled=not in_factory)
other_company = st.text_input("劳务全称") if company=="其它" else ""

workshop = st.selectbox("车间",["冲压车间","注塑车间","装配车间","质检车间","仓储物料区","办公区"], disabled=not in_factory)
job = st.selectbox("工种",["冲压操作工","注塑操作工","装配工","质检QC","物料","普工"], disabled=not in_factory)
clock_type = st.radio("打卡类型",["签到","签退"], horizontal=True, disabled=not in_factory)

# 【云端强制只能现场拍照，禁用相册，无法作弊】
st.subheader("📷 现场实时拍照（只能当场拍摄，禁止旧照片）")
st.markdown('''
<input type="file" accept="image/*" capture="environment" id="cam" style="display:none">
<script>document.getElementById("cam").click()</script>
''', unsafe_allow_html=True)
img = st.file_uploader("拍摄人脸+厂区", type=["jpg","png"], disabled=not in_factory)

# 加水印
def add_watermark(img,name):
    draw=ImageDraw.Draw(img)
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10,img.height-40),f"{name}｜{now}｜{lat},{lon}",fill="red")
    return img

# 时间校验
now=datetime.now()
current_time=now.strftime("%H:%M")
today=now.strftime("%Y-%m-%d")
is_workday=now.weekday()<5
allow_time=False
if clock_type=="签到":
    allow_time=is_workday and SIGN_IN_START<=current_time<=SIGN_IN_END
else:
    allow_time=is_workday and SIGN_OUT_START<=current_time<=SIGN_OUT_END
st.info(f"🕒 当前{current_time}")

# 打卡提交
if st.button("✅ 确认打卡", disabled=not allow_time or not in_factory or img is None):
    if not name or len(phone)!=11 or len(id_card)!=18:
        st.error("信息错误")
    else:
        pic=Image.open(io.BytesIO(img.getvalue()))
        pic=add_watermark(pic,name)
        pic_bytes=io.BytesIO()
        pic.save(pic_bytes,format="JPEG")
        work_h=""
        if clock_type=="签退":
            mask=(st.session_state.daka_data["姓名"]==name)&(st.session_state.daka_data["日期"]==today)&(st.session_state.daka_data["打卡类型"]=="签到")
            if not st.session_state.daka_data.empty and mask.any():
                t1=pd.to_datetime(st.session_state.daka_data[mask].iloc[0]["打卡时间"],format="%H:%M")
                t2=pd.to_datetime(current_time,format="%H:%M")
                mins=int((t2-t1).total_seconds()/60)
                work_h=f"{mins//60}小时{mins%60}分钟"
        new_row=pd.DataFrame([{"日期":today,"打卡时间":current_time,"姓名":name,"手机号":phone,"身份证":id_card,"劳务公司":other_company if company=="其它" else company,"车间":workshop,"工种":job,"打卡类型":clock_type,"工时":work_h,"照片":pic_bytes.getvalue()}])
        st.session_state.daka_data=pd.concat([st.session_state.daka_data,new_row],ignore_index=True)
        st.success(f"✅ {clock_type}成功，工时：{work_h}")

# 个人记录
st.divider()
st.subheader("👤 我的今日记录")
if st.button("查看我的", disabled=not in_factory or not name):
    my=st.session_state.daka_data[(st.session_state.daka_data["日期"]==today)&(st.session_state.daka_data["姓名"]==name)]
    st.dataframe(my)

# 管理员
st.divider()
st.subheader("🔐 管理员后台")
pwd=st.text_input("密码",type="password")
if pwd==ADMIN_PASSWORD:
    st.success("✅ 登录成功")
    st.dataframe(st.session_state.daka_data)
    buf=io.BytesIO()
    st.session_state.daka_data.to_excel(buf,index=False)
    st.download_button("📥 导出全部",buf.getvalue(),file_name="打卡记录.xlsx")
