import os
import pandas as pd
import streamlit as st

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="TAVEN OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------- انيميشن وتصميم عصري (Custom CSS) -----------------
st.markdown(
    """
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(12px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    .stApp {
        background-color: #f7f9fc;
        animation: fadeIn 0.8s ease-in-out;
    }
    
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    }
    
    .stButton>button {
        border-radius: 8px;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
</style>
""",
    unsafe_allow_html=True,
)

EXCEL_FILE = "TAVEN.xlsx"


def load_data():
    """تحميل البيانات بأمان وتفادي خطأ الشيتات المفقودة"""
    # البيانات الافتراضية
    default_partners = pd.DataFrame(
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
    )

    default_finance = pd.DataFrame(
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
    )

    default_ops = pd.DataFrame(
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
    )

    default_extra = pd.DataFrame(
        [
            {
                "Expense Name": "Shipping & Delivery",
                "Qty": 10,
                "Unit Cost": 50,
                "Total": 500,
                "Notes": "Sample Shipping",
            }
        ]
    )

    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            default_partners.to_excel(
                writer, sheet_name="PARTNERS", index=False
            )
            default_finance.to_excel(writer, sheet_name="FINANCE", index=False)
            default_ops.to_excel(writer, sheet_name="OPERATIONS", index=False)
            default_extra.to_excel(
                writer, sheet_name="EXTRA_EXPENSES", index=False
            )
        return default_partners, default_finance, default_ops, default_extra

    # قراءة الملف ومرعاة وجود أية شيت مفقودة
    xls = pd.ExcelFile(EXCEL_FILE)
    existing_sheets = xls.sheet_names

    partners_df = (
        pd.read_excel(xls, sheet_name="PARTNERS")
        if "PARTNERS" in existing_sheets
        else default_partners
    )
    finance_df = (
        pd.read_excel(xls, sheet_name="FINANCE")
        if "FINANCE" in existing_sheets
        else default_finance
    )
    ops_df = (
        pd.read_excel(xls, sheet_name="OPERATIONS")
        if "OPERATIONS" in existing_sheets
        else default_ops
    )
    extra_df = (
        pd.read_excel(xls, sheet_name="EXTRA_EXPENSES")
        if "EXTRA_EXPENSES" in existing_sheets
        else default_extra
    )

    return partners_df, finance_df, ops_df, extra_df


