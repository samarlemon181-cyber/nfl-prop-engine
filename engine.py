import numpy as np
import pandas as pd

class AdvancedNFLSimulationEngine:
    def __init__(self, simulations=10000):
        self.simulations = simulations

    def run_slate_simulations(self, matchups):
        """
        Calculates dynamic rolling metrics, standard deviations, and runs 
        10,000 Monte Carlo iterations per prop to find true model edges.
        """
        np.random.seed(42)
        prop_results = []
        game_results = []

        for m in matchups:
            # Game Level Scoring Distribution
            h_exp = 22.5 + (m["home_off_epa"] - m["away_def_epa"]) * 20
            a_exp = 21.5 + (m["away_off_epa"] - m["home_def_epa"]) * 20
            
            home_scores = np.random.normal(loc=h_exp, scale=9.5, size=self.simulations)
            away_scores = np.random.normal(loc=a_exp, scale=9.5, size=self.simulations)
            
            h_wins = np.sum(home_scores > away_scores)
            h_win_pct = round((h_wins / self.simulations) * 100, 1)
            
            proj_home = round(np.mean(home_scores), 1)
            proj_away = round(np.mean(away_scores), 1)

            game_results.append({
                "Matchup": f"{m['away']} @ {m['home']}",
                "Proj Score": f"{m['away']} {proj_away} - {proj_home} {m['home']}",
                "ML Pick": m['home'] if h_win_pct > 50 else m['away'],
                "Win Prob %": max(h_win_pct, 100.0 - h_win_pct)
            })

            # Player Prop Level Processing & Simulation
            for p in m["players"]:
                recent_games = p["recent_games"]
                actual_l3_avg = np.mean(recent_games[-3:])
                actual_l5_avg = np.mean(recent_games)

                opp_zone = m["away_zone"] if p["team"] == m["home"] else m["home_zone"]
                expected_efficiency = (p["zone_yprr"] * opp_zone) + (p["man_yprr"] * (1.0 - opp_zone))

                if p["market"] == "Anytime TD":
                    lambda_val = (p["rz_share"] * 0.5) * (proj_home / 24.0 if p["team"] == m["home"] else proj_away / 24.0)
                    sims = np.random.poisson(lam=max(0.1, lambda_val), size=self.simulations)
                    hit_count = np.sum(sims >= 1)
                    sim_mean = round(np.mean(sims), 2)
                    pick = "YES" if (hit_count / self.simulations) >= 0.5 else "NO"
                else:
                    std_dev = np.std(recent_games) if len(recent_games) > 1 else 15.0
                    sims = np.random.normal(loc=actual_l5_avg * (expected_efficiency / 2.0), scale=max(8.0, std_dev), size=self.simulations)
                    sims = np.maximum(0, sims)
                    
                    hit_count = np.sum(sims > p["line"])
                    sim_mean = round(np.mean(sims), 1)
                    pick = "OVER" if (hit_count / self.simulations) >= 0.5 else "UNDER"

                win_prob = round((hit_count / self.simulations) * 100, 1)
                if pick in ["UNDER", "NO"]:
                    win_prob = round(100.0 - win_prob, 1)

                line = p["line"]
                h3_hit = f"{int((sum(1 for x in recent_games[-3:] if x > line) / 3) * 100)}%"
                h5_hit = f"{int((sum(1 for x in recent_games if x > line) / len(recent_games)) * 100)}%"

                p_dec = win_prob / 100.0
                fair_val = int(-100 / (p_dec / (1 - p_dec))) if p_dec > 0.5 else int(((1 - p_dec) / p_dec) * 100)
                fair_str = f"+{fair_val}" if fair_val > 0 else f"{fair_val}"

                prop_results.append({
                    "Matchup": f"{m['away']} @ {m['home']}",
                    "Player": p["name"],
                    "Team": p["team"],
                    "Pos": p["pos"],
                    "Prop Market": f"{pick} {p['line']} {p['market']}",
                    "Book Line": p["line"],
                    "Odds": p["book_odds"],
                    "Fair Odds": fair_str,
                    "Sim Mean": sim_mean,
                    "Actual L3 Avg": round(actual_l3_avg, 1),
                    "Actual L5 Avg": round(actual_l5_avg, 1),
                    "Pick": pick,
                    "Win Prob (%)": win_prob,
                    "Edge (%)": f"+{round(win_prob - 50.0, 1)}%",
                    "Matchup Grade": p["matchup_grade"],
                    "Matchup Class": p["matchup_class"],
                    "H2H": p["h2h"],
                    "L3": h3_hit,
                    "L5": h5_hit,
                    "L10": p["l10"],
                    "26-27": p["season_26"],
                    "25-27": p["season_25"],
                    "Recent Games": recent_games,
                    "Game Labels": p["game_labels"],
                    "Raw Sims": sims
                })

        return pd.DataFrame(game_results), pd.DataFrame(prop_results)
