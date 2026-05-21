import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
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

# ================== 正式工数据库 ==================
FORMAL_WORKERS = {
  # 冲压部门
    "0001": {"name": "袁亮", "phone": "15862363175", "department": "冲压", "sub_dept": "冲压生产"},
    "0013": {"name": "朱桧", "phone": "18662309311", "department": "冲压", "sub_dept": "冲压生产"},
    "0061": {"name": "沈悦", "phone": "18014862195", "department": "冲压", "sub_dept": "生产文员"},
    "0005": {"name": "凌贤发", "phone": "15159043230", "department": "冲压", "sub_dept": "冲压生产"},
    "0007": {"name": "蒋玉宝", "phone": "15195688657", "department": "冲压", "sub_dept": "冲压生产"},
    "0017": {"name": "马金金", "phone": "18652422641", "department": "冲压", "sub_dept": "冲压生产"},
    "0021": {"name": "许昆武", "phone": "13059946926", "department": "冲压", "sub_dept": "冲压生产"},
    "0031": {"name": "李琼", "phone": "18096257156", "department": "冲压", "sub_dept": "冲压生产"},
    "0042": {"name": "莫国弟", "phone": "13179411830", "department": "冲压", "sub_dept": "冲压生产"},
    "0043": {"name": "李志强", "phone": "13935925857", "department": "冲压", "sub_dept": "冲压生产"},
    "0048": {"name": "李小娜", "phone": "15135975507", "department": "冲压", "sub_dept": "冲压生产"},
    "0054": {"name": "马文文", "phone": "18915126135", "department": "冲压", "sub_dept": "冲压生产"},
    
    # 工程部
    "0049": {"name": "方辉铭", "phone": "15051602299", "department": "工程部", "sub_dept": "研发部"},
    "0055": {"name": "黄盛军", "phone": "13812968895", "department": "工程部", "sub_dept": "工程部"},
    "0059": {"name": "沈才华", "phone": "13913086507", "department": "工程部", "sub_dept": "质量总监"},
    "0060": {"name": "朱志伟", "phone": "18952356052", "department": "工程部", "sub_dept": "工程部"},
    "0064": {"name": "王琦", "phone": "17674735668", "department": "工程部", "sub_dept": "工程部"},
    "0065": {"name": "谢洪", "phone": "13267300270", "department": "工程部", "sub_dept": "工程部"},
    "0069": {"name": "许浩", "phone": "15150426726", "department": "工程部", "sub_dept": "工程部"},
    "0071": {"name": "高杰", "phone": "13775699440", "department": "工程部", "sub_dept": "工程部"},
    "0072": {"name": "林宇", "phone": "18550440424", "department": "工程部", "sub_dept": "工程部"},
    
    # 仓库
    "0008": {"name": "赵开朝", "phone": "18962105883", "department": "仓库", "sub_dept": "仓库管理"},
    "0010": {"name": "程攀兴", "phone": "18135657323", "department": "仓库", "sub_dept": "仓库"},
    "0011": {"name": "朱友才", "phone": "18662189311", "department": "仓库", "sub_dept": "仓库"},
    "0019": {"name": "王家喜", "phone": "17768011425", "department": "仓库", "sub_dept": "仓库"},
    "0033": {"name": "杨粉荣", "phone": "19323055785", "department": "仓库", "sub_dept": "仓库"},
    "0058": {"name": "李宾冰", "phone": "13886811772", "department": "仓库", "sub_dept": "仓库"},
    
    # 品保/质量
    "0018": {"name": "朱泽丹", "phone": "17768011625", "department": "品保", "sub_dept": "质量"},
    "0026": {"name": "张建", "phone": "13814996290", "department": "品保", "sub_dept": "质量"},
    "0046": {"name": "魏梦娇", "phone": "13697809319", "department": "品保", "sub_dept": "质量"},
    "0052": {"name": "韩贵华", "phone": "13278803009", "department": "品保", "sub_dept": "质量"},
    "0057": {"name": "赵金平", "phone": "15250406635", "department": "品保", "sub_dept": "质量"},
    "0062": {"name": "张风丽", "phone": "18236518983", "department": "品保", "sub_dept": "质量"},
    
    # 后勤/保洁/后厨
    "0035": {"name": "沈继兰", "phone": "18013175817", "department": "后勤", "sub_dept": "保洁"},
    "0053": {"name": "俞霞娟", "phone": "13862300285", "department": "后勤", "sub_dept": "后厨"},
    "0056": {"name": "蔡玉群", "phone": "18791665960", "department": "后勤", "sub_dept": "后厨"},
    "0070": {"name": "范连芬", "phone": "13962327081", "department": "后勤", "sub_dept": "保洁"},
    
    # 组装
    "0006": {"name": "孙东京", "phone": "15850217477", "department": "组装", "sub_dept": "组装"},
    "0009": {"name": "张路林", "phone": "18351180905", "department": "组装", "sub_dept": "组装"},
    "0015": {"name": "谷菊花", "phone": "13913181404", "department": "组装", "sub_dept": "组装"},
    "0016": {"name": "崔翔", "phone": "18550042885", "department": "组装", "sub_dept": "组装"},
    "0020": {"name": "许秀红", "phone": "15150136971", "department": "组装", "sub_dept": "组装"},
    "0022": {"name": "邢江林", "phone": "13776237476", "department": "组装", "sub_dept": "新能源CNC"},
    "0024": {"name": "张悦", "phone": "18734959494", "department": "组装", "sub_dept": "组装"},
    "0028": {"name": "夏玮怡", "phone": "15250021022", "department": "组装", "sub_dept": "组装"},
    "0029": {"name": "范腾霄", "phone": "15235674954", "department": "组装", "sub_dept": "组装"},
    "0040": {"name": "吴章迅", "phone": "18708240113", "department": "组装", "sub_dept": "组装"},
    "0051": {"name": "张伟祥", "phone": "18662323729", "department": "组装", "sub_dept": "CNC"},
    "0066": {"name": "高杰", "phone": "18914445850", "department": "组装", "sub_dept": "CNC"},
    
    # 办公室/业务/财务/采购
    "0002": {"name": "徐清斌", "phone": "13451737900", "department": "办公室", "sub_dept": "会计"},
    "0003": {"name": "刘军", "phone": "13862030059", "department": "办公室", "sub_dept": "副总"},
    "0004": {"name": "杜卫萍", "phone": "13912628024", "department": "办公室", "sub_dept": "财务"},
    "0012": {"name": "印栋", "phone": "13812683189", "department": "办公室", "sub_dept": "业务"},
    "0014": {"name": "刘琼", "phone": "15367698811", "department": "办公室", "sub_dept": "采购"},
    "0023": {"name": "陈辉", "phone": "13755056959", "department": "办公室", "sub_dept": "业务"},
    "0025": {"name": "孙妞妞", "phone": "13962183787", "department": "办公室", "sub_dept": "业务"},
    "0030": {"name": "范德明", "phone": "13901547071", "department": "办公室", "sub_dept": "前台"},
    "0032": {"name": "金开封", "phone": "13912724648", "department": "办公室", "sub_dept": "副总"},
    "0034": {"name": "汤小平", "phone": "13901542181", "department": "办公室", "sub_dept": "总经理"},
    "0037": {"name": "刘涵", "phone": "13812974583", "department": "办公室", "sub_dept": "业务"},
    "0038": {"name": "杜国平", "phone": "18963663770", "department": "办公室", "sub_dept": "业务"},
    "0044": {"name": "叶春艳", "phone": "19556603924", "department": "办公室", "sub_dept": "业务"},
    "0050": {"name": "王心怡", "phone": "18051771918", "department": "办公室", "sub_dept": "业务"},
    "0067": {"name": "宋崟", "phone": "13901426285", "department": "办公室", "sub_dept": "业务"},
    "0068": {"name": "何佩昱", "phone": "18202758261", "department": "办公室", "sub_dept": "生管"},
    "0073": {"name": "李会香", "phone": "13218197189", "department": "办公室", "sub_dept": "财务"},
    "0074": {"name": "周建", "phone": "13862342344", "department": "办公室", "sub_dept": "采购"},
    
    # 司机/叉车司机
    "0027": {"name": "黄乐", "phone": "18606256510", "department": "司机", "sub_dept": "司机"},
    "0036": {"name": "汪友山", "phone": "13952623707", "department": "司机", "sub_dept": "司机"},
    "0039": {"name": "王晓明", "phone": "13634834006", "department": "司机", "sub_dept": "叉车司机"},
    "0045": {"name": "陈刚", "phone": "15862532531", "department": "司机", "sub_dept": "司机"},
    "0047": {"name": "单正康", "phone": "19951918249", "department": "司机", "sub_dept": "司机"},
    
    # 湖北驻厂
    "0063": {"name": "谭婷婷", "phone": "15571406650", "department": "湖北驻厂", "sub_dept": "驻厂"},
}  

