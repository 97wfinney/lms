# lms

This project is a basic script to help choose a team for Fantasy Premier League (FPL) each week. It uses data from the official FPL API to analyze team strengths and suggests the strongest available team for the upcoming gameweek.

## Features

- Fetches the latest team and fixture data from the FPL API.
- Analyzes team strengths based on attack and defense performance.
- Avoids previously selected teams by reading from a simple text file (`lms.txt`).
- Saves the chosen team to the `lms.txt` file so it's not selected again in future weeks.

## Team Selection Logic

The script selects the strongest team for the upcoming gameweek based on team performance data fetched from the Fantasy Premier League (FPL) API. It calculates a strength score for each team by considering their attack and defense metrics, both at home and away. The script then compares each team against their opponents to adjust for difficulty. Teams that were previously chosen (listed in `lms.txt`) are excluded from the selection. Finally, the strongest available team is suggested for the gameweek and added to the `lms.txt` file.

## How to Use

1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt