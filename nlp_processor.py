"""
NLP Processor for Natural Language Commands
Uses OpenAI API for understanding and processing commands
"""

import json
import re
from typing import Dict, Any, Optional, Tuple
from openai import OpenAI

from config import TournamentConfig


class NLPProcessor:
    """Process natural language commands for tournament management"""
    
    def __init__(self):
        self.config = TournamentConfig()
        self.client = None
        if self.config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def is_available(self) -> bool:
        """Check if NLP is available (API key configured)"""
        return self.client is not None
    
    def process_command(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a natural language command and return structured action
        
        Args:
            command: Natural language command from user
            context: Current tournament context (teams, matches, etc.)
            
        Returns:
            Dictionary with action type and parameters
        """
        if not self.is_available():
            return self._fallback_process(command, context)
        
        try:
            return self._llm_process(command, context)
        except Exception as e:
            print(f"LLM processing failed: {e}")
            return self._fallback_process(command, context)
    
    def _llm_process(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process command using LLM"""
        
        # Prepare context summary
        teams_summary = ", ".join([t['team_name'] for t in context.get('teams', [])])
        matches_summary = []
        for m in context.get('matches', [])[:10]:  # Limit to recent matches
            matches_summary.append(f"Match {m['match_id']}: {m['team1_name']} vs {m['team2_name']} ({m['status']})")
        
        system_prompt = f"""You are a tournament management assistant for a {self.config.SPORT_NAME} tournament.
        
Available teams: {teams_summary}

Recent matches:
{chr(10).join(matches_summary)}

You can perform these actions:
1. UPDATE_SCORE - Update match result (requires: match_id or team names, team1_score, team2_score)
2. GET_STANDINGS - Get current standings (optional: group name)
3. GET_MATCHES - Get matches (optional: stage like 'group', 'quarterfinal', 'semifinal', 'final')
4. GET_TEAM_INFO - Get team information (requires: team_name)
5. GET_SCHEDULE - Get match schedule
6. GENERATE_NEXT_STAGE - Generate fixtures for next stage

Respond with a JSON object containing:
- "action": one of the action types above
- "params": dictionary of parameters
- "message": friendly response message
- "confidence": confidence level (0-1)

If you can't understand the command, use action "UNKNOWN" with a helpful message."""

        user_prompt = f"User command: {command}"
        
        response = self.client.chat.completions.create(
            model=self.config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                result = json.loads(json_match.group())
                return result
        except json.JSONDecodeError:
            pass
        
        return {
            "action": "UNKNOWN",
            "params": {},
            "message": response_text,
            "confidence": 0.5
        }
    
    def _fallback_process(self, command: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback processing without LLM using pattern matching"""
        command_lower = command.lower()
        
        # Pattern: Update score
        score_patterns = [
            r"(?:update|set|record)\s+(?:score|result).*?(\d+)\s*[-:]\s*(\d+)",
            r"(\w+(?:\s+\w+)?)\s+(?:beat|won|defeated)\s+(\w+(?:\s+\w+)?)\s+(\d+)\s*[-:]\s*(\d+)",
            r"match\s*(\d+).*?(\d+)\s*[-:]\s*(\d+)",
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, command_lower)
            if match:
                groups = match.groups()
                
                # Check if it's match ID pattern
                if 'match' in pattern:
                    return {
                        "action": "UPDATE_SCORE",
                        "params": {
                            "match_id": int(groups[0]),
                            "team1_score": int(groups[1]),
                            "team2_score": int(groups[2])
                        },
                        "message": f"Updating match {groups[0]} score to {groups[1]}-{groups[2]}",
                        "confidence": 0.8
                    }
                elif len(groups) == 4:
                    return {
                        "action": "UPDATE_SCORE",
                        "params": {
                            "team1_name": groups[0],
                            "team2_name": groups[1],
                            "team1_score": int(groups[2]),
                            "team2_score": int(groups[3])
                        },
                        "message": f"Updating score: {groups[0]} {groups[2]} - {groups[3]} {groups[1]}",
                        "confidence": 0.7
                    }
        
        # Pattern: Get standings
        if any(word in command_lower for word in ['standing', 'leaderboard', 'points table', 'ranking']):
            group = None
            group_match = re.search(r'group\s*([a-zA-Z])', command_lower)
            if group_match:
                group = group_match.group(1).upper()
            
            return {
                "action": "GET_STANDINGS",
                "params": {"group": group},
                "message": f"Fetching standings" + (f" for Group {group}" if group else ""),
                "confidence": 0.9
            }
        
        # Pattern: Get matches
        if any(word in command_lower for word in ['match', 'fixture', 'game', 'schedule']):
            stage = None
            if 'quarter' in command_lower:
                stage = 'quarterfinal'
            elif 'semi' in command_lower:
                stage = 'semifinal'
            elif 'final' in command_lower and 'semi' not in command_lower and 'quarter' not in command_lower:
                stage = 'final'
            elif 'group' in command_lower:
                stage = 'group'
            
            return {
                "action": "GET_MATCHES",
                "params": {"stage": stage},
                "message": f"Fetching {'all ' if not stage else ''}{stage + ' ' if stage else ''}matches",
                "confidence": 0.8
            }
        
        # Pattern: Team info
        team_pattern = r"(?:info|details?|about|show)\s+(?:team\s+)?([a-zA-Z\s]+)"
        team_match = re.search(team_pattern, command_lower)
        if team_match:
            return {
                "action": "GET_TEAM_INFO",
                "params": {"team_name": team_match.group(1).strip()},
                "message": f"Fetching team information",
                "confidence": 0.7
            }
        
        # Pattern: Generate next stage
        if any(word in command_lower for word in ['generate', 'create', 'next stage', 'quarterfinal', 'semifinal', 'final']):
            return {
                "action": "GENERATE_NEXT_STAGE",
                "params": {},
                "message": "Generating next stage fixtures",
                "confidence": 0.7
            }
        
        return {
            "action": "UNKNOWN",
            "params": {},
            "message": "I couldn't understand that command. Try something like:\n- 'Update match 1 score to 3-2'\n- 'Show standings for group A'\n- 'Get all matches'\n- 'Team Alpha info'",
            "confidence": 0
        }
    
    def generate_match_summary(self, match_data: Dict) -> str:
        """Generate a natural language summary of a match"""
        if not self.is_available():
            return self._fallback_match_summary(match_data)
        
        try:
            prompt = f"""Generate a brief, exciting one-line summary for this {self.config.SPORT_NAME} match result:
            
{match_data['team1_name']} vs {match_data['team2_name']}
Score: {match_data['team1_score']} - {match_data['team2_score']}
Stage: {match_data['stage']}
Winner: {match_data.get('winner_name', 'Draw')}

Keep it concise and sports-commentary style."""

            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return self._fallback_match_summary(match_data)
    
    def _fallback_match_summary(self, match_data: Dict) -> str:
        """Fallback match summary without LLM"""
        winner = match_data.get('winner_name')
        if winner and winner != 'Draw':
            return f"🏆 {winner} wins! Final score: {match_data['team1_name']} {match_data['team1_score']} - {match_data['team2_score']} {match_data['team2_name']}"
        elif winner == 'Draw':
            return f"🤝 It's a draw! {match_data['team1_name']} {match_data['team1_score']} - {match_data['team2_score']} {match_data['team2_name']}"
        else:
            return f"📅 Upcoming: {match_data['team1_name']} vs {match_data['team2_name']}"
