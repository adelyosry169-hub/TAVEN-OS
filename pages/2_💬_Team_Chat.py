from datetime import datetime

import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Team Chat", page_icon="💬", layout="wide")
common.inject_theme_css()

st.title("💬 محادثة الشركاء")
st.caption("الشات ده مشترك بين التلاتة، وأي رسالة بتتبعت بتتحفظ فورًا عشان الكل يشوفها.")

PARTNER_OPTIONS = ["عادل 🇪🇸 (الإسباني)", "🇯🇵 الياباني", "🇷🇺 الروسي"]

col1, col2 = st.columns([1, 3])

with col1:
    sender = st.selectbox("انت مين؟", PARTNER_OPTIONS)
    if st.button("🔄 تحديث المحادثة"):
        st.rerun()

# بنقرأ فريش من الملف كل مرة (من غير كاش) عشان لو شريك تاني بعت
# رسالة من جهازه، تظهر عندك فورًا لما تحدّث الصفحة.
data = common.load_all_fresh()
chat_df = data["CHAT"]

with col2:
    st.subheader("آخر الرسائل")
    try:
        chat_box = st.container(height=420)
    except TypeError:
        # لو نسخة Streamlit قديمة ومش بتدعم height، بنرجع لكونتينر عادي
        chat_box = st.container()

    with chat_box:
        if chat_df.empty:
            st.caption("لسه مفيش رسائل... ابدأ المحادثة!")
        else:
            for _, row in chat_df.iterrows():
                st.markdown(f"**{row['Sender']}** — _{row['Time']}_")
                st.write(row["Message"])
                st.markdown("---")

msg = st.text_input("اكتب رسالتك هنا", key="chat_input")
if st.button("إرسال 📤"):
    if not msg.strip():
        common.angry_warning("مينفعش تبعت رسالة فاضية!")
    else:
        new_row = pd.DataFrame(
            [{"Time": datetime.now().strftime("%Y-%m-%d %H:%M"), "Sender": sender, "Message": msg}]
        )
        updated = pd.concat([chat_df, new_row], ignore_index=True)
        ok, err = common.save_sheet("CHAT", updated)
        if ok:
            st.success("اتبعتت!")
            st.rerun()
        else:
            st.error(err)
