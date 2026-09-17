import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="TAVEN OS & Mobile Game",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- القائمة الجانبية -----------------
st.sidebar.title("📌 القائمة الرئيسية")
app_page = st.sidebar.radio(
    "اختر الصفحة:",
    ["📊 لوحة التحكم (TAVEN OS)", "🎮 لعبة سوبر ماريو (Mobile Ready)"],
)

EXCEL_FILE = "TAVEN.xlsx"


def load_data():
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

    try:
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
    except Exception:
        return default_partners, default_finance, default_ops, default_extra


def save_sheet(df, sheet_name):
    mode = "a" if os.path.exists(EXCEL_FILE) else "w"
    with pd.ExcelWriter(
        EXCEL_FILE, engine="openpyxl", mode=mode, if_sheet_exists="replace"
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


# =========================================================================
# 📊 الصفحة الأولى: لوحة التحكم (TAVEN OS)
# =========================================================================
if app_page == "📊 لوحة التحكم (TAVEN OS)":
    partners_df, finance_df, ops_df, extra_exp_df = load_data()

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
    m3.metric("Total Exp (المصاريف)", f"{total_exp:,.0f} EGP")
    m4.metric("Net Profit (صافي الربح)", f"{net_profit:,.0f} EGP")

    st.markdown("---")

    section = st.radio(
        "اختر القسم / SECTION",
        [
            "PARTNERS",
            "FINANCE (المالية)",
            "OPERATIONS (العمليات)",
            "مصاريف إضافية (EXTRA EXPENSES)",
        ],
        horizontal=True,
    )

    col_table, col_form = st.columns([2.2, 1])

    if section == "PARTNERS":
        with col_table:
            st.subheader("جدول الشركاء (PARTNERS)")
            edited_partners = st.data_editor(
                partners_df, num_rows="dynamic", use_container_width=True
            )
            if st.button("حفظ التعديلات في الإكسيل"):
                save_sheet(edited_partners, "PARTNERS")
                st.success("تم التحديث بنجاح!")
                st.rerun()

        with col_form:
            st.subheader("DATA ENTRY: PARTNERS")
            p_name = st.text_input("Partner Name")
            p_contrib = st.number_input(
                "Contribution (EGP)", min_value=0.0, step=1000.0
            )
            p_purpose = st.text_input("Purpose")

            if st.button("+ Add Contribution"):
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
                    st.success("تمت الإضافة!")
                    st.rerun()

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
            fin_cat = st.text_input("Category (النوع)", value="Fabric")
            fin_subcat = st.text_input("Subcategory (الوصف)", value="Cotton")
            fin_qty = st.number_input(
                "الكمية (Qty)", min_value=1, value=1, step=1, key="f_qty"
            )
            fin_unit = st.number_input(
                "سعر القطعة (Unit Cost EGP)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                key="f_unit",
            )

            auto_total = float(fin_qty) * float(fin_unit)
            st.markdown(f"### 💵 الإجمالي: **{auto_total:,.2f} EGP**")

            if st.button("+ Record Expense (تسجيل المصروف)"):
                if fin_cat:
                    new_row = pd.DataFrame(
                        [
                            {
                                "Category": fin_cat,
                                "Subcategory": fin_subcat,
                                "Qty": fin_qty,
                                "Unit Cost": fin_unit,
                                "Total": auto_total,
                            }
                        ]
                    )
                    updated = pd.concat(
                        [finance_df, new_row], ignore_index=True
                    )
                    save_sheet(updated, "FINANCE")
                    st.success("تم التسجيل والإضافة أوتوماتيكياً!")
                    st.rerun()

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
            op_mat = st.text_input("Material Type (اسم الخام)")
            op_weight = st.number_input(
                "الوزن / الكمية (KG)", min_value=0.1, value=1.0, step=1.0
            )
            op_unit_cost = st.number_input(
                "سعر الكيلو (Cost per KG)", min_value=0.0, value=0.0, step=10.0
            )
            op_supp = st.text_input("المورد (Supplier)")

            auto_op_cost = float(op_weight) * float(op_unit_cost)
            st.markdown(f"### ⚖️ الإجمالي: **{auto_op_cost:,.2f} EGP**")

            if st.button("+ Log Raw Material (تسجيل الخام)"):
                if op_mat:
                    new_row = pd.DataFrame(
                        [
                            {
                                "Material": op_mat,
                                "Cost": auto_op_cost,
                                "Weight": op_weight,
                                "Cost/KG": op_unit_cost,
                                "Supplier": op_supp,
                            }
                        ]
                    )
                    updated = pd.concat([ops_df, new_row], ignore_index=True)
                    save_sheet(updated, "OPERATIONS")
                    st.success("تم الحفظ بالتكلفة المحسوبة أوتوماتيكياً!")
                    st.rerun()

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
            ext_name = st.text_input("اسم المصروف (Expense Name)")
            ext_qty = st.number_input(
                "الكمية (Qty)", min_value=1, value=1, step=1, key="x_qty"
            )
            ext_unit = st.number_input(
                "سعر الوحدة (Unit Cost EGP)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                key="x_unit",
            )
            ext_notes = st.text_input("ملاحظات (Notes)")

            auto_ext_total = float(ext_qty) * float(ext_unit)
            st.markdown(f"### 🧾 الإجمالي: **{auto_ext_total:,.2f} EGP**")

            if st.button("+ Add Extra Expense (إضافة مصروف)"):
                if ext_name:
                    new_row = pd.DataFrame(
                        [
                            {
                                "Expense Name": ext_name,
                                "Qty": ext_qty,
                                "Unit Cost": ext_unit,
                                "Total": auto_ext_total,
                                "Notes": ext_notes,
                            }
                        ]
                    )
                    updated = pd.concat(
                        [extra_exp_df, new_row], ignore_index=True
                    )
                    save_sheet(updated, "EXTRA_EXPENSES")
                    st.success("تم التسجيل بنجاح!")
                    st.rerun()

# =========================================================================
# 🎮 الصفحة الثانية: لعبة سوبر ماريو مخصصة للتليفون باللمس
# =========================================================================
elif app_page == "🎮 لعبة سوبر ماريو (Mobile Ready)":
    st.title("🍄 TAVEN Mobile Mario Game")

    mario_mobile_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            * { touch-action: manipulation; user-select: none; }
            body { text-align: center; font-family: sans-serif; margin: 0; padding: 5px; background: #121212; color: white; }
            canvas {
                background: linear-gradient(#70a5ff, #e0f0ff);
                display: block;
                margin: 0 auto;
                border: 3px solid #fff;
                border-radius: 12px;
                max-width: 100%;
            }
            .touch-controls {
                display: flex;
                justify-content: space-between;
                margin-top: 15px;
                padding: 0 10px;
            }
            .d-pad { display: flex; gap: 10px; }
            .btn {
                background: #2563eb;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 50%;
                width: 65px;
                height: 65px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.5);
                active { background: #1d4ed8; transform: scale(0.95); }
            }
            .btn-jump {
                background: #e11d48;
                width: 75px;
                height: 75px;
                border-radius: 50%;
            }
        </style>
    </head>
    <body>
        <canvas id="gameCanvas" width="360" height="320"></canvas>

        <!-- أزرار التحكم باللمس للتليفون -->
        <div class="touch-controls">
            <div class="d-pad">
                <button class="btn" id="btnLeft">⬅️</button>
                <button class="btn" id="btnRight">➡️</button>
            </div>
            <button class="btn btn-jump" id="btnJump">🚀 JUMP</button>
        </div>

        <script>
            const canvas = document.getElementById("gameCanvas");
            const ctx = canvas.getContext("2d");

            let mario = {
                x: 30, y: 220, width: 24, height: 32,
                dx: 0, dy: 0, gravity: 0.55, jumpPower: -11,
                grounded: false, color: "#e63946", score: 0
            };

            let platforms = [
                {x: 0, y: 280, width: 360, height: 40, color: "#2a9d8f"},
                {x: 80, y: 210, width: 80, height: 15, color: "#e9c46a"},
                {x: 200, y: 160, width: 90, height: 15, color: "#e9c46a"},
                {x: 60, y: 110, width: 80, height: 15, color: "#e9c46a"}
            ];

            let coins = [
                {x: 110, y: 180, radius: 7, collected: false},
                {x: 240, y: 130, radius: 7, collected: false},
                {x: 90, y: 80, radius: 7, collected: false}
            ];

            let moveLeft = false;
            let moveRight = false;

            // أحداث اللمس للتليفون
            const setupTouch = (id, startFn, endFn) => {
                const btn = document.getElementById(id);
                btn.addEventListener("touchstart", (e) => { e.preventDefault(); startFn(); });
                btn.addEventListener("touchend", (e) => { e.preventDefault(); endFn(); });
                btn.addEventListener("mousedown", startFn);
                btn.addEventListener("mouseup", endFn);
            };

            setupTouch("btnLeft", () => moveLeft = true, () => moveLeft = false);
            setupTouch("btnRight", () => moveRight = true, () => moveRight = false);
            setupTouch("btnJump", () => {
                if (mario.grounded) { mario.dy = mario.jumpPower; mario.grounded = false; }
            }, () => {});

            function update() {
                if (moveRight) mario.dx = 3.5;
                else if (moveLeft) mario.dx = -3.5;
                else mario.dx = 0;

                mario.dy += mario.gravity;
                mario.x += mario.dx;
                mario.y += mario.dy;

                if (mario.x < 0) mario.x = 0;
                if (mario.x + mario.width > canvas.width) mario.x = canvas.width - mario.width;

                mario.grounded = false;
                platforms.forEach(p => {
                    if (
                        mario.x < p.x + p.width &&
                        mario.x + mario.width > p.x &&
                        mario.y + mario.height > p.y &&
                        mario.y + mario.height < p.y + p.height + mario.dy
                    ) {
                        mario.y = p.y - mario.height;
                        mario.dy = 0;
                        mario.grounded = true;
                    }
                });

                coins.forEach(c => {
                    if (!c.collected) {
                        let distX = (mario.x + mario.width/2) - c.x;
                        let distY = (mario.y + mario.height/2) - c.y;
                        if (Math.sqrt(distX*distX + distY*distY) < c.radius + mario.width/2) {
                            c.collected = true;
                            mario.score += 100;
                        }
                    }
                });
            }

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                platforms.forEach(p => {
                    ctx.fillStyle = p.color;
                    ctx.fillRect(p.x, p.y, p.width, p.height);
                });

                coins.forEach(c => {
                    if (!c.collected) {
                        ctx.beginPath();
                        ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
                        ctx.fillStyle = "#ffb703";
                        ctx.fill();
                        ctx.closePath();
                    }
                });

                ctx.fillStyle = mario.color;
                ctx.fillRect(mario.x, mario.y, mario.width, mario.height);

                ctx.fillStyle = "#000";
                ctx.font = "bold 15px sans-serif";
                ctx.fillText("⭐ SCORE: " + mario.score, 15, 25);
            }

            function loop() {
                update();
                draw();
                requestAnimationFrame(loop);
            }
            loop();
        </script>
    </body>
    </html>
    """

    components.html(mario_mobile_html, height=460)
