import json
import urllib.request
import sys


# GitHub API endpoint for the latest BtbN FFmpeg release
API_URL = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"


def get_latest_ffmpeg():
    # 1. Fetch the latest release info
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'AIFactory-Updater'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    tag = data["tag_name"] # e.g., autobuild-2026-10-18-13-05
    
    # 2. Find the LGPL Windows zip
    download_url = ""
    for asset in data["assets"]:
        if asset["name"].endswith("win64-lgpl.zip"):
            download_url = asset["browser_download_url"]
            break
            
    if not download_url:
        print("Error: Could not find win64-lgpl.zip in assets")
        sys.exit(1)


    # Note: BtbN doesn't always provide SHA256 in the API. 
    # For now, we omit it, but the app won't auto-download until we verify it.
    # You can add a checksum here if you download and hash it in the action.
    
    # 3. Build the manifest object
    manifest = {
        "schemaVersion": 1,
        "ffmpeg": {
            "version": tag,
            "url": download_url,
            "sha256": "" # Left blank for now
        }
    }
    
    # 4. Save to file
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest updated to {tag}")


if __name__ == "__main__":
    get_latest_ffmpeg()
3. Create the GitHub Action:
Create .github/workflows/update.yml:
yaml
name: Auto-Update Manifest
on:
  schedule:
    - cron: '0 0 * * *' # Runs every day at midnight
  workflow_dispatch:    # Allows you to run it manually


jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Generate Manifest
        run: python generate_manifest.py
      - name: Commit and Push
        run: |
          git config user.name "GitHub Action"
          git config user.email "action@github.com"
          git add manifest.json
          git commit -m "Auto-update manifest to latest FFmpeg" || exit 0
          git push
Now your manifest is 100% automated. Once a day, GitHub fetches the newest BtbN release and updates manifest.json.
Your app's URL will simply be:
https://raw.githubusercontent.com/YourUsername/aifactory-updates/main/manifest.json
