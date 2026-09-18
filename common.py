
import os
from datetime import date
import pandas as pd
import streamlit as st
import gdrive

EXCEL_FILE = "TAVEN.xlsx"
MAX_HISTORY = 10

SECTIONS = {
    "PARTNERS": {
        "label": "Partners", "arabic": "الشركاء",
        "columns": ["Partner", "Contribution", "Purpose", "Date"],
        "fields": [
            {"name":"Partner","label":"اسم الشريك","type":"text"},
            {"name":"Contribution","label":"المساهمة (EGP)","type":"number","min":0.0,"step":1000.0},
            {"name":"Purpose","label":"الغرض من المساهمة","type":"text"},
            {"name":"Date","label":"التاريخ","type":"date"}],
        "total_field":"Contribution","add_label":"إضافة مساهمة"},
    "FINANCE": {
        "label":"Finance","arabic":"المالية",
        "columns":["Category","Subcategory","Qty","Unit Cost","Total","Date"],
        "fields":[
            {"name":"Category","label":"النوع","type":"text","default":"Fabric"},
            {"name":"Subcategory","label":"الوصف","type":"text","default":"Cotton"},
            {"name":"Qty","label":"الكمية","type":"int","min":1,"default":1,"step":1},
            {"name":"Unit Cost","label":"سعر الوحدة (EGP)","type":"number","min":0.0,"step":10.0},
            {"name":"Date","label":"التاريخ","type":"date"}],
        "computed_field":{"name":"Total","of":["Qty","Unit Cost"]},
        "total_field":"Total","add_label":"تسجيل مصروف"},
    "OPERATIONS": {
        "label":"Operations","arabic":"العمليات",
        "columns":["Material","Weight","Cost/KG","Supplier","Cost","Date"],
        "fields":[
            {"name":"Material","label":"اسم الخام","type":"text"},
            {"name":"Weight","label":"الوزن (KG)","type":"number","min":0.1,"default":1.0,"step":1.0},
            {"name":"Cost/KG","label":"سعر الكيلو (EGP)","type":"number","min":0.0,"step":10.0},
            {"name":"Supplier","label":"المورد","type":"text"},
            {"name":"Date","label":"التاريخ","type":"date"}],
        "computed_field":{"name":"Cost","of":["Weight","Cost/KG"]},
        "total_field":"Cost","add_label":"تسجيل خام"},
    "EXTRA_EXPENSES": {
        "label":"Other Expenses","arabic":"مصاريف إضافية",
        "columns":["Expense Name","Qty","Unit Cost","Total","Notes","Date"],
        "fields":[
            {"name":"Expense Name","label":"اسم المصروف","type":"text"},
            {"name":"Qty","label":"الكمية","type":"int","min":1,"default":1,"step":1},
            {"name":"Unit Cost","label":"سعر الوحدة (EGP)","type":"number","min":0.0,"step":10.0},
            {"name":"Notes","label":"ملاحظات","type":"text"},
            {"name":"Date","label":"التاريخ","type":"date"}],
        "computed_field":{"name":"Total","of":["Qty","Unit Cost"]},
        "total_field":"Total","add_label":"إضافة مصروف"},
    "SALES": {
        "label":"Sales","arabic":"المبيعات",
        "columns":["Product","Qty Sold","Unit Price","Total Revenue","Amount Collected","Date"],
        "fields":[
            {"name":"Product","label":"اسم المنتج","type":"text"},
            {"name":"Qty Sold","label":"الكمية المباعة","type":"int","min":1,"default":1,"step":1},
            {"name":"Unit Price","label":"سعر البيع للوحدة (EGP)","type":"number","min":0.0,"step":10.0},
            {"name":"Amount Collected","label":"المبلغ المحصّل فعليًا (EGP)","type":"number","min":0.0,"step":100.0},
            {"name":"Date","label":"التاريخ","type":"date"}],
        "computed_field":{"name":"Total Revenue","of":["Qty Sold","Unit Price"]},
        "total_field":"Total Revenue","add_label":"تسجيل عملية بيع"},
    "MANUFACTURING": {
        "label":"Manufacturing","arabic":"التصنيع",
        "columns":["Factory","Model","Qty","Unit Price","Total","Date"],
        "fields":[
            {"name":"Factory","label":"اسم المصنع","type":"text"},
            {"name":"Model","label":"اسم الموديل","type":"text"},
            {"name":"Qty","label":"الكمية","type":"int","min":1,"default":1,"step":1},
            {"name":"Unit Price","label":"سعر القطعة (EGP)","type":"number","min":0.0,"step":10.0},
            {"name":"Date","label":"التاريخ","type":"date"}],
        "computed_field":{"name":"Total","of":["Qty","Unit Price"]},
        "total_field":"Total","add_label":"تسجيل أمر تصنيع"},
}
SHEET_NAMES = list(SECTIONS.keys())
EXTRA_SHEETS_COLUMNS = {
    "CHAT":["Time","Sender","Message"],
    "IDEAS":["Date","Type","Title","Notes"],
    "ADS_CAMPAIGNS":["Campaign Name","Daily Spend","Monthly Spend"],
    "TASKS":["ID","Description","Type","Assigned To","Status","Claimed By"],
    "VISION":["Target Name","Type","Target Value","Actual Value"],
}
ALL_SHEETS = SHEET_NAMES + list(EXTRA_SHEETS_COLUMNS.keys())

