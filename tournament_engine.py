"""
Tournament Engine - Core Logic for Tournament Management
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from itertools import combinations
import pandas as pd

from config import TournamentConfig
from models import Team, Match, TeamStanding


class TournamentEngine:
    """Main engine for tournament operations"""
    
    def __init__(self):
        self.config = TournamentConfig()
        self.teams: List[Team] = []
        self.matches: List[Match] = []
        self.standings: Dict[int, TeamStanding] = {}
    
    def recalculate_all_standings(self):
        """Recalculate all standings from scratch based on completed matches.
        This ensures standings are always accurate after any changes."""
        
        # First, ensure all teams have standings entries
        for team in self.teams:
            if team.team_id not in self.standings:
                self.standings[team.team_id] = TeamStanding(
                    team_id=team.team_id,
                    team_name=team.team_name,
                    group=team.group
                )
        
        # Reset all standings to zero
        for team_id, standing in self.standings.items():
            standing.matches_played = 0
            standing.wins = 0
            standing.losses = 0
            standing.draws = 0
            standing.points = 0
            standing.score_for = 0
            standing.score_against = 0
            standing.tiebreaker_score_for = 0
            standing.tiebreaker_score_against = 0
        
        # Recalculate from all completed matches
        for match in self.matches:
            if match.status == "completed":
                self._update_standings(match)
        
    def load_teams_from_excel(self, file_path: str) -> List[Team]:
        """Load teams from Excel file"""
        df = pd.read_excel(file_path)
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        teams = []
        for idx, row in df.iterrows():
            team_name = row.get('team_name', row.get('team', row.get('name', f'Team {idx + 1}')))
            
            # Handle participants - could be in single column or multiple columns
            if 'participants' in df.columns:
                participants = str(row['participants']).split(',')
            else:
                # Look for participant columns
                participant_cols = [col for col in df.columns if 'participant' in col or 'player' in col or 'member' in col]
                if participant_cols:
                    participants = [str(row[col]) for col in participant_cols if pd.notna(row[col])]
                else:
                    participants = [team_name]
            
            participants = [p.strip() for p in participants if p.strip() and p.strip().lower() != 'nan']
            
            team = Team(
                team_id=idx + 1,
                team_name=str(team_name).strip(),
                participants=participants
            )
            teams.append(team)
        
        self.teams = teams
        return teams
    
    def load_teams_from_dataframe(self, df: pd.DataFrame) -> List[Team]:
        """Load teams from pandas DataFrame"""
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        teams = []
        for idx, row in df.iterrows():
            team_name = row.get('team_name', row.get('team', row.get('name', f'Team {idx + 1}')))
            
            if 'participants' in df.columns:
                participants = str(row['participants']).split(',')
            else:
                participant_cols = [col for col in df.columns if 'participant' in col or 'player' in col or 'member' in col]
                if participant_cols:
                    participants = [str(row[col]) for col in participant_cols if pd.notna(row[col])]
                else:
                    participants = [team_name]
            
            participants = [p.strip() for p in participants if p.strip() and p.strip().lower() != 'nan']
            
            team = Team(
                team_id=idx + 1,
                team_name=str(team_name).strip(),
                participants=participants
            )
            teams.append(team)
        
        self.teams = teams
        return teams
    
    def divide_into_groups(self, shuffle: bool = True) -> Dict[str, List[Team]]:
        """Divide teams into groups randomly"""
        teams_copy = self.teams.copy()
        
        if shuffle:
            random.shuffle(teams_copy)
        
        groups = {}
        num_groups = self.config.NUMBER_OF_GROUPS
        group_names = [chr(65 + i) for i in range(num_groups)]  # A, B, C, ...
        
        for i, team in enumerate(teams_copy):
            group_idx = i % num_groups
            group_name = group_names[group_idx]
            team.group = group_name
            
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(team)
        
        # Initialize standings
        for team in self.teams:
            self.standings[team.team_id] = TeamStanding(
                team_id=team.team_id,
                team_name=team.team_name,
                group=team.group
            )
        
        return groups
    
    def generate_round_robin_fixtures(self, teams: List[Team], stage: str = "group", match_id_start: int = 1) -> List[Match]:
        """Generate round robin fixtures for a group of teams
        
        Args:
            teams: List of teams to generate fixtures for
            stage: Tournament stage (e.g., "group", "quarterfinal")
            match_id_start: Starting match ID to use
            
        Returns:
            List of Match objects
        """
        matches = []
        
        for i, (team1, team2) in enumerate(combinations(teams, 2)):
            match = Match(
                match_id=match_id_start + i,
                team1_id=team1.team_id,
                team1_name=team1.team_name,
                team2_id=team2.team_id,
                team2_name=team2.team_name,
                stage=stage,
                group=team1.group
            )
            matches.append(match)
        
        return matches
    
    def generate_group_stage_fixtures(self, groups: Dict[str, List[Team]]) -> List[Match]:
        """Generate all group stage fixtures"""
        all_matches = []
        current_match_id = 1  # Start from 1
        
        for group_name, teams in sorted(groups.items()):  # Sort to ensure consistent ordering
            group_matches = self.generate_round_robin_fixtures(teams, stage="group", match_id_start=current_match_id)
            all_matches.extend(group_matches)
            current_match_id += len(group_matches)  # Increment for next group
        
        self.matches = all_matches
        return all_matches
    
    def schedule_matches(self, start_time: datetime, matches: List[Match] = None, parallel_matches: int = 1) -> List[Match]:
        """
        Schedule matches with start and end times
        
        Args:
            start_time: Tournament start datetime
            matches: List of matches to schedule (defaults to all matches)
            parallel_matches: Number of matches running in parallel (default 1, can be 2 or more)
        """
        if matches is None:
            matches = self.matches
        
        current_time = start_time
        match_index = 0
        
        while match_index < len(matches):
            # Schedule up to parallel_matches matches at the same time
            for _ in range(parallel_matches):
                if match_index < len(matches):
                    match = matches[match_index]
                    match.scheduled_time = current_time
                    match.end_time = current_time + timedelta(minutes=self.config.MATCH_DURATION_MINUTES)
                    match_index += 1
            
            # Move to next time slot after all parallel matches end
            current_time = current_time + timedelta(minutes=self.config.MATCH_DURATION_MINUTES)
        
        return matches
    
    def update_match_result(self, match_id: int, team1_score: int, team2_score: int, winner_id: Optional[int] = None) -> Match:
        """Update match result and standings
        
        Args:
            match_id: ID of the match to update
            team1_score: Score for team 1 (used for tiebreaker only)
            team2_score: Score for team 2 (used for tiebreaker only)
            winner_id: ID of the winning team (optional). If None, match is marked as draw.
                      This is independent of scores and determines who gets 2 points.
        
        Returns:
            Updated Match object
        """
        match = next((m for m in self.matches if m.match_id == match_id), None)
        
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        match.team1_score = team1_score
        match.team2_score = team2_score
        match.status = "completed"
        
        # Set winner based on winner_id parameter, not score comparison
        if winner_id == match.team1_id:
            match.winner_id = match.team1_id
            match.winner_name = match.team1_name
        elif winner_id == match.team2_id:
            match.winner_id = match.team2_id
            match.winner_name = match.team2_name
        else:
            # No explicit winner means draw
            match.winner_id = None
            match.winner_name = "Draw"
        
        # Recalculate ALL standings from scratch to ensure accuracy
        self.recalculate_all_standings()
        
        return match
    
    def _update_standings(self, match: Match):
        """Update team standings after a match
        
        Note: 
        - winner_id determines match winner (2 points awarded)
        - Scores are tracked separately for tiebreaking purposes
        - If teams have equal points, tiebreaker_score_difference is used
        """
        team1_standing = self.standings.get(match.team1_id)
        team2_standing = self.standings.get(match.team2_id)
        
        if team1_standing:
            team1_standing.matches_played += 1
            # Always add scores to both regular and tiebreaker tracking
            team1_standing.score_for += match.team1_score
            team1_standing.score_against += match.team2_score
            team1_standing.tiebreaker_score_for += match.team1_score
            team1_standing.tiebreaker_score_against += match.team2_score
            
            # Winner points are based on winner_id, not on score comparison
            if match.winner_id == match.team1_id:
                team1_standing.wins += 1
                team1_standing.points += self.config.POINTS_PER_WIN
            elif match.winner_id == match.team2_id:
                team1_standing.losses += 1
                team1_standing.points += self.config.POINTS_PER_LOSS
            else:
                team1_standing.draws += 1
                team1_standing.points += self.config.POINTS_PER_DRAW
        
        if team2_standing:
            team2_standing.matches_played += 1
            # Always add scores to both regular and tiebreaker tracking
            team2_standing.score_for += match.team2_score
            team2_standing.score_against += match.team1_score
            team2_standing.tiebreaker_score_for += match.team2_score
            team2_standing.tiebreaker_score_against += match.team1_score
            
            # Winner points are based on winner_id, not on score comparison
            if match.winner_id == match.team2_id:
                team2_standing.wins += 1
                team2_standing.points += self.config.POINTS_PER_WIN
            elif match.winner_id == match.team1_id:
                team2_standing.losses += 1
                team2_standing.points += self.config.POINTS_PER_LOSS
            else:
                team2_standing.draws += 1
                team2_standing.points += self.config.POINTS_PER_DRAW
    
    def get_group_standings(self, group: str = None) -> List[TeamStanding]:
        """Get standings for a group or all teams
        
        Sorting criteria (in order):
        1. Points (higher is better) - Winner is based on match winner, not score
        2. Tiebreaker score difference (higher is better) - Used only when points are equal
        3. Tiebreaker score for (higher is better) - Used only when points and score diff are equal
        """
        standings_list = list(self.standings.values())
        
        if group:
            standings_list = [s for s in standings_list if s.group == group]
        
        # Sort by points first, then use tiebreaker scores if points are equal
        standings_list.sort(key=lambda x: (-x.points, -x.tiebreaker_score_difference, -x.tiebreaker_score_for))
        
        return standings_list
    
    def get_top_teams_from_groups(self) -> Dict[str, List[TeamStanding]]:
        """Get top N teams from each group based on number of groups
        - 2 groups: Top 4 from each (8 total for quarterfinals)
        - 4 groups: Top 2 from each (8 total for quarterfinals)
        """
        groups = set(team.group for team in self.teams if team.group)
        top_teams = {}
        
        # Calculate how many teams qualify from each group
        top_n = self.config.get_top_teams_per_group()
        
        for group in groups:
            group_standings = self.get_group_standings(group)
            top_teams[group] = group_standings[:top_n]
        
        return top_teams
    
    def generate_knockout_fixtures(self, qualified_teams: List[Team], stage: str) -> List[Match]:
        """Generate knockout stage fixtures"""
        matches = []
        match_id_start = len(self.matches) + 1
        
        # Pair teams (1st vs last, 2nd vs second last, etc.)
        num_teams = len(qualified_teams)
        for i in range(num_teams // 2):
            team1 = qualified_teams[i]
            team2 = qualified_teams[num_teams - 1 - i]
            
            match = Match(
                match_id=match_id_start + i,
                team1_id=team1.team_id,
                team1_name=team1.team_name,
                team2_id=team2.team_id,
                team2_name=team2.team_name,
                stage=stage,
                group=None
            )
            matches.append(match)
        
        self.matches.extend(matches)
        return matches
    
    def generate_quarterfinals(self) -> List[Match]:
        """Generate quarterfinal fixtures from group stage qualifiers"""
        top_teams = self.get_top_teams_from_groups()
        
        # Flatten and get Team objects
        qualified = []
        for group, standings in sorted(top_teams.items()):
            for standing in standings:
                team = next((t for t in self.teams if t.team_id == standing.team_id), None)
                if team:
                    qualified.append(team)
        
        return self.generate_knockout_fixtures(qualified, "quarterfinal")
    
    def generate_semifinals(self) -> List[Match]:
        """Generate semifinal fixtures from quarterfinal winners"""
        qf_matches = [m for m in self.matches if m.stage == "quarterfinal" and m.status == "completed"]
        
        winners = []
        for match in qf_matches:
            if match.winner_id:
                team = next((t for t in self.teams if t.team_id == match.winner_id), None)
                if team:
                    winners.append(team)
        
        return self.generate_knockout_fixtures(winners, "semifinal")
    
    def generate_final(self) -> List[Match]:
        """Generate final fixture from semifinal winners"""
        sf_matches = [m for m in self.matches if m.stage == "semifinal" and m.status == "completed"]
        
        winners = []
        for match in sf_matches:
            if match.winner_id:
                team = next((t for t in self.teams if t.team_id == match.winner_id), None)
                if team:
                    winners.append(team)
        
        return self.generate_knockout_fixtures(winners, "final")
    
    def get_matches_by_stage(self, stage: str) -> List[Match]:
        """Get all matches for a specific stage"""
        return [m for m in self.matches if m.stage == stage]
    
    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        """Get a specific match by ID"""
        return next((m for m in self.matches if m.match_id == match_id), None)
    
    def get_team_by_name(self, team_name: str) -> Optional[Team]:
        """Get team by name (case-insensitive partial match)"""
        team_name_lower = team_name.lower()
        for team in self.teams:
            if team_name_lower in team.team_name.lower():
                return team
        return None
    
    def to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert all data to DataFrames for Excel export"""
        # Teams DataFrame
        teams_df = pd.DataFrame([t.to_dict() for t in self.teams])
        
        # Matches/Fixtures DataFrame
        matches_df = pd.DataFrame([m.to_dict() for m in self.matches])
        
        # Standings DataFrame
        standings_df = pd.DataFrame([s.to_dict() for s in self.standings.values()])
        standings_df = standings_df.sort_values(
            by=['group', 'points', 'score_difference', 'score_for'],
            ascending=[True, False, False, False]
        )
        
        return {
            "teams": teams_df,
            "fixtures": matches_df,
            "standings": standings_df
        }
    
    def save_to_excel(self, file_path: str):
        """Save all tournament data to Excel"""
        dfs = self.to_dataframes()
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name.capitalize(), index=False)
    
    def load_from_excel(self, file_path: str):
        """Load tournament data from Excel results file"""
        try:
            # Load teams
            teams_df = pd.read_excel(file_path, sheet_name="Teams")
            self.teams = []
            for _, row in teams_df.iterrows():
                participants = str(row['participants']).split(', ') if pd.notna(row.get('participants')) else []
                team = Team(
                    team_id=int(row['team_id']),
                    team_name=row['team_name'],
                    participants=participants,
                    group=row.get('group')
                )
                self.teams.append(team)
            
            # Load fixtures
            fixtures_df = pd.read_excel(file_path, sheet_name="Fixtures")
            self.matches = []
            for _, row in fixtures_df.iterrows():
                scheduled_time = None
                end_time = None
                if pd.notna(row.get('scheduled_time')) and row.get('scheduled_time'):
                    try:
                        scheduled_time = pd.to_datetime(row['scheduled_time'])
                    except:
                        pass
                if pd.notna(row.get('end_time')) and row.get('end_time'):
                    try:
                        end_time = pd.to_datetime(row['end_time'])
                    except:
                        pass
                
                match = Match(
                    match_id=int(row['match_id']),
                    team1_id=int(row['team1_id']),
                    team1_name=row['team1_name'],
                    team2_id=int(row['team2_id']),
                    team2_name=row['team2_name'],
                    stage=row['stage'],
                    group=row.get('group') if pd.notna(row.get('group')) else None,
                    scheduled_time=scheduled_time,
                    end_time=end_time,
                    team1_score=int(row.get('team1_score', 0)) if pd.notna(row.get('team1_score')) else 0,
                    team2_score=int(row.get('team2_score', 0)) if pd.notna(row.get('team2_score')) else 0,
                    winner_id=int(row['winner_id']) if pd.notna(row.get('winner_id')) else None,
                    winner_name=row.get('winner_name') if pd.notna(row.get('winner_name')) else None,
                    status=row.get('status', 'scheduled')
                )
                self.matches.append(match)
            
            # Load standings
            standings_df = pd.read_excel(file_path, sheet_name="Standings")
            self.standings = {}
            for _, row in standings_df.iterrows():
                standing = TeamStanding(
                    team_id=int(row['team_id']),
                    team_name=row['team_name'],
                    group=row['group'],
                    matches_played=int(row.get('matches_played', 0)),
                    wins=int(row.get('wins', 0)),
                    losses=int(row.get('losses', 0)),
                    draws=int(row.get('draws', 0)),
                    points=int(row.get('points', 0)),
                    score_for=int(row.get('score_for', 0)),
                    score_against=int(row.get('score_against', 0)),
                    tiebreaker_score_for=int(row.get('tiebreaker_score_for', 0)),
                    tiebreaker_score_against=int(row.get('tiebreaker_score_against', 0))
                )
                self.standings[standing.team_id] = standing
            
            return True
        except Exception as e:
            print(f"Error loading from Excel: {e}")
            return False
