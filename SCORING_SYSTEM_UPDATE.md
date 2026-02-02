# Tournament Scoring System Update

## Overview
The tournament system has been updated to support a more flexible scoring mechanism where:
1. **Match Winner** is explicitly selected and determines the points (2 points for winner)
2. **Match Scores** are recorded independently and used ONLY for tiebreaking when teams have equal points
3. **No automatic winner determination** based on score - winner must be explicitly selected

## Key Changes

### 1. Data Model Updates (`models.py`)

#### New Fields in `TeamStanding`:
```python
tiebreaker_score_for: int = 0      # Score accumulated (used only for tiebreaker)
tiebreaker_score_against: int = 0  # Opponent score accumulated (used only for tiebreaker)

@property
def tiebreaker_score_difference(self):
    """Score difference used only when teams have equal points"""
    return self.tiebreaker_score_for - self.tiebreaker_score_against
```

### 2. Tournament Engine Updates (`tournament_engine.py`)

#### Modified `update_match_result()` Method:
```python
def update_match_result(self, match_id: int, team1_score: int, team2_score: int, winner_id: Optional[int] = None) -> Match:
    """
    Args:
        match_id: ID of the match to update
        team1_score: Score for team 1 (used for tiebreaker only)
        team2_score: Score for team 2 (used for tiebreaker only)
        winner_id: ID of the winning team (optional). If None, match is marked as draw.
                  This is independent of scores and determines who gets 2 points.
    """
```

**Key Point**: The `winner_id` parameter is now required to explicitly set which team won, independent of the scores.

#### Updated `_update_standings()` Method:
- Tracks both regular scores AND tiebreaker scores
- Uses `winner_id` (not score comparison) to determine win/loss/draw
- Points awarded based solely on match winner

#### Updated `get_group_standings()` Sorting:
Sorting order:
1. **Points** (higher is better) - Based on match wins only
2. **Tiebreaker Score Difference** (higher is better) - Only when points are equal
3. **Tiebreaker Score For** (higher is better) - Final tiebreaker

```python
# Sort by points first, then use tiebreaker scores if points are equal
standings_list.sort(key=lambda x: (-x.points, -x.tiebreaker_score_difference, -x.tiebreaker_score_for))
```

### 3. UI Updates (`app.py`)

#### Match Update Interface:
When updating match results, admins now see:
- **Score inputs** for Team 1 and Team 2 (for reference/tiebreaker)
- **Winner selector dropdown** with options:
  - Draw
  - Team 1 Name
  - Team 2 Name

```
Enter Scores & Select Winner:
[Team1 Score] [Team2 Score] [Winner Dropdown ▼]
```

Example:
- Scores: Team A = 5, Team B = 3
- Winner: Team B
- Result: Team B gets 2 points, Team A gets 0 points
- Tiebreaker: If both teams end up with same points, their score (5 vs 3) is used as tiebreaker

### 4. Scenario Examples

#### Scenario 1: Clear Winner
- Team A: 10 points
- Team B: 8 points
- Result: Team A qualifies (clear winner in points)
- *Scores don't matter in this case*

#### Scenario 2: Tied Points - Tiebreaker Applies
- Team A: 6 points | Score difference: +5 (scored 15, conceded 10)
- Team B: 6 points | Score difference: +3 (scored 13, conceded 10)
- Result: Team A qualifies (higher tiebreaker score difference)

#### Scenario 3: Explicit Winner Selection
- Match result entered as:
  - Team X Score: 2
  - Team Y Score: 2
  - Winner: Team X
- Result: Team X gets 2 points, Team Y gets 0 points (despite tied score)

## Migration Notes

- **Existing data**: When loading old tournament data, tiebreaker scores are automatically populated from regular scores
- **Excel export**: Tiebreaker score fields are now included in the Standings sheet
- **Excel import**: Handles both old and new formats gracefully

## Benefits

1. **Flexibility**: Winner can be determined by rules other than match score (e.g., points scored in tournament overall)
2. **Fairness**: Tiebreaker mechanism ensures fair advancement even with equal wins
3. **Clarity**: Explicit winner selection prevents ambiguity
4. **Data Integrity**: Scores used for tiebreaker are preserved separately from match outcome

## Testing the System

To test the new system:

1. Create or load a tournament
2. Update a match with:
   - Different scores (e.g., Team A: 5, Team B: 3)
   - Different winner (select Team B as winner despite lower score)
3. Check standings to confirm:
   - Winner gets 2 points
   - Scores are recorded in tiebreaker columns
   - Sorting uses tiebreaker criteria when points are equal
