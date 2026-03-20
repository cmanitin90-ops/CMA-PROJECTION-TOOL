import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="CMA Data Projection Tool", layout="wide")
st.title("📊 Project Finance & CMA Projection Tool")

# --- SIDEBAR: CONFIGURATION ---
st.sidebar.header("Project Configuration")
years = st.sidebar.slider("Number of Projection Years", min_value=1, max_value=15, value=7)

# --- TABS FOR INPUT & ANALYSIS ---
tab1, tab2, tab3, tab4 = st.tabs(["Data Input", "CMA Calculations", "Ratios & DSCR", "Sensitivity Analysis"])

with tab1:
    st.subheader("Financial Inputs (Annual)")
    st.info("Enter the base values for the projection period.")
    
    # Create a dynamic dataframe for inputs
    cols = [f"Year {i+1}" for i in range(years)]
    input_metrics = ["Revenue", "Direct Costs", "Admin Expenses", "Interest", "Installment Paid", "Depreciation"]
    
    input_df = pd.DataFrame(index=input_metrics, columns=cols, dtype=float).fillna(0.0)
    edited_df = st.data_editor(input_df, num_rows="fixed")

with tab2:
    st.subheader("CMA Projection Summary")
    
    # Calculations
    ebitda = edited_df.loc["Revenue"] - edited_df.loc["Direct Costs"] - edited_df.loc["Admin Expenses"]
    pat = (ebitda - edited_df.loc["Interest"] - edited_df.loc["Depreciation"]) * 0.75  # Assuming 25% Tax
    
    cma_table = pd.DataFrame({
        "EBITDA": ebitda,
        "PAT": pat,
        "Depreciation": edited_df.loc["Depreciation"],
        "Interest": edited_df.loc["Interest"],
        "Repayment": edited_df.loc["Installment Paid"]
    }).T
    
    st.dataframe(cma_table.style.format("{:.2f}"))

with tab3:
    st.subheader("Key Financial Ratios & Debt Serviceability")
    
    # DSCR Calculation: (PAT + Depr + Interest) / (Interest + Installment)
    numerator = pat + edited_df.loc["Depreciation"] + edited_df.loc["Interest"]
    denominator = edited_df.loc["Interest"] + edited_df.loc["Installment Paid"]
    dscr = numerator / denominator.replace(0, np.nan) # Avoid division by zero
    
    # Current Ratio (Example Mockup)
    current_ratio = np.random.uniform(1.2, 2.5, years) # Logic can be expanded with BS inputs
    
    ratios_df = pd.DataFrame({
        "DSCR": dscr,
        "Current Ratio": current_ratio,
        "Net Profit Margin (%)": (pat / edited_df.loc["Revenue"] * 100).fillna(0)
    }).T
    
    st.table(ratios_df.style.format("{:.2f}"))
    
    # Visualizing DSCR
    st.line_chart(dscr)
    st.caption("DSCR Trend (Target: > 1.25 for Bank Financing)")

with tab4:
    st.subheader("Sensitivity Analysis (EBITDA vs DSCR)")
    st.write("Analyze how a drop in Revenue affects the Average DSCR.")
    
    drop_pct = st.slider("Revenue Drop (%)", 0, 50, 10)
    
    sens_rev = edited_df.loc["Revenue"] * (1 - drop_pct/100)
    sens_ebitda = sens_rev - edited_df.loc["Direct Costs"] - edited_df.loc["Admin Expenses"]
    sens_pat = (sens_ebitda - edited_df.loc["Interest"] - edited_df.loc["Depreciation"]) * 0.75
    
    sens_dscr = (sens_pat + edited_df.loc["Depreciation"] + edited_df.loc["Interest"]) / denominator.replace(0, np.nan)
    
    st.metric("New Avg DSCR", f"{sens_dscr.mean():.2f}", delta=f"{sens_dscr.mean() - dscr.mean():.2f}")
    st.area_chart(sens_dscr)

st.sidebar.markdown("---")
st.sidebar.button("Export to Excel (Mockup)")