def _default_for(name):
    cols = SECTIONS[name]["columns"] if name in SECTIONS else EXTRA_SHEETS_COLUMNS[name]
    return pd.DataFrame(columns=cols)

def load_all_fresh():
    if gdrive.is_configured():
        try: gdrive.download_file(EXCEL_FILE)
        except Exception: pass
    data = {}
    if os.path.exists(EXCEL_FILE):
        try:
            xls = pd.ExcelFile(EXCEL_FILE)
            for name in ALL_SHEETS:
                if name in xls.sheet_names:
                    data[name] = pd.read_excel(xls, sheet_name=name)
        except Exception as e:
            st.warning(f"تعذر قراءة البيانات: {e}")
    for name in ALL_SHEETS:
        data.setdefault(name, _default_for(name))
    return data

def save_sheet(name, df):
    data = load_all_fresh()
    data[name] = df
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for n, d in data.items():
                d.to_excel(writer, sheet_name=n, index=False)
    except PermissionError:
        return False, "ملف TAVEN.xlsx مفتوح في برنامج آخر. اقفله ثم حاول مرة أخرى."
    except Exception as e:
        return False, str(e)
    if gdrive.is_configured():
        try: gdrive.upload_file(EXCEL_FILE)
        except Exception as e: return False, f"تم الحفظ محليًا لكن فشل Google Drive: {e}"
    return True, None

def _history(name):
    key = f"_history_{name}"
    if key not in st.session_state:
        st.session_state[key] = {"past":[],"future":[]}
    return st.session_state[key]

def record_change(name, df_before):
    h = _history(name)
    h["past"].append(df_before.copy())
    h["past"] = h["past"][-MAX_HISTORY:]
    h["future"].clear()

def undo_redo_controls(name, current_df):
    h = _history(name)
    c1,c2,_ = st.columns([1,1,5])
    if c1.button("تراجع", key=f"undo_{name}", disabled=not h["past"]):
        h["future"].append(current_df.copy())
        save_sheet(name, h["past"].pop())
        st.rerun()
    if c2.button("إعادة", key=f"redo_{name}", disabled=not h["future"]):
        h["past"].append(current_df.copy())
        save_sheet(name, h["future"].pop())
        st.rerun()

def editable_table(name, df, num_rows="dynamic", key=None, show_undo=True):
    if show_undo: undo_redo_controls(name, df)
    edited = st.data_editor(df, num_rows=num_rows, use_container_width=True, key=key or f"editor_{name}", hide_index=True)
    if not edited.equals(df):
        record_change(name, df)
        ok, err = save_sheet(name, edited)
        if ok: st.toast("تم الحفظ تلقائيًا", icon="✓")
        else: st.error(err)
        return edited
    return df

