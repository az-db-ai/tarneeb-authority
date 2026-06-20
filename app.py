"""
app.py — هيئة الطرنيب (Tarneeb Authority)
A round-by-round score tracker for Tarneeb, built for a friend group.
"""

import streamlit as st
import db
from styles import CSS, stamp_html

st.set_page_config(page_title="هيئة الطرنيب", page_icon="🃏", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# LOGIN GATE
# ============================================================

def login_screen():
    st.markdown('<div class="app-title">هيئة الطرنيب</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Tarneeb Authority</div>', unsafe_allow_html=True)
    password = st.text_input("Password", type="password")
    if st.button("Enter", type="primary"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong password.")


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
    st.stop()


# ============================================================
# SESSION STATE DEFAULTS
# ============================================================

defaults = {
    "stage": "setup",          # setup -> playing -> finished -> post_game
    "rounds": [],               # list of round dicts (with db id) for the current game
    "game_id": None,
    "team_a": (None, None),     # (player_id, player_id)
    "team_b": (None, None),
    "win_target": 31,
    "show_round_panel": False,
    "show_qaid_panel": False,
    "winner": None,
    "prefill_players": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# HELPERS
# ============================================================

def team_totals():
    a = sum(r["team_a_round_score"] for r in st.session_state.rounds)
    b = sum(r["team_b_round_score"] for r in st.session_state.rounds)
    return a, b


def player_name(players, pid):
    for p in players:
        if p["id"] == pid:
            return p["name"]
    return "?"


def reset_for_new_game():
    st.session_state.stage = "setup"
    st.session_state.rounds = []
    st.session_state.game_id = None
    st.session_state.winner = None
    st.session_state.show_round_panel = False
    st.session_state.show_qaid_panel = False


# ============================================================
# TABS
# ============================================================

st.markdown('<div class="app-title">هيئة الطرنيب</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Tarneeb Authority</div>', unsafe_allow_html=True)

# Fetch the player list ONCE per rerun and reuse it in all three tabs below,
# instead of hitting Supabase three separate times (one per tab) on every click.
players = db.get_all_players()

tab_game, tab_players, tab_leaderboard = st.tabs(["🃏 New Game", "👥 Players", "🏆 Leaderboard"])


# ------------------------------------------------------------
# PLAYERS TAB
# ------------------------------------------------------------

with tab_players:
    st.subheader("Add a player")
    new_name = st.text_input("Player name", key="new_player_name")
    if st.button("Add Player"):
        clean_name = new_name.strip()
        if not clean_name:
            st.warning("Enter a name first.")
        else:
            try:
                db.add_player(clean_name)
                st.success(f"Added {clean_name}.")
                st.rerun()
            except Exception:
                st.error(f"'{clean_name}' already exists or couldn't be added.")

    st.subheader("Roster")
    roster = players
    if roster:
        st.dataframe(
            [{"Name": p["name"], "Points": p["total_points"], "Wins": p["wins"],
              "Losses": p["losses"], "Games": p["games_played"]} for p in roster],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No players yet — add your first friend above.")


# ------------------------------------------------------------
# LEADERBOARD TAB
# ------------------------------------------------------------

with tab_leaderboard:
    st.subheader("Leaderboard")
    board = players
    if board:
        st.dataframe(
            [{"Player": p["name"], "Points": p["total_points"], "Wins": p["wins"],
              "Losses": p["losses"], "Games Played": p["games_played"]} for p in board],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No games played yet.")


# ------------------------------------------------------------
# NEW GAME TAB
# ------------------------------------------------------------

with tab_game:
    # `players` was already fetched once above, before the tabs — reused here.

    # ---------------- SETUP STAGE ----------------
    if st.session_state.stage == "setup":
        if len(players) < 4:
            st.warning("You need at least 4 players in the roster. Add more in the Players tab.")
        else:
            st.subheader("Win target")
            st.session_state.win_target = st.radio(
                "Play to:", [31, 61], horizontal=True,
                index=[31, 61].index(st.session_state.win_target),
            )

            st.subheader("Teams")
            names = [p["name"] for p in players]
            ids_by_name = {p["name"]: p["id"] for p in players}

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Team A**")
                a1 = st.selectbox("Player 1", names, key="a1")
                a2 = st.selectbox("Player 2", names, key="a2")
            with col2:
                st.markdown("**Team B**")
                b1 = st.selectbox("Player 1", names, key="b1")
                b2 = st.selectbox("Player 2", names, key="b2")

            chosen = [a1, a2, b1, b2]
            if len(set(chosen)) < 4:
                st.error("Each player can only be picked once.")
            elif st.button("Start Game", type="primary"):
                game = db.create_game(
                    ids_by_name[a1], ids_by_name[a2],
                    ids_by_name[b1], ids_by_name[b2],
                    st.session_state.win_target,
                )
                st.session_state.game_id = game["id"]
                st.session_state.team_a = (ids_by_name[a1], ids_by_name[a2])
                st.session_state.team_b = (ids_by_name[b1], ids_by_name[b2])
                st.session_state.rounds = []
                st.session_state.stage = "playing"
                st.rerun()

    # ---------------- PLAYING STAGE ----------------
    elif st.session_state.stage == "playing":
        a_name1 = player_name(players, st.session_state.team_a[0])
        a_name2 = player_name(players, st.session_state.team_a[1])
        b_name1 = player_name(players, st.session_state.team_b[0])
        b_name2 = player_name(players, st.session_state.team_b[1])

        total_a, total_b = team_totals()

        st.markdown(f"""
        <div class="score-card">
            <div style="display:flex; justify-content:space-around;">
                <div>
                    <div class="score-team-label">{a_name1} & {a_name2}</div>
                    <div class="score-number {'winning' if total_a > total_b else ''}">{total_a}</div>
                </div>
                <div>
                    <div class="score-team-label">{b_name1} & {b_name2}</div>
                    <div class="score-number {'winning' if total_b > total_a else ''}">{total_b}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add Round", use_container_width=True, key="btn_add_round"):
                st.session_state.show_round_panel = True
                st.session_state.show_qaid_panel = False
        with col2:
            if st.button("🚩 Qaid", use_container_width=True, key="btn_qaid"):
                st.session_state.show_qaid_panel = True
                st.session_state.show_round_panel = False
        with col3:
            if st.button("↺ Undo", use_container_width=True, disabled=len(st.session_state.rounds) == 0, key="btn_undo"):
                last = st.session_state.rounds.pop()
                db.delete_round(last["id"])
                st.rerun()

        # --- Add Round panel ---
        if st.session_state.show_round_panel:
            with st.form("add_round_form"):
                st.markdown("**Add round score**")
                c1, c2 = st.columns(2)
                with c1:
                    pts_a = st.number_input(
                        f"{a_name1} & {a_name2}", step=1, value=None,
                        placeholder="0", key="pts_a",
                    )
                with c2:
                    pts_b = st.number_input(
                        f"{b_name1} & {b_name2}", step=1, value=None,
                        placeholder="0", key="pts_b",
                    )
                fc1, fc2 = st.columns(2)
                confirm = fc1.form_submit_button("Confirm", type="primary", use_container_width=True, key="btn_confirm_round")
                cancel = fc2.form_submit_button("Cancel", use_container_width=True, key="btn_cancel_round")

            if confirm:
                final_a = int(pts_a) if pts_a is not None else 0
                final_b = int(pts_b) if pts_b is not None else 0
                round_row = db.add_round(
                    st.session_state.game_id,
                    len(st.session_state.rounds) + 1,
                    final_a, final_b,
                )
                st.session_state.rounds.append(round_row)
                st.session_state.show_round_panel = False
                st.rerun()
            if cancel:
                st.session_state.show_round_panel = False
                st.rerun()

        # --- Qaid panel ---
        if st.session_state.show_qaid_panel:
            with st.form("qaid_form"):
                st.markdown("**Who got caught cheating?**")
                qaid_choice = st.radio(
                    "Team", [f"{a_name1} & {a_name2}", f"{b_name1} & {b_name2}"],
                )
                fc1, fc2 = st.columns(2)
                confirm_q = fc1.form_submit_button("Confirm", type="primary", use_container_width=True, key="btn_confirm_qaid")
                cancel_q = fc2.form_submit_button("Cancel", use_container_width=True, key="btn_cancel_qaid")

            if confirm_q:
                cheating_team = "A" if qaid_choice.startswith(a_name1) else "B"
                round_row = db.add_round(
                    st.session_state.game_id,
                    len(st.session_state.rounds) + 1,
                    -5 if cheating_team == "A" else 0,
                    -5 if cheating_team == "B" else 0,
                    is_qaid=True,
                    qaid_team=cheating_team,
                )
                st.session_state.rounds.append(round_row)
                st.session_state.show_qaid_panel = False
                st.rerun()
            if cancel_q:
                st.session_state.show_qaid_panel = False
                st.rerun()

        # --- Round history ---
        if st.session_state.rounds:
            st.markdown("**Round history**")
            for r in reversed(st.session_state.rounds):
                if r["is_qaid"]:
                    culprit = a_name1 if r["qaid_team"] == "A" else b_name1
                    st.markdown(
                        f'<div class="round-row qaid">Round {r["round_number"]} — '
                        f'🚩 Qaid called on {culprit}\'s team (-5)</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="round-row">Round {r["round_number"]} — '
                        f'{r["team_a_round_score"]} / {r["team_b_round_score"]}</div>',
                        unsafe_allow_html=True,
                    )

        # --- Win detection ---
        target = st.session_state.win_target
        if total_a >= target or total_b >= target:
            if total_a >= target and total_b >= target:
                winner = "A" if total_a > total_b else ("B" if total_b > total_a else None)
            elif total_a >= target:
                winner = "A"
            else:
                winner = "B"

            if winner:
                st.session_state.winner = winner
                st.session_state.stage = "finished"
                st.rerun()

    # ---------------- FINISHED STAGE ----------------
    elif st.session_state.stage == "finished":
        a_name1 = player_name(players, st.session_state.team_a[0])
        b_name1 = player_name(players, st.session_state.team_b[0])
        total_a, total_b = team_totals()
        winner = st.session_state.winner
        winner_label = f"TEAM {winner} WINS" if winner else "GAME OVER"

        st.markdown(stamp_html(winner_label, kind="win"), unsafe_allow_html=True)
        st.write(f"Final score — Team A: **{total_a}**, Team B: **{total_b}**")

        if st.button("Confirm & Save Result", type="primary"):
            db.finish_game(st.session_state.game_id, total_a, total_b, winner)

            for pid in st.session_state.team_a:
                db.update_player_stats(pid, point_delta=1 if winner == "A" else -1, won=(winner == "A"))
            for pid in st.session_state.team_b:
                db.update_player_stats(pid, point_delta=1 if winner == "B" else -1, won=(winner == "B"))

            st.session_state.stage = "post_game"
            st.rerun()

    # ---------------- POST GAME STAGE ----------------
    elif st.session_state.stage == "post_game":
        st.subheader("Game saved ✅")
        st.write("Set up the next game:")

        same_teams = st.radio("Same teams again?", ["Yes, replay", "No, change teams"])
        same_target = st.radio("Same target again?", ["Yes, keep it", "No, change it"])

        if st.button("Continue", type="primary"):
            prev_a = st.session_state.team_a
            prev_b = st.session_state.team_b
            prev_target = st.session_state.win_target

            reset_for_new_game()

            if same_teams == "Yes, replay" and same_target == "Yes, keep it":
                # Skip straight back into a fresh game with the same lineup.
                game = db.create_game(prev_a[0], prev_a[1], prev_b[0], prev_b[1], prev_target)
                st.session_state.game_id = game["id"]
                st.session_state.team_a = prev_a
                st.session_state.team_b = prev_b
                st.session_state.win_target = prev_target
                st.session_state.stage = "playing"
            else:
                # At least one thing is changing — send back to setup.
                # (Setup form starts fresh; win_target defaults to last value used.)
                st.session_state.win_target = prev_target if same_target == "Yes, keep it" else 31
                st.session_state.stage = "setup"

            st.rerun()