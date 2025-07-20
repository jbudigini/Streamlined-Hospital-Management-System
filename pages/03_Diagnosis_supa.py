import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
import os


# 🔐 Load credentials from .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def force_light_theme_style():
    return """
    <style>
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f0f4ff !important;
            color: black !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #e0e7ff, #d1e0fc) !important;
            color: black !important;
        }

        /* Sidebar text including navigation labels */
        [data-testid="stSidebar"] * {
            color: black !important;
        }

        /* Input labels, help text, headers */
        label, .css-1cpxqw2, .css-qrbaxs, .css-1v0mbdj, .css-1y4p8pa {
            color: black !important;
        }

        
        /* Input and button styling */
        .stTextInput input,
        .stSelectbox div,
        .stTextArea textarea,
        .stButton button {
            color: black !important;
            background-color: white !important;
        }

        .stDataFrame, .stTable, .stMarkdown, .stHeader, .stSubheader {
            color: black !important;
        }

        /* Search input label specifically */
        section input + div > label {
            color: black !important;
        }
    </style>
    """

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
st.markdown(force_light_theme_style(), unsafe_allow_html=True)
st.title("Modify Specific Records") 


# 🔍 Get visit details by record_id with patient and doctor names
def get_visit_details_by_record_id(record_id):
    try:
        # 1. Get visit row
        visit_resp = supabase.table("visits").select("*").eq("record_id", record_id).limit(1).execute()
        if not visit_resp.data:
            return None
        visit = visit_resp.data[0]

        # 2. Get patient info
        patient_resp = supabase.table("patients").select("patient_first_name, patient_last_name") \
            .eq("patient_id", visit["patient_id"]).limit(1).execute()
        patient = patient_resp.data[0] if patient_resp.data else {}

        # 3. Get doctor info
        doctor_resp = supabase.table("doctors").select("doctor_name") \
            .eq("doctor_id", visit["doctor_id"]).limit(1).execute()
        doctor = doctor_resp.data[0] if doctor_resp.data else {}

        # 4. Combine all into one dictionary
        return {
            "record_id": visit["record_id"],
            "patient_first_name": patient.get("patient_first_name", ""),
            "patient_last_name": patient.get("patient_last_name", ""),
            "doctor_name": doctor.get("doctor_name", ""),
            "symptoms": visit["symptoms"],
            "tests": visit["tests"],
            "diagnosis_notes": visit["diagnosis_notes"],
            "prescription": visit["prescription"]
        }

    except Exception as e:
        st.error(f"❌ Error retrieving data: {e}")
        return None

# 📝 Update specific visit fields
def update_specific_visit_details(record_id, symptoms, tests, diagnosis_notes, prescription):
    try:
        result = supabase.table("visits").update({
            "symptoms": symptoms,
            "tests": tests,
            "diagnosis_notes": diagnosis_notes,
            "prescription": prescription
        }).eq("record_id", record_id).execute()

        if result.data:
            st.success("✅ Visit details updated successfully!")
        else:
            st.warning("No data was updated.")
    except Exception as e:
        st.error(f"❌ Error updating record: {e}")




# 🔁 Main UI
def modify_specific_records():
    record_id = st.text_input("Enter Visit Record ID")

    if record_id:
        visit = get_visit_details_by_record_id(record_id)
        if not visit:
            st.warning("No visit found with the provided Record ID.")
        else:
            st.subheader("Visit Summary")
            st.write(f"**Record ID:** {visit['record_id']}")
            st.write(f"**Patient:** {visit['patient_first_name']} {visit['patient_last_name']}")
            st.write(f"**Doctor:** {visit['doctor_name']}")

            st.subheader("Modify Visit Details")
            symptoms = st.text_area("Symptoms", value=visit['symptoms'])
            tests = st.text_area("Tests", value=visit['tests'])
            diagnosis_notes = st.text_area("Diagnosis Notes", value=visit['diagnosis_notes'])
            prescription = st.text_area("Prescription", value=visit['prescription'])

            if st.button("Update Visit"):
                update_specific_visit_details(record_id, symptoms, tests, diagnosis_notes, prescription)

if __name__ == "__main__":
    modify_specific_records()