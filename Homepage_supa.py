import streamlit as st
import os
import base64
from dotenv import load_dotenv
from supabase import create_client, Client

# ✅ Load .env variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔁 Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🖼️ Image and styling
image_path = "images/Asset2.jpeg"
image_width = 1500
image_height = 750

def get_gradient_style(image_path, image_width, image_height):
    if not os.path.exists(image_path):
        return "<style></style>"

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()

    return f"""
    <style>
      [data-testid="stAppViewContainer"] {{
        background-image: url('data:image/png;base64,{encoded_image}');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
      }}
      [data-testid="stSidebar"] {{
        background: linear-gradient(to bottom, #e0e7ff, #d1e0fc) !important;
      }}
    </style>
    """

# def check_supabase_connection():
#     try:
#         response = supabase.table("patients").select("patient_id").limit(1).execute()
#         if response.data is not None:
#             st.success("✅ Connected to Supabase successfully.")x
#         else:
#             st.warning("⚠️ Supabase connected, but no data found.")
#     except Exception as e:
#         st.error(f"❌ Supabase connection failed: {e}")

def show_homepage():
    st.set_page_config(page_title="Hospital Management System", page_icon="🩺")
    st.markdown(get_gradient_style(image_path, image_width, image_height), unsafe_allow_html=True)
    # st.title(" Welcome to the Hospital Management System")
    # check_supabase_connection()
    # st.markdown("Use the sidebar to navigate through Patients, Visits, Invoices, and more.")

if __name__ == "__main__":
    show_homepage()