import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os


# 🌐 Load Supabase credentials from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
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
st.title("Enter Visit Details")

# 🔍 Get patients by name
def get_patients_by_name(name):
    response = supabase.table("patients") \
        .select("patient_id, patient_first_name, patient_last_name") \
        .or_(f"patient_first_name.ilike.%{name}%,patient_last_name.ilike.%{name}%") \
        .execute()
    return response.data if response.data else []

# 👨‍⚕️ Get list of doctors
def get_doctors():
    response = supabase.table("doctors").select("doctor_id, doctor_name").execute()
    return response.data if response.data else []


# 📥 Insert visit details
def insert_visit_details(patient_id, admission_type, visit_date, room_number,
                         doctor_id, symptoms, tests, diagnosis_notes, prescription,
                         payment_amount, payment_method, payment_invoice_number):
    try:
        response = supabase.table("visits").insert({
            "patient_id": patient_id,
            "admission_type": admission_type,
            "visit_date": str(visit_date),
            "room_number": room_number,
            "doctor_id": doctor_id,
            "symptoms": symptoms,
            "tests": tests,
            "diagnosis_notes": diagnosis_notes,
            "prescription": prescription,
            "payment_amount": payment_amount,
            "payment_method": payment_method,
            "payment_invoice_number": payment_invoice_number
        }).execute()

        if response.data:
            st.success("Visit details inserted successfully!")
            st.info(f"Record ID: {response.data[0]['record_id']}")
        else:
            st.warning("Insertion completed but returned no data.")
    except Exception as e:
        st.error(f"Error inserting visit: {e}")



# 🧾 Main input form
def main():
    name = st.text_input("Search Patient by First or Last Name")
    patients = get_patients_by_name(name)
    patient_options = [f"{p['patient_id']} - {p['patient_first_name']} {p['patient_last_name']}" for p in patients]

    if not patients:
        st.warning("No patients found. Please add a new patient first.")
    else:
        selected_patient_options = st.multiselect("Select Patient", patient_options, [])
        selected_patient_ids = [int(option.split(" - ")[0]) for option in selected_patient_options]

        admission_type = st.selectbox("Admission Type", ["Inpatient", "Outpatient"])
        visit_date = st.date_input("Visit Date")
        room_number = st.text_input("Room Number")

        doctors = get_doctors()
        if not doctors:
            st.error("No doctors found.")
            return

        doctor_names = [d["doctor_name"] for d in doctors]
        selected_doctor_name = st.selectbox("Doctor Name", doctor_names)
        selected_doctor_id = doctors[doctor_names.index(selected_doctor_name)]["doctor_id"]

        symptoms = st.text_area("Symptoms")
        tests = st.text_area("Tests")
        diagnosis_notes = st.text_area("Diagnosis Notes")
        prescription = st.text_area("Prescription")
        payment_amount = st.number_input("Payment Amount", min_value=0.0)
        payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Insurance"])
        payment_invoice_number = st.text_input("Payment Invoice Number")

        if st.button("Submit"):
            if selected_patient_ids:
                for patient_id in selected_patient_ids:
                    insert_visit_details(
                        patient_id, admission_type, visit_date, room_number,
                        selected_doctor_id, symptoms, tests, diagnosis_notes,
                        prescription, payment_amount, payment_method, payment_invoice_number
                    )
            else:
                st.warning("Please select at least one patient before submitting.")

if __name__ == "__main__":
    main()