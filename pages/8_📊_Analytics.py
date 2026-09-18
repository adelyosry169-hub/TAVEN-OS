
import pandas as pd
import plotly.express as px
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Analytics", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Analytics","لوحة تحليل مالية وتشغيلية مبنية على بيانات TAVEN","Analytics")
data=common.load_all_fresh()
revenue,collected,expenses,profit=common.metrics(data)
receivables=revenue-collected
a,b,c,d=st.columns(4)
with a: common.kpi("Revenue",common.fmt_egp(revenue))
with b: common.kpi("Collected",common.fmt_egp(collected))
with c: common.kpi("Receivables",common.fmt_egp(receivables))
with d: common.kpi("Net result",common.fmt_egp(profit))
st.markdown("<br>",unsafe_allow_html=True)
left,right=st.columns(2)
with left:
    common.card_open("Expense mix")
    vals={"Finance":float(data["FINANCE"]["Total"].sum()),"Operations":float(data["OPERATIONS"]["Cost"].sum()),"Other":float(data["EXTRA_EXPENSES"]["Total"].sum()),"Manufacturing":float(data["MANUFACTURING"]["Total"].sum())}
    vals={k:v for k,v in vals.items() if v>0}
    if vals:
        fig=px.pie(names=list(vals),values=list(vals),hole=.55)
        fig.update_layout(height=320,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else: st.info("لا توجد مصروفات كافية للتحليل.")
    common.card_close()
with right:
    common.card_open("Sales by product")
    sdf=data["SALES"]
    if not sdf.empty and "Product" in sdf and "Total Revenue" in sdf:
        g=sdf.groupby("Product",as_index=False)["Total Revenue"].sum().sort_values("Total Revenue",ascending=False)
        fig=px.bar(g,x="Product",y="Total Revenue")
        fig.update_layout(height=320,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)",showlegend=False)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    else: st.info("لا توجد مبيعات كافية للتحليل.")
    common.card_close()
common.card_open("Revenue vs expenses")
def ser(df,col):
    if df.empty or "Date" not in df or col not in df: return pd.Series(dtype=float)
    x=df.copy(); x["Date"]=pd.to_datetime(x["Date"],errors="coerce"); x=x.dropna(subset=["Date"])
    return x.groupby(x["Date"].dt.date)[col].sum()
rs=ser(data["SALES"],"Total Revenue")
es=pd.concat([ser(data["FINANCE"],"Total"),ser(data["OPERATIONS"],"Cost"),ser(data["EXTRA_EXPENSES"],"Total"),ser(data["MANUFACTURING"],"Total")]).groupby(level=0).sum()
chart=pd.concat([rs.rename("Revenue"),es.rename("Expenses")],axis=1).fillna(0).reset_index(names="Date")
if not chart.empty:
    fig=px.line(chart,x="Date",y=["Revenue","Expenses"],markers=True)
    fig.update_layout(height=350,margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
else: st.info("أضف بيانات بتاريخ لعرض الاتجاه.")
common.card_close()
common.end_page()
