#!/usr/bin/env python3
"""
Pokemon Moveset Crawler for Serebii.net
Crawls Pokemon from Scarlet/Violet Pokedex and extracts their movesets
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re

# Pokemon list with dex numbers from the HP stat page
POKEMON_DATA = [
    ("Zygarde", "718"), ("Dondozo", "977"), ("Wigglytuff", "040"), ("Melmetal", "809"),
    ("Vaporeon", "134"), ("Xerneas", "716"), ("Yveltal", "717"), ("Gogoat", "673"),
    ("Aurorus", "699"), ("Throh", "538"), ("Musharna", "518"), ("Jigglypuff", "039"),
    ("Baxcalibur", "998"), ("Amoonguss", "591"), ("Emboar", "500"), ("Excadrill", "530"),
    ("Annihilape", "979"), ("Stunfisk", "618"), ("Garchomp", "445"), ("Hippowdon", "450"),
    ("Mewtwo", "150"), ("Kangaskhan", "115"), ("Rayquaza", "384"), ("Audino", "531"),
    ("Aromatisse", "683"), ("Tyranitar", "248"), ("Swampert", "260"), ("Swalot", "317"),
    ("Kyogre", "382"), ("Groudon", "383"), ("Meloetta", "648"), ("Garganacl", "934"),
    ("Corviknight", "823"), ("Crabominable", "740"), ("Clefable", "036"), ("Slowbro", "080"),
    ("Gyarados", "130"), ("Umbreon", "197"), ("Slowking", "199"), ("Milotic", "350"),
    ("Salamence", "373"), ("Krookodile", "553"), ("Pangoro", "675"), ("Sylveon", "700"),
    ("Avalugg", "713"), ("Dragonite", "149"), ("Heatran", "485"), ("Cobalion", "638"),
    ("Terrakion", "639"), ("Virizion", "640"), ("Keldeo", "647"), ("Machamp", "068"),
    ("Slowpoke", "079"), ("Igglybuff", "174"), ("Ampharos", "181"), ("Abomasnow", "460"),
    ("Pignite", "499"), ("Goodra", "706"), ("Marshadow", "802"), ("Arctibax", "997"),
    ("Golurk", "623"), ("Chesnaught", "652"), ("Zeraora", "807"), ("Gholdengo", "1000"),
    ("Pyroar", "668"), ("Malamar", "687"), ("Feraligatr", "160"), ("Crobat", "169"),
    ("Porygon2", "233"), ("Staraptor", "398"), ("Porygon-Z", "474"), ("Eelektross", "604"),
    ("Diggersby", "660"), ("Trevenant", "709"), ("Noivern", "715"), ("Palossand", "770"),
    ("Overqwil", "904"), ("Armarouge", "936"), ("Tinkaton", "959"), ("Pidgeot", "018"),
    ("Glimmora", "970"), ("Slurpuff", "685"), ("Tyrantrum", "697"), ("Squawkabilly", "931"),
    ("Flamigo", "973"), ("Venusaur", "003"), ("Machoke", "067"), ("Victreebel", "071"),
    ("Aerodactyl", "142"), ("Meganium", "154"), ("Heracross", "214"), ("Blaziken", "257"),
    ("Grumpig", "326"), ("Glalie", "362"), ("Metagross", "376"), ("Latias", "380"),
    ("Latios", "381"), ("Garbodor", "569"), ("Cryogonal", "615"), ("Vivillon", "666"),
    ("Hoopa", "720"), ("Volcanion", "721"), ("Magearna", "801"), ("Grapploct", "853"),
    ("Mr. Rime", "866"), ("Mabosstiff", "943"), ("Blastoise", "009"), ("Charizard", "006"),
    ("Talonflame", "663"), ("Florges", "671"), ("Spritzee", "682"), ("Hawlucha", "701"),
    ("Drampa", "780"), ("Amaura", "698"), ("Munna", "517"), ("Golbat", "042"),
    ("Steelix", "208"), ("Houndoom", "229"), ("Altaria", "334"), ("Chimecho", "358"),
    ("Simisage", "512"), ("Simisear", "514"), ("Simipour", "516"), ("Sawk", "539"),
    ("Delphox", "655"), ("Furfrou", "676"), ("Golisopod", "768"), ("Toxtricity", "849"),
    ("Ceruledge", "937"), ("Meowstic", "678"), ("Floette", "670"), ("Zangoose", "335"),
    ("Seviper", "336"), ("Greninja", "658"), ("Barbaracle", "689"), ("Houndstone", "972"),
    ("Vanilluxe", "584"), ("Genesect", "649"), ("Clawitzer", "693"), ("Clefairy", "035"),
    ("Machop", "066"), ("Scyther", "123"), ("Ariados", "168"), ("Flaaffy", "180"),
    ("Scizor", "212"), ("Pupitar", "247"), ("Sceptile", "254"), ("Marshtomp", "259"),
    ("Aggron", "306"), ("Manectric", "310"), ("Gulpin", "316"), ("Sharpedo", "319"),
    ("Camerupt", "323"), ("Lucario", "448"), ("Froslass", "478"), ("Darkrai", "491"),
    ("Thievul", "828"), ("Perrserker", "863"), ("Kleavor", "900"), ("Cyclizar", "967"),
    ("Gardevoir", "282"), ("Gabite", "444"), ("Hippopotas", "449"), ("Gallade", "475"),
    ("Sliggoo", "705"), ("Corvisquire", "822"), ("Tatsugiri", "978"), ("Pancham", "674"),
    ("Dedenne", "702"), ("Skiddo", "672"), ("Beedrill", "015"), ("Persian", "053"),
    ("Primeape", "057"), ("Weepinbell", "070"), ("Pinsir", "127"), ("Jolteon", "135"),
    ("Flareon", "136"), ("Porygon", "137"), ("Croconaw", "159"), ("Espeon", "196"),
    ("Qwilfish", "211"), ("Skarmory", "227"), ("Absol", "359"), ("Shelgon", "372"),
    ("Lopunny", "428"), ("Leafeon", "470"), ("Glaceon", "471"), ("Tepig", "498"),
    ("Scrafty", "560"), ("Eelektrik", "603"), ("Dragalge", "691"), ("Gourgeist", "711"),
    ("Falinks", "870"), ("Scovillain", "952"), ("Tinkatuff", "958"), ("Frigibax", "996"),
    ("Foongus", "590")
]

BASE_URL = "https://www.serebii.net/pokedex-sv/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_pokemon_page(dex_number):
    """Fetch a Pokemon's page from Serebii"""
    url = f"{BASE_URL}{dex_number}.shtml"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_moves(html, pokemon_name):
    """Parse moves from a Pokemon's page"""
    if not html:
        return []

    soup = BeautifulSoup(html, 'html.parser')
    moves = set()

    # Find all tables that might contain move data
    tables = soup.find_all('table')

    for table in tables:
        # Look for move tables by checking for move-related headers
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                # Look for links to attack pages (moves)
                links = cell.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if '/attackdex-sv/' in href:
                        move_name = link.get_text(strip=True)
                        if move_name and len(move_name) > 1:
                            moves.add(move_name)

    return list(moves)

