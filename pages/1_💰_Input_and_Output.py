
from datetime import date
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Input & Output", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Input & Output", "إدارة القيود الأساسية: مبيعات، مصروفات، تصنيع، خامات وشركاء", "Input & Output")

data=common.load_all_fresh()
rev,collected,exp,profit=common.metrics(data)
a,b,c=st.columns(3)
with a: common.kpi("Sales",common.fmt_egp(rev))
with b: common.kpi("Collected",common.fmt_egp(collected))
with c: common.kpi("Expenses",common.fmt_egp(exp))

st.markdown("<br>",unsafe_allow_html=True)
section_key=st.selectbox("القسم",common.SHEET_NAMES,format_func=lambda k:f"{common.SECTIONS[k]['label']} — {common.SECTIONS[k]['arabic']}")
cfg=common.SECTIONS[section_key]
current=data[section_key]
left,right=st.columns([1.7,1])
with left:
    common.card_open(f"{cfg['label']} records","التعديل والحذف من الجدول يتم حفظه تلقائيًا.")
    edited=common.editable_table(section_key,current,key=f"table_{section_key}")
    if cfg.get("total_field") and not edited.empty:
        st.caption(f"الإجمالي: {common.fmt_egp(edited[cfg['total_field']].sum())}")
    common.card_close()
with right:
    common.card_open("Add record","أدخل البيانات ثم أضف القيد.")
    vals={}
    for f in cfg["fields"]:
        key=f"field_{section_key}_{f['name']}"
        if f["type"]=="text": vals[f["name"]]=st.text_input(f["label"],value=f.get("default",""),key=key)
        elif f["type"]=="int": vals[f["name"]]=st.number_input(f["label"],min_value=f.get("min",0),value=f.get("default",f.get("min",0)),step=f.get("step",1),key=key)
        elif f["type"]=="date": vals[f["name"]]=st.date_input(f["label"],value=date.today(),key=key)
        else: vals[f["name"]]=st.number_input(f["label"],min_value=float(f.get("min",0)),value=float(f.get("default",f.get("min",0))),step=float(f.get("step",1)),key=key)
    comp=cfg.get("computed_field")
    if comp:
        vals[comp["name"]]=float(vals[comp["of"][0]])*float(vals[comp["of"][1]])
        st.markdown(f"**الإجمالي المحسوب: {common.fmt_egp(vals[comp['name']])}**")
    req=next((f["name"] for f in cfg["fields"] if f["type"]=="text"),None)
    if st.button(cfg["add_label"],type="primary",use_container_width=True):
        if req and not str(vals.get(req,"")).strip():
            st.error("أكمل الحقل الأساسي أولًا.")
        else:
            vals["Date"]=str(vals.get("Date",date.today()))
            updated=pd.concat([current,pd.DataFrame([vals])],ignore_index=True)
            common.record_change(section_key,current)
            ok,err=common.save_sheet(section_key,updated)
            if ok: st.toast("تم الحفظ",icon="✓"); st.rerun()
            else: st.error(err)
    common.card_close()
common.end_page()
