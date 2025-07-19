import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from supabase import create_client, Client
import os

# Load Supabase credentials
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


# -----------------------------
# Supabase Query Helpers
# -----------------------------
def fetch_data(table, columns="*", filters=None):
    query = supabase.table(table).select(columns)
    if filters:
        for condition in filters:
            query = query.eq(condition[0], condition[1])
    return query.execute().data

def fetch_custom_query(table, query_string):
    return supabase.table(table).select(query_string).execute().data

# -----------------------------
# Display Functions
# -----------------------------

def display_invoices():
    data = fetch_data("visits", "patient_id, visit_id, visit_date, room_number, tests, payment_amount, payment_method")
    df = pd.DataFrame(data)
    st.write("Invoice Data:", df)
    revenue()

def revenue():  
    st.title("System Revenue")
    data = fetch_data("visits", "payment_amount")
    df = pd.DataFrame(data)
    total = df["payment_amount"].sum() if not df.empty else 0.0
    st.write(f"Total Revenue: ${total:,.2f}")



def display_highest_billing_department():
    # Manual join
    visits = fetch_data("visits", "doctor_id, payment_amount")
    doctors = fetch_data("doctors", "doctor_id, doctor_department")

    if not visits or not doctors:
        st.warning("Missing doctor or visit data.")
        return

    v_df = pd.DataFrame(visits)
    d_df = pd.DataFrame(doctors)

    merged = pd.merge(v_df, d_df, on="doctor_id", how="inner")
    grouped = merged.groupby("doctor_department")["payment_amount"].sum().reset_index()
    top5 = grouped.sort_values("payment_amount", ascending=False).head(5)

    st.write("Highest Billing Department:")
    st.dataframe(top5)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="doctor_department", y="payment_amount", data=top5, ax=ax)
    ax.set_title("Total Billing Amount by Department")
    ax.set_xlabel("Department")
    ax.set_ylabel("Total Billing Amount")
    st.pyplot(fig)


def filter_and_search():
    st.subheader("Filter and Search Invoices")
    invoice_status = st.selectbox("Select Payment Type:", ["Credit Card", "Insurance", "Cash", "Debit Card", "Medicare"])
    data = fetch_data("visits", "patient_id, visit_id, visit_date, room_number, tests, payment_amount", filters=[("payment_method", invoice_status)])
    df = pd.DataFrame(data)
    st.write("Filtered Invoices:", df)



def invoice_viz():
    data = fetch_data("visits", "patient_id, visit_date, payment_amount, payment_method")
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No invoice data available.")
        return

    st.subheader("Total Revenue Over Time")
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    revenue_over_time = df.groupby("visit_date")["payment_amount"].sum()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x=revenue_over_time.index, y=revenue_over_time.values, ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Revenue")
    ax.set_title("Total Revenue Over Time")
    st.pyplot(fig)

    st.subheader("Distribution of Invoices by Payment Method")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    df["payment_method"].value_counts().plot(kind="bar", ax=ax2)
    ax2.set_xlabel("Payment Method")
    ax2.set_ylabel("Number of Invoices")
    ax2.set_title("Distribution of Invoices by Payment Method")
    st.pyplot(fig2)



def display_common_admission_types():
    data = fetch_data("visits", "admission_type")
    df = pd.DataFrame(data)
    if df.empty:
        st.warning("No admission data.")
        return

    grouped = df["admission_type"].value_counts().reset_index()
    grouped.columns = ["Admission Type", "Count"]

    st.write("Most Common Admission Types:")
    st.dataframe(grouped)

    fig, ax = plt.subplots()
    sns.barplot(x="Admission Type", y="Count", data=grouped, ax=ax)
    ax.set_title("Most Common Admission Types")
    st.pyplot(fig)


def display_patient_age_distribution():
    data = fetch_data("patients", "age")
    df = pd.DataFrame(data)

    if df.empty:
        st.warning("No patient age data available.")
        return

    st.write("Distribution of Patient Ages:")
    st.write(df.describe())

    fig, ax = plt.subplots()
    sns.histplot(data=df, x="age", bins=10, ax=ax)
    ax.set_title("Distribution of Patient Ages")
    ax.set_xlabel("Age")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)




def display_most_used_insurance_providers():
    data = fetch_data("patients", "insurance_provider")
    df = pd.DataFrame(data)
    df = df[df["insurance_provider"].notnull()]

    if df.empty:
        st.warning("No insurance provider data available.")
        return

    grouped = df["insurance_provider"].value_counts().reset_index()
    grouped.columns = ["Insurance Provider", "Count"]

    st.write("Most Used Insurance Providers:")
    st.dataframe(grouped)

    fig, ax = plt.subplots()
    sns.barplot(x="Insurance Provider", y="Count", data=grouped, ax=ax)
    ax.set_title("Most Used Insurance Providers")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)




# -----------------------------
# Main Entry
# -----------------------------
def main():
    st.title("Invoices Dashboard")
    nav = st.sidebar.radio("Navigation", ["Display Invoices", "Filter and Search", "Analysis"])

    if nav == "Display Invoices":
        display_invoices()
        display_highest_billing_department()
    elif nav == "Filter and Search":
        filter_and_search()
    elif nav == "Analysis":
        invoice_viz()
        display_common_admission_types()
        display_patient_age_distribution()
        display_most_used_insurance_providers()

if __name__ == "__main__":
    main()