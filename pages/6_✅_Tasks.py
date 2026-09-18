import pandas as pd
import streamlit as st
import common

st.set_page_config(page_title="TAVEN OS - Tasks", page_icon="✅", layout="wide")
common.inject_theme_css()
common.require_login()

st.title("✅ التاسكات")

data = common.load_all_fresh()
tasks_df = data["TASKS"]

next_id = 1 if tasks_df.empty or "ID" not in tasks_df else int(tasks_df["ID"].max()) + 1

st.subheader("➕ توزيع تاسك جديد")
c1, c2, c3 = st.columns(3)
desc = c1.text_input("وصف التاسك")
ttype = c2.text_input("نوع التاسك")
assigned = c3.text_input("موزّع على مين؟ (اختياري)")

if st.button("+ إضافة تاسك"):
    if not desc.strip():
        common.angry_warning("محتاج توصف التاسك الأول!")
    else:
        new_row = pd.DataFrame(
            [
                {
                    "ID": next_id,
                    "Description": desc,
                    "Type": ttype,
                    "Assigned To": assigned,
                    "Status": "مفتوح",
                    "Claimed By": "",
                }
            ]
        )
        updated = pd.concat([tasks_df, new_row], ignore_index=True)
        ok, err = common.save_sheet("TASKS", updated)
        if ok:
            st.success("اتضاف التاسك!")
            st.rerun()
        else:
            st.error(err)

st.markdown("---")
st.subheader("📋 التاسكات الحالية")

if st.button("🔄 تحديث القايمة"):
    st.rerun()

if tasks_df.empty:
    st.info("مفيش تاسكات لسه.")
else:
    for _, row in tasks_df.iterrows():
        try:
            box = st.container(border=True)
        except TypeError:
            box = st.container()

        with box:
            cols = st.columns([3, 1, 1, 2])
            cols[0].markdown(
                f"**#{row['ID']} — {row['Description']}**  \n"
                f"النوع: {row['Type'] or '—'} | موزّع على: {row['Assigned To'] or '—'}"
            )
            status = row["Status"]

            if status == "مفتوح":
                cols[1].markdown("🟡 مفتوح")
                claim_name = cols[2].text_input(
                    "اسمك", key=f"claim_name_{row['ID']}", label_visibility="collapsed",
                    placeholder="اكتب اسمك",
                )
                if cols[3].button("استلام التاسك", key=f"claim_{row['ID']}"):
                    if not claim_name.strip():
                        common.angry_warning("اكتب اسمك الأول قبل ما تستلم التاسك!")
                    else:
                        fresh = common.load_all_fresh()["TASKS"]
                        idx = fresh.index[fresh["ID"] == row["ID"]]
                        if len(idx) and fresh.loc[idx[0], "Status"] != "مفتوح":
                            st.error("للأسف حد تاني استلم التاسك ده قبلك بلحظات!")
                        else:
                            fresh.loc[idx, "Status"] = "تحت التنفيذ"
                            fresh.loc[idx, "Claimed By"] = claim_name
                            ok, err = common.save_sheet("TASKS", fresh)
                            if ok:
                                st.success("استلمت التاسك!")
                                st.rerun()
                            else:
                                st.error(err)

            elif status == "تحت التنفيذ":
                cols[1].markdown(f"🔵 عند: {row['Claimed By']}")
                if cols[3].button("تسليم ✅", key=f"done_{row['ID']}"):
                    fresh = common.load_all_fresh()["TASKS"]
                    idx = fresh.index[fresh["ID"] == row["ID"]]
                    fresh.loc[idx, "Status"] = "تم"
                    ok, err = common.save_sheet("TASKS", fresh)
                    if ok:
                        st.success("تم تسليم التاسك!")
                        st.rerun()
                    else:
                        st.error(err)

            else:  # تم
                cols[1].markdown(f"🟢 تم بواسطة {row['Claimed By']}")
