import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet

# App configuration
st.set_page_config(page_title="Green Financing Awareness", layout="wide")

# Top navigation menu
menu = st.tabs(["🏠 Home", "💹 ROI Calculator"])

# ---------------- HOME PAGE ----------------
with menu[0]:
    st.title("🌱 Green Financing Awareness Hub")

    # IoT Explanation Box
    st.info("""
    🔗 **IoT in Green Investment**
    Internet of Things (IoT) devices such as smart sensors and meters help businesses track energy, water, and waste usage in real-time. 
    By monitoring efficiency, SMEs can identify savings opportunities, reduce environmental impact, and improve the accuracy of ROI calculations for green investments.
    """)

    st.header("📢 Latest News")
    st.markdown("""
    - [RHB Empowers SMEs with Green Financing for Sustainable Growth](https://www.malaysiasme.com.my/rhb-empowers-smes-with-green-financing-for-sustainable-growth/)
    - [SME Bank Sustainability Roadmap 2.0](https://www.smebank.com.my/w/sustainability-roadmap-2.0)
    """)

    st.header("🤝 Green Financing Support Links")
    st.markdown("""
    - [Green Technology Financing Scheme (GTFS)](https://www.gtfs.my/)
    - [Bank Islam Eco SME Banking](https://www.bankislam.com/business-banking/sme-banking/eco/)
    - [Maybank ESG Financing](https://www.maybank2u.com.my/maybank2u/malaysia/en/business/sme/grow/esg-financing-listing.page)
    """)

    st.success("This hub provides SMEs with awareness, resources, and financial guidance for a sustainable future.")

# ---------------- ROI CALCULATOR PAGE ----------------
with menu[1]:
    st.title("💹 ROI Calculator for Green Investment")

    # Category selection
    categories = ["Solar", "Water", "Waste Management", "Energy Efficiency", "Other"]

    # ---------------- State Selection & Average Data ----------------
    # State lists
    solar_data = {
        "Johor": 1663.31, "Kedah": 1797.00, "Kelantan": 1726.84, "Kuala Lumpur": 1663.42,
        "Labuan": 1904.39, "Melaka": 1722.05, "Negeri Sembilan": 1676.98, "Pahang": 1704.77,
        "Perak": 1747.96, "Perlis": 1810.04, "Pulau Pinang": 1820.17, "Putrajaya": 1719.69,
        "Sabah": 1756.45, "Sarawak": 1696.05, "Selangor": 1724.90, "Trengganu": 1689.71
    }

    water_data = {
        "Kuala Lumpur": 15.4, "Selangor": 15.4, "Perak": 12.6, "Pahang": 10.2, "Negeri Sembilan": 13,
        "Johor": 21, "Kelantan": 11.4, "Terengganu": 10, "Kedah": 18, "Perlis": 11.3,
        "Penang": 5, "Melaka": 14.4, "Sarawak": 12.6, "Sabah": 11.8
    }

    state_list = list(solar_data.keys())
    state = st.selectbox("🏙️ Select Your State", state_list)

    category = st.selectbox("Select Investment Category", ["Solar", "Water", "Waste Management", "Energy Efficiency", "Other"])

    # User inputs
    investment = st.number_input("💰 Initial Investment (RM)", min_value=1000, value=50000, step=1000)

    # ---------------- Default Monthly Savings ----------------
