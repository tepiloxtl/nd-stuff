#!/usr/bin/python3
import requests
import json
import base64
import time
import random
import os
import argparse

# Define headers for the HTTP request
mroheaders = {
    'authority': 'myradioonline.pl',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://myradioonline.pl',
    'referer': 'https://myradioonline.pl/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    'x-requested-with': 'XMLHttpRequest',
}

# Initial payload for POST request
mrodata = {
    'ord': '1',
    'actP': '1',
    'type': '',
}

# Available language codes
all_languages = ['at', 'cl', 'co', 'cz', 'de', 'es', 'fr', 'hu', 'ie', 'it', 'mx', 'nl', 'pe', 'pl', 'ro', 'sk', 'uk']

# Argument parser for command-line input
parser = argparse.ArgumentParser(
    description="""Generate M3U playlists for specified language(s) or all if none are provided.

Usage examples:

1. To create a combined M3U playlist for a specific language (e.g., 'uk'):
   python3 mrotom3u.py uk --combined
   This will create a single combined M3U file for the 'uk' language.

2. To create individual M3U playlists for each station under the 'uk' language:
   python3 mrotom3u.py uk --singles
   This will create separate M3U files for each radio station in a directory './playlists/uk/'.

3. To create combined M3U playlists for multiple languages (e.g., 'uk', 'fr', and 'es'):
   python3 mrotom3u.py uk fr es --combined
   This will create one combined M3U file for each of the specified languages.

4. To create individual M3U playlists for each station in multiple languages (e.g., 'uk', 'fr', 'es'):
   python3 mrotom3u.py uk fr es --singles
   This will create individual M3U files for each radio station in separate directories for each language.

5. To create both combined and individual M3U playlists for the 'uk' language:
   python3 mrotom3u.py uk --singles --combined
   This will create both a combined M3U file for the 'uk' language and individual M3U files for each radio station in the './playlists/uk/' directory.

6. To create combined M3U playlists for **all available languages**:
   python3 mrotom3u.py --combined
   This will create a combined M3U file for every language in the list of available languages.

7. To create individual M3U playlists for each station for **all available languages**:
   python3 mrotom3u.py --singles
   This will create individual M3U files for each radio station, organizing them into directories based on language codes.

Notes:
- If no language codes are provided, the script will process all available languages by default.
- You **must** specify either `--singles` or `--combined` (or both) in the command. If neither is provided, the script will display this usage message.
""",
    formatter_class=argparse.RawTextHelpFormatter  # Ensures that the formatting (like new lines) is kept intact
)

parser.add_argument('langs', nargs='*', help="Language codes (e.g., 'uk', 'es', 'fr'). If omitted, all languages are processed.")
parser.add_argument('--combined', action='store_true', help="Create a single combined M3U8 file per language.")
parser.add_argument('--singles', action='store_true', help="Create individual M3U8 files per station in lang-code directory.")
args = parser.parse_args()

# If no arguments are passed, show usage message
if not (args.langs or args.singles or args.combined):
    print("\nYou must specify at least one of the options: --singles or --combined.")
    parser.print_help()
    exit(1)

# If no language codes are provided, use all languages
langs = args.langs if args.langs else all_languages

# Validate user input for language codes
invalid_langs = [lang for lang in langs if lang not in all_languages]
if invalid_langs:
    print(f"Error: Invalid language codes: {', '.join(invalid_langs)}.")
    print(f"Valid options: {', '.join(all_languages)}")
    exit(1)

radios = {}
actP = 1

# Fetch all available radio station data
while True:
    print(f"Fetching page {actP}...")
    mrodata['actP'] = actP
    try:
        response = requests.post('https://myradioonline.pl/get-radio-list', headers=mroheaders, data=mrodata)
        response.raise_for_status()  # Raise an error for bad status codes
        thing = response.json()

        for item in thing["radios"]["list"]:
            name = item["r_name"]
            url = base64.b64decode(item["rsu_url"]).decode('utf-8')
            lang = item["lng"]
            logo = item["settings"]["list_45"].replace("list_45.jpg", "play_250_250.webp")

            if lang not in radios:
                radios[lang] = []

            radios[lang].append([name, url, lang, logo])

        if not thing["moreP"]:
            break

        actP += 1
        time.sleep(random.randint(1, 5))  # Random delay to avoid request throttling
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {actP}: {e}")
        break

# Create M3U files for the specified languages
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
        
        elif args.singles:
            # Create individual M3U8 files per station in the lang-code directory
            lang_dir = f"./playlists/{lang_code}"
            os.makedirs(lang_dir, exist_ok=True)
            
            for item in radios[lang_code]:
                # Create M3U8 file for each station under the lang-code directory
                station_file = os.path.join(lang_dir, f"{item[0].replace(' ', '_').replace('/', '_')}.m3u8")
                with open(station_file, "w", encoding="utf-8") as output:
                    output.write("#EXTM3U\n\n")
                    output.write(f'#EXTINF:-1 tvg-logo="{item[3]}", {item[0]}\n{item[1]}\n')
                print(f"Saved individual playlist for {item[0]}: {station_file}")
                
        else:
            # Ensure the output directory exists for combined playlists
            playlist_dir = f"./playlists/{lang_code}"
            os.makedirs(playlist_dir, exist_ok=True)
            
            # Create a combined M3U8 file for the language
            combined_file = os.path.join(playlist_dir, f"{lang_code}.m3u8")
            with open(combined_file, "w", encoding="utf-8") as output:
                output.write("#EXTM3U\n\n")
                for item in radios[lang_code]:
                    output.write(f'#EXTINF:-1 tvg-logo="{item[3]}", {item[0]}\n{item[1]}\n')
            print(f"Saved combined playlist for {lang_code}: {combined_file}")
    else:
        print(f"No stations found for language code: {lang_code}")

