# Readme-mrotom3u

This script generates M3U playlists for radio stations based on language codes. The M3U playlists can either be combined into one file per language or created as individual files for each radio station.

## Usage Examples

### 1. To create a combined M3U playlist for a specific language (e.g., 'uk'):

```bash
python3 mrotom3u.py uk --combined
```
This will create a single combined M3U file for the 'uk' language.

### 2. To create individual M3U playlists for each station under the 'uk' language:

```bash
python3 mrotom3u.py uk --singles
```
This will create separate M3U files for each radio station in a directory `./playlists/uk/`.

### 3. To create combined M3U playlists for multiple languages (e.g., 'uk', 'fr', and 'es'):

```bash
python3 mrotom3u.py uk fr es --combined
```
This will create one combined M3U file for each of the specified languages.

### 4. To create individual M3U playlists for each station in multiple languages (e.g., 'uk', 'fr', 'es'):

```bash
python3 mrotom3u.py uk fr es --singles
```
This will create individual M3U files for each radio station in separate directories for each language.

### 5. To create both combined and individual M3U playlists for the 'uk' language:

```bash
python3 mrotom3u.py uk --singles --combined
```
This will create both a combined M3U file for the 'uk' language and individual M3U files for each radio station in the `./playlists/uk/` directory.

### 6. To create combined M3U playlists for **all available languages**:

```bash
python3 mrotom3u.py --combined
```
This will create a combined M3U file for every language in the list of available languages.

### 7. To create individual M3U playlists for each station for **all available languages**:

```bash
python3 mrotom3u.py --singles
```
This will create individual M3U files for each radio station, organizing them into directories based on language codes.

## Notes:
- If no language codes are provided, the script will process all available languages by default.
- You **must** specify either `--singles` or `--combined` (or both) in the command. If neither is provided, the script will display this usage message.

