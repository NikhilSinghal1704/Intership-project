import streamlit as st
import pandas as pd
from datetime import datetime
from utils.firebase_helper import get_applicants

def build_dataframe(apps):
    rows = []
    for aid, d in apps.items():
        rows.append({
            "UUID": aid,
            
            "Name": d.get("name", ""),
            "Email": d.get("email", ""),
            "Institute": d.get("institute", ""),
            "Experience": float(d.get("experience", 0)),
            "Current CTC": float(d.get("current_ctc", 0)),
            "Expected CTC": float(d.get("expected_ctc", 0)),
            "Current Mode": d.get("current_mode", ""),
            "Current Duration": d.get("current_duration", ""),
            "Preferred Mode": d.get("preferred_mode", ""),
            "Preferred Duration": d.get("preferred_duration", ""),
            "City": d.get("city", ""),
            "State": d.get("state", ""),
            "Country": d.get("country", ""),
            "Details": f"/applicant_detail?uid={aid}",
            "Resume": d.get("resume_url", "Not Available"),
            "Skills": ",".join(d.get("skills", {}).keys()),
            "Phone": d.get("phone", ""),
            "Course": d.get("course", ""),
            "Specialization": d.get("specialization", ""),
            "Source": d.get("source", ""),
            "Notice Period": d.get("notice_period", ""),
            "Last Update": datetime.fromisoformat(d.get("updated_at", "")).strftime("%B %d, %Y, %I:%M %p") if d.get("updated_at") else "",
            "Created at": datetime.fromisoformat(d.get("created_at", "")).strftime("%B %d, %Y, %I:%M %p") if d.get("updated_at") else ""
        })
    return pd.DataFrame(rows)

def parse_notice_period(val):
    mapping = {
        "Immediate": 0,
        "1 Month": 1,
        "2 Months": 2,
        "3 Months": 3,
    }
    if val in mapping:
        return mapping[val]
    try:
        # Extract number if possible from string like "6 months"
        return int(''.join(filter(str.isdigit, val)))
    except:
        return 99  # default high value for unknowns

def filters(df, pre_filters=None):
    pre_filters = pre_filters or {}

    st.sidebar.subheader("📊 Filters")

    # Numeric filters
    for num_col in ["Experience", "Current CTC", "Expected CTC"]:
        col_min, col_max = float(df[num_col].min()), float(df[num_col].max())
        min_val = pre_filters.get(f"{num_col}_min", col_min)
        max_val = pre_filters.get(f"{num_col}_max", col_max)

        min_input = st.sidebar.number_input(
            f"{num_col} ≥", value=min_val, min_value=col_min, max_value=col_max,
            step=0.1 if num_col == "Experience" else 1000.0
        )
        max_input = st.sidebar.number_input(
            f"{num_col} ≤", value=max_val, min_value=col_min, max_value=col_max,
            step=0.1 if num_col == "Experience" else 1000.0
        )
        df = df[(df[num_col] >= min_input) & (df[num_col] <= max_input)]

    # Categorical filters
    for col in [
        "Course", "Institute", "Country", "State", "City",
        "Current Mode", "Preferred Mode", "Current Duration", "Preferred Duration", "Source"
    ]:
        options = sorted(df[col].dropna().unique())
        # Fallback if pre_filter contains invalid entries
        default_selected = pre_filters.get(col, ["All"])
        valid_default = [val for val in default_selected if val in options]
        default_final = default_selected if valid_default else ["All"]

        selected = st.sidebar.multiselect(f"{col}", ["All"] + options, default=default_final)
        if "All" not in selected:
            df = df[df[col].isin(selected)]

    # Notice Period Filter
    notice_options = ["Immediate", "1 Month", "2 Months", "3 Months", "More than 3 Months"]
    default_notice = pre_filters.get("Notice Period", ["All"])
    valid_notice = [val for val in default_notice if val in notice_options]
    selected_notice = st.sidebar.multiselect("Notice Period", ["All"] + notice_options, default=valid_notice or ["All"])

    if "All" not in selected_notice:
        if "More than 3 Months" in selected_notice:
            df = df[df["Notice Period"].apply(lambda x: parse_notice_period(x) > 3)]
        else:
            selected_nums = [parse_notice_period(opt) for opt in selected_notice]
            df = df[df["Notice Period"].apply(lambda x: parse_notice_period(x) in selected_nums)]

    return df

def search(df):
    st.subheader("🔎 Search")

    # Create two columns with ratio 30:70
    col1, col2 = st.columns([3, 7])

    with col1:
        search_by = st.selectbox("Search By", ["UUID", "Name or Email"])

    with col2:
        if search_by == "UUID":
            keyword = st.text_input("Applicant UUID", placeholder="Enter UUID to filter")
            if keyword:
                df = df[df["UUID"].str.contains(keyword, case=False)]
        else:
            keyword = st.text_input("Keyword", placeholder="Enter name or email to search")
            if keyword:
                df = df[df["Name"].str.contains(keyword, case=False) | df["Email"].str.contains(keyword, case=False)]

    return df

def sort_dataframe(df, pre_sort=None):
    # Add numeric column for notice period sorting
    df["notice_period_num"] = df["Notice Period"].apply(parse_notice_period)

    sort_options = {
        "None": None,
        "Experience": "Experience",
        "CTC": "CTC",
        "Notice Period": "notice_period_num"
    }

    default_sort = pre_sort.get("column", "None") if pre_sort else "None"
    default_order = pre_sort.get("order", "Ascending") if pre_sort else "Ascending"

    st.sidebar.subheader("↕️ Sort Options")
    sort_choice = st.sidebar.selectbox("Sort by", list(sort_options.keys()), index=list(sort_options.keys()).index(default_sort))

    if sort_choice != "None":
        ascending = st.sidebar.radio("Order", ["Ascending", "Descending"], horizontal=True) == default_order
        sort_col = sort_options[sort_choice]
        df = df.sort_values(by=sort_col, ascending=ascending)

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

    # --- 📊 Sorting ---
    with st.spinner("Sorting applicants..."):
        df = sort_dataframe(df)

    # --- 📄 Display ---

    df = search(df)  # Apply search after filters and sorting
    
    # Calculate dynamic height: ~35px per row + header
    n_rows = len(df)
    height = min((n_rows + 1) * 35 + 5, 800)  # Cap at e.g. 800px to avoid massive pages

    st.header(f"👥 Applicants ({n_rows})")
    df.drop(columns=["notice_period_num"], inplace=True, errors='ignore')  # Clean up temp column if exists
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
            ),
            "Resume": st.column_config.LinkColumn(
                label="Resume",
                help="Click to view resume",
                display_text="View Resume"
            ),
        },
    )
