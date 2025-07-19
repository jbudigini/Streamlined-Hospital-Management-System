import streamlit as st
import pandas as pd
import base64
import os
from dotenv import load_dotenv
from supabase import create_client, Client


# ✅ Load environment variables from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔁 Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_gradient_style():
    """
    Defines the CSS style targeting the main app container.
    """
    return """
    <style>
      [data-testid="stAppViewContainer"] {
        background: linear-gradient(to bottom, #e0e7ff, #d1e0fc);
      }

      [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #e0e7ff, #d1e0fc) !important;
      }
    </style>
    """


st.markdown(get_gradient_style(), unsafe_allow_html=True)
st.title("Patients")

# 📥 Fetch all patient data
def fetch_patient_data():
    response = supabase.table("patients").select("*").execute()
    return response.data if response.data else []

# 📤 Insert a new patient record
def insert_patient_data(first_name, last_name, age, gender, height, weight, allergies, address, insurance_provider):
    response = supabase.table("patients").insert({
        "patient_first_name": first_name,
        "patient_last_name": last_name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "allergies": allergies,
        "address": address,
        "insurance_provider": insurance_provider
    }).execute()
    st.success("Patient record added successfully!")

# 🗑️ Delete patient by ID
def delete_patient_record(patient_id):
    supabase.table("patients").delete().eq("patient_id", patient_id).execute()
    st.success("Patient record deleted successfully!")

# 📊 Display patient data in table
def display_patient_data(patient_data):
    if patient_data:
        df = pd.DataFrame(patient_data)
        # Optionally format columns for UI
        df = df.rename(columns={
            "patient_id": "Patient ID",
            "patient_first_name": "First Name",
            "patient_last_name": "Last Name",
            "age": "Age",
            "gender": "Gender",
            "height": "Height (cm)",
            "weight": "Weight (kg)",
            "allergies": "Allergies",
            "address": "Address",
            "insurance_provider": "Insurance Provider"
        })
        st.dataframe(df)
    else:
        st.info("No patient data found.")


# 🧾 Display data with delete checkboxes
def display_patient_data_with_delete(patient_data):
    if patient_data:
        df = pd.DataFrame(patient_data)
        df["Delete"] = df.apply(lambda row: st.checkbox("", value=False, key=f"delete_{row['patient_id']}"), axis=1)
        st.dataframe(df.drop(columns=["Delete"]))
        to_delete = [row["patient_id"] for _, row in df.iterrows() if row["Delete"]]

        if st.button("Delete Selected"):
            for pid in to_delete:
                delete_patient_record(pid)
            st.rerun()
    else:
        st.write("No matching patients found.")


# ➕ Patient input form
def add_patient_form():
    st.subheader("Add New Patient")
    with st.form("patient_form"):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        age = st.number_input("Age", min_value=0, step=1)
        gender = st.selectbox("Gender", ["M", "F"])
        height = st.number_input("Height (cm)", min_value=0.0)
        weight = st.number_input("Weight (kg)", min_value=0.0)
        allergies = st.text_area("Allergies")
        address = st.text_area("Address")
        insurance_provider = st.text_input("Insurance Provider")
        submit = st.form_submit_button("Add Patient")
        if submit:
            insert_patient_data(first_name, last_name, age, gender, height, weight, allergies, address, insurance_provider)
    


# 🔍 Search patients
def search_patients():
    st.subheader("Search Patients")
    search_term = st.text_input("Enter patient's first or last name:")
    if search_term:
        response = supabase.table("patients") \
            .select("*") \
            .or_(f"patient_first_name.ilike.%{search_term}%,patient_last_name.ilike.%{search_term}%") \
            .execute()
        search_results = response.data
        if search_results:
            st.write("Search Results:")
            display_patient_data_with_delete(search_results)
        else:
            st.write("No matching patients found.")



# 📂 Patient profile view (all data)
def patient_profile():
    st.subheader("Patient Profile")
    data = fetch_patient_data()
    display_patient_data(data)

# 📌 Sidebar navigation
page_selection = st.sidebar.radio("Navigation", ["Search Patients", "Add Patient", "Patient Profile"])

if page_selection == "Search Patients":
    search_patients()
elif page_selection == "Add Patient":
    add_patient_form()
elif page_selection == "Patient Profile":
    patient_profile()
