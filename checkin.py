import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import io
from PIL import Image, ImageDraw
import math
import os
import re

# ================== 配置参数 ==================
FACTORY_LAT = 31.3040
FACTORY_LON = 120.6280
ALLOW_RADIUS = 500
SIGN_IN_START = "07:30"
SIGN_IN_END = "08:30"
SIGN_OUT_START = "17:00"
SIGN_OUT_END = "18:00"
ADMIN_PASSWORD = "admin123"
DATA_FILE = "daka_records.xlsx"

# ================== 正式工数据库 ==================
FORMAL_WORKERS = {
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
    "0049": {"name": "方辉铭", "phone": "15051602299", "department": "工程部", "sub_dept": "研发部"},
    "0055": {"name": "黄盛军", "phone": "13812968895", "department": "工程部", "sub_dept": "工程部"},
    "0059": {"name": "沈才华", "phone": "13913086507", "department": "工程部", "sub_dept": "质量总监"},
    "0060": {"name": "朱志伟", "phone": "18952356052", "department": "工程部", "sub_dept": "工程部"},
    "0064": {"name": "王琦", "phone": "17674735668", "department": "工程部", "sub_dept": "工程部"},
    "0065": {"name": "谢洪", "phone": "13267300270", "department": "工程部", "sub_dept": "工程部"},
    "0069": {"name": "许浩", "phone": "15150426726", "department": "工程部", "sub_dept": "工程部"},
    "0071": {"name": "高杰", "phone": "13775699440", "department": "工程部", "sub_dept": "工程部"},
    "0072": {"name": "林宇", "phone": "18550440424", "department": "工程部", "sub_dept": "工程部"},
    "0008": {"name": "赵开朝", "phone": "18962105883", "department": "仓库", "sub_dept": "仓库管理"},
    "0010": {"name": "程攀兴", "phone": "18135657323", "department": "仓库", "sub_dept": "仓库"},
    "0011": {"name": "朱友才", "phone": "18662189311", "department": "仓库", "sub_dept": "仓库"},
    "0019": {"name": "王家喜", "phone": "17768011425", "department": "仓库", "sub_dept": "仓库"},
    "0033": {"name": "杨粉荣", "phone": "19323055785", "department": "仓库", "sub_dept": "仓库"},
    "0058": {"name": "李宾冰", "phone": "13886811772", "department": "仓库", "sub_dept": "仓库"},
    "0018": {"name": "朱泽丹", "phone": "17768011625", "department": "品保", "sub_dept": "质量"},
    "0026": {"name": "张建", "phone": "13814996290", "department": "品保", "sub_dept": "质量"},
    "0046": {"name": "魏梦娇", "phone": "13697809319", "department": "品保", "sub_dept": "质量"},
    "0052": {"name": "韩贵华", "phone": "13278803009", "department": "品保", "sub_dept": "质量"},
    "0057": {"name": "赵金平", "phone": "15250406635", "department": "品保", "sub_dept": "质量"},
    "0062": {"name": "张风丽", "phone": "18236518983", "department": "品保", "sub_dept": "质量"},
    "0035": {"name": "沈继兰", "phone": "18013175817", "department": "后勤", "sub_dept": "保洁"},
    "0053": {"name": "俞霞娟", "phone": "13862300285", "department": "后勤", "sub_dept": "后厨"},
    "0056": {"name": "蔡玉群", "phone": "18791665960", "department": "后勤", "sub_dept": "后厨"},
    "0070": {"name": "范连芬", "phone": "13962327081", "department": "后勤", "sub_dept": "保洁"},
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
    "0027": {"name": "黄乐", "phone": "18606256510", "department": "司机", "sub_dept": "司机"},
    "0036": {"name": "汪友山", "phone": "13952623707", "department": "司机", "sub_dept": "司机"},
    "0039": {"name": "王晓明", "phone": "13634834006", "department": "司机", "sub_dept": "叉车司机"},
    "0045": {"name": "陈刚", "phone": "15862532531", "department": "司机", "sub_dept": "司机"},
    "0047": {"name": "单正康", "phone": "19951918249", "department": "司机", "sub_dept": "司机"},
    "0063": {"name": "谭婷婷", "phone": "15571406650", "department": "湖北驻厂", "sub_dept": "驻厂"},
}

