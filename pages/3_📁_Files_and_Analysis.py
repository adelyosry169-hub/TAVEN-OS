
import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN CO — Files & Analysis", page_icon="T", layout="wide")
common.inject_theme_css()
common.page_header("Files & Analysis","حلل Excel وCSV بسرعة داخل مساحة العمل","Files & Analysis")
uploads=st.file_uploader("رفع ملفات",type=["xlsx","xls","csv"],accept_multiple_files=True)
if not uploads:
    common.card_open("Upload a file","الملفات هنا تُحلل داخل الجلسة ولا تُضاف تلقائيًا إلى TAVEN.xlsx.")
    st.info("ارفع Excel أو CSV للبدء.")
    common.card_close()
for file in uploads:
    try: df=pd.read_csv(file) if file.name.lower().endswith(".csv") else pd.read_excel(file)
    except Exception as e: st.error(f"{file.name}: {e}"); continue
    common.card_open(file.name,f"{len(df):,} rows · {len(df.columns):,} columns")
    st.dataframe(df,use_container_width=True,hide_index=True)
    nums=df.select_dtypes(include="number").columns.tolist()
    if nums:
        cols=st.columns(min(4,len(nums)))
        for i,c in enumerate(nums[:4]):
            with cols[i]: common.kpi(c,f"{df[c].sum():,.2f}",f"متوسط {df[c].mean():,.2f}")
        chosen=st.selectbox("اختيار عمود للرسم",nums,key=f"chart_{file.name}")
        st.bar_chart(df[chosen])
    common.card_close()
common.end_page()
