import os
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="TAVEN OS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

EXCEL_FILE = "TAVEN.xlsx"


def load_data():
    """تحميل البيانات من ملف الإكسيل وإنشاء الشيتات الأساسية إذا لم تكن موجودة"""
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            # الشركاء
            pd.DataFrame(
                [
                    {
                        "Partner": "Partner A",
                        "Contribution": 50000,
                        "Purpose": "Initial Inventory Funding",
                    },
                    {
                        "Partner": "Partner B",
                        "Contribution": 30000,
                        "Purpose": "Marketing & Ads Capital",
                    },
                ]
            ).to_excel(writer, sheet_name="PARTNERS", index=False)

            # المصاريف والمالية
            pd.DataFrame(
                [
                    {
                        "Category": "Fabric",
                        "Subcategory": "French Terry",
                        "Qty": 100,
                        "Unit Cost": 150,
                        "Total": 15000,
                    },
                    {
                        "Category": "Ads",
                        "Subcategory": "Meta Ads",
                        "Qty": 1,
                        "Unit Cost": 5000,
                        "Total": 5000,
                    },
                ]
            ).to_excel(writer, sheet_name="FINANCE", index=False)

            # العمليات والمواد الخام
            pd.DataFrame(
                [
                    {
                        "Material": "French Terry Cotton 400GSM",
                        "Cost": 15000,
                        "Weight": 100,
                        "Cost/KG": 150,
                        "Supplier": "Nile Textiles",
                    },
                    {
                        "Material": "Ribbing Fabric",
                        "Cost": 2400,
                        "Weight": 20,
                        "Cost/KG": 120,
                        "Supplier": "Delta Weave",
                    },
                ]
            ).to_excel(writer, sheet_name="OPERATIONS", index=False)

    return (
        pd.read_excel(EXCEL_FILE, sheet_name="PARTNERS"),
        pd.read_excel(EXCEL_FILE, sheet_name="FINANCE"),
        pd.read_excel(EXCEL_FILE, sheet_name="OPERATIONS"),
    )


def save_sheet(df, sheet_name):
    """حفظ التعديلات في شيت الإكسيل مباشرة"""
    with pd.ExcelWriter(
        EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


partners_df, finance_df, ops_df = load_data()

# ---------------- الهيدر والمؤشرات الرئيسية ----------------
st.title("TAVEN OS")

total_exp = finance_df["Total"].sum() if not finance_df.empty else 0
total_contrib = (
    partners_df["Contribution"].sum() if not partners_df.empty else 0
)
gross_val = 11600
realized = 5000
net_profit = realized - total_exp
margin = (net_profit / gross_val * 100) if gross_val != 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gross Val", f"{gross_val:,.0f} EGP")
m2.metric("Realized", f"{realized:,.0f} EGP")
m3.metric("Total Exp", f"{total_exp:,.0f} EGP")
m4.metric("Net Profit", f"{net_profit:,.0f} EGP")

st.markdown("---")

# ---------------- القائمة الرئيسية ----------------
section = st.radio(
    "القسم / SECTION",
    ["PARTNERS", "FINANCE", "OPERATIONS"],
    horizontal=True,
)

col_table, col_form = st.columns([2.2, 1])

# ---------------- 1. قسم الشركاء ----------------
if section == "PARTNERS":
    with col_table:
        st.subheader("جدول الشركاء (PARTNERS)")
        edited_partners = st.data_editor(
            partners_df, num_rows="dynamic", use_container_width=True
        )
        if st.button("حفظ التعديلات والحذف في الشيت"):
            save_sheet(edited_partners, "PARTNERS")
            st.success("تم تحديث شيت TAVEN بنجاح!")
            st.rerun()

    with col_form:
        st.subheader("DATA ENTRY: PARTNERS")
        with st.form("form_partners"):
            p_name = st.text_input("Partner Name")
            p_contrib = st.number_input(
                "Contribution (EGP)", min_value=0.0, step=1000.0
            )
            p_purpose = st.text_input("Purpose")
            if st.form_submit_button("+ Add Contribution"):
                if p_name:
                    new_row = pd.DataFrame(
                        [
                            {
                                "Partner": p_name,
                                "Contribution": p_contrib,
                                "Purpose": p_purpose,
                            }
                        ]
                    )
                    updated = pd.concat(
                        [partners_df, new_row], ignore_index=True
                    )
                    save_sheet(updated, "PARTNERS")
                    st.success("تم إضافة الشريك بنجاح!")
                    st.rerun()

# ---------------- 2. قسم المالية والمصاريف ----------------
elif section == "FINANCE":
    with col_table:
        st.subheader("جدول المصاريف والمالية (FINANCE)")
        edited_finance = st.data_editor(
            finance_df, num_rows="dynamic", use_container_width=True
        )
        if st.button("حفظ التعديلات والحذف في الشيت"):
            save_sheet(edited_finance, "FINANCE")
            st.success("تم تحديث شيت TAVEN بنجاح!")
            st.rerun()

    with col_form:
        st.subheader("DATA ENTRY: FINANCE")
        with st.form("form_finance"):
            cat = st.text_input("Category")
            subcat = st.text_input("Subcategory")
            qty = st.number_input("Quantity", min_value=1, value=1)
            unit_cost = st.number_input(
                "Unit Cost (EGP)", min_value=0.0, step=50.0
            )
            if st.form_submit_button("+ Record Expense"):
                if cat:
                    new_row = pd.DataFrame(
                        [
                            {
                                "Category": cat,
                                "Subcategory": subcat,
                                "Qty": qty,
                                "Unit Cost": unit_cost,
                                "Total": qty * unit_cost,
                            }
                        ]
                    )
                    updated = pd.concat(
                        [finance_df, new_row], ignore_index=True
                    )
                    save_sheet(updated, "FINANCE")
                    st.success("تم تسجيل المصروف بنجاح!")
                    st.rerun()

# ---------------- 3. قسم العمليات والمواد الخام ----------------
elif section == "OPERATIONS":
    with col_table:
        st.subheader("جدول المدخلات والعمليات (OPERATIONS)")
        edited_ops = st.data_editor(
            ops_df, num_rows="dynamic", use_container_width=True
        )
        if st.button("حفظ التعديلات والحذف في الشيت"):
            save_sheet(edited_ops, "OPERATIONS")
            st.success("تم تحديث شيت TAVEN بنجاح!")
            st.rerun()

    with col_form:
        st.subheader("DATA ENTRY: OPERATIONS")
        with st.form("form_ops"):
            mat = st.text_input("Material Type")
            cost = st.number_input(
                "Total Cost (EGP)", min_value=0.0, step=500.0
            )
            weight = st.number_input("Weight (KG)", min_value=0.1, step=1.0)
            supplier = st.text_input("Supplier")
            if st.form_submit_button("+ Log Raw Material"):
                if mat:
                    new_row = pd.DataFrame(
                        [
                            {
                                "Material": mat,
                                "Cost": cost,
                                "Weight": weight,
                                "Cost/KG": (cost / weight) if weight else 0,
                                "Supplier": supplier,
                            }
                        ]
                    )
                    updated = pd.concat([ops_df, new_row], ignore_index=True)
                    save_sheet(updated, "OPERATIONS")
                    st.success("تم إضافة المادة بنجاح!")
                    st.rerun()
