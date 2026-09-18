import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Analytics", page_icon="📊", layout="wide")
common.inject_theme_css()
common.require_login()

st.title("📊 التحليل المالي الشامل")

data = common.load_all_fresh()

finance_df = data["FINANCE"]
ops_df = data["OPERATIONS"]
extra_df = data["EXTRA_EXPENSES"]
manu_df = data["MANUFACTURING"]
sales_df = data["SALES"]

# ================== المؤشرات الرئيسية ==================
gross_val = sales_df["Total Revenue"].sum() if "Total Revenue" in sales_df else 0
realized = sales_df["Amount Collected"].sum() if "Amount Collected" in sales_df else 0
fin_total = finance_df["Total"].sum() if "Total" in finance_df else 0
ops_total = ops_df["Cost"].sum() if "Cost" in ops_df else 0
extra_total = extra_df["Total"].sum() if "Total" in extra_df else 0
manu_total = manu_df["Total"].sum() if "Total" in manu_df else 0
total_exp = fin_total + ops_total + extra_total + manu_total
net_profit = realized - total_exp

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gross Val", f"{gross_val:,.0f} EGP")
m2.metric("Realized", f"{realized:,.0f} EGP")
m3.metric("Total Exp", f"{total_exp:,.0f} EGP")
m4.metric("Net Profit", f"{net_profit:,.0f} EGP", delta=f"{net_profit:,.0f}")

st.markdown("---")

# ألوان متناسقة مع ثيم التطبيق
PLOTLY_TEMPLATE = "plotly_dark"
ACCENT_COLORS = ["#6366f1", "#a78bfa", "#f472b6", "#fb923c", "#34d399", "#60a5fa"]

col1, col2 = st.columns(2)

# ================== توزيع المصاريف حسب المصدر ==================
with col1:
    st.subheader("🧾 توزيع المصاريف حسب المصدر")
    breakdown = {
        "Finance": fin_total,
        "Operations": ops_total,
        "Extra Expenses": extra_total,
        "Manufacturing": manu_total,
    }
    breakdown = {k: v for k, v in breakdown.items() if v > 0}
    if breakdown:
        fig = px.pie(
            names=list(breakdown.keys()),
            values=list(breakdown.values()),
            hole=0.45,
            color_discrete_sequence=ACCENT_COLORS,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لسه مفيش بيانات مصاريف كفاية نرسمها.")

# ================== المبيعات حسب المنتج ==================
with col2:
    st.subheader("🛍️ المبيعات حسب المنتج")
    if not sales_df.empty and "Product" in sales_df.columns and "Total Revenue" in sales_df.columns:
        grouped = sales_df.groupby("Product", as_index=False)["Total Revenue"].sum()
        fig = px.bar(
            grouped,
            x="Product",
            y="Total Revenue",
            color="Product",
            color_discrete_sequence=ACCENT_COLORS,
            template=PLOTLY_TEMPLATE,
        )
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لسه مفيش بيانات مبيعات كفاية نرسمها.")

st.markdown("---")

# ================== الإيراد مقابل المصاريف عبر الوقت ==================
st.subheader("📈 الإيراد مقابل المصاريف عبر الوقت")


def _daily_series(df, value_col, date_col="Date"):
    if df.empty or date_col not in df.columns or value_col not in df.columns:
        return pd.Series(dtype=float)
    tmp = df.copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna(subset=[date_col])
    return tmp.groupby(tmp[date_col].dt.date)[value_col].sum()


revenue_series = _daily_series(sales_df, "Total Revenue")
expenses_series = pd.concat(
    [
        _daily_series(finance_df, "Total"),
        _daily_series(ops_df, "Cost"),
        _daily_series(extra_df, "Total"),
        _daily_series(manu_df, "Total"),
    ]
).groupby(level=0).sum()

if revenue_series.empty and expenses_series.empty:
    st.info("لسه مفيش تواريخ كفاية في البيانات عشان نرسم الاتجاه عبر الوقت. أضف تواريخ للسجلات في صفحة Input & Output.")
else:
    fig = go.Figure()
    if not revenue_series.empty:
        fig.add_trace(go.Scatter(
            x=list(revenue_series.index), y=list(revenue_series.values),
            mode="lines+markers", name="الإيراد", line=dict(color="#34d399", width=3),
        ))
    if not expenses_series.empty:
        fig.add_trace(go.Scatter(
            x=list(expenses_series.index), y=list(expenses_series.values),
            mode="lines+markers", name="المصاريف", line=dict(color="#f87171", width=3),
        ))
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ================== مساهمات الشركاء ==================
st.subheader("🤝 مساهمات الشركاء")
partners_df = data["PARTNERS"]
if not partners_df.empty and "Partner" in partners_df.columns and "Contribution" in partners_df.columns:
    fig = px.bar(
        partners_df, x="Partner", y="Contribution", color="Partner",
        color_discrete_sequence=ACCENT_COLORS, template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("لسه مفيش مساهمات شركاء متسجلة.")
