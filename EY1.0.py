import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import openai
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="AI-Driven Green Investment Platform", layout="wide")
menu = st.tabs(["🏠 Home", "💹 ROI Calculator", "🤖 AI Green Advisor"])

# ---------------- HOME ----------------
with menu[0]:
    st.title("AI-Driven Green Financing Awareness Hub")
    st.info("IoT sensors and AI tools empower SMEs to track energy, water, and waste for sustainable ROI decisions.")
    st.header("📢 Latest News")
    st.markdown("""
    - [RHB Empowers SMEs with Green Financing for Sustainable Growth](https://www.malaysiasme.com.my/rhb-empowers-smes-with-green-financing-for-sustainable-growth/)
    - [SME Bank Sustainability Roadmap 2.0](https://www.smebank.com.my/w/sustainability-roadmap-2.0)
    """)
    st.header("🔗 Green Financing Resources")
    st.markdown("""
    - [Green Technology Financing Scheme (GTFS)](https://www.gtfs.my/)
    - [Bank Islam Eco SME Banking](https://www.bankislam.com/business-banking/sme-banking/eco/)
    - [Maybank ESG Financing](https://www.maybank2u.com.my/maybank2u/malaysia/en/business/sme/grow/esg-financing-listing.page)
    """)
    st.success("Empowering SMEs with AI insights for sustainable growth.")

# ---------------- ROI CALCULATOR ----------------
with menu[1]:
    st.title("💹 ROI Calculator for Green Investment")

    solar_data = {"Johor":1663.31,"Kedah":1797.00,"Kelantan":1726.84,"Kuala Lumpur":1663.42,"Melaka":1722.05,
                  "Negeri Sembilan":1676.98,"Pahang":1704.77,"Perak":1747.96,"Perlis":1810.04,"Pulau Pinang":1820.17,
                  "Putrajaya":1719.69,"Sabah":1756.45,"Sarawak":1696.05,"Selangor":1724.90,"Terengganu":1689.71}
    water_data = {"Kuala Lumpur":15.4,"Selangor":15.4,"Perak":12.6,"Pahang":10.2,"Negeri Sembilan":13,"Johor":21,
                  "Kelantan":11.4,"Terengganu":10,"Kedah":18,"Perlis":11.3,"Pulau Pinang":5,"Melaka":14.4,"Sarawak":12.6,"Sabah":11.8}
    tariffs_tiers=[(1,200,0.218),(201,300,0.334),(301,600,0.516),(601,900,0.546),(901,float('inf'),0.571)]

    state = st.selectbox("🏙️ Select State", list(solar_data.keys()))
    category = st.selectbox("Investment Category", ["Solar","Water","Other"])
    if category == "Other": st.warning("⚠️ 'Other' category not supported yet."); st.stop()
    investment = st.number_input("💰 Initial Investment (RM)", min_value=1000, value=5000, step=1000)

    def calculate_bill_from_kwh(kwh):
        bill, remaining = 0.0, kwh
        for low, high, rate in tariffs_tiers:
            limit = high - low + 1 if high != float('inf') else float('inf')
            use = min(remaining, limit)
            bill += use * rate
            remaining -= use
            if remaining <= 0: break
        return round(bill,2)

    def calculate_kwh_from_bill(target_bill):
        for kwh in range(1,5000):
            if calculate_bill_from_kwh(kwh) >= target_bill: return kwh
        return 5000

    house_types={"Terrace":(4,6),"Semi-detached":(6,9),"Bungalow":(9,13)}
    if category=="Solar":
        house_type=st.selectbox("🏠 House Type", list(house_types.keys()))
        system_min,system_max=house_types[house_type]

    bill_label="💡 Monthly Bill (RM)" if category=="Solar" else "💧 Monthly Bill (RM)"
    input_type=st.radio("Choose Input Type", [bill_label,"Monthly Consumption"])
    if input_type==bill_label:
        monthly_bill=st.number_input("Enter your monthly bill",min_value=10,value=300)
        if category=="Solar":
            monthly_kwh=calculate_kwh_from_bill(monthly_bill)
            estimated_system=(system_min+system_max)/2
            monthly_savings_default=int(estimated_system*60)
        else:
            monthly_kwh=None; monthly_savings_default=int(monthly_bill*0.2)
    else:
        if category=="Solar":
            monthly_kwh=st.number_input("Enter monthly consumption (kWh)",min_value=1,value=400)
            monthly_bill=calculate_bill_from_kwh(monthly_kwh)
            estimated_system=(system_min+system_max)/2
            monthly_savings_default=int(estimated_system*60)
        else:
            monthly_kwh=st.number_input("Enter monthly consumption (m³)",min_value=1,value=20)
            monthly_bill=monthly_kwh*0.5
            monthly_savings_default=int(monthly_bill*0.2)

    monthly_savings=st.number_input("⚡ Monthly Savings (RM)",min_value=1,value=monthly_savings_default,step=100)
    years=st.slider("⏳ Years",1,10,5)

    total_savings=monthly_savings*12*years
    roi=((total_savings-investment)/investment)*100
    payback_months=investment/monthly_savings if monthly_savings>0 else float('inf')
    payback_years=payback_months/12 if payback_months!=float('inf') else float('inf')

    st.subheader("📊 Results")
    st.write(f"**ROI:** {roi:.2f}%")
    st.write(f"**Total Savings ({years} yrs): RM {total_savings:,.2f}**")
    st.write(f"**Payback:** {payback_years:.1f} years")

    # ---------- AI Level 1: ROI Prediction ----------
    X=np.array([[1000],[5000],[10000],[20000],[30000],[50000]])
    y=np.array([8,25,45,60,75,85])
    model=LinearRegression().fit(X,y)
    predicted_roi=model.predict(np.array([[investment]]))[0]
    st.info(f"🤖 AI Predicted ROI: {predicted_roi:.2f}%")

    # ---------- AI Level 2: Recommendation ----------
    def ai_recommendation(state,category,investment):
        if category=="Solar":
            if solar_data[state]>1750 and investment<20000:
                return "🌞 High ROI potential — consider 6–8 kWp system."
            elif solar_data[state]<1700:
                return "⚠️ Low irradiation — ROI may be slower. Combine with water projects."
            else:
                return "✅ Balanced investment for your state."
        elif category=="Water":
            return "💧 High tariff area — good efficiency ROI." if water_data[state]>15 else "💧 Moderate ROI — pair with solar."
    st.success(f"🧠 AI Suggestion: {ai_recommendation(state,category,investment)}")

    # ---------- Chart ----------
    months=np.arange(1,years*12+1)
    savings=np.cumsum(np.full(years*12,monthly_savings)+np.random.normal(0,monthly_savings*0.05,years*12))
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(months,savings,label="Cumulative Savings")
    ax.axhline(y=investment,linestyle="--",label="Investment")
    ax.legend(); ax.set_xlabel("Months"); ax.set_ylabel("RM")
    st.pyplot(fig)

    # ---------- Export ----------
    export=st.selectbox("Export Format",["CSV","PDF"])
    if st.button("Export Report"):
        df=pd.DataFrame({"Month":months,"Cumulative Savings":savings})
        if export=="CSV":
            st.download_button("Download CSV",df.to_csv(index=False).encode("utf-8"),file_name="roi.csv",mime="text/csv")
        else:
            buffer=BytesIO()
            doc=SimpleDocTemplate(buffer,pagesize=A4)
            styles=getSampleStyleSheet()
            data=[["Month","Cumulative Savings"]]+[[m,f"RM {s:,.2f}"] for m,s in zip(months,savings[:120])]
            table=Table(data,colWidths=[100,200])
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.green),
                                       ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                                       ('ALIGN',(0,0),(-1,-1),'CENTER'),
                                       ('GRID',(0,0),(-1,-1),1,colors.black)]))
            elements=[Paragraph("ROI Report",styles["Title"]),Spacer(1,12),table]
            doc.build(elements)
            pdf=buffer.getvalue()
            st.download_button("Download PDF",data=pdf,file_name="roi_report.pdf",mime="application/pdf")

