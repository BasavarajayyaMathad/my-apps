"""
Carrom Tournament Builder - Streamlit Application
Main application file for tournament management
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

from config import TournamentConfig
from tournament_engine import TournamentEngine
from nlp_processor import NLPProcessor
from visualizations import TournamentVisualizer
from streamlit_auth import StreamlitAuthManager, PermissionChecker

# Page configuration MUST be first Streamlit command
st.set_page_config(
    page_title=f"{TournamentConfig.SPORT_NAME} Tournament Manager",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication
StreamlitAuthManager.init_session_state()

# Check authentication - redirect to login if not authenticated
if not StreamlitAuthManager.is_authenticated():
    StreamlitAuthManager.render_login_page()
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
        margin-top: 1rem;
    }
    .match-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1E88E5;
    }
    .winner-highlight {
        background-color: #e8f5e9;
        border-left-color: #4CAF50 !important;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'engine' not in st.session_state:
        st.session_state.engine = TournamentEngine()
    if 'nlp' not in st.session_state:
        st.session_state.nlp = NLPProcessor()
    if 'viz' not in st.session_state:
        st.session_state.viz = TournamentVisualizer()
    if 'tournament_initialized' not in st.session_state:
        st.session_state.tournament_initialized = False
    if 'groups' not in st.session_state:
        st.session_state.groups = {}
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = "setup"
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None


def load_existing_tournament():
    """Try to load existing tournament data"""
    results_file = TournamentConfig.RESULTS_FILE
    if os.path.exists(results_file):
        if st.sidebar.button("📂 Load Existing Tournament"):
            if st.session_state.engine.load_from_excel(results_file):
                st.session_state.tournament_initialized = True
                st.session_state.current_stage = "group"
                # Rebuild groups
                st.session_state.groups = {}
                for team in st.session_state.engine.teams:
                    if team.group not in st.session_state.groups:
                        st.session_state.groups[team.group] = []
                    st.session_state.groups[team.group].append(team)
                st.success("✅ Tournament loaded successfully!")
                st.rerun()


def save_tournament():
    """Save tournament to Excel"""
    try:
        st.session_state.engine.save_to_excel(TournamentConfig.RESULTS_FILE)
        return True
    except Exception as e:
        st.error(f"Error saving tournament: {e}")
        return False


def reset_tournament():
    """Reset the tournament to start fresh"""
    # Check permission
    if not PermissionChecker.check_edit_tournament():
        PermissionChecker.show_permission_denied()
        return
    
    # Clear session state
    st.session_state.engine = TournamentEngine()
    st.session_state.tournament_initialized = False
    st.session_state.groups = {}
    st.session_state.current_stage = "setup"
    st.session_state.start_time = None
    
    # Clear date/time selections
    if 'selected_date' in st.session_state:
        del st.session_state.selected_date
    if 'selected_time' in st.session_state:
        del st.session_state.selected_time
    
    # Optionally delete the results file
    if os.path.exists(TournamentConfig.RESULTS_FILE):
        try:
            os.remove(TournamentConfig.RESULTS_FILE)
        except:
            pass
    
    st.success("🔄 Tournament reset successfully!")
    
    # Log action
    from user_manager import UserManager
    user_manager = UserManager()
    user = StreamlitAuthManager.get_current_user()
    user_manager.log_action(user.email if user else None, "Reset tournament")


def render_sidebar():
    """Render sidebar with navigation and settings"""
    st.sidebar.markdown(f"## 🏆 {TournamentConfig.SPORT_NAME} Tournament")
    
    # User information and logout
    StreamlitAuthManager.render_logout_button()
    
    st.sidebar.markdown("---")
    
    # Tournament settings
    st.sidebar.markdown("### ⚙️ Settings")
    
    # Number of Groups (only show if tournament not initialized)
    if not st.session_state.tournament_initialized:
        # Check if user is admin to allow settings changes
        if PermissionChecker.check_edit_tournament():
            new_num_groups = st.sidebar.selectbox(
                "Number of Groups",
                options=[2, 4],
                index=0 if TournamentConfig.NUMBER_OF_GROUPS == 2 else 1,
                help="2 groups: Top 4 teams qualify from each group\n4 groups: Top 2 teams qualify from each group"
            )
            TournamentConfig.NUMBER_OF_GROUPS = new_num_groups
            
            # Show qualification info
            top_per_group = TournamentConfig.get_top_teams_per_group()
            st.sidebar.info(f"📊 Top {top_per_group} teams from each group will qualify for Quarter Finals")
        else:
            st.sidebar.info("⏳ Waiting for tournament initialization...")
    else:
        st.sidebar.markdown(f"**Groups:** {TournamentConfig.NUMBER_OF_GROUPS}")
        top_per_group = TournamentConfig.get_top_teams_per_group()
        st.sidebar.markdown(f"**Qualifiers per group:** {top_per_group}")
    
    # Match duration - only for admins
    if PermissionChecker.check_edit_tournament():
        new_duration = st.sidebar.number_input(
            "Match Duration (minutes)",
            min_value=5,
            max_value=120,
            value=TournamentConfig.MATCH_DURATION_MINUTES,
            step=5
        )
        TournamentConfig.MATCH_DURATION_MINUTES = new_duration
        
        # Points per win
        new_points = st.sidebar.number_input(
            "Points per Win",
            min_value=1,
            max_value=10,
            value=TournamentConfig.POINTS_PER_WIN,
            step=1
        )
        TournamentConfig.POINTS_PER_WIN = new_points
    
    st.sidebar.markdown("---")
    
    # Load existing tournament
    load_existing_tournament()
    
    # Save and Reset buttons - only for admins
    if st.session_state.tournament_initialized:
        if PermissionChecker.check_edit_tournament():
            if st.sidebar.button("💾 Save Tournament"):
                if save_tournament():
                    st.sidebar.success("✅ Saved!")
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### ⚠️ Danger Zone")
            
            # Reset Tournament button with confirmation
            if 'confirm_reset' not in st.session_state:
                st.session_state.confirm_reset = False
            
            if not st.session_state.confirm_reset:
                if st.sidebar.button("🔄 Reset Tournament", type="secondary"):
                    st.session_state.confirm_reset = True
                    st.rerun()
            else:
                st.sidebar.warning("Are you sure? This will delete all tournament data!")
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("✅ Yes, Reset"):
                        st.session_state.confirm_reset = False
                        reset_tournament()
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel"):
                        st.session_state.confirm_reset = False
                        st.rerun()
        else:
            st.sidebar.info("🔒 Admin features are locked for Viewers")
    
    st.sidebar.markdown("---")
    
    # NLP Status
    nlp_status = "🟢 Active" if st.session_state.nlp.is_available() else "🔴 Not configured"
    st.sidebar.markdown(f"**NLP Status:** {nlp_status}")
    
    if not st.session_state.nlp.is_available():
        st.sidebar.info("Add OPENAI_API_KEY to .env file to enable NLP features")


def render_setup_page():
    """Render tournament setup page"""
    st.markdown('<div class="main-header">🏆 Tournament Setup</div>', unsafe_allow_html=True)
    
    # Check if user is admin
    if not PermissionChecker.check_edit_tournament():
        st.info("👁️ You are viewing as a Viewer")
        # Check if any tournament exists by trying to load from file
        results_file = TournamentConfig.RESULTS_FILE
        if os.path.exists(results_file):
            st.success("✅ An active tournament exists. Tournament data is available.")
            st.info("Contact an admin to set up a new tournament.")
        else:
            st.warning("⏳ No active tournaments exist.")
            st.info("Contact an admin to set up and initialize a new tournament.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📤 Upload Teams")
        st.markdown("""
        Upload an Excel file with team information. The file should have columns:
        - `team_name` or `team` - Name of the team
        - `participants` or `player1`, `player2`, etc. - Team members
        """)
        
        uploaded_file = st.file_uploader(
            "Choose Excel file",
            type=['xlsx', 'xls'],
            help="Upload an Excel file with team names and participants"
        )
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                st.success(f"✅ Found {len(df)} teams in the file")
                st.dataframe(df, use_container_width=True)
                
                # Load teams
                st.session_state.engine.load_teams_from_dataframe(df)
                
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    with col2:
        st.markdown("### 📋 Sample Format")
        sample_df = pd.DataFrame({
            'team_name': ['Team Alpha', 'Team Beta', 'Team Gamma'],
            'participants': ['John, Jane', 'Bob, Alice', 'Mike, Sarah']
        })
        st.dataframe(sample_df)
        
        # Download sample
        sample_excel = sample_df.to_csv(index=False)
        st.download_button(
            "📥 Download Sample Template",
            sample_excel,
            "sample_teams.csv",
            "text/csv"
        )
    
    st.markdown("---")
    
    # Schedule settings
    if st.session_state.engine.teams:
        st.markdown("### ⏰ Schedule Settings")
        
        col1, col2, col3 = st.columns(3)
        
        # Use session state to persist date/time selections
        if 'selected_date' not in st.session_state:
            st.session_state.selected_date = datetime.now().date()
        if 'selected_end_date' not in st.session_state:
            st.session_state.selected_end_date = (datetime.now() + timedelta(days=1)).date()
        if 'selected_time' not in st.session_state:
            st.session_state.selected_time = datetime.now().replace(hour=9, minute=0).time()
        
        with col1:
            start_date = st.date_input(
                "Tournament Start Date",
                value=st.session_state.selected_date,
                key="tournament_date"
            )
            st.session_state.selected_date = start_date
        
        with col2:
            end_date = st.date_input(
                "Tournament End Date",
                value=st.session_state.selected_end_date,
                key="tournament_end_date"
            )
            st.session_state.selected_end_date = end_date
        
        with col3:
            start_time = st.time_input(
                "Start Time",
                value=st.session_state.selected_time,
                key="tournament_time"
            )
            st.session_state.selected_time = start_time
        
        st.session_state.start_time = datetime.combine(start_date, start_time)
        st.session_state.end_time = datetime.combine(end_date, st.session_state.selected_time)
        
        # Display tournament duration
        duration_days = (end_date - start_date).days + 1
        st.info(f"📅 Tournament Duration: {duration_days} day(s) (from {start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')})")
        
        st.markdown("---")
        
        # Initialize tournament button
        if st.button("🚀 Initialize Tournament", type="primary", use_container_width=True):
            # Divide into groups
            st.session_state.groups = st.session_state.engine.divide_into_groups(shuffle=True)
            
            # Generate group stage fixtures
            st.session_state.engine.generate_group_stage_fixtures(st.session_state.groups)
            
            # Schedule matches with parallel execution (2 matches at same time)
            st.session_state.engine.schedule_matches(st.session_state.start_time, parallel_matches=2)
            
            # Save initial state
            save_tournament()
            
            st.session_state.tournament_initialized = True
            st.session_state.current_stage = "group"
            
            st.success("✅ Tournament initialized successfully!")
            st.rerun()


def render_group_stage():
    """Render group stage view"""
    st.markdown('<div class="main-header">📊 Group Stage</div>', unsafe_allow_html=True)
    
    # Group tabs
    groups = sorted(st.session_state.groups.keys())
    tabs = st.tabs([f"Group {g}" for g in groups] + ["All Matches"])
    
    for i, group in enumerate(groups):
        with tabs[i]:
            render_group_view(group)
    
    # All matches tab
    with tabs[-1]:
        render_all_matches("group")
    
    # Check if group stage is complete
    group_matches = st.session_state.engine.get_matches_by_stage("group")
    completed = all(m.status == "completed" for m in group_matches)
    
    if completed and group_matches:
        st.markdown("---")
        st.success("🎉 Group stage complete!")
        
        if st.button("➡️ Generate Quarter Finals", type="primary"):
            st.session_state.engine.generate_quarterfinals()
            # Schedule quarterfinal matches
            last_match = max(group_matches, key=lambda m: m.end_time if m.end_time else datetime.min)
            start = last_match.end_time + timedelta(minutes=30) if last_match.end_time else datetime.now()
            qf_matches = st.session_state.engine.get_matches_by_stage("quarterfinal")
            st.session_state.engine.schedule_matches(start, qf_matches)
            save_tournament()
            st.session_state.current_stage = "quarterfinal"
            st.rerun()


def render_group_view(group: str):
    """Render a single group view"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"### 📋 Group {group} Standings")
        
        standings = st.session_state.engine.get_group_standings(group)
        standings_data = [s.to_dict() for s in standings]
        
        if standings_data:
            df = pd.DataFrame(standings_data)
            df = df[['team_name', 'matches_played', 'wins', 'losses', 'draws', 'points', 'score_difference']]
            df.columns = ['Team', 'MP', 'W', 'L', 'D', 'Pts', '+/-']
            
            # Add visual indicators - show trophy for qualifying teams
            top_n = TournamentConfig.get_top_teams_per_group()
            df['Status'] = df.apply(
                lambda r: '🏆' if r.name < top_n else '',
                axis=1
            )
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Standings chart
            fig = st.session_state.viz.create_standings_chart(standings_data, group)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"No standings data found for Group {group}")
    
    with col2:
        st.markdown(f"### 🎮 Group {group} Matches")
        matches = [m for m in st.session_state.engine.matches if m.stage == "group" and m.group == group]
        render_match_list(matches, key_prefix=f"grp_{group}")


def render_all_matches(stage: str = None):
    """Render all matches for a stage in a read-only summary table"""
    if stage:
        matches = st.session_state.engine.get_matches_by_stage(stage)
    else:
        matches = st.session_state.engine.matches
    
    if not matches:
        st.info("No matches found")
        return
    
    # Display as a summary table (read-only to avoid duplicate key issues)
    render_matches_table(matches)


def render_matches_table(matches):
    """Render matches as a read-only summary table"""
    st.markdown("### 📋 Match Schedule & Results")
    st.info("💡 To update match scores, go to the specific Group tab above.")
    
    match_data = []
    for match in matches:
        status_icon = TournamentConfig.VISUAL_INDICATORS.get(match.status, "")
        winner_icon = TournamentConfig.VISUAL_INDICATORS.get('win', '')
        
        # Format score display
        if match.status == "completed":
            t1_display = f"{winner_icon} " if match.winner_id == match.team1_id else ""
            t2_display = f"{winner_icon} " if match.winner_id == match.team2_id else ""
            score = f"{match.team1_score} - {match.team2_score}"
        else:
            t1_display = ""
            t2_display = ""
            score = "vs"
        
        # Format time
        time_str = match.scheduled_time.strftime('%H:%M') if match.scheduled_time else "-"
        
        match_data.append({
            "Match": f"#{match.match_id}",
            "Group": match.group or "-",
            "Time": time_str,
            "Team 1": f"{t1_display}{match.team1_name}",
            "Score": score,
            "Team 2": f"{t2_display}{match.team2_name}",
            "Status": f"{status_icon} {match.status.title()}"
        })
    
    df = pd.DataFrame(match_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_match_list(matches, key_prefix: str = "default"):
    """Render a list of matches with update capability
    
    Args:
        matches: List of Match objects to render
        key_prefix: Unique prefix to avoid duplicate widget keys when same matches are shown in multiple tabs
    """
    can_update = PermissionChecker.check_update_match()
    
    for match in matches:
        status_icon = TournamentConfig.VISUAL_INDICATORS.get(match.status, "")
        
        # Define keys outside the conditional blocks for consistent access
        t1_key = f"{key_prefix}_t1_{match.match_id}"
        t2_key = f"{key_prefix}_t2_{match.match_id}"
        update_key = f"{key_prefix}_update_{match.match_id}"
        
        with st.expander(
            f"{status_icon} Match {match.match_id}: {match.team1_name} vs {match.team2_name}",
            expanded=(match.status != "completed")
        ):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"**Stage:** {TournamentConfig.STAGES.get(match.stage, match.stage)}")
                if match.group:
                    st.markdown(f"**Group:** {match.group}")
                if match.scheduled_time:
                    st.markdown(f"**Time:** {match.scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                if match.status == "completed":
                    winner_indicator = TournamentConfig.VISUAL_INDICATORS['win']
                    t1_ind = winner_indicator if match.winner_id == match.team1_id else ""
                    t2_ind = winner_indicator if match.winner_id == match.team2_id else ""
                    
                    st.markdown(f"**{t1_ind} {match.team1_name}:** {match.team1_score}")
                    st.markdown(f"**{t2_ind} {match.team2_name}:** {match.team2_score}")
                    
                    if match.winner_name:
                        st.success(f"Winner: {match.winner_name}")
                else:
                    # Score input (editable only for admins)
                    if can_update:
                        st.markdown("**Enter Scores:**")
                        score_col1, score_col2 = st.columns(2)
                        
                        with score_col1:
                            st.number_input(
                                match.team1_name,
                                min_value=0,
                                max_value=100,
                                value=match.team1_score,
                                key=t1_key
                            )
                        
                        with score_col2:
                            st.number_input(
                                match.team2_name,
                                min_value=0,
                                max_value=100,
                                value=match.team2_score,
                                key=t2_key
                            )
                    else:
                        st.info("🔒 Only Admins can update match scores")
            
            with col3:
                if match.status != "completed" and can_update:
                    if st.button("✅ Update", key=update_key):
                        # Get values from session state and ensure they are integers
                        score1 = int(st.session_state.get(t1_key, 0))
                        score2 = int(st.session_state.get(t2_key, 0))
                        
                        st.session_state.engine.update_match_result(
                            match.match_id,
                            score1,
                            score2
                        )
                        save_tournament()
                        
                        # Log action
                        from user_manager import UserManager
                        user_manager = UserManager()
                        user = StreamlitAuthManager.get_current_user()
                        user_manager.log_action(user.email if user else None, f"Updated match {match.match_id} score to {score1}-{score2}")
                        
                        st.rerun()


def render_knockout_stage(stage: str):
    """Render knockout stage view"""
    stage_name = TournamentConfig.STAGES.get(stage, stage.title())
    st.markdown(f'<div class="main-header">🏆 {stage_name}</div>', unsafe_allow_html=True)
    
    matches = st.session_state.engine.get_matches_by_stage(stage)
    
    if not matches:
        st.info(f"No {stage_name.lower()} matches yet")
        return
    
    # Bracket visualization
    all_knockout = [m.to_dict() for m in st.session_state.engine.matches 
                    if m.stage in ['quarterfinal', 'semifinal', 'final']]
    if all_knockout:
        fig = st.session_state.viz.create_tournament_bracket(all_knockout)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Match cards
    render_match_list(matches, key_prefix=stage)
    
    # Check if stage is complete
    completed = all(m.status == "completed" for m in matches)
    
    if completed and matches:
        st.markdown("---")
        st.success(f"🎉 {stage_name} complete!")
        
        # Next stage button
        next_stage = None
        if stage == "quarterfinal":
            next_stage = ("semifinal", "Semi Finals", st.session_state.engine.generate_semifinals)
        elif stage == "semifinal":
            next_stage = ("final", "Final", st.session_state.engine.generate_final)
        
        if next_stage:
            if st.button(f"➡️ Generate {next_stage[1]}", type="primary"):
                next_stage[2]()
                # Schedule
                last_match = max(matches, key=lambda m: m.end_time if m.end_time else datetime.min)
                start = last_match.end_time + timedelta(minutes=30) if last_match.end_time else datetime.now()
                new_matches = st.session_state.engine.get_matches_by_stage(next_stage[0])
                st.session_state.engine.schedule_matches(start, new_matches)
                save_tournament()
                st.session_state.current_stage = next_stage[0]
                st.rerun()
        elif stage == "final":
            final_match = matches[0]
            if final_match.winner_name:
                st.balloons()
                st.markdown(f"## 🏆🎉 Champion: {final_match.winner_name}! 🎉🏆")


def render_nlp_interface():
    """Render NLP command interface"""
    st.markdown("### 💬 Natural Language Commands")
    
    st.info("""
    **Try commands like:**
    - "Update match 1 score to 3-2"
    - "Show standings for group A"
    - "Team Alpha info"
    - "Get all quarterfinal matches"
    """)
    
    command = st.text_input(
        "Enter your command:",
        placeholder="e.g., 'Show me the standings for group A'"
    )
    
    if command:
        # Prepare context
        context = {
            "teams": [t.to_dict() for t in st.session_state.engine.teams],
            "matches": [m.to_dict() for m in st.session_state.engine.matches]
        }
        
        # Process command
        result = st.session_state.nlp.process_command(command, context)
        
        st.markdown(f"**Understanding:** {result.get('message', 'Processing...')}")
        st.markdown(f"**Confidence:** {result.get('confidence', 0) * 100:.0f}%")
        
        action = result.get('action')
        params = result.get('params', {})
        
        if action == "UPDATE_SCORE":
            match_id = params.get('match_id')
            if match_id:
                st.session_state.engine.update_match_result(
                    match_id,
                    params.get('team1_score', 0),
                    params.get('team2_score', 0)
                )
                save_tournament()
                st.success("✅ Score updated!")
                st.rerun()
            else:
                st.warning("Please specify match ID")
        
        elif action == "GET_STANDINGS":
            group = params.get('group')
            standings = st.session_state.engine.get_group_standings(group)
            df = pd.DataFrame([s.to_dict() for s in standings])
            st.dataframe(df, use_container_width=True)
        
        elif action == "GET_MATCHES":
            stage = params.get('stage')
            if stage:
                matches = st.session_state.engine.get_matches_by_stage(stage)
            else:
                matches = st.session_state.engine.matches
            
            for m in matches:
                st.write(f"Match {m.match_id}: {m.team1_name} vs {m.team2_name} ({m.status})")
        
        elif action == "GET_TEAM_INFO":
            team_name = params.get('team_name')
            team = st.session_state.engine.get_team_by_name(team_name)
            if team:
                st.json(team.to_dict())
            else:
                st.warning(f"Team '{team_name}' not found")
        
        elif action == "UNKNOWN":
            st.warning(result.get('message', "Command not understood"))


def render_schedule_view():
    """Render schedule and timeline view"""
    st.markdown('<div class="main-header">📅 Tournament Schedule</div>', unsafe_allow_html=True)
    
    matches_data = [m.to_dict() for m in st.session_state.engine.matches]
    
    if not matches_data:
        st.info("No matches scheduled yet")
        return
    
    # Timeline visualization
    fig = st.session_state.viz.create_match_timeline(matches_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Schedule table
    df = pd.DataFrame(matches_data)
    df = df[['match_id', 'team1_name', 'team2_name', 'stage', 'scheduled_time', 'end_time', 'status']]
    df.columns = ['Match #', 'Team 1', 'Team 2', 'Stage', 'Start Time', 'End Time', 'Status']
    
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_analytics():
    """Render analytics and statistics page"""
    st.markdown('<div class="main-header">📈 Tournament Analytics</div>', unsafe_allow_html=True)
    
    if not st.session_state.engine.standings:
        st.info("No data available yet")
        return
    
    standings_data = [s.to_dict() for s in st.session_state.engine.standings.values()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Win/Loss chart
        fig = st.session_state.viz.create_win_loss_chart(standings_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Score difference chart
        fig = st.session_state.viz.create_score_difference_chart(standings_data)
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary metrics
    st.markdown("### 📊 Summary")
    
    total_matches = len(st.session_state.engine.matches)
    completed_matches = len([m for m in st.session_state.engine.matches if m.status == "completed"])
    total_teams = len(st.session_state.engine.teams)
    
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric("Total Teams", total_teams)
    
    with metric_cols[1]:
        st.metric("Total Matches", total_matches)
    
    with metric_cols[2]:
        st.metric("Completed", completed_matches)
    
    with metric_cols[3]:
        st.metric("Remaining", total_matches - completed_matches)


def render_admin_panel():
    """Render admin panel for user management"""
    st.markdown('<div class="main-header">⚙️ Admin Panel</div>', unsafe_allow_html=True)
    
    # Check if user is admin
    if not PermissionChecker.check_manage_users():
        st.error("❌ This page is only for Admins")
        return
    
    from user_manager import UserManager
    user_manager = UserManager()
    
    # Admin tabs
    admin_tabs = st.tabs(["👥 User Management", "📋 Audit Log"])
    
    with admin_tabs[0]:
        st.markdown("### 👥 Manage Users")
        
        # Get all users
        users = user_manager.get_all_users()
        current_user = StreamlitAuthManager.get_current_user()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    "Email": user.email,
                    "Name": user.name,
                    "Role": f"🔐 Admin" if user.is_admin() else "👁️ Viewer",
                    "Provider": user.provider.capitalize(),
                    "Joined": user.created_at[:10],
                    "Last Login": user.last_login[:10] if user.last_login else "-"
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            
            # Add new user section
            st.markdown("### ➕ Add New User")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                new_email = st.text_input("Email Address", placeholder="user@example.com", key="new_user_email")
            
            with col2:
                new_name = st.text_input("Display Name", placeholder="John Doe", key="new_user_name")
            
            with col3:
                new_role = st.selectbox("Role", options=["Viewer", "Admin"], key="new_user_role")
            
            if st.button("➕ Add User", key="add_new_user", use_container_width=True):
                if new_email and new_name:
                    # Check if user already exists
                    if any(u.email == new_email for u in users):
                        st.error(f"❌ User {new_email} already exists")
                    else:
                        # Add new user
                        role_lower = "admin" if new_role == "Admin" else "viewer"
                        if user_manager.register_user(
                            email=new_email,
                            name=new_name,
                            provider="manual",
                            provider_id="",
                            role=role_lower
                        ):
                            st.success(f"✅ User {new_email} added as {new_role}")
                            user_manager.log_action(current_user.email, f"Added new user {new_email} as {new_role}")
                            st.rerun()
                        else:
                            st.error("Failed to add user")
                else:
                    st.warning("⚠️ Please fill in Email and Display Name")
            
            st.markdown("---")
            
            # User management options
            st.markdown("### Change User Role")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                selected_email = st.selectbox(
                    "Select User",
                    options=[u.email for u in users if u.email != current_user.email],
                    placeholder="Choose a user to manage..."
                )
            
            if selected_email:
                selected_user = next((u for u in users if u.email == selected_email), None)
                
                with col2:
                    current_role = "Admin" if selected_user.is_admin() else "Viewer"
                    st.markdown(f"**Current Role:** {current_role}")
                
                with col3:
                    new_role = st.selectbox(
                        "New Role",
                        options=["Viewer", "Admin"],
                        index=1 if selected_user.is_admin() else 0,
                        key=f"role_select_{selected_email}"
                    )
                
                if st.button("✅ Update Role", key=f"update_role_{selected_email}"):
                    success = user_manager.promote_to_admin(selected_email) if new_role == "Admin" else user_manager.demote_to_viewer(selected_email)
                    
                    if success:
                        st.success(f"✅ {selected_user.name} is now a {new_role}")
                        user_manager.log_action(current_user.email, f"Updated {selected_email} role to {new_role}")
                        st.rerun()
                    else:
                        st.error("Failed to update user role")
                
                # Disable user option
                st.markdown("---")
                st.markdown("### Remove User Access")
                
                if st.button("🗑️ Disable User Account", key=f"disable_user_{selected_email}", type="secondary"):
                    if user_manager.disable_user(selected_email):
                        st.success(f"✅ {selected_email} has been disabled")
                        user_manager.log_action(current_user.email, f"Disabled user {selected_email}")
                        st.rerun()
                    else:
                        st.error("Failed to disable user")
        else:
            st.info("No users found")
    
    with admin_tabs[1]:
        st.markdown("### 📋 Audit Log")
        
        # Get audit log
        audit_log = user_manager.get_audit_log(limit=50)
        
        if audit_log:
            log_data = []
            for log_entry in audit_log:
                log_data.append({
                    "User": log_entry.get('User', "System"),
                    "Action": log_entry.get('Action', ""),
                    "Details": log_entry.get('Details', "-"),
                    "Time": log_entry.get('Timestamp', '')[:19] if log_entry.get('Timestamp') else "-"
                })
            
            df = pd.DataFrame(log_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Download audit log
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Audit Log (CSV)",
                csv,
                "audit_log.csv",
                "text/csv"
            )
        else:
            st.info("No audit log entries found")


def main():
    """Main application entry point"""
    init_session_state()
    render_sidebar()
    
    # Navigation
    if not st.session_state.tournament_initialized:
        render_setup_page()
    else:
        # Tab list
        tab_list = [
            "🎯 Group Stage",
            "🏆 Quarter Finals",
            "⚔️ Semi Finals",
            "👑 Final",
            "📅 Schedule",
            "📈 Analytics",
            "💬 NLP Commands"
        ]
        
        # Add admin tab if user is admin
        if PermissionChecker.check_manage_users():
            tab_list.append("⚙️ Admin")
        
        # Tab navigation
        tabs = st.tabs(tab_list)
        
        with tabs[0]:
            render_group_stage()
        
        with tabs[1]:
            render_knockout_stage("quarterfinal")
        
        with tabs[2]:
            render_knockout_stage("semifinal")
        
        with tabs[3]:
            render_knockout_stage("final")
        
        with tabs[4]:
            render_schedule_view()
        
        with tabs[5]:
            render_analytics()
        
        with tabs[6]:
            render_nlp_interface()
        
        # Admin tab (if user is admin)
        if PermissionChecker.check_manage_users():
            with tabs[7]:
                render_admin_panel()


if __name__ == "__main__":
    main()
