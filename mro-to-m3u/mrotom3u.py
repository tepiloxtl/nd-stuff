#!/usr/bin/python3
"""
mrotom3u.py - Generate M3U playlists from MyRadioOnline.

This script fetches radio station data from MyRadioOnline and generates M3U playlist files
based on language codes. It can create:
- A single combined M3U file per language (`--combined`).
- Individual M3U files for each station in a language (`--singles`).

Usage examples:
1. Create a combined M3U playlist for a specific language:
   python3 mrotom3u.py uk --combined

2. Create individual M3U playlists for each station in a language:
   python3 mrotom3u.py uk --singles

3. Process multiple languages:
   python3 mrotom3u.py uk fr es --combined

4. Process all available languages:
   python3 mrotom3u.py --combined

5. Create both combined and individual M3U playlists:
   python3 mrotom3u.py uk --singles --combined

Notes:
- If no language codes are provided, the script defaults to all available languages.
- Either `--singles` or `--combined` must be specified.
"""

import requests
import json
import base64
import time
import random
import os
import argparse

# Define HTTP request headers to mimic a web browser request
mroheaders = {
    'authority': 'myradioonline.pl',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://myradioonline.pl',
    'referer': 'https://myradioonline.pl/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'x-requested-with': 'XMLHttpRequest',
}

# Initial POST request payload
mrodata = {
    'ord': '1',  # Order of stations (1 = default order)
    'actP': '1',  # Active page (pagination)
    'type': '',   # Type filter (empty means all)
}

# List of available language codes
all_languages = ['at', 'cl', 'co', 'cz', 'de', 'es', 'fr', 'hu', 'ie', 'it', 
                 'mx', 'nl', 'pe', 'pl', 'ro', 'sk', 'uk']

# Argument parser for command-line input
parser = argparse.ArgumentParser(
    description="Generate M3U playlists for specified language(s) or all if none are provided.\n\n"
                "Examples:\n"
                "  python3 mrotom3u.py uk --combined  # Create a combined M3U for UK\n"
                "  python3 mrotom3u.py uk --singles   # Create separate M3U files for UK stations\n"
                "  python3 mrotom3u.py --combined     # Process all languages as combined files\n"
                "  python3 mrotom3u.py --singles      # Process all languages as individual station files\n",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('langs', nargs='*', help="Language codes (e.g., 'uk', 'es', 'fr'). If omitted, all languages are processed.")
parser.add_argument('--combined', action='store_true', help="Create a single combined M3U8 file per language.")
parser.add_argument('--singles', action='store_true', help="Create individual M3U8 files per station in lang-code directory.")
args = parser.parse_args()

# If no arguments are provided, display help message and exit
if not args.langs and not args.combined and not args.singles:
    parser.print_help()
    exit(1)

# Determine which languages to process
langs = args.langs if args.langs else all_languages

# Validate user-provided language codes
invalid_langs = [lang for lang in langs if lang not in all_languages]
if invalid_langs:
    print(f"Error: Invalid language codes: {', '.join(invalid_langs)}.")
    print(f"Valid options: {', '.join(all_languages)}")
    exit(1)

# Ensure at least one output option is selected
if not args.combined and not args.singles:
    print("You must specify at least one of the options: --singles or --combined.")
    parser.print_usage()
    exit(1)

radios = {}  # Dictionary to store station data categorized by language
actP = 1     # Pagination counter for fetching station data

# Fetch all available radio station data
while True:
    print(f"Fetching page {actP}...")
    mrodata['actP'] = actP
    response = requests.post('https://myradioonline.pl/get-radio-list', headers=mroheaders, data=mrodata)
    thing = response.json()  # Parse JSON response

    for item in thing["radios"]["list"]:
        name = item["r_name"]  # Station name
        url = base64.b64decode(item["rsu_url"]).decode('utf-8')  # Decode stream URL
        lang = item["lng"]  # Language code
        logo = item["settings"]["list_45"].replace("list_45.jpg", "play_250_250.webp")  # Extract station logo

        if lang not in radios:
            radios[lang] = []

        radios[lang].append([name, url, lang, logo])

    # If no more pages, break the loop
    if not thing["moreP"]:
        break

    actP += 1
    time.sleep(random.randint(1, 5))  # Random delay to avoid request throttling

# Create M3U files based on the selected options
for lang_code in langs:
    if lang_code in radios:
        if args.combined:
            # Create a single M3U8 file for the language
            combined_file = f"./playlists/{lang_code}.m3u8"
            os.makedirs("./playlists", exist_ok=True)
            with open(combined_file, "w", encoding="utf-8") as output:
                output.write("#EXTM3U\n\n")
                for item in radios[lang_code]:
                    output.write(f'#EXTINF:-1 tvg-logo="{item[3]}", {item[0]}\n{item[1]}\n')
            print(f"Saved combined playlist: {combined_file}")

        if args.singles:
            # Ensure the output directory exists
            playlist_dir = f"./playlists/{lang_code}/"
            os.makedirs(playlist_dir, exist_ok=True)

            # Create individual M3U8 files per station
            for item in radios[lang_code]:
                station_file = os.path.join(playlist_dir, f"{item[0].replace(' ', '_').replace('/', '_')}.m3u8")
                with open(station_file, "w", encoding="utf-8") as output:
                    output.write("#EXTM3U\n\n")
                    output.write(f'#EXTINF:-1 tvg-logo="{item[3]}", {item[0]}\n{item[1]}\n')
                print(f"Saved playlist for {item[0]}: {station_file}")
    else:
        print(f"No stations found for language code: {lang_code}")

