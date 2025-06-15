import streamlit as st
#from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from urllib.parse import quote
from utils.firebase_helper import get_applicants

def app():
    if not st.session_state.get("logged_in", False):
        st.error("🚫 Please log in.")
        st.stop()

    applicants = get_applicants()
    if not applicants:
        st.info("No applicants found.")
        return

    rows = []
    for aid, data in applicants.items():
        link = f"/applicant_details?uid={quote(aid)}"
        rows.append({
            "UUID": aid,
            "Details": link,
            "Name": data.get("name"),
            "Email": data.get("email"),
            "Skills": ", ".join(data.get("skills", [])),
            "Experience": data.get("experience"),
            "Location": data.get("location")
        })

    df = pd.DataFrame(rows)


    st.dataframe(
        df,
        column_config={
            "Details": st.column_config.LinkColumn(
                label="Details",
                help="Click to view applicant details",
                display_text="View"
            )
        },
        hide_index=True,
        use_container_width=True
    )