def save_sheet(df, sheet_name):
    """حفظ التعديلات أوتوماتيكياً في الإكسيل"""
    mode = "a" if os.path.exists(EXCEL_FILE) else "w"
    with pd.ExcelWriter(
        EXCEL_FILE, engine="openpyxl", mode=mode, if_sheet_exists="replace"
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


partners_df, finance_df, ops_df, extra_exp_df = load_data()

# ---------------- الهيدر وحساب المؤشرات التلقائي ----------------
st.title("⚡ TAVEN OS")

fin_total = (
    finance_df["Total"].sum()
    if not finance_df.empty and "Total" in finance_df
    else 0
)
extra_total = (
    extra_exp_df["Total"].sum()
    if not extra_exp_df.empty and "Total" in extra_exp_df
    else 0
)
total_exp = fin_total + extra_total

gross_val = 11600
realized = 5000
net_profit = realized - total_exp

m1, m2, m3, m4 = st.columns(4)
m1.metric("Gross Val", f"{gross_val:,.0f} EGP")
m2.metric("Realized", f"{realized:,.0f} EGP")
m3.metric("Total Exp (إجمالي المصاريف)", f"{total_exp:,.0f} EGP")
m4.metric("Net Profit (صافي الربح)", f"{net_profit:,.0f} EGP")

st.markdown("---")

# ---------------- قائمة الأقسام الرئيسية ----------------
section = st.radio(
    "القسم الحالي / SECTION",
    [
        "PARTNERS",
        "FINANCE (المالية)",
        "OPERATIONS (العمليات)",
        "مصاريف إضافية (EXTRA EXPENSES)",
    ],
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
        if st.button("حفظ التعديلات في الإكسيل"):
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
                    st.success("تمت الإضافة بنجاح!")
                    st.rerun()

# ---------------- 2. قسم المالية (مع حساب أوتوماتيك) ----------------
elif section == "FINANCE (المالية)":
    with col_table:
        st.subheader("جدول المصاريف والمالية")
        edited_finance = st.data_editor(
            finance_df, num_rows="dynamic", use_container_width=True
        )
        if st.button("حفظ التعديلات في الإكسيل"):
            save_sheet(edited_finance, "FINANCE")
            st.success("تم التحديث بنجاح!")
            st.rerun()

    with col_form:
        st.subheader("DATA ENTRY: FINANCE")
        cat = st.text_input("Category (النوع)", key="fin_cat")
        subcat = st.text_input("Subcategory (الوصف)", key="fin_subcat")
        qty = st.number_input(
            "الكمية (Quantity)", min_value=1, value=1, key="fin_qty"
        )
        unit_cost = st.number_input(
            "سعر القطعة (Unit Cost EGP)",
            min_value=0.0,
            step=10.0,
            key="fin_unit",
        )

        calculated_total = qty * unit_cost
        st.info(f"💡 الإجمالي المحسوب تلقائياً: **{calculated_total:,.2f} EGP**")

        if st.button("+ Record Expense (تسجيل المصروف)"):
            if cat:
                new_row = pd.DataFrame(
                    [
                        {
                            "Category": cat,
                            "Subcategory": subcat,
                            "Qty": qty,
                            "Unit Cost": unit_cost,
                            "Total": calculated_total,
                        }
                    ]
                )
                updated = pd.concat([finance_df, new_row], ignore_index=True)
                save_sheet(updated, "FINANCE")
                st.success("تم تسجيل المصروف والإجمالي أوتوماتيكياً!")
                st.rerun()

# ---------------- 3. قسم العمليات (مع حساب أوتوماتيك) ----------------
elif section == "OPERATIONS (العمليات)":
    with col_table:
        st.subheader("جدول المدخلات والعمليات")
        edited_ops = st.data_editor(
            ops_df, num_rows="dynamic", use_container_width=True
        )
        if st.button("حفظ التعديلات في الإكسيل"):
            save_sheet(edited_ops, "OPERATIONS")
            st.success("تم التحديث بنجاح!")
            st.rerun()

    with col_form:
        st.subheader("DATA ENTRY: OPERATIONS")
        mat = st.text_input("Material Type (اسم المادة الخامات)", key="op_mat")
        weight = st.number_input(
            "الوزن / الكمية (KG)", min_value=0.1, value=1.0, key="op_weight"
        )
        unit_cost_kg = st.number_input(
            "سعر الكيلو / القطعة (Cost per KG/Unit)",
            min_value=0.0,
            step=10.0,
            key="op_unit_cost",
        )
        supplier = st.text_input("المورد (Supplier)", key="op_supp")

        calc_op_total = weight * unit_cost_kg
        st.info(
            f"💡 إجمالي التكلفة المحسوبة: **{calc_op_total:,.2f} EGP** (تكلفة الكيلو: {unit_cost_kg} EGP)"
        )

        if st.button("+ Log Raw Material (تسجيل الخام)"):
            if mat:
                new_row = pd.DataFrame(
                    [
                        {
                            "Material": mat,
                            "Cost": calc_op_total,
                            "Weight": weight,
                            "Cost/KG": unit_cost_kg,
                            "Supplier": supplier,
                        }
                    ]
                )
                updated = pd.concat([ops_df, new_row], ignore_index=True)
                save_sheet(updated, "OPERATIONS")
                st.success("تم الحفظ بالتكلفة المحسوبة أوتوماتيكياً!")
                st.rerun()

# ---------------- 4. قسم مصاريف إضافية ----------------
elif section == "مصاريف إضافية (EXTRA EXPENSES)":
    with col_table:
        st.subheader("جدول المصاريف الإضافية والنثرية")
        edited_extra = st.data_editor(
            extra_exp_df, num_rows="dynamic", use_container_width=True
        )
        if st.button("حفظ التعديلات في الإكسيل"):
            save_sheet(edited_extra, "EXTRA_EXPENSES")
            st.success("تم التحديث بنجاح!")
            st.rerun()

    with col_form:
        st.subheader("DATA ENTRY: EXTRA EXPENSES")
        exp_name = st.text_input("اسم المصروف (Expense Name)", key="ext_name")
        ext_qty = st.number_input(
            "الكمية (Qty)", min_value=1, value=1, key="ext_qty"
        )
        ext_unit = st.number_input(
            "سعر القطعة / الوحدة (Unit Cost EGP)",
            min_value=0.0,
            step=10.0,
            key="ext_unit",
        )
        ext_notes = st.text_input("ملاحظات (Notes)", key="ext_notes")

        calc_ext_total = ext_qty * ext_unit
        st.info(f"💡 إجمالي المصروف الإضافي: **{calc_ext_total:,.2f} EGP**")

        if st.button("+ Add Extra Expense (إضافة مصروف إضافي)"):
            if exp_name:
                new_row = pd.DataFrame(
                    [
                        {
                            "Expense Name": exp_name,
                            "Qty": ext_qty,
                            "Unit Cost": ext_unit,
                            "Total": calc_ext_total,
                            "Notes": ext_notes,
                        }
                    ]
                )
                updated = pd.concat([extra_exp_df, new_row], ignore_index=True)
                save_sheet(updated, "EXTRA_EXPENSES")
                st.success("تم تسجيل المصروف الإضافي بنجاح!")
                st.rerun()
                updated = pd.concat([extra_exp_df, new_row], ignore_index=True)
                save_sheet(updated, "EXTRA_EXPENSES")
                st.success("تم تسجيل المصروف الإضافي بنجاح!")
                st.rerun()
