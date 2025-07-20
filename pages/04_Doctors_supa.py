import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load .env credentials
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


def doctors_page():
    st.title("Doctors Page")

    st.header("Add New Doctor")
    doctor_name = st.text_input("Doctor Name")
    doctor_specialty = st.text_input("Doctor Specialty")
    departments = get_departments()
    doctor_department = st.selectbox("Doctor Department", departments)

    if st.button("Add Doctor"):
        if doctor_name and doctor_specialty and doctor_department:
            add_new_doctor(doctor_name, doctor_specialty, doctor_department)
        else:
            st.error("Please fill in all fields.")

    st.write("---")
    st.header("Search Doctors")

    search_name = st.text_input("Search Doctor by Name")
    if search_name:
        st.write(f"Search Results for '{search_name}':")
        search_results = search_doctors_by_name(search_name)
        if not search_results.empty:
            search_results['Selected'] = search_results.apply(lambda x: st.checkbox(f"Select {x['doctor_name']}", key=x['doctor_id']), axis=1)
            st.dataframe(search_results)
        else:
            st.write("No results found.")

    search_department = st.selectbox("Search Doctors by Department", [""] + departments)
    if search_department:
        st.write(f"Search Results for Doctors in '{search_department}' Department:")
        search_results = search_doctors_by_department(search_department)
        if not search_results.empty:
            search_results['Selected'] = search_results.apply(lambda x: st.checkbox(f"Select {x['doctor_name']}", key=x['doctor_id']), axis=1)
            st.dataframe(search_results)
        else:
            st.write("No results found.")

    if st.button("Delete Selected Doctors"):
        selected_doctors = [row['doctor_id'] for index, row in search_results.iterrows() if row['Selected']]
        if selected_doctors:
            delete_doctor_and_update_visits(selected_doctors)
            st.success("Selected doctors deleted successfully!")
        else:
            st.warning("No doctors selected for deletion.")


def search_doctors_by_name(name):
    response = supabase.table("doctors") \
        .select("*") \
        .ilike("doctor_name", f"%{name}%") \
        .execute()
    return pd.DataFrame(response.data)


def search_doctors_by_department(department):
    response = supabase.table("doctors") \
        .select("*") \
        .eq("doctor_department", department) \
        .execute()
    return pd.DataFrame(response.data)


def get_departments():
    response = supabase.table("doctors").select("doctor_department").execute()
    df = pd.DataFrame(response.data)
    if "doctor_department" in df.columns:
        return sorted(df["doctor_department"].dropna().unique().tolist())
    else:
        st.warning("No department data found.")
        return []




def add_new_doctor(name, specialty, department):
    try:
        supabase.table("doctors").insert({
            "doctor_name": name,
            "doctor_specialty": specialty,
            "doctor_department": department
        }).execute()
        st.success("Doctor added successfully!")
    except Exception as e:
        st.error(f"Failed to add doctor. Error: {e}")


def delete_doctor_and_update_visits(doctor_ids):
    try:
        # Step 1: Assign visits of deleted doctors to Dr. Temp
        temp_response = supabase.table("doctors") \
            .select("doctor_id") \
            .eq("doctor_name", "Dr. Temp") \
            .limit(1) \
            .execute()

        if not temp_response.data:
            st.error("Dr. Temp not found. Please ensure this placeholder doctor exists.")
            return

        temp_id = temp_response.data[0]["doctor_id"]

        for doc_id in doctor_ids:
            # Reassign visits to Dr. Temp
            supabase.table("visits").update({
                "doctor_id": temp_id
            }).eq("doctor_id", doc_id).execute()

            # Delete doctor record
            supabase.table("doctors").delete().eq("doctor_id", doc_id).execute()

    except Exception as e:
        st.error(f"Failed to delete doctor and update visits. Error: {e}")


if __name__ == "__main__":
    doctors_page()
    