def crawl_all_pokemon():
    """Crawl all Pokemon and their movesets"""
    results = []
    total = len(POKEMON_DATA)

    for i, (name, dex) in enumerate(POKEMON_DATA):
        print(f"[{i+1}/{total}] Fetching {name} (#{dex})...")

        html = fetch_pokemon_page(dex)
        moves = parse_moves(html, name)

        results.append({
            'name': name,
            'dex_number': dex,
            'moves': moves
        })

        # Be polite to the server
        time.sleep(0.5)

    return results

def save_to_csv(results, filename='pokemon_movesets.csv'):
    """Save results to CSV file"""
    # Create two CSV files:
    # 1. Summary with all moves as comma-separated
    # 2. Detailed with one row per pokemon-move combination

    # Summary CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pokemon', 'Dex_Number', 'Move_Count', 'All_Moves'])

        for pokemon in results:
            moves_str = '; '.join(sorted(pokemon['moves']))
            writer.writerow([
                pokemon['name'],
                pokemon['dex_number'],
                len(pokemon['moves']),
                moves_str
            ])

    print(f"Saved summary to {filename}")

    # Detailed CSV (one row per move)
    detailed_filename = filename.replace('.csv', '_detailed.csv')
    with open(detailed_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pokemon', 'Dex_Number', 'Move'])

        for pokemon in results:
            for move in sorted(pokemon['moves']):
                writer.writerow([
                    pokemon['name'],
                    pokemon['dex_number'],
                    move
                ])

    print(f"Saved detailed list to {detailed_filename}")

def main():
    print("Starting Pokemon Moveset Crawler...")
    print(f"Will crawl {len(POKEMON_DATA)} Pokemon from Serebii.net")
    print()

    results = crawl_all_pokemon()

    print()
    print("Saving results to CSV...")
    save_to_csv(results)

    # Print summary
    total_moves = sum(len(p['moves']) for p in results)
    print()
    print(f"Done! Crawled {len(results)} Pokemon with {total_moves} total move entries")

if __name__ == "__main__":
    main()