# ================== 初始化 session_state ==================
if "daka_data" not in st.session_state:
    st.session_state.daka_data = pd.DataFrame()
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
if "user_lon" not in st.session_state:
    st.session_state.user_lon = None
if "location_verified" not in st.session_state:
    st.session_state.location_verified = False
if "worker_type" not in st.session_state:
    st.session_state.worker_type = None
if "formal_worker_info" not in st.session_state:
    st.session_state.formal_worker_info = None
if "selected_worker_id" not in st.session_state:
    st.session_state.selected_worker_id = None
if "scan_code" not in st.session_state:
    st.session_state.scan_code = None

st.set_page_config(page_title="荣基打卡", layout="wide")
st.title("🏭 荣基精密｜现场打卡系统")

# ================== 获取北京时间 ==================
def get_beijing_time():
    utc_now = datetime.now(timezone.utc)
    beijing_now = utc_now.astimezone(timezone(timedelta(hours=8)))
    return beijing_now

# ================== 处理URL参数中的坐标 ==================
query_params = st.query_params
if "lat" in query_params and "lon" in query_params:
    try:
        st.session_state.user_lat = float(query_params["lat"])
        st.session_state.user_lon = float(query_params["lon"])
        st.session_state.location_verified = True
        st.query_params.clear()
        st.rerun()
    except:
        pass

