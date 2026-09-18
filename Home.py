import streamlit as st
import common

st.set_page_config(
    page_title="TAVEN OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
common.inject_theme_css()
common.require_login()

st.markdown(
    "<h1 style='background: linear-gradient(135deg, #818cf8, #c084fc); "
    "-webkit-background-clip: text; -webkit-text-fill-color: transparent; "
    "font-weight:800;'>⚡ TAVEN OS</h1>",
    unsafe_allow_html=True,
)
st.caption("النظام الإداري والمالي لبراند TAVEN")

data = common.load_all_fresh()

gross_val = data["SALES"]["Total Revenue"].sum() if "Total Revenue" in data["SALES"] else 0
realized = data["SALES"]["Amount Collected"].sum() if "Amount Collected" in data["SALES"] else 0
total_exp = (
    (data["FINANCE"]["Total"].sum() if "Total" in data["FINANCE"] else 0)
    + (data["OPERATIONS"]["Cost"].sum() if "Cost" in data["OPERATIONS"] else 0)
    + (data["EXTRA_EXPENSES"]["Total"].sum() if "Total" in data["EXTRA_EXPENSES"] else 0)
    + (data["MANUFACTURING"]["Total"].sum() if "Total" in data["MANUFACTURING"] else 0)
)
net_profit = realized - total_exp

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gross Val (إجمالي المبيعات)", f"{gross_val:,.0f} EGP")
m2.metric("Realized (المحصّل فعليًا)", f"{realized:,.0f} EGP")
m3.metric("Total Exp (كل المصاريف)", f"{total_exp:,.0f} EGP")
m4.metric("Net Profit (صافي الربح)", f"{net_profit:,.0f} EGP")

st.markdown("---")
st.markdown(
    """
استخدم القائمة على الشمال ⬅️ للتنقل بين الصفحات:

- 💰 **Input & Output المالية** — الشركاء، المصاريف، العمليات، التصنيع، والمبيعات
- 💬 **Team Chat** — محادثة الشركاء التلاتة
- 📁 **Files & Analysis** — رفع ملفات إكسيل/داتا وتحليلها فورًا
- 💡 **Ideas & Plans** — سجل الأفكار، الكولكشن الجديد، النوتس، وصور
- 📢 **Ads Manager** — متابعة كامبينات ميتا وصرفها اليومي/الشهري
- ✅ **Tasks** — توزيع التاسكات ومتابعة استلامها وتسليمها
- 🎯 **Vision & Targets** — الأهداف الشهرية والثانوية وهل اتحققت ولا لأ
- 📊 **Analytics** — رسوم بيانية تفاعلية لكل حاجة
"""
)
