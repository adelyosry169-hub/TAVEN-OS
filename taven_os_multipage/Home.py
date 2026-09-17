import streamlit as st
import common

st.set_page_config(
    page_title="TAVEN OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
common.inject_theme_css()

st.title("⚡ TAVEN OS")
st.caption("النظام الإداري والمالي لبراند TAVEN")

# لو المستخدم زار صفحة "Input & Output المالية" في نفس الجلسة، بنستخدم
# نفس النسخة اللي هو شغال عليها (حتى لو لسه مش محفوظة) عشان الداشبورد
# يفضل تفاعلي وحي من أول لحظة، مش بس بعد الحفظ في الإكسيل.
if "io_data" in st.session_state:
    d = st.session_state.io_data
else:
    fresh = common.load_all_fresh()
    d = {name: fresh[name] for name in common.SHEET_NAMES}

gross_val = d["SALES"]["Total Revenue"].sum() if "Total Revenue" in d["SALES"] else 0
realized = d["SALES"]["Amount Collected"].sum() if "Amount Collected" in d["SALES"] else 0
total_exp = (
    (d["FINANCE"]["Total"].sum() if "Total" in d["FINANCE"] else 0)
    + (d["OPERATIONS"]["Cost"].sum() if "Cost" in d["OPERATIONS"] else 0)
    + (d["EXTRA_EXPENSES"]["Total"].sum() if "Total" in d["EXTRA_EXPENSES"] else 0)
    + (d["MANUFACTURING"]["Total"].sum() if "Total" in d["MANUFACTURING"] else 0)
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
"""
)
