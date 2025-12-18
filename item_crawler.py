#!/usr/bin/env python3
"""
Item Image Crawler - Downloads item sprites from Serebii
"""

import requests
import os
import time

# Items used in the tier list
ITEMS = {
    "blue-orb": "Blue Orb",
    "red-orb": "Red Orb",
    "life-orb": "Life Orb",
    "assault-vest": "Assault Vest",
    "focus-sash": "Focus Sash",
    "yache-berry": "Yache Berry",
    "shuca-berry": "Shuca Berry",
    "charti-berry": "Charti Berry",
    "chople-berry": "Chople Berry",
    "kasib-berry": "Kasib Berry",
    "occa-berry": "Occa Berry",
    "rindo-berry": "Rindo Berry",
    "haban-berry": "Haban Berry",
    "rocky-helmet": "Rocky Helmet",
    "leftovers": "Leftovers",
    "expert-belt": "Expert Belt",
    # Mega Stones
    "charizardite-x": "Charizardite X",
    "charizardite-y": "Charizardite Y",
    "blastoisinite": "Blastoisinite",
    "mewtwonite-x": "Mewtwonite X",
    "mewtwonite-y": "Mewtwonite Y",
    "tyranitarite": "Tyranitarite",
    "salamencite": "Salamencite",
    "metagrossite": "Metagrossite",
    "garchompite": "Garchompite",
    "lucarionite": "Lucarionite",
    "scizorite": "Scizorite",
    "gyaradosite": "Gyaradosite",
    "blazikenite": "Blazikenite",
    "swampertite": "Swampertite",
    "gardevoirite": "Gardevoirite",
    "galladite": "Galladite",
    "latiosite": "Latiosite",
    "latiasite": "Latiasite",
    "rayquazite": "Rayquazite",
}

# Map item names to filenames
ITEM_FILENAME = {
    "Blue Orb": "blue-orb",
    "Red Orb": "red-orb",
    "Life Orb": "life-orb",
    "Assault Vest": "assault-vest",
    "Focus Sash": "focus-sash",
    "Yache Berry": "yache-berry",
    "Shuca Berry": "shuca-berry",
    "Charti Berry": "charti-berry",
    "Chople Berry": "chople-berry",
    "Kasib Berry": "kasib-berry",
    "Occa Berry": "occa-berry",
    "Rindo Berry": "rindo-berry",
    "Haban Berry": "haban-berry",
    "Rocky Helmet": "rocky-helmet",
    "Leftovers": "leftovers",
    "Expert Belt": "expert-belt",
}

OUTPUT_DIR = "images/items"

def download_item_image(item_id, item_name):
    """Download item image from multiple sources"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_path = os.path.join(OUTPUT_DIR, f"{item_id}.png")
    if os.path.exists(output_path):
        print(f"  Already have {item_name}")
        return True

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Convert item_id to different formats
    # e.g., "life-orb" -> "lifeorb", "Life_Orb"
    item_nospace = item_id.replace("-", "")
    item_underscore = item_id.replace("-", "_")
    item_caps = item_name.replace(" ", "_")

    urls = [
        f"https://www.serebii.net/itemdex/sprites/sv/{item_id}.png",
        f"https://www.serebii.net/itemdex/sprites/pgl/{item_id}.png",
        f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/{item_id}.png",
        f"https://img.pokemondb.net/sprites/items/{item_id}.png",
    ]

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and len(response.content) > 100:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  Downloaded {item_name}")
                return True
        except Exception as e:
            continue

    print(f"  Failed to download {item_name}")
    return False


def main():
    print("Downloading item images...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    success = 0
    failed = []

    for item_id, item_name in ITEMS.items():
        if download_item_image(item_id, item_name):
            success += 1
        else:
            failed.append(item_name)
        time.sleep(0.3)

    print(f"\nDownloaded {success}/{len(ITEMS)} items")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
