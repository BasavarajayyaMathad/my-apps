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
    
    # Auto-load existing tournament if it exists and not yet loaded
    if not st.session_state.tournament_initialized:
        results_file = TournamentConfig.RESULTS_FILE
        if os.path.exists(results_file):
            try:
                if st.session_state.engine.load_from_excel(results_file):
                    st.session_state.tournament_initialized = True
                    st.session_state.current_stage = "group"
                    # Rebuild groups
                    st.session_state.groups = {}
                    for team in st.session_state.engine.teams:
                        if team.group not in st.session_state.groups:
                            st.session_state.groups[team.group] = []
                        st.session_state.groups[team.group].append(team)
            except Exception:
                # If loading fails, keep tournament_initialized as False
                pass


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
    
    # Rules of the Game section
    if st.sidebar.button("📖 View Rules of Game", use_container_width=True):
        st.session_state.show_rules = True
    
    st.sidebar.markdown("---")
    
    # NLP Status
    nlp_status = "🟢 Active" if st.session_state.nlp.is_available() else "🔴 Not configured"
    st.sidebar.markdown(f"**NLP Status:** {nlp_status}")
    
    if not st.session_state.nlp.is_available():
        st.sidebar.info("Add OPENAI_API_KEY to .env file to enable NLP features")


def render_rules_viewer():
    """Display Rules of the Game for all logged-in users"""
    import os
    
    rules_dir = "tournament_rules"
    
    # Check if rules directory exists and has files
    if not os.path.exists(rules_dir):
        st.info("📖 Rules of the Game document will be available here once uploaded by an admin.")
        return
    
    files = os.listdir(rules_dir)
    latest_files = [f for f in files if f.startswith("rules_latest")]
    
    if not latest_files:
        st.info("📖 Rules of the Game document will be available here once uploaded by an admin.")
        return
    
    latest_file = latest_files[0]
    rules_path = os.path.join(rules_dir, latest_file)
    file_size = os.path.getsize(rules_path) / 1024  # Size in KB
    
    st.markdown("### 📖 Rules of the Game")
    st.info(f"📄 **Document:** {latest_file.replace('rules_latest.', '').upper()} ({file_size:.1f} KB)")
    
    # Display preview for text files
    if latest_file.endswith(".txt"):
        try:
            with open(rules_path, 'r', encoding='utf-8', errors='ignore') as f:
                rules_content = f.read()
                st.text_area("Document Content:", value=rules_content, height=400, disabled=True)
        except:
            st.warning("Could not display text file content")
    else:
        st.markdown(f"**File Format:** {latest_file.split('.')[-1].upper()}")
        st.info("Use the Download button below to view this document")
    
    # Download button
    with open(rules_path, "rb") as f:
        st.download_button(
            label="📥 Download Rules Document",
            data=f.read(),
            file_name=latest_file.replace("rules_latest.", "Rules_of_Game."),
            mime="application/octet-stream",
            use_container_width=True
        )


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
        
        # Manual group assignment
        st.markdown("### 👥 Assign Teams to Groups")
        
        # Initialize session state for group assignments if not exists
        if 'group_assignments_session' not in st.session_state:
            st.session_state.group_assignments_session = {'A': [], 'B': [], 'C': [], 'D': []}
        
        # Initialize parallel matches config
        if 'parallel_matches' not in st.session_state:
            st.session_state.parallel_matches = 2
        
        num_groups = 4
        group_names = ['A', 'B', 'C', 'D']
        
        # Collect all already-assigned teams
        all_assigned_team_ids = []
        for team_ids in st.session_state.group_assignments_session.values():
            all_assigned_team_ids.extend(team_ids)
        
        # Create list of unassigned teams
        unassigned_teams = [t for t in st.session_state.engine.teams if t.team_id not in all_assigned_team_ids]
        unassigned_team_names = [t.team_name for t in unassigned_teams]
        
        # Dropdown View Only
        st.markdown("#### Select Teams by Group")
        
        cols = st.columns(num_groups)
        
        for col_idx, group_name in enumerate(group_names):
            with cols[col_idx]:
                st.markdown(f"#### Group {group_name}")
                
                # Get available teams for this group (exclude already selected)
                group_team_ids = st.session_state.group_assignments_session[group_name]
                available_for_group = [t for t in st.session_state.engine.teams 
                                     if t.team_id not in all_assigned_team_ids or t.team_id in group_team_ids]
                available_names = [t.team_name for t in available_for_group]
                
                # Current selection
                current_selection = [next((t.team_name for t in st.session_state.engine.teams 
                                          if t.team_id == tid), None) 
                                    for tid in group_team_ids]
                current_selection = [name for name in current_selection if name is not None]
                
                selected_teams = st.multiselect(
                    f"Group {group_name}",
                    options=available_names,
                    default=current_selection,
                    key=f"group_{group_name}_select",
                    help=f"Select teams for Group {group_name}"
                )
                
                # Update session state
                st.session_state.group_assignments_session[group_name] = [
                    next((t.team_id for t in st.session_state.engine.teams if t.team_name == team_name), None)
                    for team_name in selected_teams
                ]
                st.session_state.group_assignments_session[group_name] = [
                    tid for tid in st.session_state.group_assignments_session[group_name] if tid is not None
                ]
                
                # Clear button for individual group
                if st.button(f"🗑️ Clear Group {group_name}", key=f"clear_{group_name}", use_container_width=True):
                    st.session_state.group_assignments_session[group_name] = []
                    st.rerun()
        
        # Clear all groups button
        st.divider()
        if st.button("🗑️ Clear All Groups", type="secondary", use_container_width=True):
            st.session_state.group_assignments_session = {'A': [], 'B': [], 'C': [], 'D': []}
            st.rerun()
        
        st.divider()
        
        # Parallel matches configuration
        st.markdown("#### ⚡ Tournament Settings")
        st.session_state.parallel_matches = st.number_input(
            "Maximum matches running in parallel",
            min_value=1,
            max_value=10,
            value=st.session_state.parallel_matches,
            step=1,
            help="Number of boards/courts available. Duration = (total_matches / parallel) × match_duration"
        )
        
        st.divider()
        
        # Initialize tournament button
        if st.button("🚀 Initialize Tournament", type="primary", use_container_width=True):
            # Check if all teams are assigned
            all_assigned_teams = []
            for team_ids in st.session_state.group_assignments_session.values():
                all_assigned_teams.extend(team_ids)
            
            # Debug: Show what we're checking
            total_teams = len(st.session_state.engine.teams)
            assigned_teams = len(all_assigned_teams)
            unique_teams = len(set(all_assigned_teams))
            
            if assigned_teams != total_teams:
                st.error(f"❌ Please assign ALL teams to groups! ({assigned_teams}/{total_teams} assigned)")
            elif unique_teams != assigned_teams:
                st.error("❌ Each team can only be in one group!")
            elif unique_teams != total_teams:
                st.error(f"❌ Teams mismatch: {unique_teams} unique vs {total_teams} total")
            else:
                # Assign teams to groups
                st.session_state.groups = st.session_state.engine.assign_teams_to_groups(st.session_state.group_assignments_session)
                
                # Generate group stage fixtures
                st.session_state.engine.generate_group_stage_fixtures(st.session_state.groups)
                
                # Schedule matches with user-specified parallel matches
                st.session_state.engine.schedule_matches(st.session_state.start_time, parallel_matches=st.session_state.parallel_matches)
                
                # Save initial state
                save_tournament()
                
                st.session_state.tournament_initialized = True
                st.session_state.current_stage = "group"
                
                st.success("✅ Tournament initialized successfully!")
                st.rerun()


