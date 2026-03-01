import streamlit as st

# ── Tax Engine ──────────────────────────────────────────────────────────────
def compare_tax_regimes(gross, basic, hra_received, rent_paid, is_metro, s80c, s80d, s80tta=0):
    def old_tax(ti):
        tax = 0
        if ti <= 250000: tax = 0
        elif ti <= 500000: tax = (ti-250000)*0.05
        elif ti <= 1000000: tax = 12500+(ti-500000)*0.20
        else: tax = 112500+(ti-1000000)*0.30
        if ti <= 500000: tax = 0
        return round(tax*1.04, 2)
    def new_tax(ti):
        tax, rem = 0, ti
        for lim, rate in [(300000,0),(400000,.05),(300000,.10),(200000,.15),(300000,.20)]:
            if rem<=0: break
            tax += min(rem,lim)*rate; rem -= lim
        if rem>0: tax += rem*0.30
        if ti<=700000: tax=0
        return round(tax*1.04, 2)
    hra = 0
    if rent_paid>0:
        p = 0.5 if is_metro else 0.4
        hra = max(0, min(hra_received, p*basic, rent_paid-0.1*basic))
    ded = 50000+hra+min(s80c,150000)+min(s80d,25000)+min(s80tta,10000)
    ot = old_tax(max(0,gross-ded))
    nt = new_tax(max(0,gross-75000))
    rec = "Old Regime" if ot<nt else "New Regime"
    return {
        "old_regime": {"tax_payable": ot, "deductions_breakdown": {"total_deductions": ded, "hra": hra, "s80c": min(s80c,150000), "s80d": min(s80d,25000)}},
        "new_regime": {"tax_payable": nt},
        "recommended_regime": rec,
        "annual_savings": round(abs(ot-nt), 2)
    }

def explain_tax_result(gross, s80c, s80d, result):
    ot    = result['old_regime']['tax_payable']
    nt    = result['new_regime']['tax_payable']
    rec   = result['recommended_regime']
    saves = result['annual_savings']
    ded   = result['old_regime']['deductions_breakdown']['total_deductions']
    if rec == "Old Regime":
        reason = f"Your total deductions of Rs.{ded:,.0f} (80C Rs.{min(s80c,150000):,} and 80D Rs.{min(s80d,25000):,}) significantly reduce your taxable income under the Old Regime."
    else:
        reason = f"Your deductions of Rs.{ded:,.0f} are not high enough to beat the New Regime's lower slab rates. Consider maximizing 80C to Rs.1,50,000 to potentially switch."
    return (
        f"**Old Regime:** After deductions of Rs.{ded:,.0f}, tax = Rs.{ot:,.0f}\n\n"
        f"**New Regime:** After standard deduction Rs.75,000, tax = Rs.{nt:,.0f}\n\n"
        f"**Why {rec}?** {reason}"
    )

# ── UI ───────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Indian Tax Assistant", page_icon="🇮🇳", layout="centered")
st.title("🇮🇳 Indian Tax Filing Assistant")
st.caption("FY 2024-25 | Compare Old vs New Tax Regime instantly")

with st.form("tax_form"):
    st.subheader("Enter Your Details")
    col1, col2 = st.columns(2)

    with col1:
        gross   = st.number_input("Gross Annual Salary (Rs.)", min_value=0, value=1000000, step=10000)
        basic   = st.number_input("Basic Salary (Rs.)", min_value=0, value=500000, step=10000)
        hra_r   = st.number_input("HRA Received from Employer (Rs.)", min_value=0, value=200000, step=5000)

    with col2:
        rent    = st.number_input("Annual Rent Paid (Rs.)", min_value=0, value=180000, step=5000)
        s80c    = st.number_input("80C Investments (Rs.) — max 1,50,000", min_value=0, max_value=150000, value=150000, step=5000)
        s80d    = st.number_input("Health Insurance Premium (Rs.) — max 25,000", min_value=0, max_value=25000, value=25000, step=1000)

    s80tta  = st.number_input("Savings Account Interest 80TTA (Rs.) — max 10,000", min_value=0, max_value=10000, value=0, step=1000)
    is_metro = st.checkbox("I live in a Metro city (Mumbai/Delhi/Kolkata/Chennai)", value=True)

    submitted = st.form_submit_button("Calculate Tax", use_container_width=True)

if submitted:
    result = compare_tax_regimes(gross, basic, hra_r, rent, is_metro, s80c, s80d, s80tta)
    ot     = result['old_regime']['tax_payable']
    nt     = result['new_regime']['tax_payable']
    rec    = result['recommended_regime']
    saves  = result['annual_savings']
    db     = result['old_regime']['deductions_breakdown']

    st.divider()
    st.subheader("Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Old Regime Tax", f"Rs.{ot:,.0f}")
    col2.metric("New Regime Tax", f"Rs.{nt:,.0f}")
    col3.metric("Annual Savings", f"Rs.{saves:,.0f}")

    if rec == "Old Regime":
        st.success(f"Recommended: OLD REGIME saves you Rs.{saves:,.0f}/year")
    else:
        st.success(f"Recommended: NEW REGIME saves you Rs.{saves:,.0f}/year")

    st.divider()
    st.subheader("AI Explanation")
    st.markdown(explain_tax_result(gross, s80c, s80d, result))

    st.divider()
    st.subheader("Deductions Breakdown (Old Regime)")
    st.table({
        "Deduction": ["Standard Deduction", "HRA Exemption", "Section 80C", "Section 80D", "Total"],
        "Amount (Rs.)": [
            f"{50000:,}",
            f"{db['hra']:,.0f}",
            f"{db['s80c']:,}",
            f"{db['s80d']:,}",
            f"{db['total_deductions']:,.0f}"
        ]
    })

