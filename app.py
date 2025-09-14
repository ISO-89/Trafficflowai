# app.py
import streamlit as st
import time
import random

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Traffic Control MVP",
    page_icon="🚦",
    layout="wide"
)

# --- Simulation State Initialization ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'lights' not in st.session_state:
    st.session_state.lights = {'N': 'red', 'S': 'red', 'E': 'green', 'W': 'green'}
if 'cars' not in st.session_state:
    st.session_state.cars = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
if 'total_wait_time' not in st.session_state:
    st.session_state.total_wait_time = 0
if 'total_cars_passed' not in st.session_state:
    st.session_state.total_cars_passed = 0
if 'timer' not in st.session_state:
    st.session_state.timer = 0
if 'last_switch_time' not in st.session_state:
    st.session_state.last_switch_time = 0

# --- Helper Functions ---
def get_light_color(status):
    return "green" if status == "green" else "red" if status == "red" else "yellow"

def get_opposite_direction(direction):
    return {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}[direction]

# --- Main Simulation Logic ---
def run_simulation_step(mode, fixed_duration):
    for direction in st.session_state.cars:
        if random.random() < 0.3:
            st.session_state.cars[direction] += 1

    cars_waiting_this_step = sum(st.session_state.cars.values())
    st.session_state.total_wait_time += cars_waiting_this_step

    for direction, status in st.session_state.lights.items():
        if status == 'green' and st.session_state.cars[direction] > 0:
            cars_to_pass = min(st.session_state.cars[direction], 2)
            st.session_state.cars[direction] -= cars_to_pass
            st.session_state.total_cars_passed += cars_to_pass

    current_time = time.time()
    time_since_last_switch = current_time - st.session_state.get('last_switch_time', current_time)

    if mode == 'Fixed-Timer':
        if time_since_last_switch >= fixed_duration:
            if st.session_state.lights['N'] == 'red':
                st.session_state.lights = {'N': 'green', 'S': 'green', 'E': 'red', 'W': 'red'}
            else:
                st.session_state.lights = {'N': 'red', 'S': 'red', 'E': 'green', 'W': 'green'}
            st.session_state.last_switch_time = current_time
    
    elif mode == 'Smart Control':
        if time_since_last_switch >= 10:
            vertical_traffic = st.session_state.cars['N'] + st.session_state.cars['S']
            horizontal_traffic = st.session_state.cars['E'] + st.session_state.cars['W']
            is_ns_green = st.session_state.lights['N'] == 'green'
            
            if is_ns_green and vertical_traffic < horizontal_traffic:
                 st.session_state.lights = {'N': 'red', 'S': 'red', 'E': 'green', 'W': 'green'}
                 st.session_state.last_switch_time = current_time
            elif not is_ns_green and horizontal_traffic < vertical_traffic:
                 st.session_state.lights = {'N': 'green', 'S': 'green', 'E': 'red', 'W': 'red'}
                 st.session_state.last_switch_time = current_time

# --- UI and Visualization ---
st.title("🚦 Smart Traffic Light Management ")
st.write("A demonstration of an AI-like traffic control system compared to a traditional fixed-timer system.")

with st.sidebar:
    st.header("Controls")
    control_mode = st.radio("Select Control Mode", ('Fixed-Timer', 'Smart Control'))
    
    fixed_duration = 15
    if control_mode == 'Fixed-Timer':
        fixed_duration = st.slider("Fixed Green Light Duration (seconds)", 5, 30, 15)

    if st.button("Start Simulation"):
        st.session_state.running = True
        st.session_state.last_switch_time = time.time()
    if st.button("Stop Simulation"):
        st.session_state.running = False
    
    if st.button("Reset Simulation"):
        st.session_state.running = False
        st.session_state.cars = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        st.session_state.lights = {'N': 'red', 'S': 'red', 'E': 'green', 'W': 'green'}
        st.session_state.total_wait_time = 0
        st.session_state.total_cars_passed = 0

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Live Intersection View")
    intersection_placeholder = st.empty()

with col2:
    st.subheader("Key Performance Indicators (KPIs)")
    kpi1 = st.empty()
    kpi2 = st.empty()
    kpi3 = st.empty()

while st.session_state.running:
    run_simulation_step(control_mode, fixed_duration)
    total_cars_waiting = sum(st.session_state.cars.values())
    avg_wait_time = st.session_state.total_wait_time / (st.session_state.total_cars_passed + 1)

    with kpi1:
        st.metric(label="Total Cars Currently Waiting", value=total_cars_waiting)
    with kpi2:
        st.metric(label="Total Cars Passed", value=st.session_state.total_cars_passed)
    with kpi3:
        st.metric(label="Average Wait Time (seconds)", value=f"{avg_wait_time:.2f}")

    with intersection_placeholder.container():
        st.markdown(f"""
        <style>
            .light {{ width: 30px; height: 30px; border-radius: 50%; border: 2px solid black; }}
            .road {{ background-color: #444; color: white; padding: 10px; border-radius: 5px; text-align: center; min-height: 80px; }}
            .intersection-grid {{ display: grid; grid-template-columns: 1fr 50px 1fr; grid-template-rows: 1fr 50px 1fr; gap: 5px; width: 400px; height: 400px; margin: auto; }}
            .center-box {{ grid-column: 2; grid-row: 2; background-color: #666; }}
        </style>
        <div class="intersection-grid">
            <div></div> 
            <div style="display: flex; justify-content: center; align-items: flex-end;"><div class="light" style="background-color:{get_light_color(st.session_state.lights['N'])}"></div></div>
            <div></div>
            <div style="display: flex; justify-content: flex-end; align-items: center;"><div class="light" style="background-color:{get_light_color(st.session_state.lights['W'])}"></div></div>
            <div class="center-box"></div>
            <div style="display: flex; justify-content: flex-start; align-items: center;"><div class="light" style="background-color:{get_light_color(st.session_state.lights['E'])}"></div></div>
            <div></div>
            <div style="display: flex; justify-content: center; align-items: flex-start;"><div class="light" style="background-color:{get_light_color(st.session_state.lights['S'])}"></div></div>
            <div></div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='road'><b>West ⬅️</b><br>Cars: {st.session_state.cars['W']}</div>", unsafe_allow_html=True)
        # THIS IS THE NEW, CORRECTED CODE
        with c2:
            st.markdown(f"<div class='road'><b>North ⬆️</b><br>Cars: {st.session_state.cars['N']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='road' style='margin-top:5px;'><b>South ⬇️</b><br>Cars: {st.session_state.cars['S']}</div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='road'><b>East ➡️</b><br>Cars: {st.session_state.cars['E']}</div>", unsafe_allow_html=True)
        
    time.sleep(1)