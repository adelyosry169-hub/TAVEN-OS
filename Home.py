
import streamlit as st
import pandas as pd
import plotly.express as px
import common

st.set_page_config(page_title="TAVEN CO", page_icon="T", layout="wide", initial_sidebar_state="expanded")
common.inject_theme_css()
data = common.load_all_fresh()
common.page_header("Dashboard", "ملخص لحظي للأداء المالي والتشغيلي", "Dashboard")

revenue, collected, expenses, profit = common.metrics(data)
receivables = revenue - collected
m1,m2,m3,m4 = st.columns(4)
with m1: common.kpi("Revenue", common.fmt_egp(revenue), "إجمالي قيمة المبيعات")
with m2: common.kpi("Collected", common.fmt_egp(collected), "المحصّل فعليًا")
with m3: common.kpi("Expenses", common.fmt_egp(expenses), "إجمالي المصروفات والتصنيع")
with m4: common.kpi("Net Result", common.fmt_egp(profit), "المحصّل ناقص المصروفات")

st.markdown("<br>", unsafe_allow_html=True)
left,right = st.columns([1.55,1])
with left:
    common.card_open("Revenue vs Expenses", "اتجاه يومي بناءً على البيانات المسجلة")
    def series(df,col):
        if df.empty or "Date" not in df or col not in df: return pd.Series(dtype=float)
        x=df.copy(); x["Date"]=pd.to_datetime(x["Date"],errors="coerce"); x=x.dropna(subset=["Date"])
        return x.groupby(x["Date"].dt.date)[col].sum()
    rs=series(data["SALES"],"Total Revenue")
    es=pd.concat([series(data["FINANCE"],"Total"),series(data["OPERATIONS"],"Cost"),series(data["EXTRA_EXPENSES"],"Total"),series(data["MANUFACTURING"],"Total")]).groupby(level=0).sum()
    chart=pd.concat([rs.rename("Revenue"),es.rename("Expenses")],axis=1).fillna(0).reset_index(names="Date")
    if not chart.empty:
        fig=px.line(chart,x="Date",y=["Revenue","Expenses"],markers=True)
        fig.update_layout(height=310,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",legend_title_text="")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else: st.info("أضف أول عملية بيع أو مصروف لبدء الرسم البياني.")
    common.card_close()

with right:
    common.card_open("Cash Position", "المبالغ المحصّلة مقابل المصروفات")
    st.markdown(f"### {common.fmt_egp(collected-expenses)}")
    st.caption("صافي الحركة النقدية المسجلة")
    st.progress(min(max((collected/(expenses or 1)),0),1))
    st.markdown(f"**Receivables:** {common.fmt_egp(receivables)}")
    st.markdown(f"**Collection rate:** {(collected/revenue*100 if revenue else 0):.1f}%")
    common.card_close()

common.card_open("Quick access")
q=st.columns(4)
for i,(title,desc,path) in enumerate([
    ("Sales","تسجيل ومراجعة المبيعات","pages/1_💰_Input_and_Output.py"),
    ("Expenses","المصاريف والعمليات","pages/1_💰_Input_and_Output.py"),
    ("Tasks","متابعة التنفيذ","pages/6_✅_Tasks.py"),
    ("Analytics","تقارير وتحليلات","pages/8_📊_Analytics.py")]):
    with q[i]:
        st.markdown(f"**{title}**")
        st.caption(desc)
        try: st.page_link(path,label="فتح")
        except: pass

common.card_close()
common.end_page()
