import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Files & Analysis", page_icon="📁", layout="wide")
common.inject_theme_css()
common.require_login()

st.title("📁 رفع الملفات والتحليل المالي")
st.caption("ارفع ملف إكسيل أو CSV وهيتحول لجدول جوا التطبيق مع تحليل سريع للأرقام.")

uploaded_files = st.file_uploader(
    "ارفع ملف واحد أو أكتر", type=["xlsx", "xls", "csv"], accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        st.markdown("---")
        st.subheader(f"📄 {file.name}")
        try:
            if file.name.lower().endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            st.error(f"تعذر قراءة الملف: {e}")
            continue

        st.dataframe(df, use_container_width=True)

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            st.markdown("#### 📊 ملخص إحصائي")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)

            chosen = st.selectbox(
                f"اختار عمود لعرضه كرسم بياني ({file.name})",
                numeric_cols,
                key=f"chart_col_{file.name}",
            )
            st.bar_chart(df[chosen])

            st.markdown("#### 💰 إجماليات سريعة")
            totals_cols = st.columns(min(len(numeric_cols), 4))
            for i, col_name in enumerate(numeric_cols[:4]):
                totals_cols[i].metric(col_name, f"{df[col_name].sum():,.2f}")
        else:
            st.info("مفيش أعمدة أرقام في الملف ده نقدر نحلّلها.")
else:
    st.info("ارفع ملف عشان تشوف الجدول والتحليل بتاعه هنا.")

st.markdown("---")
st.caption(
    "ملحوظة: الملفات المرفوعة هنا بتتحلل لحظيًا في الصفحة بس، ومش بتتحفظ بشكل "
    "دائم على السيرفر. لو عايز الملف يتحول لشيت دائم في TAVEN.xlsx يتحدث منه، "
    "قولّي وهنضيف زرار 'حفظ كشيت دائم'."
)
