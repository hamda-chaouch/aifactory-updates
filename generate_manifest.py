import json
import urllib.request
import sys


# GitHub API endpoint for the latest BtbN FFmpeg release
API_URL = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"


def get_latest_ffmpeg():
    # Fetch a list of recent releases instead of just "latest"
    API_URL = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases"
    print("Fetching recent releases info...")
    
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'AIFactory-Updater'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    
    # Find the first release that actually has an "autobuild-" tag
    tag = ""
    download_url = ""
    for release in data:
        if release["tag_name"].startswith("autobuild-"):
            tag = release["tag_name"]
            for asset in release["assets"]:
                if asset["name"].endswith("win64-lgpl.zip"):
                    download_url = asset["browser_download_url"]
                    break
            if download_url:
                break
                
    if not download_url:
        print("Error: Could not find autobuild win64-lgpl.zip")
        sys.exit(1)

    print(f"Downloading {download_url} to calculate SHA256...")
    zip_req = urllib.request.Request(download_url, headers={'User-Agent': 'AIFactory-Updater'})
    with urllib.request.urlopen(zip_req) as zip_resp:
        zip_data = zip_resp.read()
        sha256_hash = hashlib.sha256(zip_data).hexdigest().upper()

    manifest = {
        "schemaVersion": 1,
        "ffmpeg": {
            "version": tag,
            "url": download_url,
            "sha256": sha256_hash
        }
    }
    
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest updated to {tag}")


if __name__ == "__main__":
    get_latest_ffmpeg()
