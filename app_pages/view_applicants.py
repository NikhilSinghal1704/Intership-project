import streamlit as st
import pandas as pd
from utils.firebase_helper import get_applicants

def build_dataframe(apps):
    rows = []
    for aid, d in apps.items():
        rows.append({
            "UUID": aid,
            "Details": f"/applicant_detail?uid={aid}",
            "Name": d.get("name", ""),
            "Email": d.get("email", ""),
            "Phone": d.get("phone", ""),
            "Course": d.get("course", ""),
            "Specialization": d.get("specialization", ""),
            "Institute": d.get("institute", ""),
            "Experience": float(d.get("experience", 0)),
            "CTC": float(d.get("ctc", 0)),
            "Country": d.get("country", ""),
            "State": d.get("state", ""),
            "City": d.get("city", ""),
            "Current Mode": d.get("current_mode", ""),
            "Current Duration": d.get("current_duration", ""),
            "Preferred Mode": d.get("preferred_mode", ""),
            "Preferred Duration": d.get("preferred_duration", ""),
            "Source": d.get("source", ""),
            "notice_period": d.get("notice_period", ""),
        })
    return pd.DataFrame(rows)

def filters(df):

    st.sidebar.subheader("🔎 Search")
    # Search
    keyword = st.sidebar.text_input("Keyword (Name or Email)")
    if keyword:
        df = df[df["Name"].str.contains(keyword, case=False) | df["Email"].str.contains(keyword, case=False)]

    st.sidebar.subheader("📊 Filters")
    # Numeric filters: Experience & CTC with min/max inputs
    for num_col in ["Experience", "CTC"]:
        col_min, col_max = float(df[num_col].min()), float(df[num_col].max())
        min_input = st.sidebar.number_input(f"{num_col} ≥", value=col_min, min_value=col_min, max_value=col_max, step=0.1 if num_col=="Experience" else 1000.0)
        max_input = st.sidebar.number_input(f"{num_col} ≤", value=col_max, min_value=col_min, max_value=col_max, step=0.1 if num_col=="Experience" else 1000.0)
        # Apply filter
        df = df.loc[(df[num_col] >= min_input) & (df[num_col] <= max_input)]

    # Discrete filters (allow multiselect)
    for col in ["Course", "Institute", "Country", "State", "City", "Current Mode", "Preferred Mode", "Source", "notice_period"]:
        options = sorted(df[col].dropna().unique())
        selected = st.sidebar.multiselect(f"{col}", ["All"] + options, default=["All"])
        if "All" not in selected:
            df = df[df[col].isin(selected)]

    return df

def app():
    # Auth guard
    if not st.session_state.get("logged_in", False):
        st.error("🚫 Please log in.")
        st.stop()

    with st.spinner("Loading applicants..."):
        apps = get_applicants()
    if not apps:
        st.info("No applicants found.")
        return

    # Build DataFrame
    with st.spinner("Building applicant data..."):
        df = build_dataframe(apps)

    # --- 🧩 Sidebar Filters ---
    with st.spinner("Applying filters..."):
        df = filters(df)

    # --- 📄 Display ---
    
    # Calculate dynamic height: ~35px per row + header
    n_rows = len(df)
    height = min((n_rows + 1) * 35 + 5, 800)  # Cap at e.g. 800px to avoid massive pages

    st.header(f"👥 Applicants ({n_rows})")
    st.dataframe(
        df,
        use_container_width=True,
        height=height,
        hide_index=True,
        column_config={
            "Details": st.column_config.LinkColumn(
                label="Details",
                help="Click to view applicant details",
                display_text="View"
            )
        },
    )
