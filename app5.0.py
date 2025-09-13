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
    
    Internet of Things (IoT) devices such as smart sensors and meters help businesses 
    track energy, water, and waste usage in real-time. By monitoring efficiency, 
    SMEs can identify savings opportunities, reduce environmental impact, 
    and improve the accuracy of ROI calculations for green investments.
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
    category = st.selectbox("📂 Select Investment Category", categories)

    # User inputs
    investment = st.number_input("💰 Initial Investment (RM)", min_value=1000, value=50000, step=1000)
    monthly_savings = st.number_input("⚡ Monthly Savings (RM)", min_value=100, value=3000, step=100)
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
    chart_options = ["Cumulative Savings Over Time", "Investment vs. Total Savings", "ROI Benchmark by Category"]
    selected_charts = st.multiselect("Select chart(s) to display", chart_options)

    if "Cumulative Savings Over Time" in selected_charts:
        st.markdown("### 📈 Cumulative Savings Over Time")
        fig1, ax1 = plt.subplots(figsize=(8, 4))
        ax1.plot(months, savings, label="Cumulative Savings", color="green")
        ax1.axhline(y=investment, color="red", linestyle="--", label="Initial Investment")
        ax1.axvline(x=payback_months, color="blue", linestyle="--", label="Payback Period")
        ax1.set_xlabel("Months")
        ax1.set_ylabel("RM")
        ax1.set_title("Monthly Cumulative Electricity Savings")
        ax1.legend()
        st.pyplot(fig1)

    if "Investment vs. Total Savings" in selected_charts:
        st.markdown("### 📊 Investment vs. Total Savings")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.bar(["Initial Investment", f"Savings ({years} yrs)"], [investment, total_savings], color=["red", "green"])
        ax2.set_ylabel("RM")
        ax2.set_title("Comparison of Investment vs. Total Savings")
        st.pyplot(fig2)

    if "ROI Benchmark by Category" in selected_charts:
        st.markdown("### 📊 ROI Benchmark by Category")
        roi_values = {
            "Solar": ((monthly_savings*12*years - investment)/investment)*100,
            "Water": ((monthly_savings*12*years*0.9 - investment)/investment)*100,
            "Waste Management": ((monthly_savings*12*years*1.1 - investment)/investment)*100,
            "Energy Efficiency": ((monthly_savings*12*years*1.05 - investment)/investment)*100,
            "Other": ((monthly_savings*12*years*0.95 - investment)/investment)*100
        }
        fig3, ax3 = plt.subplots(figsize=(7,4))
        ax3.bar(roi_values.keys(), roi_values.values(), color="skyblue")
        ax3.set_ylabel("ROI (%)")
        ax3.set_title("ROI Benchmark Across Categories")
        st.pyplot(fig3)

    # Export options
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
            st.download_button("Download Monthly CSV", data=csv_monthly, file_name="roi_monthly.csv", mime="text/csv")

            csv_yearly = df_yearly.to_csv(index=False).encode("utf-8")
            st.download_button("Download Yearly CSV", data=csv_yearly, file_name="roi_yearly.csv", mime="text/csv")

        elif export_format == "PDF":
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []

            # Report text
            elements.append(Paragraph("ROI Report - Green Investment", styles['Title']))
            elements.append(Spacer(1, 12))
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

            # ROI summary
            roi_summary_text = f"Payback achieved in ~{payback_years:.1f} years"
            roi_summary_table = Table([[Paragraph(f"<b>{roi_summary_text}</b>", styles['Normal'])]], colWidths=[300])
            roi_summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
                ('BOX', (0, 0), (-1, -1), 1, colors.green),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            roi_summary_wrapper = Table([[roi_summary_table]], colWidths=[450])
            roi_summary_wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            elements.append(roi_summary_wrapper)
            elements.append(Spacer(1, 6))

            # Final ROI
            roi_final = ((df_yearly["Yearly Cumulative Savings"].iloc[-1] - investment) / investment) * 100
            roi_final_text = f"Final ROI after {years} years: {roi_final:.2f}%"
            roi_final_table = Table([[Paragraph(f"<b>{roi_final_text}</b>", styles['Normal'])]], colWidths=[300])
            roi_final_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgreen),
                ('BOX', (0, 0), (-1, -1), 1, colors.green),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            roi_final_wrapper = Table([[roi_final_table]], colWidths=[450])
            roi_final_wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
            elements.append(roi_final_wrapper)
            elements.append(Spacer(1, 12))

            # Always include all 3 charts in PDF
            img_buffer1 = BytesIO()
            fig1.savefig(img_buffer1, format="png")
            img_buffer1.seek(0)
            elements.append(Image(img_buffer1, width=400, height=200))
            elements.append(Spacer(1, 12))

            img_buffer2 = BytesIO()
            fig2.savefig(img_buffer2, format="png")
            img_buffer2.seek(0)
            elements.append(Image(img_buffer2, width=400, height=200))
            elements.append(Spacer(1, 12))

            img_buffer3 = BytesIO()
            fig3.savefig(img_buffer3, format="png")
            img_buffer3.seek(0)
            elements.append(Image(img_buffer3, width=400, height=200))

            # Build PDF
            doc.build(elements)
            st.download_button("Download PDF", data=buffer.getvalue(), file_name="roi_report.pdf", mime="application/pdf")
