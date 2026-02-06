"""
Tournament Configuration Module
Easy to modify settings for any sport tournament
"""

import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# TOURNAMENT SETTINGS - EASY TO MODIFY
# =============================================================================

class TournamentConfig:
    """Configuration class for tournament settings"""
    
    # Sport Name
    SPORT_NAME = "AP Carrom Tournament 2026"
    
    # Match Duration in minutes
    MATCH_DURATION_MINUTES = int(os.getenv("MATCH_DURATION_MINUTES", 20))
    
    # Points System
    POINTS_PER_WIN = int(os.getenv("POINTS_PER_WIN", 2))
    POINTS_PER_DRAW = 1
    POINTS_PER_LOSS = 0
    
    # Group Stage Settings
    NUMBER_OF_GROUPS = 2  # Divide teams into N groups (2 or 4)
    TOTAL_QUALIFIERS_FOR_KNOCKOUT = 8  # Total teams that qualify for knockout stage
    
    @classmethod
    def get_top_teams_per_group(cls):
        """Calculate how many teams qualify from each group
        - If 2 groups: Top 4 from each group (8 total)
        - If 4 groups: Top 2 from each group (8 total)
        """
        return cls.TOTAL_QUALIFIERS_FOR_KNOCKOUT // cls.NUMBER_OF_GROUPS
    
    # TOP_TEAMS_FROM_GROUP is now calculated dynamically via get_top_teams_per_group()
    
    # Tournament Stages
    STAGES = {
        "group": "Group Stage (Round Robin)",
        "quarterfinal": "Quarter Finals",
        "semifinal": "Semi Finals",
        "final": "Final"
    }
    
    # Match Status Options
    MATCH_STATUS = {
        "scheduled": "Scheduled",
        "in_progress": "In Progress",
        "completed": "Completed",
        "cancelled": "Cancelled"
    }
    
    # Visual Indicators (Emojis/Colors)
    VISUAL_INDICATORS = {
        "win": "🏆",
        "loss": "❌",
        "draw": "🤝",
        "scheduled": "📅",
        "in_progress": "🔴",
        "completed": "✅",
        "cancelled": "🚫"
    }
    
    # Colors for UI
    COLORS = {
        "win": "#28a745",
        "loss": "#dc3545",
        "draw": "#ffc107",
        "primary": "#007bff",
        "secondary": "#6c757d"
    }
    
    # Excel File Names
    TEAMS_FILE = "teams_input.xlsx"
    RESULTS_FILE = "tournament_results.xlsx"
    
    # Excel Sheet Names
    SHEETS = {
        "teams": "Teams",
        "fixtures": "Fixtures",
        "standings": "Standings",
        "match_results": "Match Results"
    }
    
    # LLM Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = "gpt-3.5-turbo"
    
    # User Authentication Settings
    INITIAL_ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "")
    SESSION_TIMEOUT_DAYS = 30
    
    @classmethod
    def get_stage_display_name(cls, stage_key):
        return cls.STAGES.get(stage_key, stage_key)
    
    @classmethod
    def get_status_indicator(cls, status):
        return cls.VISUAL_INDICATORS.get(status, "")
