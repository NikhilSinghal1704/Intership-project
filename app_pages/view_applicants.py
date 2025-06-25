import streamlit as st
import pandas as pd
from utils.firebase_helper import get_applicants

def app():
    # 🛡 Login guard
    if not st.session_state.get("logged_in", False):
        st.error("🚫 Please log in.")
        st.stop()

    applicants = get_applicants()
    if not applicants:
        st.info("No applicants found.")
        return

    # -------------------- TRANSFORM DATA --------------------
    rows = []
    for aid, data in applicants.items():
        rows.append({
            "UUID": aid,
            "Details": f"/applicant_detail?uid={aid}",
            "Name": data.get("name", ""),
            "Email": data.get("email", ""),
            "Skills": ", ".join(data.get("skills", [])),
            "Skills Raw": data.get("skills", []),
            "Experience": data.get("experience", 0),
            "Country": data.get("country", "N/A"),
            "State": data.get("state", "N/A"),
            "City": data.get("city", "N/A"),
        })

    df = pd.DataFrame(rows)

    # -------------------- SIDEBAR FILTERS --------------------
    with st.sidebar:
        st.header("🔍 Filter Applicants")

        search = st.text_input("Search by Name or Email")

        # Country → State → City hierarchy
        countries = sorted(df["Country"].dropna().unique())
        selected_country = st.selectbox("Select Country", countries, index=countries.index("India") if "India" in countries else 0)

        state_options = sorted(df[df["Country"] == selected_country]["State"].dropna().unique())
        selected_state = st.selectbox("Select State", ["All"] + state_options)

        city_df = df[df["Country"] == selected_country]
        if selected_state != "All":
            city_df = city_df[city_df["State"] == selected_state]
        city_options = sorted(city_df["City"].dropna().unique())
        selected_city = st.selectbox("Select City", ["All"] + city_options)

        # Skills
        all_skills = sorted({skill for skills in df["Skills Raw"] for skill in skills})
        selected_skills = st.multiselect("Filter by Skills", options=all_skills)

        min_exp = st.slider("Minimum Experience (years)", 0, 20, 0)

    # -------------------- APPLY FILTERS --------------------
    if search:
        df = df[df["Name"].str.contains(search, case=False, na=False) | 
                df["Email"].str.contains(search, case=False, na=False)]

    df = df[df["Country"] == selected_country]

    if selected_state != "All":
        df = df[df["State"] == selected_state]

    if selected_city != "All":
        df = df[df["City"] == selected_city]

    if selected_skills:
        df = df[df["Skills Raw"].apply(lambda skills: all(skill in skills for skill in selected_skills))]

    df = df[df["Experience"] >= min_exp]

    # -------------------- DISPLAY TABLE --------------------
    df = df.drop(columns=["Skills Raw", "Country", "State", "City"])  # optional: hide intermediate data

    st.header(f"👥 Applicants ({len(df)})")
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