# ================== 定位UI ==================
st.subheader("📍 位置验证")

col1, col2 = st.columns(2)
with col1:
    lat_display = st.text_input("纬度", value=f"{st.session_state.user_lat:.6f}" if st.session_state.user_lat else "未获取", disabled=True)
with col2:
    lon_display = st.text_input("经度", value=f"{st.session_state.user_lon:.6f}" if st.session_state.user_lon else "未获取", disabled=True)

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("📍 使用厂区坐标定位", use_container_width=True):
        st.session_state.user_lat = FACTORY_LAT
        st.session_state.user_lon = FACTORY_LON
        st.session_state.location_verified = True
        st.rerun()
with col_btn2:
    if st.button("🔄 重置定位", use_container_width=True):
        st.session_state.user_lat = None
        st.session_state.user_lon = None
        st.session_state.location_verified = False
        st.rerun()

if st.session_state.location_verified:
    st.success(f"✅ 当前定位：纬度 {st.session_state.user_lat:.6f}，经度 {st.session_state.user_lon:.6f}")
else:
    st.info("💡 请点击「使用厂区坐标定位」按钮")

# ================== 距离计算 ==================
def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

if st.session_state.location_verified:
    distance = get_distance(st.session_state.user_lat, st.session_state.user_lon, FACTORY_LAT, FACTORY_LON)
    in_factory = distance <= ALLOW_RADIUS
    if in_factory:
        st.success(f"✅ 厂区范围内｜距离 {distance:.0f} 米")
        disabled = False
    else:
        st.error(f"❌ 不在厂区｜距离 {distance:.0f} 米")
        disabled = True
else:
    in_factory = False
    disabled = True

# ================== 员工类型选择 ==================
st.divider()
st.subheader("👥 员工类型")

if not disabled:
    col_type1, col_type2 = st.columns(2)
    with col_type1:
        if st.button("🔖 正式工", use_container_width=True):
            st.session_state.worker_type = "formal"
            st.session_state.formal_worker_info = None
            st.session_state.selected_worker_id = None
            st.rerun()
    with col_type2:
        if st.button("📝 临时工", use_container_width=True):
            st.session_state.worker_type = "temporary"
            st.session_state.formal_worker_info = None
            st.session_state.selected_worker_id = None
            st.rerun()
    
    if st.session_state.worker_type == "formal":
        st.info("🔖 正式工模式：请扫码或输入工号")
    elif st.session_state.worker_type == "temporary":
        st.info("📝 临时工模式：请填写以下信息")
    else:
        st.warning("👆 请选择员工类型")

