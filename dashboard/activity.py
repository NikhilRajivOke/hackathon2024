import streamlit as st
from st_pages import Page, show_pages
from utils import run_query, get_athletes, get_attempts

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

st.title(":orange[Athlete Activity] & :orange[Performance Analysis] :running:")

def get_data_all_attempts(athlete):
    query=f"""
        with shifted_data as (
            select 
                row_number() over (partition by attempt order by time) as point,
                attempt,
                time - lag(time) over (partition by attempt order by time) as delta
            from 
                athlete
            where
                person = '{athlete}'
        )
        select
            attempt,
            point,
            delta
        from
            shifted_data
            where
                point <= 30
        order by
            point
        ;
    """
    data = run_query(query)
    if data is None:
        return []
    else:
        data = [
            {
                "attempt": str(d[0]),
                "point": d[1],
                "delta": d[2]
            }
            for d in data
        ]
    return data


def get_data(athlete, attempt, mode):
    query = f"""
        WITH shifted_data AS (
            SELECT 
                point AS point_x,
                LAG(point) OVER (ORDER BY time) AS point_y,
                time - LAG(time) OVER (ORDER BY time) AS delta,
                time as time
            FROM 
                athlete
            WHERE
                person = '{athlete}'
                AND
                attempt = '{attempt}'
                AND
                mode = '{mode}'
        )
        SELECT 
            point_x,
            point_y,
            delta,
            time
        FROM 
            shifted_data
        ;
    """
    data = run_query(query)

    if data is None:
        return []
    else:
        data = [
            {
                "point_x": d[0],
                "point_y": d[1],
                "delta": d[2],
                "time": d[3]
            }
            for d in data
        ]
    return data

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    athlete = st.selectbox("Select an athlete", get_athletes())
with col2:
    mode = st.selectbox("Select a mode", ["Mode1", "Mode2"])
with col3:
    attempt = st.selectbox("Select an attempt", get_attempts(athlete))


if athlete and attempt:
    c1, c2 = st.columns([1, 1])
    with c1:
        data = get_data(athlete, attempt, mode)
        line_chart_data = [
                d["delta"]
            for d in data
        ]
        st.line_chart(line_chart_data, color="#39ff14", use_container_width=True)

    with c2:
        

        data = get_data(athlete, attempt, mode)
        movements = {
            "12":"Lateral",
            "13":"Backward",
            "23":"Backward",
            "32":"Forward",
            "21":"Lateral",
            "31":"Forward"
        }
            
        move_data = []
        move_cnt = {
            "Lateral": 0,
            "Backward": 0,
            "Forward": 0,
            "Unknown": 0
        }
        for d in data:
            movement = movements.get(str(d["point_x"]) + str(d["point_y"]), "Unknown")
            move_data.append({
                "movement": movement,
                "point": move_cnt[movement],
                "delta": d["delta"]
            })
            move_cnt[movement] += 1
            
        # st.line_chart(move_data,x = "point", y="delta", color="movement",use_container_width=True)
        st.scatter_chart(move_data, x="movement", y="delta", color="movement", use_container_width=True)

st.markdown("""---""")
st.title(":orange[All Attempts]")
all_data = get_data_all_attempts(athlete)
st.line_chart(all_data,x="point",y="delta", color="attempt",use_container_width=True)
