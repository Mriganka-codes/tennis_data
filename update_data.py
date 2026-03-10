import json
import os
from tennis_scraper import get_matches
from datetime import datetime

DATA_FILE = "matches.json"

def update():
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching ATP matches...")
        atp_matches = get_matches('atp', main_only=True)
        for m in atp_matches: 
            m['tour'] = 'ATP'
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching WTA matches...")
        wta_matches = get_matches('wta', main_only=True)
        for m in wta_matches: 
            m['tour'] = 'WTA'
        
        all_matches = atp_matches + wta_matches
        
        # Sort by time
        all_matches = sorted(all_matches, key=lambda x: x['time'] if x['time'] else "23:59")
        
        # Save to JSON
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "count": len(all_matches),
                "matches": all_matches
            }, f, indent=2, ensure_ascii=False)
            
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully saved {len(all_matches)} matches to {DATA_FILE}")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error updating data: {e}")

if __name__ == "__main__":
    update()
