"""
Visualization Components for Tournament Dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict

from config import TournamentConfig


class TournamentVisualizer:
    """Create visualizations for tournament data"""
    
    def __init__(self):
        self.config = TournamentConfig()
    
    def create_standings_chart(self, standings_data: List[Dict], group: str = None) -> go.Figure:
        """Create a horizontal bar chart for standings"""
        df = pd.DataFrame(standings_data)
        
        if group:
            df = df[df['group'] == group]
        
        df = df.sort_values('points', ascending=True)
        
        # Create color based on position - use dynamic calculation for qualifying teams
        top_n = self.config.get_top_teams_per_group()
        colors = [self.config.COLORS['win'] if i >= len(df) - top_n 
                  else self.config.COLORS['secondary'] 
                  for i in range(len(df))]
        
        fig = go.Figure(go.Bar(
            x=df['points'],
            y=df['team_name'],
            orientation='h',
            marker_color=colors,
            text=df['points'],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Points: %{x}<br>W: %{customdata[0]} L: %{customdata[1]} D: %{customdata[2]}<extra></extra>',
            customdata=df[['wins', 'losses', 'draws']].values
        ))
        
        title = f"Group {group} Standings" if group else "Overall Standings"
        fig.update_layout(
            title=title,
            xaxis_title="Points",
            yaxis_title="Team",
            height=max(300, len(df) * 40),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_win_loss_chart(self, standings_data: List[Dict]) -> go.Figure:
        """Create a stacked bar chart showing wins, losses, draws"""
        df = pd.DataFrame(standings_data)
        df = df.sort_values('points', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Wins',
            y=df['team_name'],
            x=df['wins'],
            orientation='h',
            marker_color=self.config.COLORS['win']
        ))
        
        fig.add_trace(go.Bar(
            name='Draws',
            y=df['team_name'],
            x=df['draws'],
            orientation='h',
            marker_color=self.config.COLORS['draw']
        ))
        
        fig.add_trace(go.Bar(
            name='Losses',
            y=df['team_name'],
            x=df['losses'],
            orientation='h',
            marker_color=self.config.COLORS['loss']
        ))
        
        fig.update_layout(
            barmode='stack',
            title='Team Performance (Wins/Draws/Losses)',
            xaxis_title='Matches',
            yaxis_title='Team',
            height=max(300, len(df) * 35),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    
    def create_score_difference_chart(self, standings_data: List[Dict]) -> go.Figure:
        """Create a bar chart showing score difference"""
        df = pd.DataFrame(standings_data)
        df = df.sort_values('score_difference', ascending=True)
        
        colors = [self.config.COLORS['win'] if x >= 0 else self.config.COLORS['loss'] 
                  for x in df['score_difference']]
        
        fig = go.Figure(go.Bar(
            x=df['score_difference'],
            y=df['team_name'],
            orientation='h',
            marker_color=colors,
            text=df['score_difference'],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Score Difference',
            xaxis_title='Score Difference',
            yaxis_title='Team',
            height=max(300, len(df) * 35),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        return fig
    
    def create_tournament_bracket(self, matches_data: List[Dict]) -> go.Figure:
        """Create a tournament bracket visualization for knockout stages"""
        # Filter knockout matches
        knockout_matches = [m for m in matches_data if m['stage'] in ['quarterfinal', 'semifinal', 'final', 'third_place']]
        
        if not knockout_matches:
            return None
        
        # Create a simple bracket visualization
        fig = go.Figure()
        
        stages = ['quarterfinal', 'semifinal', 'final', 'third_place']
        stage_positions = {'quarterfinal': 0, 'semifinal': 1, 'final': 2, 'third_place': 2.5}
        
        for stage in stages:
            stage_matches = [m for m in knockout_matches if m['stage'] == stage]
            x_pos = stage_positions[stage]
            
            for i, match in enumerate(stage_matches):
                y_pos = i * 2 - (len(stage_matches) - 1)
                
                # Determine colors based on winner
                team1_color = self.config.COLORS['win'] if match.get('winner_id') == match['team1_id'] else self.config.COLORS['secondary']
                team2_color = self.config.COLORS['win'] if match.get('winner_id') == match['team2_id'] else self.config.COLORS['secondary']
                
                # Team 1
                fig.add_trace(go.Scatter(
                    x=[x_pos],
                    y=[y_pos + 0.3],
                    mode='markers+text',
                    text=[f"{match['team1_name']} ({match['team1_score']})"],
                    textposition='middle right',
                    marker=dict(size=15, color=team1_color, symbol='square'),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f"{match['team1_name']}: {match['team1_score']} points"
                ))
                
                # Team 2
                fig.add_trace(go.Scatter(
                    x=[x_pos],
                    y=[y_pos - 0.3],
                    mode='markers+text',
                    text=[f"{match['team2_name']} ({match['team2_score']})"],
                    textposition='middle right',
                    marker=dict(size=15, color=team2_color, symbol='square'),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f"{match['team2_name']}: {match['team2_score']} points"
                ))
        
        fig.update_layout(
            title='Tournament Bracket',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(len(stages))),
                ticktext=['Quarter Finals', 'Semi Finals', 'Final', '3rd Place'],
                showgrid=False
            ),
            yaxis=dict(showticklabels=False, showgrid=False),
            height=400,
            margin=dict(l=20, r=150, t=40, b=20)
        )
        
        return fig
    
    def create_match_timeline(self, matches_data: List[Dict]) -> go.Figure:
        """Create a timeline of matches"""
        df = pd.DataFrame(matches_data)
        
        if 'scheduled_time' not in df.columns or df['scheduled_time'].isna().all():
            return None
        
        df = df[df['scheduled_time'].notna()]
        df['scheduled_time'] = pd.to_datetime(df['scheduled_time'])
        df = df.sort_values('scheduled_time')
        
        # Create color mapping for status
        color_map = {
            'completed': self.config.COLORS['win'],
            'in_progress': self.config.COLORS['draw'],
            'scheduled': self.config.COLORS['primary'],
            'cancelled': self.config.COLORS['loss']
        }
        
        df['color'] = df['status'].map(color_map).fillna(self.config.COLORS['secondary'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['scheduled_time'],
            y=df['match_id'],
            mode='markers+text',
            marker=dict(
                size=15,
                color=df['color'],
                symbol='circle'
            ),
            text=df.apply(lambda r: f"{r['team1_name']} vs {r['team2_name']}", axis=1),
            textposition='middle right',
            hovertemplate='<b>Match %{y}</b><br>%{text}<br>Time: %{x}<br>Status: %{customdata}<extra></extra>',
            customdata=df['status']
        ))
        
        fig.update_layout(
            title='Match Schedule Timeline',
            xaxis_title='Time',
            yaxis_title='Match #',
            height=max(300, len(df) * 30),
            margin=dict(l=20, r=150, t=40, b=20)
        )
        
        return fig
    
    def get_status_badge(self, status: str) -> str:
        """Get HTML badge for match status"""
        indicator = self.config.VISUAL_INDICATORS.get(status, "")
        color = {
            'completed': self.config.COLORS['win'],
            'in_progress': self.config.COLORS['draw'],
            'scheduled': self.config.COLORS['primary'],
            'cancelled': self.config.COLORS['loss']
        }.get(status, self.config.COLORS['secondary'])
        
        return f'<span style="color: {color}; font-weight: bold;">{indicator} {status.title()}</span>'
    
    def get_result_indicator(self, team_id: int, winner_id: int) -> str:
        """Get visual indicator for match result"""
        if winner_id is None:
            return self.config.VISUAL_INDICATORS['scheduled']
        elif team_id == winner_id:
            return self.config.VISUAL_INDICATORS['win']
        else:
            return self.config.VISUAL_INDICATORS['loss']
