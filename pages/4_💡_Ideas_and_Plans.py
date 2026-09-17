from datetime import date

import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Ideas & Plans", page_icon="💡", layout="wide")
common.inject_theme_css()

st.title("💡 سجل الأفكار والخطط والكولكشن الجديد")

data = common.load_all_fresh()
ideas_df = data["IDEAS"]

col_table, col_form = st.columns([2, 1])

with col_table:
    st.subheader("السجل الحالي")
    edited = st.data_editor(ideas_df, num_rows="dynamic", use_container_width=True, key="ideas_editor")
    if st.button("💾 حفظ التعديلات"):
        ok, err = common.save_sheet("IDEAS", edited)
        if ok:
            st.success("تم الحفظ!")
        else:
            st.error(err)

with col_form:
    st.subheader("إضافة فكرة / خطة / اقتراح")
    idea_type = st.selectbox("النوع", ["فكرة", "خطة", "كولكشن جديد", "اقتراح عميل", "ملاحظة"])
    title = st.text_input("العنوان")
    notes = st.text_area("التفاصيل / النوتس")
    if st.button("+ إضافة"):
        if not title.strip():
            common.angry_warning("محتاج عنوان للفكرة الأول!")
        else:
            new_row = pd.DataFrame(
                [{"Date": str(date.today()), "Type": idea_type, "Title": title, "Notes": notes}]
            )
            updated = pd.concat([ideas_df, new_row], ignore_index=True)
            ok, err = common.save_sheet("IDEAS", updated)
            if ok:
                st.success("اتضافت!")
                st.rerun()
            else:
                st.error(err)

st.markdown("---")
st.subheader("🖼️ معرض صور الكولكشن")
images = st.file_uploader(
    "ارفع صور الموديلات/الكولكشن الجديد", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="idea_images"
)
if images:
    cols = st.columns(4)
    for i, img in enumerate(images):
        cols[i % 4].image(img, use_container_width=True)

st.caption(
    "ملحوظة: الصور دي بتتعرض للجلسة الحالية بس ومش بتتحفظ بشكل دائم على السيرفر "
    "لحد ما نربط تخزين خارجي (زي Google Drive أو S3) — قولّي لو عايز ده كخطوة جاية."
)