# ================== 验证函数 ==================
def validate_id_card(id_card):
    if not id_card:
        return False, "身份证号不能为空"
    id_str = str(id_card).strip().upper()
    if len(id_str) != 18:
        return False, "身份证号必须是18位"
    if not re.match(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$', id_str):
        return False, "身份证号格式错误"
    return True, ""

def validate_phone(phone):
    if not phone:
        return False, "手机号不能为空"
    phone_str = str(phone).strip()
    if not phone_str.isdigit():
        return False, "手机号只能包含数字"
    if len(phone_str) != 11:
        return False, "手机号必须是11位"
    if phone_str[0] != '1':
        return False, "手机号必须以1开头"
    if phone_str[1] not in ['3', '4', '5', '6', '7', '8', '9']:
        return False, "手机号格式错误"
    return True, ""

def validate_name(name):
    if not name or not str(name).strip():
        return False, "姓名不能为空"
    name_str = str(name).strip()
    if len(name_str) < 2:
        return False, "姓名至少2个字符"
    if len(name_str) > 20:
        return False, "姓名不能超过20个字符"
    return True, ""

def validate_temp_worker(name, phone, id_card):
    errors = {}
    name_valid, name_msg = validate_name(name)
    if not name_valid:
        errors["name"] = name_msg
    phone_valid, phone_msg = validate_phone(phone)
    if not phone_valid:
        errors["phone"] = phone_msg
    id_valid, id_msg = validate_id_card(id_card)
    if not id_valid:
        errors["id_card"] = id_msg
    return len(errors) == 0, errors

# ================== 工号标准化函数 ==================
def normalize_worker_id(worker_id):
    if not worker_id:
        return None
    worker_id = str(worker_id).strip()
    if worker_id in FORMAL_WORKERS:
        return worker_id
    match = re.search(r'(\d{4})$', worker_id)
    if match:
        extracted_id = match.group(1)
        if extracted_id in FORMAL_WORKERS:
            return extracted_id
    return None

# ================== 数据持久化函数 ==================
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_excel(DATA_FILE)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df):
    if df is not None and not df.empty:
        try:
            df_to_save = df.drop(columns=['照片'], errors='ignore')
            df_to_save.to_excel(DATA_FILE, index=False)
        except:
            pass

# ================== 初始化 session_state ==================
if "daka_data" not in st.session_state:
    st.session_state.daka_data = load_data()
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
if "temp_info" not in st.session_state:
    st.session_state.temp_info = {}
if "current_worker_name" not in st.session_state:
    st.session_state.current_worker_name = None
if "last_scanned_id" not in st.session_state:
    st.session_state.last_scanned_id = None

st.set_page_config(page_title="荣基打卡", layout="wide", initial_sidebar_state="collapsed")
st.title("🏭 荣基精密｜现场打卡系统")

# ================== 辅助函数 ==================
def get_beijing_time():
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(timezone(timedelta(hours=8)))

def time_to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def add_watermark(img, name, lat, lon):
    draw = ImageDraw.Draw(img)
    now_str = get_beijing_time().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((10, img.height - 40), f"{name}｜{now_str}｜{lat:.6f},{lon:.6f}", fill="red")
    return img

# ================== 获取当前时间 ==================
beijing_now = get_beijing_time()
current_time = beijing_now.strftime("%H:%M")
today = beijing_now.strftime("%Y-%m-%d")
is_workday = beijing_now.weekday() < 5
current_minutes = time_to_minutes(current_time)

SIGN_IN_START_MIN = time_to_minutes(SIGN_IN_START)
SIGN_IN_END_MIN = time_to_minutes(SIGN_IN_END)
SIGN_OUT_START_MIN = time_to_minutes(SIGN_OUT_START)
SIGN_OUT_END_MIN = time_to_minutes(SIGN_OUT_END)