# ---------------- AI GREEN ADVISOR ----------------
with menu[2]:

    st.title("🤖 AI Green Financing Advisor")
    st.write("Ask about ROI, ESG, or financing opportunities.")

    # User input
    user_question = st.text_input("💬 Your question:")
    
    if st.button("Ask AI"):
        ql = user_question.lower().strip()
        
        if ql == "":
            st.write("Please enter a question.")
        
        # Rule-based quick answers
        elif "loan" in ql or "finance" in ql:
            st.write("💬 AI Advisor: GTFS and LCTF offer low-interest green financing for SMEs.")
        elif "roi" in ql or "payback" in ql:
            st.write("💬 AI Advisor: Solar ROI typically ranges from 30–80% depending on state irradiation.")
        elif "esg" in ql:
            st.write("💬 AI Advisor: ESG adoption improves access to capital and brand reputation.")
        
        # Fallback to OpenAI GPT
        else:
            try:
                # Check if API key exists
                api_key = st.secrets.get("OPENAI_API_KEY", None)
                if not api_key:
                    st.error("OpenAI API key is missing! Please add it in Streamlit Secrets.")
                else:
                    openai.api_key = api_key
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",  # works with all API keys
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": user_question}
                        ],
                        temperature=0.7,
                        max_tokens=300
                    )
                    answer = response.choices[0].message.content
                    st.write(f"💬 AI Advisor (GPT): {answer}")
            except Exception as e:
                st.error(f"Error contacting AI: {e}")
