# tennis-data

Automated tennis match data scraper. Scrapes ATP, WTA, and Challenger matches with odds from tennisexplorer.com every 6 hours via GitHub Actions.

## Data

`matches.json` is updated automatically and contains today's matches with odds.

### Access the data

```
https://raw.githubusercontent.com/Mriganka-codes/tennis-data/main/matches.json
```

## Schedule

Runs at midnight, 6am, 12pm, and 6pm UTC daily. Can also be triggered manually from the Actions tab.

## Local usage

```bash
pip install -r requirements.txt
python update_data.py
```