# ================== 正式工：扫码识别 ==================
formal_verified = False
if st.session_state.worker_type == "formal" and not disabled:
    st.subheader("🔖 正式工身份验证")
    
    # 方式1：拍照扫码
    st.markdown("**方式一：拍摄工牌二维码**")
    qr_image = st.camera_input("将工牌二维码对准摄像头", disabled=disabled, key="qr_camera")
    
    if qr_image:
        try:
            # 尝试解码二维码
            from PIL import Image as PILImage
            from pyzbar import pyzbar
            
            img = PILImage.open(qr_image)
            decoded_objects = pyzbar.decode(img)
            
            if decoded_objects:
                scanned_id = decoded_objects[0].data.decode('utf-8')
                if scanned_id in FORMAL_WORKERS:
                    st.session_state.formal_worker_info = FORMAL_WORKERS[scanned_id]
                    st.session_state.selected_worker_id = scanned_id
                    formal_verified = True
                    st.success(f"✅ 扫码成功：{FORMAL_WORKERS[scanned_id]['name']}")
                    st.rerun()
                else:
                    st.error(f"❌ 工号 {scanned_id} 不存在")
            else:
                st.error("未识别到二维码，请重新拍摄")
        except ImportError:
            st.error("请先安装二维码识别库：pip install pyzbar pillow")
        except Exception as e:
            st.error(f"识别失败：{e}")
    
    # 方式2：手动输入
    st.markdown("**方式二：手动输入工号**")
    scan_input = st.text_input("输入工号", placeholder="例如：YL001", key="manual_scan")
    
    if scan_input and scan_input != st.session_state.selected_worker_id:
        if scan_input in FORMAL_WORKERS:
            st.session_state.formal_worker_info = FORMAL_WORKERS[scan_input]
            st.session_state.selected_worker_id = scan_input
            formal_verified = True
            st.success(f"✅ 识别成功：{FORMAL_WORKERS[scan_input]['name']}")
            st.rerun()
        else:
            st.error(f"❌ 工号 {scan_input} 不存在")
    
    # 显示已识别的员工信息
    if st.session_state.formal_worker_info:
        info = st.session_state.formal_worker_info
        formal_verified = True
        st.markdown(f"""
        <div style="background-color: #d1fae5; padding: 15px; border-radius: 10px; margin: 10px 0;">
            <strong>✅ 已识别员工信息</strong><br>
            姓名：{info['name']}<br>
            工号：{st.session_state.selected_worker_id}<br>
            部门：{info['department']} - {info['sub_dept']}<br>
            手机号：{info['phone']}
        </div>
        """, unsafe_allow_html=True)

# ================== 临时工：填写信息 ==================
temporary_info = {}
if st.session_state.worker_type == "temporary" and not disabled:
    st.subheader("📝 临时工信息填写")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        temp_name = st.text_input("姓名 *", key="temp_name")
        temp_id_card = st.text_input("身份证号 *", key="temp_id_card")
        temp_workshop = st.selectbox("车间 *", ["冲压车间", "组装车间", "仓库"],key="temp_workshop")
    with col_t2:
        temp_phone = st.text_input("手机号 *", key="temp_phone")
        temp_job = st.selectbox("工种 *", ["组装临时工", "冲压临时工", "仓库临时工"], key="temp_job")
    
    temp_company = st.radio("劳务公司 *", ["苏州众达人力", "苏州博仁劳务", "苏州汇思人力", "苏州优才派遣", "其它"], horizontal=True, key="temp_company")
    temp_other_company = st.text_input("请输入劳务公司全称", key="temp_other") if temp_company == "其它" else ""
    
    temporary_info = {
        "name": temp_name,
        "phone": temp_phone,
        "id_card": temp_id_card,
        "workshop": temp_workshop,
        "job": temp_job,
        "company": temp_other_company if temp_company == "其它" else temp_company,
    }

# ================== 打卡类型选择 ==================
st.divider()
st.subheader("⏰ 打卡类型")

col_clock1, col_clock2 = st.columns(2)
clock_in = col_clock1.button("✅ 签到", use_container_width=True, disabled=disabled or not in_factory)
clock_out = col_clock2.button("🔚 签退", use_container_width=True, disabled=disabled or not in_factory)

# ================== 拍照 ==================
st.subheader("📷 现场拍照")
st.markdown("**必须当场拍摄，禁止使用相册旧照片**")
camera_image = st.camera_input("请拍摄人脸+厂区背景", disabled=disabled or not in_factory, label_visibility="collapsed")

# ================== 时间校验 ==================
beijing_now = get_beijing_time()
current_time = beijing_now.strftime("%H:%M")
today = beijing_now.strftime("%Y-%m-%d")
is_workday = beijing_now.weekday() < 5

def time_to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

current_minutes = time_to_minutes(current_time)

clock_type = None
if clock_in:
    clock_type = "签到"
elif clock_out:
    clock_type = "签退"

if clock_type == "签到":
    allow_time = is_workday and time_to_minutes(SIGN_IN_START) <= current_minutes <= time_to_minutes(SIGN_IN_END)
    time_msg = f"签到时间：{SIGN_IN_START} - {SIGN_IN_END}"
else:
    allow_time = is_workday and time_to_minutes(SIGN_OUT_START) <= current_minutes <= time_to_minutes(SIGN_OUT_END)
    time_msg = f"签退时间：{SIGN_OUT_START} - {SIGN_OUT_END}"

st.info(f"🕒 **当前北京时间：{current_time}** | {time_msg}")

if not disabled and in_factory and clock_type:
    if allow_time:
        st.success("✅ 当前时间允许打卡")
    else:
        st.error("❌ 当前时间不在打卡时段内")

# ================== 水印函数 ==================
def add_watermark(img, name, lat, lon):
    draw = ImageDraw.Draw(img)
    now_str = get_beijing_time().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, img.height - 40), f"{name}｜{now_str}｜{lat:.6f},{lon:.6f}", fill="red")
    return img

# ================== 提交打卡 ==================
if clock_type and camera_image is not None and allow_time and in_factory:
    worker_name = None
    worker_phone = None
    worker_id_card = None
    worker_company = None
    worker_workshop = None
    worker_job = None
    
    # 正式工提交
    if st.session_state.worker_type == "formal" and formal_verified and st.session_state.formal_worker_info:
        info = st.session_state.formal_worker_info
        worker_name = info['name']
        worker_phone = info['phone']
        worker_id_card = "正式工"
        worker_company = f"正式工-{info['department']}"
        worker_workshop = info['sub_dept']
        worker_job = "正式员工"
    
    # 临时工提交
    elif st.session_state.worker_type == "temporary":
        if temporary_info.get("name") and len(temporary_info.get("phone", "")) == 11 and len(temporary_info.get("id_card", "")) == 18:
            worker_name = temporary_info["name"]
            worker_phone = temporary_info["phone"]
            worker_id_card = temporary_info["id_card"]
            worker_company = temporary_info["company"]
            worker_workshop = temporary_info["workshop"]
            worker_job = temporary_info["job"]
        else:
            st.error("请完整填写临时工信息（姓名、11位手机号、18位身份证号）")
    
    if worker_name:
        img = Image.open(camera_image)
        img = add_watermark(img, worker_name, st.session_state.user_lat, st.session_state.user_lon)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        
        work_h = ""
        if clock_type == "签退":
            mask = (st.session_state.daka_data["姓名"] == worker_name) & \
                   (st.session_state.daka_data["日期"] == today) & \
                   (st.session_state.daka_data["打卡类型"] == "签到")
            if not st.session_state.daka_data.empty and mask.any():
                t1_str = st.session_state.daka_data[mask].iloc[0]["打卡时间"]
                t1 = datetime.strptime(t1_str, "%H:%M")
                t2 = datetime.strptime(current_time, "%H:%M")
                mins = int((t2 - t1).total_seconds() / 60)
                work_h = f"{mins // 60}小时{mins % 60}分钟"
        
        new_row = pd.DataFrame([{
            "日期": today, "打卡时间": current_time, "姓名": worker_name,
            "手机号": worker_phone, "身份证": worker_id_card, "劳务公司": worker_company,
            "车间": worker_workshop, "工种": worker_job, "打卡类型": clock_type,
            "工时": work_h, "纬度": st.session_state.user_lat, "经度": st.session_state.user_lon,
            "照片": img_bytes.getvalue()
        }])
        st.session_state.daka_data = pd.concat([st.session_state.daka_data, new_row], ignore_index=True)
        st.success(f"✅ {clock_type}成功！{worker_name}" + (f" 工时：{work_h}" if work_h else ""))
        st.balloons()
        
        # 打卡成功后重置
        st.session_state.worker_type = None
        st.session_state.formal_worker_info = None
        st.session_state.selected_worker_id = None
        st.rerun()

# ================== 查看记录 ==================
st.divider()
st.subheader("👤 我的打卡记录")

if st.button("查看今日记录"):
    worker_name_filter = None
    if st.session_state.worker_type == "formal" and st.session_state.formal_worker_info:
        worker_name_filter = st.session_state.formal_worker_info["name"]
    elif st.session_state.worker_type == "temporary" and temporary_info.get("name"):
        worker_name_filter = temporary_info["name"]
    
    if worker_name_filter:
        my_records = st.session_state.daka_data[
            (st.session_state.daka_data["日期"] == today) &
            (st.session_state.daka_data["姓名"] == worker_name_filter)
        ]
        if my_records.empty:
            st.info("今日暂无打卡记录")
        else:
            display_cols = ["打卡时间", "打卡类型", "车间", "工种", "工时"]
            st.dataframe(my_records[display_cols])
    else:
        st.info("请先完成员工身份确认")

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
        st.download_button("📥 导出打卡记录", data=excel_buffer.getvalue(), 
                          file_name=f"打卡记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
