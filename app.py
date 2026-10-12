import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from engine import AdvancedNFLSimulationEngine

st.set_page_config(
    page_title="Trends - NFL Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    div[data-testid="stToolbar"] { visibility: hidden; }
    
    .section-header {
        font-size: 16px;
        font-weight: 700;
        color: #00e676;
        margin-top: 15px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .outlier-card {
        background-color: #12161f;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
        border: 1px solid #1f2430;
    }
    .player-title { font-size: 17px; font-weight: 700; color: #ffffff; }
    .prop-sub { font-size: 13px; color: #8b949e; margin-bottom: 6px; }
    
    .matchup-aplus { color: #00e676; font-weight: 600; font-size: 12px; }
    .matchup-b { color: #29b6f6; font-weight: 600; font-size: 12px; }
    .matchup-c { color: #ff9800; font-weight: 600; font-size: 12px; }
    
    .odds-badge {
        background-color: #1c2333;
        color: #ffffff;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        float: right;
        text-align: center;
    }
    .edge-green { color: #00e676; font-size: 11px; display: block; font-weight: 600; }
    
    .stat-row {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid #1a202c;
        text-align: center;
    }
    .stat-box { flex: 1; }
    .stat-label { font-size: 10px; color: #6e7681; font-weight: 600; }
    .stat-val-green { font-size: 12px; color: #00e676; font-weight: 700; }
    .stat-val-red { font-size: 12px; color: #ff5252; font-weight: 700; }
    .stat-val-yellow { font-size: 12px; color: #ffd700; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

st.markdown("### 📊 Trends & Simulation Terminal")

col_nav1, col_nav2 = st.columns([1, 1])
with col_nav1:
    sport = st.selectbox("League Slate", ["🏈 NFL (Week 6 Live)", "🏀 NBA", "⚾ MLB"], index=0)
with col_nav2:
    terminal_view = st.selectbox("Terminal View", ["🔥 Sim-Recommended Best Bets", "📋 All Player Trends", "🏟️ Game Slate Projections"], index=0)

col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    timeframe = st.select_slider("Trend Window", options=["H2H", "L3", "L5", "L10", "'26-'27", "'25-'27"], value="'26-'27")
with col_f2:
    min_edge_val = st.slider("Min Edge (%)", 50, 85, 58)

st.markdown("---")

@st.cache_data
def get_week6_live_data():
    return [
        {
            "home": "DEN", "away": "SEA",
            "home_off_epa": 0.02, "home_def_epa": -0.08, "home_zone": 0.68,
            "away_off_epa": 0.12, "away_def_epa": -0.02, "away_zone": 0.60,
            "players": [
                {
                    "name": "Jaxon Smith-Njigba", "team": "SEA", "pos": "WR", "market": "Receiving YDs",
                    "line": 62.5, "book_odds": "+185", "zone_yprr": 2.45, "man_yprr": 1.80,
                    "matchup_grade": "@ DEN (B+ Matchup)", "matchup_class": "matchup-b",
                    "h2h": "100%", "l10": "70%", "season_26": "80%", "season_25": "55%",
                    "recent_games": [78, 84, 52, 91, 68], "game_labels": ["vs SF", "vs LAC", "@ ARI", "vs MIA", "@ CAR"]
                }
            ]
        },
        {
            "home": "JAC", "away": "HOU",
            "home_off_epa": 0.04, "home_def_epa": 0.08, "home_zone": 0.74,
            "away_off_epa": 0.10, "away_def_epa": -0.04, "away_zone": 0.58,
            "players": [
                {
                    "name": "Nico Collins", "team": "HOU", "pos": "WR", "market": "Receiving YDs",
                    "line": 64.5, "book_odds": "+195", "zone_yprr": 3.12, "man_yprr": 2.20,
                    "matchup_grade": "@ JAC (A+ Matchup)", "matchup_class": "matchup-aplus",
                    "h2h": "0%", "l10": "50%", "season_26": "100%", "season_25": "32%",
                    "recent_games": [72, 85, 45, 68, 90], "game_labels": ["@ TEN", "vs DAL", "@ IND", "vs CIN", "vs BUF"]
                }
            ]
        },
        {
            "home": "CLE", "away": "BAL",
            "home_off_epa": -0.06, "home_def_epa": -0.02, "home_zone": 0.62,
            "away_off_epa": 0.18, "away_def_epa": -0.06, "away_zone": 0.65,
            "players": [
                {
                    "name": "Derrick Henry", "team": "BAL", "pos": "RB", "market": "Rush YDs",
                    "line": 84.5, "book_odds": "+160", "zone_yprr": 2.10, "man_yprr": 1.75,
                    "matchup_grade": "@ CLE (A+ Matchup)", "matchup_class": "matchup-aplus",
                    "h2h": "100%", "l10": "70%", "season_26": "80%", "season_25": "62%",
                    "recent_games": [108, 92, 65, 115, 102], "game_labels": ["@ ATL", "vs BUF", "vs CIN", "@ NYJ", "vs PIT"]
                },
                {
                    "name": "Derrick Henry", "team": "BAL", "pos": "RB", "market": "Anytime TD",
                    "line": 0.5, "book_odds": "-145", "zone_yprr": 1.0, "man_yprr": 1.0, "rz_share": 0.65,
                    "matchup_grade": "@ CLE (A+ Matchup)", "matchup_class": "matchup-aplus",
                    "h2h": "100%", "l10": "80%", "season_26": "100%", "season_25": "75%",
                    "recent_games": [1, 1, 0, 2, 1], "game_labels": ["@ ATL", "vs BUF", "vs CIN", "@ NYJ", "vs PIT"]
                }
            ]
        },
        {
            "home": "GB", "away": "DAL",
            "home_off_epa": 0.14, "home_def_epa": 0.01, "home_zone": 0.64,
            "away_off_epa": 0.08, "away_def_epa": 0.05, "away_zone": 0.56,
            "players": [
                {
                    "name": "CeeDee Lamb", "team": "DAL", "pos": "WR", "market": "Receiving YDs",
                    "line": 78.5, "book_odds": "+190", "zone_yprr": 2.80, "man_yprr": 3.10,
                    "matchup_grade": "@ GB (B+ Matchup)", "matchup_class": "matchup-b",
                    "h2h": "80%", "l10": "70%", "season_26": "80%", "season_25": "68%",
                    "recent_games": [92, 105, 64, 88, 110], "game_labels": ["vs TB", "@ HOU", "vs NYG", "@ CAR", "vs WAS"]
                }
            ]
        }
    ]

matchups = get_week6_live_data()
engine = AdvancedNFLSimulationEngine(simulations=10000)
df_games, df_props = engine.run_slate_simulations(matchups)

df_filtered = df_props[df_props["Win Prob (%)"] >= min_edge_val]

if terminal_view == "🔥 Sim-Recommended Best Bets":
    st.markdown('<div class="section-header">⚡ Top Model-Verified Edges</div>', unsafe_allow_html=True)
    best_bets = df_props.sort_values(by="Win Prob (%)", ascending=False).head(4)
    
    for idx, p in best_bets.iterrows():
        st.markdown(f"""
            <div class="outlier-card">
                <div class="odds-badge">
                    {p['Odds']}
                    <span class="edge-green">Edge: {p['Edge (%)']}</span>
                </div>
                <div class="player-title">{p['Player']} ({p['Team']})</div>
                <div class="prop-sub">🔥 Recommended: {p['Prop Market']} (Win Prob: {p['Win Prob (%)']}%)</div>
                <div class="{p['Matchup Class']}">{p['Matchup Grade']}</div>
                
                <div class="stat-row">
                    <div class="stat-box"><div class="stat-label">Sim Avg</div><div class="stat-val-green">{p['Sim Mean']}</div></div>
                    <div class="stat-box"><div class="stat-label">L3 Avg</div><div class="stat-val-green">{p['Actual L3 Avg']}</div></div>
                    <div class="stat-box"><div class="stat-label">L5 Avg</div><div class="stat-val-green">{p['Actual L5 Avg']}</div></div>
                    <div class="stat-box"><div class="stat-label">Fair Odds</div><div class="stat-val-yellow">{p['Fair Odds']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

elif terminal_view == "📋 All Player Trends":
    st.markdown('<div class="section-header">📋 Complete Player Prop Terminal</div>', unsafe_allow_html=True)
    
    for idx, p in df_filtered.iterrows():
        st.markdown(f"""
            <div class="outlier-card">
                <div class="odds-badge">
                    {p['Odds']}
                    <span class="edge-green">Edge: {p['Edge (%)']}</span>
                </div>
                <div class="player-title">{p['Player']} ({p['Team']})</div>
                <div class="prop-sub">{p['Prop Market']}</div>
                <div class="{p['Matchup Class']}">{p['Matchup Grade']}</div>
                
                <div class="stat-row">
                    <div class="stat-box"><div class="stat-label">H2H</div><div class="stat-val-green">{p['H2H']}</div></div>
                    <div class="stat-box"><div class="stat-label">L3</div><div class="stat-val-green">{p['L3']}</div></div>
                    <div class="stat-box"><div class="stat-label">L5</div><div class="stat-val-green">{p['L5']}</div></div>
                    <div class="stat-box"><div class="stat-label">L10</div><div class="stat-val-yellow">{p['L10']}</div></div>
                    <div class="stat-box"><div class="stat-label">'26-'27</div><div class="stat-val-green">{p['26-27']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.expander(f"📊 View {p['Player']} Recent Log Breakdown"):
            recent_vals = p["Recent Games"]
            game_labels = p["Game Labels"]
            target_line = p["Book Line"]
            
            fig = go.Figure()
            bar_colors = ['#00e676' if v > target_line else '#ff5252' for v in recent_vals]
            
            fig.add_trace(go.Bar(
                x=game_labels,
                y=recent_vals,
                marker_color=bar_colors,
                text=recent_vals,
                textposition='outside'
            ))
            
            fig.add_hline(
                y=target_line,
                line_dash="dash",
                line_color="#29b6f6",
                annotation_text=f"Line: {target_line}"
            )
            
            fig.update_layout(
                template="plotly_dark",
                height=220,
                margin=dict(l=10, r=10, t=25, b=10),
                yaxis_title="Output",
                xaxis_title="Recent Opponents"
            )
            st.plotly_chart(fig, use_container_width=True)

else:
    st.markdown('<div class="section-header">🏟️ Week 6 Game Slate Simulations</div>', unsafe_allow_html=True)
    st.dataframe(df_games.style.background_gradient(subset=["Win Prob %"], cmap="Greens"), use_container_width=True)
