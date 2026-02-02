# 🏆 Carrom Tournament Builder

A comprehensive Streamlit application for managing carrom (or any sport) tournaments with group stages, knockout rounds, NLP commands, and visual analytics.

## Features

### 📋 Tournament Management
- **Excel-based team input**: Upload teams via Excel file
- **Automatic group division**: Random distribution into groups
- **Round Robin group stage**: All teams play against each other in groups
- **Knockout stages**: Quarter Finals → Semi Finals → Final
- **Automatic scheduling**: Set start time, matches auto-scheduled with durations

### 📊 Scoring & Standings
- **Easy score updates**: Click-to-update match results
- **Real-time standings**: Auto-calculated points, wins, losses
- **Visual indicators**: 🏆 for wins, ❌ for losses, ✅ for completed matches
- **Points system**: Configurable (default: 2 points per win)

### 💬 NLP Commands
- Update scores using natural language
- Query standings, matches, team info
- Powered by OpenAI (optional)
- Fallback pattern matching when API not available

### 📈 Analytics & Visualization
- Standings bar charts
- Win/Loss/Draw breakdowns
- Score difference charts
- Tournament bracket visualization
- Match timeline

### 💾 Data Persistence
- All data saved to `tournament_results.xlsx`
- Resume tournaments anytime
- Manual Excel edits supported

## Installation

1. **Clone/Download the project**

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment** (optional, for NLP):
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key

5. **Generate sample teams file**:
   ```bash
   python create_sample_teams.py
   ```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Tournament Workflow

1. **Setup Phase**:
   - Upload Excel file with teams
   - Set tournament start time
   - Click "Initialize Tournament"

2. **Group Stage**:
   - View groups and standings
   - Update match scores
   - Wait for all group matches to complete

3. **Quarter Finals**:
   - Click "Generate Quarter Finals"
   - Top 4 teams from each group qualify
   - Update knockout match scores

4. **Semi Finals & Final**:
   - Progress through knockout stages
   - Crown the champion!

### Excel File Format

Your input Excel file should have these columns:

| team_name | participants |
|-----------|--------------|
| Team Alpha | John Doe, Jane Smith |
| Team Beta | Bob Wilson, Alice Brown |

### NLP Commands

Try these commands in the NLP tab:
- "Update match 1 score to 3-2"
- "Show standings for group A"
- "Get all quarterfinal matches"
- "Team Alpha info"

## Configuration

Edit `config.py` to customize:

```python
# Sport name
SPORT_NAME = "Carrom"

# Match duration
MATCH_DURATION_MINUTES = 20

# Points system
POINTS_PER_WIN = 2
POINTS_PER_DRAW = 1
POINTS_PER_LOSS = 0

# Tournament structure
NUMBER_OF_GROUPS = 2  # Can be 2 or 4
# Teams qualifying per group is calculated automatically:
# - 2 groups: Top 4 teams per group (8 total for quarterfinals)
# - 4 groups: Top 2 teams per group (8 total for quarterfinals)
```

## File Structure

```
Carrom Tournament Builder/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── models.py              # Data models (Team, Match, Standing)
├── tournament_engine.py   # Core tournament logic
├── nlp_processor.py       # Natural language processing
├── visualizations.py      # Charts and visual components
├── create_sample_teams.py # Utility to create sample data
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── sample_teams.xlsx      # Sample input file
└── tournament_results.xlsx # Auto-generated results file
```

## Adapting for Other Sports

This application is designed to be sport-agnostic. To adapt for another sport:

1. **Update `config.py`**:
   ```python
   SPORT_NAME = "Table Tennis"
   MATCH_DURATION_MINUTES = 15
   POINTS_PER_WIN = 3
   ```

2. **Modify tournament structure** (if needed):
   ```python
   # For 4 groups with 2 teams qualifying per group:
   NUMBER_OF_GROUPS = 4
   # This will automatically calculate: Top 2 teams from each group
   ```

3. **Customize visual indicators** in `config.py`

## Troubleshooting

### "NLP Status: Not configured"
- Add your OpenAI API key to `.env` file
- NLP will still work with basic pattern matching

### "Error reading file"
- Ensure Excel file has correct column names
- Check file is `.xlsx` or `.xls` format

### "Tournament not saving"
- Check write permissions in the directory
- Ensure no other program has the Excel file open

## License

MIT License - Feel free to modify and use for your tournaments!

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
