import streamlit as st
import time
import pandas as pd
import database_manager as db
from hardware_interface import HardwareInterface
from agent_brain import AgentBrain

# --- SETUP ---
st.set_page_config(page_title="Production Diagnostic System", layout="wide")
db.init_db()

# --- INITIALIZE MODULES ---
if 'hw' not in st.session_state:
    st.session_state.hw = HardwareInterface(port='COM3') 
    st.session_state.hw.connect() 
    
if 'brain' not in st.session_state:
    st.session_state.brain = AgentBrain()

if 'running' not in st.session_state:
    st.session_state.running = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("Admin Console")
    
    if st.session_state.hw.is_connected:
        st.success(f"🔌 Connected: {st.session_state.hw.port}")
    else:
        st.warning("⚠️ Simulation Mode")
        
    if st.button("Start/Stop Monitoring", type="primary"):
        st.session_state.running = not st.session_state.running
        
    st.divider()
    
    if st.button("🗑️ Clear Database History"):
        db.clear_db()
        st.success("History & ID Reset!")
        time.sleep(0.5)
        st.rerun()

    st.divider()
    
    # UPDATED BUTTON LOGIC
    st.subheader("Testing")
    # Determine button label based on current state
    btn_label = "🔥 Stop Overheat" if st.session_state.hw.fault_active else "🔥 Inject Overheat"
    if st.button(btn_label):
        is_active = st.session_state.hw.inject_sim_fault()
        if is_active:
            st.error("Fault Active: System Heating Up...")
        else:
            st.success("Fault Cleared: System Cooling Down...")

# --- MAIN DASHBOARD UI ---
st.title("🛡️ Agentic AI Diagnostic Hub")

col1, col2, col3, col4 = st.columns(4)
with col1: t_metric = st.empty()
with col2: v_metric = st.empty()
with col3: c_metric = st.empty()
with col4: s_metric = st.empty()

c1, c2 = st.columns([2, 1])
with c1: 
    st.subheader("Live Sensor Data")
    chart_spot = st.empty()
with c2: 
    st.subheader("Agent Decision Log")
    log_spot = st.empty()

# --- CONTROL LOOP ---
if st.session_state.running:
    while st.session_state.running:
        data = st.session_state.hw.get_data()
        decision = st.session_state.brain.analyze(data)
        
        if decision['actions']:
            for action in decision['actions']:
                st.session_state.hw.send_command(action)
        
        db.log_data(data['temp'], data['volt'], data['curr'])
        
        if decision['status'] != "NORMAL" and decision['status'] != "LEARNING":
            recent_logs = db.get_recent_events(1)
            if recent_logs.empty or recent_logs.iloc[0]['message'] != decision['reason']:
                db.log_event(decision['status'], decision['reason'])

        # UI UPDATE
        t_metric.metric("Temperature", f"{data['temp']} °C")
        v_metric.metric("Voltage", f"{data['volt']} V")
        c_metric.metric("Current", f"{data['curr']} A")
        
        status_color = "green"
        if decision['status'] == "WARNING": status_color = "orange"
        if decision['status'] == "FAULT": status_color = "red"
        if decision['status'] == "LEARNING": status_color = "blue"
        s_metric.markdown(f"### :{status_color}[{decision['status']}]")
        
        # Graph with Cycle ID
        df = db.get_recent_readings(50)
        if not df.empty:
            chart_data = df.set_index("id")[["temperature", "voltage"]]
            chart_spot.line_chart(chart_data)
        
        ev = db.get_recent_events(5)
        if not ev.empty:
            log_spot.dataframe(ev[["timestamp", "event_type", "message"]], hide_index=True)
        
        time.sleep(1)
        if not st.session_state.running: break