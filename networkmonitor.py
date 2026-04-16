import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime
from collections import deque

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="ZenByte Red Team Lab", layout="wide")

MAX_LOGS = 200
event_logs = deque(maxlen=MAX_LOGS)

# -----------------------------
# THREAT ENGINE
# -----------------------------
def classify_threat(event):
    score = 0

    if event["event_type"] == "FAILED_LOGIN":
        score += 30
    if event["event_type"] == "ENUMERATION":
        score += 50
    if event["attempts"] > 5:
        score += 40
    if event["unique_users_tried"] > 3:
        score += 30

    if score >= 80:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level


# -----------------------------
# ATTACK SIMULATION
# -----------------------------
def generate_event():
    attack_types = ["BRUTE_FORCE", "ENUMERATION", "NORMAL", "MIXED"]

    attack = random.choice(attack_types)

    event = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "ip": f"192.168.1.{random.randint(1, 255)}",
        "event_type": "",
        "username": random.choice(["admin", "test", "user", "root", "guest"]),
        "attempts": random.randint(1, 10),
        "unique_users_tried": random.randint(1, 5),
    }

    if attack == "BRUTE_FORCE":
        event["event_type"] = "FAILED_LOGIN"
        event["attempts"] = random.randint(5, 15)

    elif attack == "ENUMERATION":
        event["event_type"] = "ENUMERATION"
        event["unique_users_tried"] = random.randint(4, 10)

    elif attack == "MIXED":
        event["event_type"] = "FAILED_LOGIN"
        event["attempts"] = random.randint(3, 12)
        event["unique_users_tried"] = random.randint(2, 6)

    else:
        event["event_type"] = "SUCCESS_LOGIN"
        event["attempts"] = 1
        event["unique_users_tried"] = 1

    score, level = classify_threat(event)
    event["threat_score"] = score
    event["threat_level"] = level

    return event


# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("🛡️ZenBytr Red Team Lab")
st.markdown("Real-time attack simulation + threat detection dashboard")

col1, col2, col3 = st.columns(3)

start = st.button("▶ Start Simulation")
stop = st.button("⛔ Stop")

placeholder = st.empty()

# -----------------------------
# SIMULATION LOOP
# -----------------------------
running = True if start else False

if "running" not in st.session_state:
    st.session_state.running = False

if start:
    st.session_state.running = True

if stop:
    st.session_state.running = False

while st.session_state.running:
    event = generate_event()
    event_logs.append(event)

    df = pd.DataFrame(list(event_logs))

    with placeholder.container():
        col1, col2, col3 = st.columns(3)

        high = len(df[df["threat_level"] == "HIGH"])
        medium = len(df[df["threat_level"] == "MEDIUM"])
        low = len(df[df["threat_level"] == "LOW"])

        col1.metric("🔥 HIGH Threats", high)
        col2.metric("⚠️ MEDIUM Threats", medium)
        col3.metric("🟢 LOW Threats", low)

        st.subheader("📡 Live Event Stream")
        st.dataframe(df.tail(20), use_container_width=True)

        st.subheader("📊 Threat Distribution")
        st.bar_chart(df["threat_level"].value_counts())

    time.sleep(1)
