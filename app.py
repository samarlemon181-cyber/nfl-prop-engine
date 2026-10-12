import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="NFL Prop Engine", layout="wide", initial_sidebar_state="collapsed")

# Mobile Styling Optimization
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e222d; padding: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏈 NFL Monte Carlo Engine")
st.caption("Coverage & Zone/Man Prop Analytics")

# Quick Controls
sim_count = st.select_slider("Simulations per Run", options=[1000, 5000, 10000], value=5000)
min_edge = st.slider("Min Win Probability (%)", 50, 75, 55)

# Engine Logic
def run_sims(sims):
    data = []
    players = [
        {"name": "Amon-Ra St. Brown", "pos": "WR", "mkt": "Rec Yards", "line": 74.5, "z_yprr": 2.85, "m_yprr": 1.65, "opp_zone": 0.74},
        {"name": "Ja'Marr Chase", "pos": "WR", "mkt": "Rec Yards", "line": 82.5, "z_yprr": 1.95, "m_yprr": 3.40, "opp_zone": 0.48},
        {"name": "Derrick Henry", "pos": "RB", "mkt": "Rush Yards", "line": 82.5, "z_yprr": 2.10, "m_yprr": 1.80, "opp_zone": 0.60},
        {"name": "Lamar Jackson", "pos": "QB", "mkt": "Pass Yards", "line": 225.5, "z_yprr": 2.40, "m_yprr": 2.10, "opp_zone": 0.65}
    ]
    
    for p in players:
        # Weighted metric based on opponent zone rate
        yprr = (p["z_yprr"] * p["opp_zone"]) + (p["m_yprr"] * (1 - p["opp_zone"]))
        sim_yards = np.random.gamma(shape=2.2, scale=(yprr * 32) / 2.2, size=sims)
        
        over_prob = round((np.sum(sim_yards > p["line"]) / sims) * 100, 1)
        
        data.append({
            "Player": p["name"],
            "Market": p["mkt"],
            "Line": p["line"],
            "Opp Zone %": f"{int(p['opp_zone']*100)}%",
            "Sim Avg": round(np.mean(sim_yards), 1),
            "Pick": "OVER" if over_prob > 50 else "UNDER",
            "Win Prob (%)": over_prob if over_prob > 50 else round(100 - over_prob, 1),
            "Raw": sim_yards
        })
    return pd.DataFrame(data)

df = run_sims(sim_count)
filtered_df = df[df["Win Prob (%)"] >= min_edge].drop(columns=["Raw"])

# Mobile Dashboard Display
st.subheader("⚡ Highest Edge Props")
st.dataframe(filtered_df, use_container_width=True)

st.markdown("---")
st.subheader("📊 Visual Distribution")
selected_player = st.selectbox("Select Player", df["Player"].unique())
p_row = df[df["Player"] == selected_player].iloc[0]

fig = go.Figure()
fig.add_trace(go.Histogram(x=p_row["Raw"], nbinsx=30, marker_color="#00cc96"))
fig.add_vline(x=p_row["Line"], line_dash="dash", line_color="red", annotation_text=f"Line: {p_row['Line']}")
fig.update_layout(template="plotly_dark", height=300, margin=dict(l=10, r=10, t=30, b=10))

st.plotly_chart(fig, use_container_width=True)
st.success(f"{p_row['Player']} hits the {p_row['Pick']} in {p_row['Win Prob (%)']}% of Monte Carlo runs vs this coverage scheme.")
