import streamlit as st
import plotly.express as px
from utils.firebase_helper import get_clients, get_open_jobs, get_applicants, get_jobs, get_vacancies

def app():
    st.set_page_config(page_title="Dashboard", layout="wide")
    st.title("📊 Dashboard")

    st.markdown("""
    <style>
    .metric-card {
      background-color: #f0f8ff;  /* light blue background */
      padding: 16px;
      border-radius: 8px;
      text-align: center;
      box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
      transition: transform 0.2s;
      margin: 8px;
    }
    .metric-card:hover {
      transform: scale(1.03);
    }
    .metric-card h3 {
      margin: 0;
      font-size: 1.1rem;
      color: #333;
    }
    .metric-card .value {
      margin-top: 8px;
      font-size: 2rem;
      font-weight: bold;
      color: #0073e6;
    }
    </style>
    """, unsafe_allow_html=True)


    # Fetch data
    total_clients = len(get_clients())
    total_applicants = len(get_applicants())
    total_job_posts = len(get_jobs())  # or len(get_open_jobs()) if you want only open
    total_vacancies, vacancies_by_dept, vacancies_by_mode = get_vacancies(breakdown=True)

    # Layout: 4 columns for metrics
    cols = st.columns(4)
    # Option 1: static display using styled cards
    cols[0].markdown(f'<div class="metric-card"><h3>Clients</h3><div class="value">{total_clients}</div></div>',
                     unsafe_allow_html=True)
    cols[1].markdown(f'<div class="metric-card"><h3>Open Vacancies</h3><div class="value">{total_vacancies}</div></div>',
                     unsafe_allow_html=True)
    cols[2].markdown(f'<div class="metric-card"><h3>Applicants</h3><div class="value">{total_applicants}</div></div>',
                     unsafe_allow_html=True)
    cols[3].markdown(f'<div class="metric-card"><h3>Job Posts</h3><div class="value">{total_job_posts}</div></div>',
                     unsafe_allow_html=True)

    # Option 2: animated counters instead (uncomment if desired)
    # animate_counter("Clients", total_clients, cols[0])
    # animate_counter("Open Vacancies", total_vacancies, cols[1])
    # animate_counter("Applicants", total_applicants, cols[2])
    # animate_counter("Job Posts", total_job_posts, cols[3])

    st.markdown("---")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Vacancies by Department")
        if vacancies_by_dept:
            labels = list(vacancies_by_dept.keys())
            values = list(vacancies_by_dept.values())
            fig = px.pie(
                names=labels,
                values=values,
                title="",  # we already have a subheader
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No open vacancies found.")
    
    with col2:
        st.subheader("Vacancies by Work Mode")
        if vacancies_by_mode:
            labels = list(vacancies_by_mode.keys())
            values = list(vacancies_by_mode.values())
            fig2 = px.pie(
                names=labels,
                values=values,
                title="",
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No open vacancies to break down by work mode.")
