import streamlit as st
from st_pages import Page, show_pages
from utils import run_query

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title(":orange[Smart Athlete Performance Analysis]")
st.markdown("""
Welcome to the Smart Athlete Performance Analysis App.
This app is designed to help athletes track their performance, agility, endurance and help them understand and improve their performance.
""")

st.markdown("""---""")
st.markdown("""
        ## :orange[Athlete Rankings]
""")

def get_rankings(mode):
    query = f"""
        with shifted_data as (
            select 
                person,
                attempt,
                time - lag(time) over (order by time) as delta
            from 
                athlete
            where
                mode = '{mode}'
        )
        select
            person,
            avg(avg_delta) as avg_delta
        from
        (
        select 
            person,
            avg(delta) as avg_delta
        from
            shifted_data
        group by
            person, attempt
        )a
        group by
            person
        order by
            avg_delta;
    """
    data = run_query(query)
    if data is None:
        return []
    else:
        data = [
            {
                "person": d[0],
                "avg_delta": d[1]
            }
            for d in data
        ]
    return data


col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("""
    ### Mode 1
    """)
    st.dataframe(get_rankings("Mode1"),column_config={
        "person": "Athlete",
        "avg_delta": "Average Time in Seconds",
        }, use_container_width=True) 

with col2:
    st.markdown("""
    ### Mode 2
    """)
    st.dataframe(get_rankings("Mode2"),column_config={
        "person": "Athlete",
        "avg_delta": "Average Time in Seconds",
        }, use_container_width=True)





show_pages(
    [
        Page("./app.py", "Home"),
        Page("./activity.py", "Activity & Response"),
        Page("./compare.py", "Compare Athletes"),
        Page("./info.py","About"),
    ]
)