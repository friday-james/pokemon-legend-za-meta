#!/usr/bin/env python3
"""
Pokemon Image Crawler - Downloads Pokemon sprites from Serebii
"""

import os
import requests
import time
import csv

# Pokemon to download (top meta Pokemon)
META_POKEMON = [
    # S Tier
    "kyogre",
    # A Tier
    "volcanion", "groudon", "keldeo", "vaporeon", "greninja", "milotic",
    # B Tier
    "xerneas", "toxtricity", "heatran", "slowbro", "slowking", "armarouge",
    "charizard", "darkrai", "sylveon",
    # C Tier
    "clefable", "jolteon", "glaceon", "mewtwo", "excadrill", "garchomp",
    "espeon", "gholdengo", "rayquaza", "latios", "hoopa", "yveltal",
    "magearna", "gardevoir", "dragalge", "blastoise", "genesect", "lucario",
    "zeraora", "marshadow", "goodra", "zygarde", "tyranitar", "dragonite",
    "salamence", "annihilape", "baxcalibur", "noivern", "tinkaton", "scizor",
    "cobalion", "terrakion", "virizion", "blaziken", "gallade", "ceruledge",
    "corviknight", "aggron", "steelix", "skarmory", "umbreon", "feraligatr",
    "swampert", "metagross", "latias", "eelektross", "glimmora", "dondozo",
    "melmetal", "gyarados"
]

# Mega evolutions to download
MEGA_POKEMON = {
    "charizard-mega-x": ["mega-charizard-x", "charizard-megax"],
    "charizard-mega-y": ["mega-charizard-y", "charizard-megay"],
    "blastoise-mega": ["mega-blastoise", "blastoise-mega"],
    "mewtwo-mega-x": ["mega-mewtwo-x", "mewtwo-megax"],
    "mewtwo-mega-y": ["mega-mewtwo-y", "mewtwo-megay"],
    "tyranitar-mega": ["mega-tyranitar", "tyranitar-mega"],
    "salamence-mega": ["mega-salamence", "salamence-mega"],
    "metagross-mega": ["mega-metagross", "metagross-mega"],
    "garchomp-mega": ["mega-garchomp", "garchomp-mega"],
    "lucario-mega": ["mega-lucario", "lucario-mega"],
    "scizor-mega": ["mega-scizor", "scizor-mega"],
    "gyarados-mega": ["mega-gyarados", "gyarados-mega"],
    "blaziken-mega": ["mega-blaziken", "blaziken-mega"],
    "swampert-mega": ["mega-swampert", "swampert-mega"],
    "gardevoir-mega": ["mega-gardevoir", "gardevoir-mega"],
    "gallade-mega": ["mega-gallade", "gallade-mega"],
    "latios-mega": ["mega-latios", "latios-mega"],
    "latias-mega": ["mega-latias", "latias-mega"],
    "rayquaza-mega": ["mega-rayquaza", "rayquaza-mega"],
}

# Serebii sprite URL patterns
SPRITE_URLS = [
    "https://www.serebii.net/scarletviolet/pokemon/new/{name}.png",
    "https://www.serebii.net/swordshield/pokemon/{name}.png",
    "https://www.serebii.net/pokemon/art/{dex:03d}.png",
]

# Pokemon name to dex number mapping for fallback
POKEMON_DEX = {
    "bulbasaur": 1, "ivysaur": 2, "venusaur": 3, "charmander": 4, "charmeleon": 5,
    "charizard": 6, "squirtle": 7, "wartortle": 8, "blastoise": 9,
    "mewtwo": 150, "mew": 151,
    "kyogre": 382, "groudon": 383, "rayquaza": 384,
    "garchomp": 445, "lucario": 448,
    "darkrai": 491,
    "zygarde": 718, "xerneas": 716, "yveltal": 717,
    "volcanion": 721,
    "greninja": 658, "sylveon": 700, "goodra": 706,
    "tyranitar": 248, "dragonite": 149, "salamence": 373,
    "metagross": 376, "latias": 380, "latios": 381,
    "jolteon": 135, "vaporeon": 134, "flareon": 136, "espeon": 196, "umbreon": 197,
    "glaceon": 471, "leafeon": 470,
    "heatran": 485, "magearna": 801, "marshadow": 802, "zeraora": 807,
    "genesect": 649, "keldeo": 647, "cobalion": 638, "terrakion": 639, "virizion": 640,
    "milotic": 350, "slowbro": 80, "slowking": 199, "clefable": 36,
    "scizor": 212, "steelix": 208, "skarmory": 227, "aggron": 306,
    "blaziken": 257, "swampert": 260, "feraligatr": 160,
    "excadrill": 530, "hoopa": 720,
    "gardevoir": 282, "gallade": 475,
}

def download_image(pokemon_name, output_dir="images"):
    """Download Pokemon sprite"""
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{pokemon_name}.png")
    if os.path.exists(output_path):
        print(f"  {pokemon_name}: Already exists")
        return True

    # Try different URL patterns
    urls_to_try = [
        f"https://www.serebii.net/scarletviolet/pokemon/new/{pokemon_name}.png",
        f"https://www.serebii.net/swordshield/pokemon/{pokemon_name}.png",
        f"https://www.serebii.net/pokemon/art/{pokemon_name}.png",
        f"https://img.pokemondb.net/artwork/large/{pokemon_name}.jpg",
        f"https://img.pokemondb.net/sprites/home/normal/{pokemon_name}.png",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for url in urls_to_try:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and len(response.content) > 1000:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"  {pokemon_name}: Downloaded from {url.split('/')[2]}")
                return True
        except Exception as e:
            continue

    print(f"  {pokemon_name}: FAILED")
    return False


def download_mega_image(pokemon_name, alt_names, output_dir="images"):
    """Download Mega Pokemon sprite"""
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{pokemon_name}.png")
    if os.path.exists(output_path):
        print(f"  {pokemon_name}: Already exists")
        return True

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Try all name variations
    for name in [pokemon_name] + alt_names:
        urls_to_try = [
            f"https://img.pokemondb.net/artwork/large/{name}.jpg",
            f"https://img.pokemondb.net/sprites/home/normal/{name}.png",
            f"https://www.serebii.net/pokemon/art/{name}.png",
            f"https://www.serebii.net/xy/pokemon/{name.replace('-', '')}.png",
        ]

        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200 and len(response.content) > 1000:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"  {pokemon_name}: Downloaded")
                    return True
            except Exception:
                continue

    print(f"  {pokemon_name}: FAILED")
    return False


def main():
    print("Pokemon Image Crawler")
    print("=" * 50)

    success = 0
    failed = []

    # Download regular Pokemon
    print("\nDownloading regular Pokemon...")
    for pokemon in META_POKEMON:
        if download_image(pokemon):
            success += 1
        else:
            failed.append(pokemon)
        time.sleep(0.3)  # Be nice to servers

    print(f"\nRegular Pokemon: {success}/{len(META_POKEMON)}")

    # Download Mega evolutions
    print("\nDownloading Mega evolutions...")
    mega_success = 0
    mega_failed = []

    for mega_name, alt_names in MEGA_POKEMON.items():
        if download_mega_image(mega_name, alt_names):
            mega_success += 1
        else:
            mega_failed.append(mega_name)
        time.sleep(0.3)

    print(f"\nMega Pokemon: {mega_success}/{len(MEGA_POKEMON)}")

    if failed:
        print(f"Failed regular: {', '.join(failed)}")
    if mega_failed:
        print(f"Failed mega: {', '.join(mega_failed)}")


if __name__ == "__main__":
    main()
