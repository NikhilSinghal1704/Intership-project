import pandas as pd
import streamlit as st
from utils.firebase_helper import get_hired_applications

def format_hired_applications(hired_data: list[dict]) -> pd.DataFrame:
    """
    Converts a list of hired application dicts into a formatted DataFrame
    with readable column names and 'id' as the index.
    """
    if not hired_data:
        return pd.DataFrame()

    # Create DataFrame
    df = pd.DataFrame(hired_data)

    # Rename columns for readability
    df.rename(columns={
        "applicant_id": "Applicant ID",
        "application_id": "Application ID",
        "job_id": "Job ID",
        "hired_on": "Hired On",
        "joining_date": "Joining Date",
        "notice_period_days": "Notice Period (Days)",
        "offered_ctc": "Offered CTC (INR)",
        "comments": "Comments",
        "status": "Status"
    }, inplace=True)

    # Add links
    df["Job Details"] = df["Job ID"].apply(lambda job_id: f"/job_details?id={job_id}")
    df["Applicant Details"] = df["Applicant ID"].apply(lambda app_id: f"/applicant_detail?uid={app_id}")

    # Set 'Hired ID' as the index
    df.set_index("id", inplace=True)

    # Define preferred column order
    preferred_order = [
        "Application ID",
        "Job ID",
        "Job Details",
        "Applicant ID",
        "Applicant Details",
        "Hired On",
        "Joining Date",
        "Notice Period (Days)",
        "Offered CTC (INR)",
        "Status",
        "Comments"
    ]

    # Reorder columns (keeping only those that exist)
    ordered_columns = [col for col in preferred_order if col in df.columns]
    df = df[ordered_columns]

    return df


def app():
    st.title("📋 Hired Applications")

    hired_apps = get_hired_applications()
    
    df = format_hired_applications(hired_apps)

    if df.empty:
        st.info("No hired applications available.")
        return
    
    else:
        n_rows = len(df)
        height = min((n_rows + 1) * 35 + 5, 800)  # Cap at e.g. 800px to avoid massive pages
    
        st.subheader(f"Total ({n_rows})")
        st.dataframe(
            df,
            use_container_width=True,
            height=height,
            hide_index=True,
            column_config={
                "Applicant Details": st.column_config.LinkColumn(
                    label="Applicant Details",
                    help="Click to view applicant details",
                    display_text="View"
                ),
                "Job Details": st.column_config.LinkColumn(
                    label="Job Details",
                    help="Click to view job details",
                    display_text="View"
                )
            },
        )