# ================== 定位UI ==================
with st.expander("📍 位置验证", expanded=not st.session_state.location_verified):
    col1, col2 = st.columns(2)
    with col1:
        lat_display = st.text_input("纬度", value=f"{st.session_state.user_lat:.6f}" if st.session_state.user_lat else "未获取", disabled=True)
    with col2:
        lon_display = st.text_input("经度", value=f"{st.session_state.user_lon:.6f}" if st.session_state.user_lon else "未获取", disabled=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📍 厂区定位", use_container_width=True):
            st.session_state.user_lat = FACTORY_LAT
            st.session_state.user_lon = FACTORY_LON
            st.session_state.location_verified = True
            st.rerun()
    with col_btn2:
        if st.button("🔄 重置", use_container_width=True):
            st.session_state.user_lat = None
            st.session_state.user_lon = None
            st.session_state.location_verified = False
            st.rerun()

if st.session_state.location_verified:
    distance = get_distance(st.session_state.user_lat, st.session_state.user_lon, FACTORY_LAT, FACTORY_LON)
    in_factory = distance <= ALLOW_RADIUS
    if in_factory:
        st.success(f"✅ 厂区内｜距离 {distance:.0f} 米")
        disabled = False
    else:
        st.error(f"❌ 不在厂区｜距离 {distance:.0f} 米")
        disabled = True
else:
    in_factory = False
    disabled = True

st.info(f"🕒 当前时间：{current_time} | {'工作日' if is_workday else '周末'}")

# ================== 员工类型选择 ==================
if not disabled:
    col_type1, col_type2 = st.columns(2)
    with col_type1:
        if st.button("🔖 正式工", use_container_width=True):
            st.session_state.worker_type = "formal"
            st.session_state.formal_worker_info = None
            st.session_state.selected_worker_id = None
            st.session_state.current_worker_name = None
            st.session_state.last_scanned_id = None
            st.rerun()
    with col_type2:
        if st.button("📝 临时工", use_container_width=True):
            st.session_state.worker_type = "temporary"
            st.session_state.formal_worker_info = None
            st.session_state.selected_worker_id = None
            st.session_state.temp_info = {}
            st.session_state.current_worker_name = None
            st.session_state.last_scanned_id = None
            st.rerun()

# ================== 正式工 ==================
formal_verified = False
if st.session_state.worker_type == "formal" and not disabled:
    st.subheader("🔖 正式工验证")
    scan_input = st.text_input("工号", placeholder="0001 / YL0001", key="manual_scan")
    if scan_input and scan_input != st.session_state.last_scanned_id:
        st.session_state.formal_worker_info = None
        st.session_state.selected_worker_id = None
        st.session_state.current_worker_name = None
        st.session_state.last_scanned_id = scan_input
        normalized_id = normalize_worker_id(scan_input)
        if normalized_id and normalized_id in FORMAL_WORKERS:
            st.session_state.formal_worker_info = FORMAL_WORKERS[normalized_id]
            st.session_state.selected_worker_id = normalized_id
            st.session_state.current_worker_name = FORMAL_WORKERS[normalized_id]['name']
            formal_verified = True
            st.success(f"✅ 识别成功：{FORMAL_WORKERS[normalized_id]['name']}")
            st.rerun()
        else:
            st.error(f"❌ 工号 {scan_input} 不存在")
            st.session_state.formal_worker_info = None
    if st.session_state.formal_worker_info and st.session_state.selected_worker_id:
        info = st.session_state.formal_worker_info
        formal_verified = True
        st.success(f"当前员工：{info['name']} | {info['department']} - {info['sub_dept']}")

# ================== 临时工 ==================
temp_valid = False
if st.session_state.worker_type == "temporary" and not disabled:
    st.subheader("📝 临时工信息填写")
    st.markdown("**⚠️ 请填写真实信息，信息错误将无法打卡**")
    col1, col2 = st.columns(2)
    with col1:
        temp_name = st.text_input("姓名 *", key="temp_name")
        temp_id_card = st.text_input("身份证号 *", key="temp_id")
    with col2:
        temp_phone = st.text_input("手机号 *", key="temp_phone")
        temp_workshop = st.selectbox("车间 *", ["冲压车间", "组装车间", "仓库"], key="temp_ws")
    temp_company = st.radio("劳务公司 *", ["苏州众达人力", "苏州博仁劳务", "苏州汇思人力", "苏州优才派遣", "其它"], horizontal=True)
    temp_other = st.text_input("请输入劳务公司全称") if temp_company == "其它" else ""
    is_valid, errors = validate_temp_worker(temp_name, temp_phone, temp_id_card)
    temp_valid = is_valid
    if temp_name or temp_phone or temp_id_card:
        if temp_valid:
            st.success("✅ 所有信息验证通过")
        else:
            st.error("❌ 信息验证失败，请修正后重试")
            for field, msg in errors.items():
                st.error(f"• {msg}")
    st.session_state.temp_info = {
        "name": temp_name if temp_name else "",
        "phone": temp_phone if temp_phone else "",
        "id_card": temp_id_card if temp_id_card else "",
        "workshop": temp_workshop,
        "job": "临时工",
        "company": temp_other if temp_company == "其它" else temp_company,
    }
    if temp_name and temp_valid:
        st.session_state.current_worker_name = temp_name

# ================== 拍照和打卡 ==================
st.divider()
st.subheader("📷 现场拍照")
st.markdown("**请拍摄本人照片（背景为厂区即可）**")

camera_col, info_col = st.columns([2, 1])
with camera_col:
    camera_image = st.camera_input("点击拍照", disabled=disabled or not in_factory, key="camera")
with info_col:
    if camera_image:
        st.success("✅ 照片已拍摄")
        st.caption("照片将添加水印后保存")
    else:
        st.info("📸 请点击上方相机拍照")

# ================== 打卡按钮 ==================
col_clock1, col_clock2 = st.columns(2)
formal_ok = (st.session_state.worker_type == "formal" and formal_verified)
temp_ok = (st.session_state.worker_type == "temporary" and temp_valid)
base_clock_ok = camera_image is not None and in_factory and st.session_state.location_verified
sign_in_ok = base_clock_ok and is_workday and (SIGN_IN_START_MIN <= current_minutes <= SIGN_IN_END_MIN) and (formal_ok or temp_ok)
clock_in = col_clock1.button("✅ 签到", use_container_width=True, disabled=not sign_in_ok)
sign_out_ok = base_clock_ok and is_workday and (SIGN_OUT_START_MIN <= current_minutes <= SIGN_OUT_END_MIN) and (formal_ok or temp_ok)
clock_out = col_clock2.button("🔚 签退", use_container_width=True, disabled=not sign_out_ok)

# ================== 提交打卡 ==================
clock_type = None
if clock_in:
    clock_type = "签到"
elif clock_out:
    clock_type = "签退"

if clock_type and camera_image and in_factory and st.session_state.location_verified:
    # 时间校验
    if clock_type == "签到":
        if not (SIGN_IN_START_MIN <= current_minutes <= SIGN_IN_END_MIN):
            st.error(f"❌ 签到时间：{SIGN_IN_START} - {SIGN_IN_END}")
            st.stop()
    else:
        if not (SIGN_OUT_START_MIN <= current_minutes <= SIGN_OUT_END_MIN):
            st.error(f"❌ 签退时间：{SIGN_OUT_START} - {SIGN_OUT_END}")
            st.stop()
    
    worker_name = None
    if st.session_state.worker_type == "formal" and st.session_state.formal_worker_info:
        info = st.session_state.formal_worker_info
        worker_name = info['name']
        worker_phone = info['phone']
        worker_id = "正式工"
        worker_company = f"正式工-{info['department']}"
        worker_workshop = info['sub_dept']
        worker_job = "正式员工"
    elif st.session_state.worker_type == "temporary" and st.session_state.temp_info.get("name"):
        t = st.session_state.temp_info
        is_valid, _ = validate_temp_worker(t.get("name", ""), t.get("phone", ""), t.get("id_card", ""))
        if is_valid:
            worker_name = t["name"]
            worker_phone = t["phone"]
            worker_id = t["id_card"]
            worker_company = t["company"]
            worker_workshop = t["workshop"]
            worker_job = t["job"]
        else:
            st.error("❌ 临时工信息验证失败")
    
    if worker_name:
        img = Image.open(camera_image)
        img = add_watermark(img, worker_name, st.session_state.user_lat, st.session_state.user_lon)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        
        work_h = ""
        if clock_type == "签退" and not st.session_state.daka_data.empty:
            mask = (st.session_state.daka_data["姓名"] == worker_name) & \
                   (st.session_state.daka_data["日期"] == today) & \
                   (st.session_state.daka_data["打卡类型"] == "签到")
            if mask.any():
                t1 = datetime.strptime(st.session_state.daka_data[mask].iloc[0]["打卡时间"], "%H:%M")
                t2 = datetime.strptime(current_time, "%H:%M")
                mins = int((t2 - t1).total_seconds() / 60)
                work_h = f"{mins // 60}小时{mins % 60}分钟"
        
        new_row = pd.DataFrame([{
            "日期": today, "打卡时间": current_time, "姓名": worker_name,
            "手机号": worker_phone, "身份证": worker_id, "劳务公司": worker_company,
            "车间": worker_workshop, "工种": worker_job, "打卡类型": clock_type,
            "工时": work_h, "纬度": st.session_state.user_lat, "经度": st.session_state.user_lon,
            "照片": img_bytes.getvalue()
        }])
        st.session_state.daka_data = pd.concat([st.session_state.daka_data, new_row], ignore_index=True)
        save_data(st.session_state.daka_data)
        st.success(f"✅ {clock_type}成功！{worker_name}")
        st.balloons()
        
        # 重置状态
        st.session_state.worker_type = None
        st.session_state.formal_worker_info = None
        st.session_state.temp_info = {}
        st.session_state.last_scanned_id = None
        st.rerun()

# ================== 查看记录 ==================
st.divider()
st.subheader("📋 我的打卡记录")
if st.button("查看今日记录"):
    worker_name = st.session_state.current_worker_name
    if not worker_name:
        if st.session_state.worker_type == "formal" and st.session_state.formal_worker_info:
            worker_name = st.session_state.formal_worker_info["name"]
        elif st.session_state.worker_type == "temporary" and st.session_state.temp_info.get("name"):
            worker_name = st.session_state.temp_info["name"]
    if not worker_name:
        st.warning("请先选择员工类型并输入工号/姓名")
    elif st.session_state.daka_data.empty:
        st.info("📭 暂无任何打卡记录")
    else:
        try:
            records = st.session_state.daka_data[
                (st.session_state.daka_data["日期"] == today) & 
                (st.session_state.daka_data["姓名"] == worker_name)
            ]
            if records.empty:
                st.info(f"📭 {worker_name} 今日暂无打卡记录")
            else:
                st.success(f"✅ {worker_name} 今日打卡记录")
                st.dataframe(records[["打卡时间", "打卡类型", "工时", "车间"]])
        except Exception as e:
            st.error(f"查询失败：{e}")

# ================== 管理员 ==================
st.divider()
with st.expander("🔐 管理员"):
    pwd = st.text_input("密码", type="password")
    if pwd == ADMIN_PASSWORD:
        st.success("登录成功")
        if not st.session_state.daka_data.empty:
            st.dataframe(st.session_state.daka_data)
            excel = io.BytesIO()
            st.session_state.daka_data.drop(columns=["照片"], errors="ignore").to_excel(excel, index=False)
            st.download_button("📥 导出", excel.getvalue(), "打卡记录.xlsx")
        else:
            st.info("暂无数据")
