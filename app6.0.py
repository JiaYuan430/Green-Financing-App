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

# HOME PAGE
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

# ROI CALCULATOR PAGE
with menu[1]:
    st.title("💹 ROI Calculator for Green Investment")

    # Category selection
    categories = ["Solar", "Water", "Waste Management", "Energy Efficiency", "Other"]

    # State lists and solar yearly potential (kWh)
    solar_data = {
        "Johor": 1663.31, "Kedah": 1797.00, "Kelantan": 1726.84, "Kuala Lumpur": 1663.42, 
        "Melaka": 1722.05, "Negeri Sembilan": 1676.98, "Pahang": 1704.77,
        "Perak": 1747.96, "Perlis": 1810.04, "Pulau Pinang": 1820.17, "Putrajaya": 1719.69,
        "Sabah": 1756.45, "Sarawak": 1696.05, "Selangor": 1724.90, "Terengganu": 1689.71
    }

    water_data = {
        "Kuala Lumpur": 15.4, "Selangor": 15.4, "Perak": 12.6, "Pahang": 10.2, "Negeri Sembilan": 13,
        "Johor": 21, "Kelantan": 11.4, "Terengganu": 10, "Kedah": 18, "Perlis": 11.3,
        "Penang": 5, "Melaka": 14.4, "Sarawak": 12.6, "Sabah": 11.8
    }

    state_list = list(solar_data.keys())
    state = st.selectbox("🏙️ Select Your State", state_list)

    category = st.selectbox("Select Investment Category", categories)

    # User inputs
    investment = st.number_input("💰 Initial Investment (RM)", min_value=1000, value=50000, step=1000)

    # Tiered TNB residential tariff
    tariffs = {
        (1, 200): 0.218,
        (201, 300): 0.334,
        (301, 600): 0.516,
        (601, 900): 0.546,
        (901, float('inf')): 0.571
    }

    def calculate_solar_savings(monthly_consumption_kwh, solar_kwh):
        remaining_offset = solar_kwh
        savings = 0
        lower = 1
        for (low, high), rate in tariffs.items():
            upper = min(high, monthly_consumption_kwh)
            tier_kwh = min(upper - lower + 1, remaining_offset)
            if tier_kwh > 0:
                savings += tier_kwh * rate
                remaining_offset -= tier_kwh
            lower = high + 1
            if remaining_offset <= 0:
                break
        return savings

    avg_monthly_consumption = st.number_input("🏠 Average Monthly Electricity Consumption (kWh)", min_value=50, value=400, step=10)

    house_types = {
        "Terrace House": {"system_range": (4, 6), "cost_range": (16000, 24000)},
        "Semi-detached": {"system_range": (6, 9), "cost_range": (24000, 34000)},
        "Bungalow": {"system_range": (9, 13), "cost_range": (34000, 46000)}
    }
    
    solar_bill_map = [
        {"min": 170, "max": 230, "size": 4.5, "kwh": 473, "saving": (168, 203)},
        {"min": 240, "max": 310, "size": 5.5, "kwh": 578, "saving": (239, 281)},
        {"min": 320, "max": 440, "size": 7.0, "kwh": 735, "saving": (319, 389)},
        {"min": 450, "max": 570, "size": 9.5, "kwh": 998, "saving": (448, 520)},
        {"min": 580, "max": 700, "size": 11.5, "kwh": 1208, "saving": (577, 648)},
        {"min": 701, "max": 99999, "size": 13.0, "kwh": 1365, "saving": (685, 704)},
    ]
    
    # Water tariffs (RM/m³) by state
    water_tariffs = {
        "Kuala Lumpur": 0.57, "Selangor": 0.57, "Perak": 0.50, "Pahang": 0.48,
        "Negeri Sembilan": 0.55, "Johor": 0.60, "Kelantan": 0.45, "Terengganu": 0.47,
        "Kedah": 0.52, "Perlis": 0.49, "Pulau Pinang": 0.50, "Melaka": 0.53,
        "Sarawak": 0.51, "Sabah": 0.50
    }
    
    # Default User Input Value
    if category == "Solar":
        house_types = {
            "Terrace House": {"system_range": (4, 6), "cost_range": (16000, 24000)},
            "Semi-detached": {"system_range": (6, 9), "cost_range": (24000, 34000)},
            "Bungalow": {"system_range": (9, 13), "cost_range": (34000, 46000)}
        }
        house_type = st.selectbox("🏠 House Type", list(house_types.keys()))
        system_min, system_max = house_types[house_type]["system_range"]

        solar_bill_map = [
            {"min": 170, "max": 230, "size": 4.5, "kwh": 473, "saving": (168, 203)},
            {"min": 240, "max": 310, "size": 5.5, "kwh": 578, "saving": (239, 281)},
            {"min": 320, "max": 440, "size": 7.0, "kwh": 735, "saving": (319, 389)},
            {"min": 450, "max": 570, "size": 9.5, "kwh": 998, "saving": (448, 520)},
            {"min": 580, "max": 700, "size": 11.5, "kwh": 1208, "saving": (577, 648)},
            {"min": 710, "max": 9999, "size": 13.0, "kwh": 1365, "saving": (685, 704)},
        ]

        monthly_bill = st.number_input("💡 Monthly TNB Bill (RM)", min_value=50, value=300, step=10)

        matched = None
        for row in solar_bill_map:
            if row["min"] <= monthly_bill <= row["max"]:
                matched = row
                break

        if matched:
            # check the size for house type
            system_size_kw = matched["size"]
            if system_size_kw < system_min:
                system_size_kw = system_min
            elif system_size_kw > system_max:
                system_size_kw = system_max

            monthly_savings_default = int(np.mean(matched["saving"]))
        else:
            # If not match
            system_size_kw = (system_min + system_max) / 2
            monthly_savings_default = int(system_size_kw * 60) 

        st.write(f"🔧 Recommended System Size: {system_size_kw:.1f} kWp ({house_type})")
    
    elif category == "Water":
        monthly_usage = st.number_input("🚰 Monthly Water Usage (m³)", min_value=5, value=20, step=1)
        efficiency = st.slider("💧 Efficiency Improvement (%)", 1, 50, 20)
        tariff = water_tariffs.get(state, 0.5)
    
        monthly_bill = monthly_usage * tariff
        monthly_savings_default = int(monthly_bill * (efficiency / 100))
    
    else:
        monthly_savings_default = 1000
    
    monthly_savings = st.number_input(
        "⚡ Monthly Savings (RM)", 
        min_value=1,
        value=int(monthly_savings_default), 
        step=100
    )
    
    years = st.slider("⏳ Investment Horizon (Years)", 1, 10, 5)
    
    # ROI calculation
    total_savings = monthly_savings * 12 * years
    roi = ((total_savings - investment) / investment) * 100
    payback_months = investment / monthly_savings
    payback_years = payback_months / 12
    
    st.subheader("📊 Results")
    st.write(f"**Category:** {category}")
    st.write(f"**Total Savings (over {years} years): RM {total_savings:,.2f}**")
    st.write(f"**ROI: {roi:.2f}%**")
    st.write(f"**Payback Period: {payback_months:.1f} months (~{payback_years:.1f} years)**")
    
    # Monthly savings chart data
    months = np.arange(1, years * 12 + 1)
    savings = np.cumsum(np.random.normal(monthly_savings, monthly_savings * 0.1, years * 12))

    # Chart section
    st.subheader("📊 Visualization Options")
    chart_options = ["Cumulative Savings Over Time", "Investment vs. Total Savings"]
    selected_charts = st.multiselect("Select chart(s) to display", chart_options)

    if "Cumulative Savings Over Time" in selected_charts or "Investment vs. Total Savings" in selected_charts:
        col1, col2 = st.columns(2)
        if "Cumulative Savings Over Time" in selected_charts:
            with col1:
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
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                ax2.bar(["Initial Investment", f"Savings ({years} yrs)"], [investment, total_savings], color=["red", "green"])
                ax2.set_ylabel("RM")
                ax2.set_title(f"Investment vs. Total Savings in {state} for {category}")
                st.pyplot(fig2)

    # Export options
    st.subheader("📤 Export Report")
    export_format = st.selectbox("Choose format", ["CSV", "PDF"])

    if st.button("Export Report"):
        # Prepare dataframes
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
            elements.append(Spacer(1, 12))
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

            # ROI Summary
            roi_summary_text = (f"ROI: {roi:.2f}% | Total Savings: RM {total_savings:,.2f} | Investment: RM {investment:,.2f}<br/>"
    )
            roi_summary_table = Table([[Paragraph(f"<b>{roi_summary_text}</b>", styles['Normal'])]], colWidths=[400])
            roi_summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
                ('BOX', (0, 0), (-1, -1), 1, colors.green),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),('FONTSIZE', (0,0), (-1,-1), 10),
            ]))
            roi_summary_wrapper = Table([[roi_summary_table]], colWidths=[450])
            roi_summary_wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            elements.append(roi_summary_wrapper)
            elements.append(Spacer(1, 12))

            # Charts
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

            doc.build(elements)
            st.download_button("Download PDF", data=buffer.getvalue(), file_name=f"roi_report_{state}_{category}.pdf", mime="application/pdf")











