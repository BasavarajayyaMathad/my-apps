"""
Utility script to create sample teams Excel file
Run this to generate a sample input file
"""

import pandas as pd

# Sample teams data
teams_data = {
    'team_name': [
        'Thunder Strikers',
        'Carrom Kings',
        'Power Players',
        'Victory Squad',
        'Elite Force',
        'Champion Stars',
        'Blazing Arrows',
        'Royal Knights',
        'Storm Breakers',
        'Golden Eagles',
        'Silver Sharks',
        'Diamond Dukes'
    ],
    'participants': [
        'Rahul Sharma, Priya Patel',
        'Amit Kumar, Sneha Reddy',
        'Vikram Singh, Anita Desai',
        'Ravi Gupta, Meera Iyer',
        'Suresh Nair, Kavita Joshi',
        'Arjun Menon, Lakshmi Rao',
        'Deepak Verma, Pooja Kapoor',
        'Karthik Subramaniam, Divya Krishnan',
        'Manish Agarwal, Swati Mishra',
        'Nikhil Choudhary, Rashmi Hegde',
        'Pranav Pillai, Anjali Shetty',
        'Sanjay Bhat, Neha Kulkarni'
    ]
}

# Create DataFrame
df = pd.DataFrame(teams_data)

# Save to Excel
df.to_excel('sample_teams.xlsx', index=False, sheet_name='Teams')

print("✅ Sample teams Excel file created: sample_teams.xlsx")
print(f"   Total teams: {len(df)}")
print("\nTeams:")
for idx, row in df.iterrows():
    print(f"   {idx + 1}. {row['team_name']}: {row['participants']}")
