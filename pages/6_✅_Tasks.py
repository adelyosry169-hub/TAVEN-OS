
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Tasks", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Tasks","توزيع ومتابعة المهام بين الفريق","Tasks")
df=common.load_all_fresh()["TASKS"]
open_n=int((df["Status"]=="مفتوح").sum()) if "Status" in df else 0
doing=int((df["Status"]=="تحت التنفيذ").sum()) if "Status" in df else 0
done=int((df["Status"]=="تم").sum()) if "Status" in df else 0
a,b,c=st.columns(3)
with a: common.kpi("Open",str(open_n))
with b: common.kpi("In progress",str(doing))
with c: common.kpi("Done",str(done))
common.card_open("New task")
c1,c2,c3=st.columns(3)
desc=c1.text_input("وصف التاسك"); typ=c2.text_input("النوع"); assigned=c3.text_input("موزع على")
if st.button("إضافة تاسك",type="primary"):
    next_id=1 if df.empty else int(pd.to_numeric(df["ID"],errors="coerce").max())+1
    row={"ID":next_id,"Description":desc,"Type":typ,"Assigned To":assigned,"Status":"مفتوح","Claimed By":""}
    if not desc.strip(): st.error("اكتب وصف التاسك.")
    else:
        ok,err=common.save_sheet("TASKS",pd.concat([df,pd.DataFrame([row])],ignore_index=True))
        if ok: st.toast("تمت الإضافة",icon="✓"); st.rerun()
        else: st.error(err)
common.card_close()
common.card_open("Task board")
if df.empty: st.info("لا توجد مهام.")
for _,r in df.iterrows():
    cols=st.columns([3,1.3,1.5,1])
    cols[0].markdown(f"**#{r['ID']} — {r['Description']}**\n\n{r.get('Type','')} · {r.get('Assigned To','')}")
    status=r.get("Status","مفتوح")
    cols[1].markdown(f'<span class="badge badge-{"green" if status=="تم" else "blue" if status=="تحت التنفيذ" else "amber"}">{status}</span>',unsafe_allow_html=True)
    if status=="مفتوح":
        who=cols[2].text_input("اسمك",key=f"who_{r['ID']}",label_visibility="collapsed",placeholder="اسمك")
        if cols[3].button("استلام",key=f"claim_{r['ID']}"):
            fresh=common.load_all_fresh()["TASKS"]; idx=fresh.index[fresh["ID"]==r["ID"]]
            if len(idx):
                fresh.loc[idx[0],"Status"]="تحت التنفيذ"; fresh.loc[idx[0],"Claimed By"]=who
                common.save_sheet("TASKS",fresh); st.rerun()
    elif status=="تحت التنفيذ":
        cols[2].caption(f"عند: {r.get('Claimed By','')}")
        if cols[3].button("إنهاء",key=f"done_{r['ID']}"):
            fresh=common.load_all_fresh()["TASKS"]; idx=fresh.index[fresh["ID"]==r["ID"]]
            if len(idx): fresh.loc[idx[0],"Status"]="تم"; common.save_sheet("TASKS",fresh); st.rerun()
    else: cols[2].caption(f"بواسطة: {r.get('Claimed By','')}")
common.card_close(); common.end_page()