if category == "Solar":
    # Ask user for house type
    house_type = st.selectbox("Select Your House Type", ["Terrace House", "Semi-detached", "Bungalow"])
    
    # Map house type to typical system capacity (kWp)
    house_solar_system = {
        "Terrace House": 5,      # avg 4–6 kWp
        "Semi-detached": 7.5,    # avg 6–9 kWp
        "Bungalow": 11           # avg 9–13 kWp
    }

    system_size = house_solar_system[house_type]

    # Estimate monthly savings based on state average + system size
    # Assume average system size across keys = 7.5 kWp (for scaling)
    average_system_size = 7.5
    annual_saving = solar_data[state]  # yearly RM saving per state
    monthly_savings_default = int((annual_saving * (system_size / average_system_size)) / 12)

    elif category == "Water":
        monthly_savings_default = water_data[state]  # average monthly bill as default
    else:
        monthly_savings_default = 1000  # fallback for other categories

    monthly_savings = st.number_input(
        "⚡ Monthly Savings (RM)", 
        min_value=50,  # lower min_value to prevent errors
        value=int(monthly_savings_default), 
        step=50
    )

    years = st.slider("⏳ Investment Horizon (Years)", 1, 10, 5)

    # ROI calculation
    total_savings = monthly_savings * 12 * years
    roi = ((total_savings - investment) / investment) * 100

    # Payback period
    payback_months = investment / monthly_savings
    payback_years = payback_months / 12

    st.subheader("📊 Results")
    st.write(f"**Category:** {category}")
    st.write(f"**Total Savings (over {years} years): RM {total_savings:,.2f}**")
    st.write(f"**ROI: {roi:.2f}%**")
    st.write(f"**Payback Period: {payback_months:.1f} months (~{payback_years:.1f} years)**")

    # Data for charts
    months = np.arange(1, years * 12 + 1)
    savings = np.cumsum(np.random.normal(monthly_savings, monthly_savings * 0.1, years * 12))


    # --- Chart selection ---
    st.subheader("📊 Visualization Options")
    chart_options = ["Cumulative Savings Over Time", "Investment vs. Total Savings"]
    selected_charts = st.multiselect("Select chart(s) to display", chart_options)

    if "Cumulative Savings Over Time" in selected_charts or "Investment vs. Total Savings" in selected_charts:
        # Use columns for side-by-side layout
        col1, col2 = st.columns(2)

        if "Cumulative Savings Over Time" in selected_charts:
            with col1:
                st.markdown(f"### 📈 Cumulative Savings Over Time ({state} - {category})")
                fig1, ax1 = plt.subplots(figsize=(6, 4))
                ax1.plot(months, savings, label="Cumulative Savings", color="green")
                ax1.axhline(y=investment, color="red", linestyle="--", label="Initial Investment")
                if monthly_savings > 0 and payback_months <= years * 12:
                    ax1.axvline(x=payback_months, color="blue", linestyle="--", label="Payback Period")
                ax1.set_xlabel("Months")
                ax1.set_ylabel("RM")
                ax1.set_title(f"Monthly Cumulative Savings in {state} for {category}")
                ax1.legend()
                st.pyplot(fig1)

        if "Investment vs. Total Savings" in selected_charts:
            with col2:
                st.markdown(f"### 📊 Investment vs. Total Savings ({state} - {category})")
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                ax2.bar(["Initial Investment", f"Savings ({years} yrs)"], [investment, total_savings], color=["red", "green"])
                ax2.set_ylabel("RM")
                ax2.set_title(f"Investment vs. Total Savings in {state} for {category}")
                st.pyplot(fig2)

    # ---------------- Export options ----------------
    st.subheader("📤 Export Report")
    export_format = st.selectbox("Choose format", ["CSV", "PDF"])

    if st.button("Export Report"):
        # --- Prepare dataframes
        df_monthly = pd.DataFrame({"Month": months, "Cumulative Savings": savings})
        df_yearly = df_monthly.groupby((df_monthly.index)//12 + 1).last().reset_index(drop=True)
        df_yearly.index += 1
        df_yearly = df_yearly.rename(columns={"Cumulative Savings": "Yearly Cumulative Savings"})
        df_yearly.insert(0, "Year", df_yearly.index)

        if export_format == "CSV":
            csv_monthly = df_monthly.to_csv(index=False).encode("utf-8")
            st.download_button("Download Monthly CSV", data=csv_monthly, file_name=f"roi_monthly_{state}_{category}.csv", mime="text/csv")

            csv_yearly = df_yearly.to_csv(index=False).encode("utf-8")
            st.download_button("Download Yearly CSV", data=csv_yearly, file_name=f"roi_yearly_{state}_{category}.csv", mime="text/csv")

        elif export_format == "PDF":
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # Report text
            elements.append(Paragraph("ROI Report - Green Investment", styles['Title']))
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(f"State: {state}", styles['Normal']))
            elements.append(Paragraph(f"Category: {category}", styles['Normal']))
            elements.append(Paragraph(f"Initial Investment: RM {investment:,.2f}", styles['Normal']))
            elements.append(Paragraph(f"Total Savings: RM {total_savings:,.2f}", styles['Normal']))
            elements.append(Paragraph(f"ROI: {roi:.2f}%", styles['Normal']))
            elements.append(Paragraph(f"Payback Period: {payback_months:.1f} months (~{payback_years:.1f} years)", styles['Normal']))
            elements.append(Spacer(1, 12))

            # Monthly table
            data_monthly = [["Month", "Cumulative Savings"]] + [[m, f"RM {s:,.2f}"] for m, s in zip(months, savings)]
            table_monthly = Table(data_monthly, colWidths=[100, 200])
            monthly_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
            ])
            if payback_months <= years * 12:
                payback_row = int(round(payback_months))
                monthly_style.add('BACKGROUND', (0, payback_row), (-1, payback_row), colors.yellow)
                monthly_style.add('TEXTCOLOR', (0, payback_row), (-1, payback_row), colors.black)
                monthly_style.add('FONTNAME', (0, payback_row), (-1, payback_row), 'Helvetica-Bold')
            table_monthly.setStyle(monthly_style)
            elements.append(Paragraph("📅 Monthly Savings", styles['Heading2']))
            elements.append(table_monthly)
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("<i>Highlighted row = Month when investment is fully recovered</i>", styles['Normal']))
            elements.append(Spacer(1, 12))

            # Yearly table
            data_yearly = [["Year", "Cumulative Savings"]] + [[y, f"RM {s:,.2f}"] for y, s in zip(df_yearly["Year"], df_yearly["Yearly Cumulative Savings"])]
            table_yearly = Table(data_yearly, colWidths=[100, 200])
            table_yearly.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
            ]))
            elements.append(Paragraph("📆 Yearly Savings Summary", styles['Heading2']))
            elements.append(table_yearly)
            elements.append(Spacer(1, 12))

            # ---------------- ROI Summary ----------------
            roi_summary_text = f"State: {state} | Category: {category} | Payback achieved in ~{payback_years:.1f} years"
            roi_summary_table = Table([[Paragraph(f"<b>{roi_summary_text}</b>", styles['Normal'])]], colWidths=[400])
            roi_summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
                ('BOX', (0, 0), (-1, -1), 1, colors.green),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            roi_summary_wrapper = Table([[roi_summary_table]], colWidths=[450])
            roi_summary_wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            elements.append(roi_summary_wrapper)
            elements.append(Spacer(1, 12))

            # Add charts with state & category info
            if "Cumulative Savings Over Time" in selected_charts and "fig1" in locals():
                img_buffer1 = BytesIO()
                fig1.savefig(img_buffer1, format="png")
                img_buffer1.seek(0)
                elements.append(Paragraph(f"Cumulative Savings Over Time ({state} - {category})", styles['Heading3']))
                elements.append(Image(img_buffer1, width=400, height=200))
                elements.append(Spacer(1, 12))

            if "Investment vs. Total Savings" in selected_charts and "fig2" in locals():
                img_buffer2 = BytesIO()
                fig2.savefig(img_buffer2, format="png")
                img_buffer2.seek(0)
                elements.append(Paragraph(f"Investment vs. Total Savings ({state} - {category})", styles['Heading3']))
                elements.append(Image(img_buffer2, width=400, height=200))
                elements.append(Spacer(1, 12))

            # Build PDF
            doc.build(elements)
            st.download_button("Download PDF", data=buffer.getvalue(), file_name=f"roi_report_{state}_{category}.pdf", mime="application/pdf")

