"""
db.py — All Supabase reads/writes live here.
Keeping every database call in one place makes the app easy to debug:
if something looks wrong in the data, this is the only file to check.
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_client() -> Client:
    """Create (once) and reuse the Supabase client for the whole session."""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# ---------- PLAYERS ----------

def get_all_players():
    """Return every player, sorted by total_points (leaderboard order)."""
    client = get_client()
    res = client.table("players").select("*").order("total_points", desc=True).execute()
    return res.data


def add_player(name: str):
    """Add a new player to the roster. Raises if the name already exists."""
    client = get_client()
    return client.table("players").insert({"name": name}).execute()


def update_player_stats(player_id: int, point_delta: int, won: bool):
    """
    Read a player's current stats, apply the change, write it back.
    This is the 'read-modify-write' pattern — fine for a friend-group app
    where two updates at the exact same instant are essentially impossible.
    """
    client = get_client()
    current = client.table("players").select("*").eq("id", player_id).single().execute().data

    new_points = current["total_points"] + point_delta
    new_wins = current["wins"] + (1 if won else 0)
    new_losses = current["losses"] + (0 if won else 1)
    new_games = current["games_played"] + 1

    client.table("players").update({
        "total_points": new_points,
        "wins": new_wins,
        "losses": new_losses,
        "games_played": new_games,
    }).eq("id", player_id).execute()


# ---------- GAMES ----------

def create_game(team_a_p1, team_a_p2, team_b_p1, team_b_p2, win_target):
    """Insert a new in-progress game row and return it (with its id)."""
    client = get_client()
    res = client.table("games").insert({
        "team_a_player1": team_a_p1,
        "team_a_player2": team_a_p2,
        "team_b_player1": team_b_p1,
        "team_b_player2": team_b_p2,
        "win_target": win_target,
        "is_finished": False,
    }).execute()
    return res.data[0]


def finish_game(game_id: int, final_a: int, final_b: int, winning_team: str):
    """Mark a game as finished and store its final result."""
    client = get_client()
    client.table("games").update({
        "final_team_a_score": final_a,
        "final_team_b_score": final_b,
        "winning_team": winning_team,
        "is_finished": True,
    }).eq("id", game_id).execute()


# ---------- ROUNDS ----------

def add_round(game_id, round_number, team_a_score, team_b_score, is_qaid=False, qaid_team=None):
    """Insert a round and return it (with its id, used later for Undo)."""
    client = get_client()
    res = client.table("rounds").insert({
        "game_id": game_id,
        "round_number": round_number,
        "team_a_round_score": team_a_score,
        "team_b_round_score": team_b_score,
        "is_qaid": is_qaid,
        "qaid_team": qaid_team,
    }).execute()
    return res.data[0]


def delete_round(round_id: int):
    """Used by the Undo button to remove the last submitted round."""
    client = get_client()
    client.table("rounds").delete().eq("id", round_id).execute()