import urllib.request
import argparse
import json
import ssl
import re
from bs4 import BeautifulSoup
from datetime import datetime

def get_matches(match_type, date_str=None, main_only=False):
    """
    Scrapes tennis matches and odds from tennisexplorer.com
    match_type: 'atp' or 'wta'
    date_str: 'YYYY-MM-DD' (optional, defaults to today)
    main_only: Boolean, if True filters out challengers, ITF, Futures, and UTR matches
    """
    if match_type not in ['atp', 'wta']:
        raise ValueError("Match type must be 'atp' or 'wta'")
        
    url = f"https://www.tennisexplorer.com/matches/?type={match_type}-single"
    
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            url += f"&year={date_obj.year}&month={date_obj.month:02d}&day={date_obj.day:02d}"
        except ValueError:
            raise ValueError("Date format must be YYYY-MM-DD")
            
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Context to handle potential SSL issues
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    matches = []
    
    # Lowercase terms that indicate non-main tournaments
    lower_tier_terms = ["itf", "futures", "utr", "exhibition"]
    
    tables = soup.find_all("table", class_="result")
    for table in tables:
        current_tournament = "Unknown"
        skip_tournament = False
        rows = table.find_all("tr")
        
        i = 0
        while i < len(rows):
            row = rows[i]
            
            # Extract Tournament Name
            if "head" in row.get("class", []) and "flags" in row.get("class", []):
                t_name_td = row.find("td", class_="t-name")
                if t_name_td:
                    current_tournament = t_name_td.text.strip()
                    if main_only:
                        t_lower = current_tournament.lower()
                        skip_tournament = any(term in t_lower for term in lower_tier_terms)
                    else:
                        skip_tournament = False
                i += 1
                continue
                
            if skip_tournament:
                i += 1
                continue
                
            if row.get("id"):
                classes = row.get("class", [])
                
                # Check for the first row of a match (has class "one" or "two" and doesn't end with "b")
                if not row.get("id").endswith("b") and ("one" in classes or "two" in classes):
                    # Player 1
                    p1_name_td = row.find("td", class_="t-name")
                    p1_name = p1_name_td.text.strip() if p1_name_td else "Unknown"
                    
                    # Odds columns frequently use "course" or "coursew" class
                    odds_tds = row.find_all("td", class_=["course", "coursew"])
                    odds_1 = None
                    odds_2 = None
                    
                    # Filter empty tags / non-breaking spaces
                    valid_odds = [td.text.strip() for td in odds_tds if td.text.strip() and td.text.strip() != '\xa0']
                    if len(valid_odds) >= 2:
                        try:
                            odds_1 = float(valid_odds[0])
                            odds_2 = float(valid_odds[1])
                        except ValueError:
                            odds_1 = valid_odds[0]
                            odds_2 = valid_odds[1]
                    
                    # Match Time
                    time_td = row.find("td", class_="time")
                    match_time = ""
                    if time_td:
                        # 2. Use regex to find only the HH:MM pattern (e.g., 20:00)
                        time_match = re.search(r'\d{2}:\d{2}', time_td.text)
                        match_time = time_match.group(0) if time_match else ""
                    
                    # Player 2 (typically found in the adjacent row)
                    p2_name = "Unknown"
                    if i + 1 < len(rows):
                        next_row = rows[i+1]
                        if next_row.get("id") and next_row.get("id") == row.get("id") + "b":
                            p2_name_td = next_row.find("td", class_="t-name")
                            if p2_name_td:
                                p2_name = p2_name_td.text.strip()
                            i += 1 # Consume the Player 2 row
                    
                    matches.append({
                        "tournament": current_tournament,
                        "time": match_time,
                        "player1": p1_name,
                        "player2": p2_name,
                        "odds1": odds_1,
                        "odds2": odds_2
                    })
            i += 1

    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape tennisexplorer.com for matches and ML odds")
    parser.add_argument("--type", choices=["atp", "wta"], required=True, help="Type of matches to scrape (atp or wta)")
    parser.add_argument("--date", type=str, help="Date to scrape in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--output", type=str, help="Optional output filename. Defaults to <type>_matches_<date>.json")
    parser.add_argument("--main-only", action="store_true", help="Filter out Challengers, ITF, Futures, and UTR matches to only show main tournaments")
    
    args = parser.parse_args()
    
    try:
        results = get_matches(args.type, args.date, args.main_only)
        match_date = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
        
        output_data = {
            "type": args.type,
            "date": match_date,
            "count": len(results),
            "matches": results
        }
        
        filename = args.output if args.output else f"{args.type}_matches_{match_date}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully scraped {len(results)} {args.type.upper()} matches.")
        print(f"Data saved to {filename}")
        
    except Exception as e:
        print(f"Error executing scraper: {e}")