def render_group_stage():
    """Render group stage view"""
    st.markdown('<div class="main-header">📊 Group Stage</div>', unsafe_allow_html=True)
    
    # Refresh button
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        if st.button("🔄 Refresh Standings", use_container_width=True):
            # Reload tournament data from Excel file
            results_file = TournamentConfig.RESULTS_FILE
            if os.path.exists(results_file):
                try:
                    if st.session_state.engine.load_from_excel(results_file):
                        # Rebuild groups
                        st.session_state.groups = {}
                        for team in st.session_state.engine.teams:
                            if team.group not in st.session_state.groups:
                                st.session_state.groups[team.group] = []
                            st.session_state.groups[team.group].append(team)
                        st.success("✅ Standings refreshed successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error refreshing standings: {e}")
    
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
            st.plotly_chart(fig, use_container_width=True, key=f"standings_chart_{group}")
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
    
    if not matches:
        st.info("No matches found")
        return
    
    # Collapse/Expand buttons
    col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
    with col1:
        if st.button("📂 Expand All", key=f"{key_prefix}_expand_all", use_container_width=True):
            # Set all expanders to expanded state by adding to session state
            for match in matches:
                st.session_state[f"{key_prefix}_expander_{match.match_id}"] = True
            st.rerun()
    
    with col2:
        if st.button("📁 Collapse All", key=f"{key_prefix}_collapse_all", use_container_width=True):
            # Set all expanders to collapsed state
            for match in matches:
                st.session_state[f"{key_prefix}_expander_{match.match_id}"] = False
            st.rerun()
    
    st.divider()
    
    for match in matches:
        status_icon = TournamentConfig.VISUAL_INDICATORS.get(match.status, "")
        
        # Define keys outside the conditional blocks for consistent access
        t1_key = f"{key_prefix}_t1_{match.match_id}"
        t2_key = f"{key_prefix}_t2_{match.match_id}"
        update_key = f"{key_prefix}_update_{match.match_id}"
        expander_key = f"{key_prefix}_expander_{match.match_id}"
        
        # Determine if this expander should be expanded
        default_expanded = match.status != "completed"
        is_expanded = st.session_state.get(expander_key, default_expanded)
        
        with st.expander(
            f"{status_icon} Match {match.match_id}: {match.team1_name} vs {match.team2_name}",
            expanded=is_expanded
        ):
            # Match Information Section
            st.markdown("#### Match Information")
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                stage_name = TournamentConfig.STAGES.get(match.stage, match.stage)
                st.write(f"**Stage:** {stage_name}")
            
            with info_col2:
                if match.group:
                    st.write(f"**Group:** {match.group}")
            
            with info_col3:
                if match.scheduled_time:
                    time_str = match.scheduled_time.strftime('%Y-%m-%d %H:%M')
                    st.write(f"**Time:** {time_str}")
            
            st.divider()
            
            # Score and Winner Section
            if match.status == "completed":
                st.markdown("#### Current Result")
                
                winner_indicator = TournamentConfig.VISUAL_INDICATORS['win']
                t1_ind = winner_indicator if match.winner_id == match.team1_id else ""
                t2_ind = winner_indicator if match.winner_id == match.team2_id else ""
                
                # Display teams and scores clearly
                result_col1, result_col2, result_col3 = st.columns([1.5, 1, 1.5])
                
                with result_col1:
                    st.write(f"**{t1_ind} {match.team1_name}**")
                    st.markdown(f"### {match.team1_score}")
                
                with result_col2:
                    st.write("**vs**")
                
                with result_col3:
                    st.write(f"**{t2_ind} {match.team2_name}**")
                    st.markdown(f"### {match.team2_score}")
                
                if match.winner_name and match.winner_name != "Draw":
                    st.success(f"🏆 Winner: {match.winner_name}")
                elif match.winner_name == "Draw":
                    st.info("🤝 Result: Draw")
                
                if can_update:
                    st.divider()
                    st.markdown("#### Edit Match Result")
            else:
                if can_update:
                    st.markdown("#### Enter Match Result")
                else:
                    st.info("🔒 Only Admins can update match scores")
            
            # Update form (for both pending and completed matches if admin)
            if can_update:
                # Score inputs with clear team labels
                st.markdown("**Scores:**")
                
                score_col1, score_col2, score_col3 = st.columns([1.8, 1.8, 0.4])
                
                with score_col1:
                    st.write(f"**{match.team1_name}**")
                    score1 = st.number_input(
                        label=f"Score for {match.team1_name}",
                        min_value=0,
                        max_value=100,
                        value=match.team1_score,
                        key=t1_key,
                        label_visibility="collapsed"
                    )
                
                with score_col2:
                    st.write(f"**{match.team2_name}**")
                    score2 = st.number_input(
                        label=f"Score for {match.team2_name}",
                        min_value=0,
                        max_value=100,
                        value=match.team2_score,
                        key=t2_key,
                        label_visibility="collapsed"
                    )
                
                st.markdown("**Select Winner:**")
                winner_key = f"winner_{match.match_id}"
                winner_options = [
                    ("Draw", None),
                    (match.team1_name, match.team1_id),
                    (match.team2_name, match.team2_id)
                ]
                
                selected_winner_name = st.selectbox(
                    label="Winner",
                    options=[opt[0] for opt in winner_options],
                    key=winner_key,
                    index=0,
                    label_visibility="collapsed"
                )
                
                # Update button with better spacing
                st.markdown("")
                if st.button("✅ Update Match Result", key=update_key, use_container_width=True, type="primary"):
                    winner_id = next(
                        (opt[1] for opt in winner_options if opt[0] == selected_winner_name),
                        None
                    )
                    
                    st.session_state.engine.update_match_result(
                        match.match_id,
                        score1,
                        score2,
                        winner_id
                    )
                    save_tournament()
                    
                    # Log action
                    from user_manager import UserManager
                    user_manager = UserManager()
                    user = StreamlitAuthManager.get_current_user()
                    action_type = "Updated" if match.status == "completed" else "Recorded"
                    user_manager.log_action(user.email if user else None, f"{action_type} match {match.match_id} score to {score1}-{score2}, winner: {selected_winner_name}")
                    
                    st.success(f"✅ Match {match.match_id} updated successfully!")
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
                    if m.stage in ['quarterfinal', 'semifinal', 'final', 'third_place']]
    if all_knockout:
        fig = st.session_state.viz.create_tournament_bracket(all_knockout)
        if fig:
            st.plotly_chart(fig, use_container_width=True, key=f"bracket_{stage}")
    
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
            # Show final results
            final_matches = [m for m in matches if m.stage == "final"]
            third_place_matches = [m for m in matches if m.stage == "third_place"]
            
            if final_matches and final_matches[0].winner_name:
                st.balloons()
                
                # Get champion info
                champion = final_matches[0].winner_name
                runner_up = final_matches[0].team2_name if final_matches[0].winner_id == final_matches[0].team1_id else final_matches[0].team1_name
                
                st.markdown("---")
                st.markdown("### 🏆 TOURNAMENT FINAL RESULTS")
                st.markdown("---")
                
                # Create columns for podium display
                col1, col2, col3 = st.columns(3)
                
                # Runner-up (2nd place) - left
                with col1:
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    st.markdown("### 🥈 Runner-Up")
                    st.markdown(f"## {runner_up}")
                    st.markdown(f"Score: {final_matches[0].team2_score if final_matches[0].winner_id == final_matches[0].team1_id else final_matches[0].team1_score}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Champion - center
                with col2:
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    st.markdown("### 🥇 CHAMPION")
                    st.markdown(f"## {champion}")
                    st.markdown(f"Score: {final_matches[0].team1_score if final_matches[0].winner_id == final_matches[0].team1_id else final_matches[0].team2_score}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Third place - right
                with col3:
                    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
                    if third_place_matches and third_place_matches[0].winner_name:
                        st.markdown("### 🥉 Third Place")
                        st.markdown(f"## {third_place_matches[0].winner_name}")
                        st.markdown(f"Score: {third_place_matches[0].team1_score if third_place_matches[0].winner_id == third_place_matches[0].team1_id else third_place_matches[0].team2_score}")
                    else:
                        st.markdown("### 🥉 Third Place")
                        st.markdown("*Pending*")
                    st.markdown('</div>', unsafe_allow_html=True)
            elif not final_matches:
                st.info("Final match not yet generated")
            elif not final_matches[0].winner_name:
                st.info("Final match result pending")



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
                # NLP commands only update scores; winner must be set via UI
                st.session_state.engine.update_match_result(
                    match_id,
                    params.get('team1_score', 0),
                    params.get('team2_score', 0),
                    winner_id=None  # NLP doesn't specify winner - this marks as draw
                )
                save_tournament()
                st.warning("⚠️ Score updated but winner marked as Draw. Please use the UI to explicitly select the match winner.")
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
        st.plotly_chart(fig, use_container_width=True, key="match_timeline")
    
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
        st.plotly_chart(fig, use_container_width=True, key="win_loss_chart")
    
    with col2:
        # Score difference chart
        fig = st.session_state.viz.create_score_difference_chart(standings_data)
        st.plotly_chart(fig, use_container_width=True, key="score_diff_chart")
    
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


def load_payment_data():
    """Load payment data from JSON file"""
    import json
    payment_file = "users_paid.json"
    if os.path.exists(payment_file):
        try:
            with open(payment_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_payment_data(data):
    """Save payment data to JSON file"""
    import json
    payment_file = "users_paid.json"
    try:
        with open(payment_file, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving payment data: {e}")
        return False


def render_export_data():
    """Render data export interface"""
    st.markdown('<div class="main-header">📥 Export Tournament Data</div>', unsafe_allow_html=True)
    
    if not st.session_state.tournament_initialized:
        st.warning("⚠️ Tournament not initialized yet!")
        return
    
    st.markdown("### Export Options")
    export_type = st.selectbox(
        "Select data to export",
        ["Groups", "Group Fixtures", "Standings", "All Matches", "Knockouts", "Complete Tournament"]
    )
    
    file_format = st.selectbox("File format", ["CSV", "Excel"])
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📥 Export", use_container_width=True, type="primary"):
            try:
                import pandas as pd
                from io import BytesIO
                
                data_exported = False
                
                if export_type == "Groups":
                    # Export groups and teams
                    data = []
                    for group_name, teams in st.session_state.groups.items():
                        for team in teams:
                            data.append({
                                'Group': group_name,
                                'Team ID': team.team_id,
                                'Team Name': team.team_name,
                                'Members': team.members_count if hasattr(team, 'members_count') else 'N/A'
                            })
                    df = pd.DataFrame(data)
                    data_exported = True
                    
                elif export_type == "Group Fixtures":
                    # Export only group stage matches
                    data = []
                    group_matches = [m for m in st.session_state.engine.matches if m.stage == "group"]
                    for match in group_matches:
                        data.append({
                            'Match ID': match.match_id,
                            'Group': match.group if match.group else 'N/A',
                            'Team 1': match.team1_name,
                            'Team 2': match.team2_name,
                            'Scheduled Time': match.scheduled_time.strftime('%d-%b-%Y %H:%M') if match.scheduled_time else 'N/A',
                            'Status': match.status,
                            'Winner': match.winner_name if match.winner_name else 'Pending'
                        })
                    df = pd.DataFrame(data)
                    data_exported = True
                    
                elif export_type == "Standings":
                    # Export group standings
                    data = []
                    
                    # Get all standings grouped by group
                    groups = set(s.group for s in st.session_state.engine.standings.values() if s.group)
                    
                    for group in sorted(groups):
                        group_standings = st.session_state.engine.get_group_standings(group)
                        for idx, standing in enumerate(group_standings, 1):
                            data.append({
                                'Group': group,
                                'Rank': idx,
                                'Team': standing.team_name,
                                'Played': standing.matches_played,
                                'Won': standing.wins,
                                'Drawn': standing.draws,
                                'Lost': standing.losses,
                                'Points': standing.points
                            })
                    df = pd.DataFrame(data)
                    data_exported = True
                    
                elif export_type == "All Matches":
                    # Export all matches
                    data = []
                    for match in st.session_state.engine.matches:
                        data.append({
                            'Match ID': match.match_id,
                            'Stage': match.stage,
                            'Team 1': match.team1_name,
                            'Team 2': match.team2_name,
                            'Scheduled Time': match.scheduled_time.strftime('%d-%b-%Y %H:%M') if match.scheduled_time else 'N/A',
                            'Status': match.status,
                            'Team 1 Score': match.team1_score if match.team1_score is not None else '-',
                            'Team 2 Score': match.team2_score if match.team2_score is not None else '-',
                            'Winner': match.winner_name if match.winner_name else 'Pending'
                        })
                    df = pd.DataFrame(data)
                    data_exported = True
                    
                elif export_type == "Knockouts":
                    # Export knockout stage matches only
                    data = []
                    knockout_matches = [m for m in st.session_state.engine.matches if m.stage != "group"]
                    for match in knockout_matches:
                        data.append({
                            'Stage': match.stage.upper(),
                            'Match ID': match.match_id,
                            'Team 1': match.team1_name,
                            'Team 2': match.team2_name,
                            'Scheduled Time': match.scheduled_time.strftime('%d-%b-%Y %H:%M') if match.scheduled_time else 'N/A',
                            'Status': match.status,
                            'Team 1 Score': match.team1_score if match.team1_score is not None else '-',
                            'Team 2 Score': match.team2_score if match.team2_score is not None else '-',
                            'Winner': match.winner_name if match.winner_name else 'Pending'
                        })
                    df = pd.DataFrame(data)
                    data_exported = True
                    
                elif export_type == "Complete Tournament":
                    # Export everything
                    # This will return a dict with multiple sheets
                    export_dict = {}
                    
                    # Groups
                    groups_data = []
                    for group_name, teams in st.session_state.groups.items():
                        for team in teams:
                            groups_data.append({
                                'Group': group_name,
                                'Team Name': team.team_name,
                                'Members': team.members_count if hasattr(team, 'members_count') else 'N/A'
                            })
                    export_dict['Groups'] = pd.DataFrame(groups_data)
                    
                    # All Matches
                    matches_data = []
                    for match in st.session_state.engine.matches:
                        matches_data.append({
                            'Stage': match.stage,
                            'Team 1': match.team1_name,
                            'Team 2': match.team2_name,
                            'Time': match.scheduled_time.strftime('%d-%b-%Y %H:%M') if match.scheduled_time else 'N/A',
                            'Status': match.status,
                            'Score 1': match.team1_score if match.team1_score is not None else '-',
                            'Score 2': match.team2_score if match.team2_score is not None else '-',
                            'Winner': match.winner_name if match.winner_name else 'Pending'
                        })
                    export_dict['Matches'] = pd.DataFrame(matches_data)
                    
                    # Standings
                    standings_data = []
                    groups = set(s.group for s in st.session_state.engine.standings.values() if s.group)
                    
                    for group in sorted(groups):
                        group_standings = st.session_state.engine.get_group_standings(group)
                        for idx, standing in enumerate(group_standings, 1):
                            standings_data.append({
                                'Group': group,
                                'Rank': idx,
                                'Team': standing.team_name,
                                'Wins': standing.wins,
                                'Draws': standing.draws,
                                'Losses': standing.losses,
                                'Points': standing.points
                            })
                    export_dict['Standings'] = pd.DataFrame(standings_data)
                    
                    # Export to Excel with multiple sheets
                    if file_format == "Excel":
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            for sheet_name, df in export_dict.items():
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                        output.seek(0)
                        st.download_button(
                            label="📥 Download Excel File",
                            data=output.getvalue(),
                            file_name=f"tournament_complete_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        # CSV format - multiple files
                        st.info("Complete tournament export in CSV format includes multiple files (Groups, Matches, Standings)")
                        for sheet_name, df in export_dict.items():
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label=f"📥 Download {sheet_name}",
                                data=csv,
                                file_name=f"{sheet_name.lower()}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    data_exported = True
                
                if data_exported and export_type != "Complete Tournament":
                    # For single-sheet exports
                    if file_format == "Excel":
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, sheet_name='Data', index=False)
                        output.seek(0)
                        st.download_button(
                            label="📥 Download Excel File",
                            data=output.getvalue(),
                            file_name=f"{export_type.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV File",
                            data=csv,
                            file_name=f"{export_type.lower().replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    
                    st.success(f"✅ {export_type} exported successfully!")
                    
            except ImportError:
                st.error("❌ pandas or openpyxl not installed. Install with: pip install pandas openpyxl")
            except Exception as e:
                st.error(f"❌ Error exporting data: {e}")
    
    with export_col2:
        st.info("""
        **Export Formats:**
        - **CSV**: Good for spreadsheets and data analysis
        - **Excel**: Better formatting and multiple sheets
        """)


def render_payment_tracking():
    """Render payment tracking tab for participants"""
    st.markdown("### 💰 Participant Payment Tracking")
    
    # Get all unique participants from teams
    participants_set = set()
    for team in st.session_state.engine.teams:
        participants_set.update(team.participants)
    
    participants_list = sorted(list(participants_set))
    
    if not participants_list:
        st.info("No participants found. Please initialize the tournament first.")
        return
    
    # Load existing payment data
    payment_data = load_payment_data()
    
    # Create a dataframe for display
    payment_records = []
    for participant in participants_list:
        is_paid = payment_data.get(participant, False)
        payment_records.append({
            "Participant": participant,
            "Paid": is_paid
        })
    
    st.markdown("#### Participant Payment Status")
    
    # Display with checkboxes
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Name**")
    with col2:
        st.markdown("**Paid** ✓")
    
    st.divider()
    
    # Create checkboxes for each participant
    updated_payment_data = {}
    for idx, participant in enumerate(participants_list):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(participant)
        
        with col2:
            is_paid = st.checkbox(
                label="Paid",
                value=payment_data.get(participant, False),
                key=f"payment_{participant}",
                label_visibility="collapsed"
            )
            updated_payment_data[participant] = is_paid
    
    st.divider()
    
    # Save button
    if st.button("💾 Save Payment Status", type="primary", use_container_width=True):
        if save_payment_data(updated_payment_data):
            st.success("✅ Payment status saved successfully!")
            
            # Log action
            from user_manager import UserManager
            user_manager = UserManager()
            user = StreamlitAuthManager.get_current_user()
            paid_count = sum(1 for v in updated_payment_data.values() if v)
            user_manager.log_action(user.email if user else None, f"Updated payment status: {paid_count}/{len(participants_list)} participants paid")
            
            st.rerun()
    
    # Display summary
    st.markdown("---")
    st.markdown("#### Summary")
    
    paid_count = sum(1 for v in updated_payment_data.values() if v)
    total_count = len(participants_list)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Participants", total_count)
    
    with col2:
        st.metric("Paid", paid_count)
    
    with col3:
        st.metric("Pending", total_count - paid_count)
    
    # Pending payments list
    if total_count - paid_count > 0:
        st.markdown("#### Pending Payments")
        pending = [p for p in participants_list if not updated_payment_data.get(p, False)]
        for p in pending:
            st.write(f"• {p}")
    
    # Export payment data
    st.markdown("---")
    st.markdown("#### Export Payment Data")
    
    export_df = pd.DataFrame([
        {"Participant": p, "Status": "Paid" if updated_payment_data.get(p, False) else "Pending"}
        for p in participants_list
    ])
    
    csv = export_df.to_csv(index=False)
    st.download_button(
        "📥 Download Payment Report (CSV)",
        csv,
        "payment_report.csv",
        "text/csv"
    )


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
    admin_tabs = st.tabs(["👥 User Management", "💰 Payments", "📋 Audit Log", "📖 Rules of Game"])
    
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
        render_payment_tracking()
    
    with admin_tabs[2]:
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
    
    with admin_tabs[3]:
        st.markdown("### 📖 Rules of Game Management")
        
        import os
        rules_dir = "tournament_rules"
        if not os.path.exists(rules_dir):
            os.makedirs(rules_dir)
        
        # File upload section
        st.markdown("#### 📤 Upload Rules Document")
        
        uploaded_file = st.file_uploader(
            "Upload Rules of the Game (PDF, DOCX, TXT)",
            type=["pdf", "docx", "doc", "txt", "xlsx", "xls"],
            key="rules_upload"
        )
        
        if uploaded_file is not None:
            if st.button("💾 Save Rules Document", type="primary", use_container_width=True):
                try:
                    # Save file to rules directory with timestamp
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = uploaded_file.name.split('.')[-1]
                    saved_filename = f"rules_{timestamp}.{file_extension}"
                    rules_path = os.path.join(rules_dir, saved_filename)
                    
                    # Save the uploaded file
                    with open(rules_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Create a symlink to "rules_latest" for quick access
                    latest_path = os.path.join(rules_dir, f"rules_latest.{file_extension}")
                    if os.path.exists(latest_path):
                        os.remove(latest_path)
                    
                    # On Windows, create a copy instead of symlink
                    import shutil
                    shutil.copy(rules_path, latest_path)
                    
                    st.success(f"✅ Rules document saved successfully: {uploaded_file.name}")
                    user_manager.log_action(
                        StreamlitAuthManager.get_current_user().email if StreamlitAuthManager.get_current_user() else "Admin",
                        "Uploaded new Rules of Game document",
                        f"File: {uploaded_file.name}"
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving file: {e}")
        
        st.divider()
        
        # Current rules document
        st.markdown("#### 📄 Current Rules Document")
        
        # Find latest rules file
        if os.path.exists(rules_dir):
            files = os.listdir(rules_dir)
            latest_files = [f for f in files if f.startswith("rules_latest")]
            
            if latest_files:
                latest_file = latest_files[0]
                rules_path = os.path.join(rules_dir, latest_file)
                file_size = os.path.getsize(rules_path) / 1024  # Size in KB
                
                st.info(f"📄 **{latest_file}** ({file_size:.1f} KB)")
                
                # Display preview for text files
                if latest_file.endswith(".txt"):
                    try:
                        with open(rules_path, 'r', encoding='utf-8', errors='ignore') as f:
                            rules_content = f.read()
                            st.text_area("Document Preview:", value=rules_content, height=300, disabled=True)
                    except:
                        st.warning("Could not preview text file")
                
                # Download button
                with open(rules_path, "rb") as f:
                    st.download_button(
                        label="📥 Download Current Rules",
                        data=f.read(),
                        file_name=latest_file,
                        mime="application/octet-stream",
                        use_container_width=True
                    )
                
                st.divider()
                
                # Version history
                st.markdown("#### 📋 Version History")
                all_rules_files = sorted([f for f in files if f.startswith("rules_") and not f.startswith("rules_latest")], reverse=True)
                
                if all_rules_files:
                    history_data = []
                    for file in all_rules_files[:10]:  # Show last 10 versions
                        file_path = os.path.join(rules_dir, file)
                        file_size = os.path.getsize(file_path) / 1024
                        history_data.append({
                            "Version": file,
                            "Size (KB)": f"{file_size:.1f}",
                        })
                    
                    history_df = pd.DataFrame(history_data)
                    st.dataframe(history_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No previous versions found")
            else:
                st.warning("⚠️ No rules document has been uploaded yet")
        else:
            st.warning("⚠️ No rules document has been uploaded yet")


def main():
    """Main application entry point"""
    init_session_state()
    render_sidebar()
    
    # Check if show_rules flag is set
    if st.session_state.get('show_rules', False):
        st.markdown('<div class="main-header">📖 Rules of the Game</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([10, 1])
        with col2:
            if st.button("✕", help="Close Rules"):
                st.session_state.show_rules = False
                st.rerun()
        
        render_rules_viewer()
        st.markdown("---")
        return
    
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
            "� Export Data",
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
            render_export_data()
        
        with tabs[7]:
            render_nlp_interface()
        
        # Admin tab (if user is admin)
        if PermissionChecker.check_manage_users():
            with tabs[8]:
                render_admin_panel()


if __name__ == "__main__":
    main()
