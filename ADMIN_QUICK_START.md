# Quick Start Guide - Updated Scoring System

## Overview

The tournament scoring system has been updated to allow:
- **Explicit winner selection** for each match
- **Independent score tracking** for tiebreaking purposes
- **Flexible match outcomes** not tied to score

## For Admins: How to Update Match Results

### Step 1: Navigate to Match Update
1. Go to the Group Stage tab for the match's group
2. Find the match you want to update
3. Click the expand arrow to open the match details

### Step 2: Enter Match Information
The interface now has three input sections:

```
┌─────────────────────────────────────────────────────┐
│ Enter Scores & Select Winner:                       │
├─────────────────────────────────────────────────────┤
│ [Team A Score: __] [Team B Score: __] [Winner ▼]   │
│                                                     │
│ Where Winner can be:                                │
│   • Draw (neither team wins)                        │
│   • Team A (Team A wins)                            │
│   • Team B (Team B wins)                            │
└─────────────────────────────────────────────────────┘
```

### Step 3: Click Update
Click the "✅ Update" button to save the match result.

## Important Rules

### Rule 1: Winner Determines Points
```
Winner Selection → Points Awarded
• Select Team A  → Team A gets 2 points (Team B gets 0)
• Select Team B  → Team B gets 2 points (Team A gets 0)
• Select Draw    → Both teams get 1 point each
```

### Rule 2: Scores Don't Determine Winner
```
Example 1:
  Score: Team A 10, Team B 2
  Winner: Team B
  Result: Team B gets 2 points (despite losing on score!)

Example 2:
  Score: Team A 5, Team B 5
  Winner: Team A
  Result: Team A gets 2 points (winner despite tied score)
```

### Rule 3: Scores Used Only for Tiebreaking
```
Scenario: Two teams have same points (6 pts each)
  Team A: 6 points, Score recorded (5 for, 3 against)
  Team B: 6 points, Score recorded (4 for, 2 against)
  
Tiebreaker Result:
  Team A score difference: +2 (5-3)
  Team B score difference: +2 (4-2)
  Next criterion: Team A scored 5, Team B scored 4
  
Ranking: Team A qualifies (higher score for)
```

## Worked Examples

### Example 1: Clear Winner with Unrelated Score

**Match Setup:**
- Team Alpha vs Team Beta
- Alpha Scores: 3
- Beta Scores: 1
- Winner Selected: **Beta** (selected because Beta won on points, not individual match)

**Standing Update:**
- Team Alpha: Gets 0 points, tiebreaker scores: 3 for / 1 against
- Team Beta: Gets 2 points, tiebreaker scores: 1 for / 3 against

**Use Case:** When tournament rules determine winner by overall tournament points, not individual match score

---

### Example 2: Tied Match Results

**Match Setup:**
- Team Gamma vs Team Delta
- Gamma Scores: 4
- Delta Scores: 4
- Winner Selected: **Draw**

**Standing Update:**
- Team Gamma: Gets 1 point (draw), tiebreaker scores: 4 for / 4 against
- Team Delta: Gets 1 point (draw), tiebreaker scores: 4 for / 4 against

**Use Case:** When match ends in tie and both teams share the point

---

### Example 3: Tiebreaker Application

**Group Stage Standings:**
- Match 1: Team A vs Team B → A wins (2-1) → A gets 2 points
- Match 2: Team A vs Team C → Draw (1-1) → A gets 1 point, C gets 1 point
- Match 3: Team B vs Team C → C wins (1-0) → C gets 2 points, B gets 0 points

**Final Standings:**
- Team A: 3 points, Tiebreaker: 3 for / 2 against = +1
- Team C: 3 points, Tiebreaker: 2 for / 1 against = +1
- Team B: 2 points

**Qualification (Top 2 from group):**
1. Team A (3 points, tiebreaker +1, scored 3)
2. Team C (3 points, tiebreaker +1, scored 2) ← Loses tiebreaker on score for

Team B doesn't qualify (only 2 points)

## Frequently Asked Questions

**Q: What if I accidentally select the wrong winner?**
A: You can update the match again. Just change the winner selection and click Update.

**Q: Do scores affect who wins the match?**
A: No. Winner is determined by your explicit selection, independent of scores.

**Q: Are the old match scores lost?**
A: No. Scores are preserved in the tiebreaker columns and used when teams have equal points.

**Q: Can NLP commands update match winners?**
A: Currently, NLP can only update scores. Use the UI to select the winner. (This may be improved in future versions)

**Q: What happens if I load an old tournament file?**
A: Old score data is automatically used for tiebreaker fields. Everything works seamlessly.

## Admin Checklist Before Tournament Start

- [ ] Understand that winner is selected separately from score
- [ ] Confirm all admins understand the new system
- [ ] Test with a sample match before tournament starts
- [ ] Brief participants if explaining match results to them
- [ ] Document your tournament's specific winner determination rule (if different from standard)

## For Troubleshooting

If standings look unexpected:
1. Verify all match winners are correctly selected
2. Check tiebreaker score columns in standings view
3. Confirm no matches are marked as incomplete
4. Save and refresh tournament data
5. Check the SCORING_SYSTEM_UPDATE.md for detailed examples

---

**Need Help?** Check SCORING_SYSTEM_UPDATE.md for comprehensive documentation.