def inject_theme_css():
    st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
 --taven-bg:#f7f8fa;--taven-card:#fff;--taven-border:#e5e7eb;--taven-text:#111827;
 --taven-muted:#6b7280;--taven-brand:#4f46e5;--taven-brand2:#4338ca;--taven-soft:#eef2ff;
}
html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif}
.stApp{background:var(--taven-bg)}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--taven-border)}
[data-testid="stSidebar"]>div:first-child{padding-top:1.2rem}
.taven-brand{padding:4px 8px 18px;border-bottom:1px solid var(--taven-border);margin-bottom:18px}
.taven-brand .logo{font-size:23px;font-weight:800;letter-spacing:-.8px;color:#111827}
.taven-brand .sub{font-size:11px;color:var(--taven-muted);margin-top:3px}
.taven-page{animation:tavenIn .35s ease-out}
@keyframes tavenIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
.taven-title{font-size:28px;font-weight:800;letter-spacing:-.7px;color:var(--taven-text);margin:2px 0 3px}
.taven-subtitle{color:var(--taven-muted);font-size:13px;margin-bottom:20px}
.taven-section{background:#fff;border:1px solid var(--taven-border);border-radius:14px;padding:18px 18px 12px;box-shadow:0 1px 2px rgba(15,23,42,.03);margin-bottom:16px}
.kpi{background:#fff;border:1px solid var(--taven-border);border-radius:14px;padding:17px 18px;box-shadow:0 1px 2px rgba(15,23,42,.03);min-height:112px}
.kpi-label{font-size:12px;color:var(--taven-muted);font-weight:600}
.kpi-value{font-size:25px;font-weight:800;color:var(--taven-text);margin-top:8px;letter-spacing:-.5px}
.kpi-note{font-size:11px;color:var(--taven-muted);margin-top:6px}
.badge{display:inline-block;padding:4px 9px;border-radius:999px;font-size:11px;font-weight:700}
.badge-green{background:#ecfdf3;color:#047857}.badge-blue{background:#eef2ff;color:#4338ca}.badge-amber{background:#fffbeb;color:#b45309}.badge-gray{background:#f3f4f6;color:#4b5563}
.stButton>button{border-radius:9px;border:1px solid #d1d5db;background:#fff;color:#111827;font-weight:600;transition:.15s}
.stButton>button:hover{border-color:#a5b4fc;color:#3730a3;transform:translateY(-1px)}
button[kind="primary"]{background:var(--taven-brand)!important;border-color:var(--taven-brand)!important;color:#fff!important}
div[data-testid="stMetric"]{background:#fff;border:1px solid var(--taven-border);border-radius:14px;padding:13px 16px}
div[data-baseweb="input"]>div,div[data-baseweb="select"]>div,textarea{border-radius:9px}
[data-testid="stDataFrame"]{border:1px solid var(--taven-border);border-radius:12px;overflow:hidden}
hr{border-color:var(--taven-border)}
@media(max-width:800px){.taven-title{font-size:23px}.kpi-value{font-size:20px}.taven-section{padding:13px}}
</style>
""", unsafe_allow_html=True)

def app_shell(active="Dashboard"):
    with st.sidebar:
        st.markdown('<div class="taven-brand"><div class="logo">TAVEN CO</div><div class="sub">Business Operating System</div></div>', unsafe_allow_html=True)
        nav = {
            "Dashboard":"Home.py",
            "Input & Output":"pages/1_💰_Input_and_Output.py",
            "Team Chat":"pages/2_💬_Team_Chat.py",
            "Files & Analysis":"pages/3_📁_Files_and_Analysis.py",
            "Ideas & Plans":"pages/4_💡_Ideas_and_Plans.py",
            "Ads Manager":"pages/5_📢_Ads_Manager.py",
            "Tasks":"pages/6_✅_Tasks.py",
            "Vision & Targets":"pages/7_🎯_Vision.py",
            "Analytics":"pages/8_📊_Analytics.py",
        }
        for label, path in nav.items():
            if label == active:
                st.markdown(f'<div style="background:#eef2ff;color:#4338ca;border-radius:9px;padding:9px 11px;font-weight:700;margin:3px 0">{label}</div>', unsafe_allow_html=True)
            else:
                try: st.page_link(path, label=label)
                except Exception: st.markdown(f"**{label}**")
        st.markdown("---")
        st.caption("Data")
        st.caption(gdrive.status_message())

def page_header(title, subtitle="", active="Dashboard"):
    app_shell(active)
    st.markdown('<div class="taven-page">', unsafe_allow_html=True)
    st.markdown(f'<div class="taven-title">{title}</div>', unsafe_allow_html=True)
    if subtitle: st.markdown(f'<div class="taven-subtitle">{subtitle}</div>', unsafe_allow_html=True)

def end_page():
    st.markdown("</div>", unsafe_allow_html=True)

def kpi(label, value, note=""):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>', unsafe_allow_html=True)

def card_open(title=None, subtitle=None):
    st.markdown('<div class="taven-section">', unsafe_allow_html=True)
    if title: st.markdown(f"**{title}**")
    if subtitle: st.caption(subtitle)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def fmt_egp(v):
    try: return f"{float(v):,.0f} EGP"
    except: return "0 EGP"

def metrics(data):
    sales=data["SALES"]; fin=data["FINANCE"]; ops=data["OPERATIONS"]; extra=data["EXTRA_EXPENSES"]; manu=data["MANUFACTURING"]
    revenue=float(sales["Total Revenue"].sum()) if "Total Revenue" in sales else 0
    collected=float(sales["Amount Collected"].sum()) if "Amount Collected" in sales else 0
    expenses=sum(float(df[col].sum()) if col in df else 0 for df,col in [(fin,"Total"),(ops,"Cost"),(extra,"Total"),(manu,"Total")])
    return revenue,collected,expenses,collected-expenses
