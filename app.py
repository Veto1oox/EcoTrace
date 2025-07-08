
import streamlit as st
import openai
import json
import matplotlib.pyplot as plt

# --- Configuration ---
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Use Streamlit secrets for security

# --- UI ---
st.title("EcoTrace: Estimate Your Carbon Emissions")

st.write("Answer the questions below to get an estimated breakdown of your company's annual carbon emissions.")

locations = st.number_input("How many physical locations do you operate?", min_value=1, step=1)
employees = st.selectbox("How many employees work on-site?", ["<10", "10–50", "51–200", "200+"])
energy_type = st.selectbox("What type of energy do you use?", ["Electricity (Grid)", "Natural Gas", "Solar", "Diesel"])
shipping_volume = st.number_input("How many packages do you ship per week?", min_value=0, step=10)
materials = st.multiselect("Which materials do you primarily use?", ["Plastic", "Cardboard", "Aluminum", "Textiles", "Other"])

if st.button("Estimate My Emissions"):

    prompt = f'''
    You are a sustainability analyst. A company has the following characteristics:
    - {locations} physical locations
    - {employees} employees working on-site
    - Energy source: {energy_type}
    - Ships {shipping_volume} packages per week
    - Uses materials: {", ".join(materials)}

    Estimate their annual carbon emissions in metric tons CO2, and return a JSON like:
    {{
        "total_tCO2_range": "X–Y",
        "breakdown_by_category": {{
            "Energy": A,
            "Transportation": B,
            "Materials": C
        }}
    }}
    '''

    with st.spinner("Calculating with GPT..."):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response['choices'][0]['message']['content']

        try:
            result = json.loads(content)
            st.success(f"Estimated Annual Emissions: {result['total_tCO2_range']} tCO₂")

            breakdown = result['breakdown_by_category']
            labels = list(breakdown.keys())
            sizes = list(breakdown.values())

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

        except Exception as e:
            st.error("Error parsing GPT output. Please try again.")
            st.text(content)
