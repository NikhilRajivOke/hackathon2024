import streamlit as st
from st_pages import Page, show_pages
from utils import run_query, get_athletes, get_attempts

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
st.title(":orange[Compete yourself]")
st.markdown("""
    Take the last attempt of each athlete and compare them.
""")

col1, col2 = st.columns([1, 1])
with col1:
    athlete1 = st.selectbox("Select an athlete", get_athletes(), key="athlete1")

with col2:
    athlete2 = st.selectbox("Select an athlete", get_athletes(), key="athlete2")



def get_data(athlete):
    query = f"""
        with shifted_data as (
            select 
                person,
                row_number() over (partition by person order by time) as point,
                time - lag(time) over (order by time) as delta
            from 
                athlete
            where
                person = '{athlete}' and
                attempt = (select max(attempt) from athlete where person = '{athlete}')
        )
        select
            person,
            point,
            delta as delta
        from
            shifted_data
    """
    data = run_query(query)
    if data is None:
        return []
    else:
        data = [
            {
                "person": d[0],
                "point": d[1],
                "delta": d[2]
            }
            for d in data
        ]
    return data

if athlete1 and athlete2 and athlete1 == athlete2:
    st.error("Please select different athletes")
elif athlete1 and athlete2:
    st.write(f"Comparing {athlete1} and {athlete2}")

    data1 = get_data(athlete1)
    data2 = get_data(athlete2)
    data = []
    colors = []
    for d in data1:
        data.append(d)
    for d in data2:
        data.append(d)
    st.line_chart(data,x="point", y="delta", color="person", use_container_width=True)

# neon green: #39ff14, #0cff14, #14ff39, #14ff0c, #0cff39, #39ff0c