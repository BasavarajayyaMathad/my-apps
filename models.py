"""
Data Models for Tournament Management
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd


@dataclass
class Team:
    """Team data model"""
    team_id: int
    team_name: str
    participants: List[str]
    group: Optional[str] = None
    
    def to_dict(self):
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "participants": ", ".join(self.participants),
            "group": self.group
        }


@dataclass
class Match:
    """Match data model"""
    match_id: int
    team1_id: int
    team1_name: str
    team2_id: int
    team2_name: str
    stage: str
    group: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    team1_score: int = 0
    team2_score: int = 0
    winner_id: Optional[int] = None
    winner_name: Optional[str] = None
    status: str = "scheduled"
    
    def to_dict(self):
        return {
            "match_id": self.match_id,
            "team1_id": self.team1_id,
            "team1_name": self.team1_name,
            "team2_id": self.team2_id,
            "team2_name": self.team2_name,
            "stage": self.stage,
            "group": self.group,
            "scheduled_time": self.scheduled_time.strftime("%Y-%m-%d %H:%M") if self.scheduled_time else "",
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M") if self.end_time else "",
            "team1_score": self.team1_score,
            "team2_score": self.team2_score,
            "winner_id": self.winner_id,
            "winner_name": self.winner_name,
            "status": self.status
        }


@dataclass
class TeamStanding:
    """Team standing in tournament"""
    team_id: int
    team_name: str
    group: str
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    points: int = 0
    score_for: int = 0
    score_against: int = 0
    
    @property
    def score_difference(self):
        return self.score_for - self.score_against
    
    def to_dict(self):
        return {
            "team_id": self.team_id,
            "team_name": self.team_name,
            "group": self.group,
            "matches_played": self.matches_played,
            "wins": self.wins,
            "losses": self.losses,
            "draws": self.draws,
            "points": self.points,
            "score_for": self.score_for,
            "score_against": self.score_against,
            "score_difference": self.score_difference
        }
