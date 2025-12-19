#!/usr/bin/env python3
"""
Pokemon Tier List Image Generator
Creates a visual tier list from meta analysis data
"""

from PIL import Image, ImageDraw, ImageFont
import os
import csv

# Tier list configuration - NO LEGENDARIES SEASON
# Format: (pokemon_name, recommended_item)
TIERS = {
    "S": {"color": (255, 127, 127), "pokemon": [
        ("blastoise-mega", "Blastoisinite"),
        ("charizard-mega-y", "Charizardite Y"),
    ]},
    "A": {"color": (255, 191, 127), "pokemon": [
        ("charizard-mega-x", "Charizardite X"),
        ("gardevoir-mega", "Gardevoirite"),
        ("vaporeon", "Life Orb"),
        ("greninja", "Life Orb"),
        ("milotic", "Life Orb"),
        ("garchomp-mega", "Garchompite"),
        ("blastoise", "Life Orb"),
        ("swampert-mega", "Swampertite"),
        ("armarouge", "Life Orb"),
    ]},
    "B": {"color": (255, 255, 127), "pokemon": [
        ("slowbro", "Life Orb"),
        ("slowking", "Life Orb"),
        ("sylveon", "Assault Vest"),
        ("glimmora", "Shuca Berry"),
        ("jolteon", "Life Orb"),
        ("glaceon", "Life Orb"),
        ("clefable", "Life Orb"),
        ("gardevoir", "Life Orb"),
        ("tyranitar-mega", "Tyranitarite"),
        ("excadrill", "Life Orb"),
    ]},
    "C": {"color": (191, 255, 127), "pokemon": [
        ("dragalge", "Life Orb"),
        ("espeon", "Life Orb"),
        ("toxtricity", "Shuca Berry"),
        ("gholdengo", "Life Orb"),
        ("gallade-mega", "Galladite"),
        ("blaziken-mega", "Blazikenite"),
        ("charizard", "Charti Berry"),
        ("lucario", "Life Orb"),
        ("lucario-mega", "Lucarionite"),
        ("gyarados-mega", "Gyaradosite"),
    ]},
    "D": {"color": (127, 255, 255), "pokemon": [
        ("scizor-mega", "Scizorite"),
        ("metagross-mega", "Metagrossite"),
        ("goodra", "Assault Vest"),
        ("noivern", "Life Orb"),
        ("garchomp", "Yache Berry"),
        ("swampert", "Rindo Berry"),
        ("tyranitar", "Chople Berry"),
        ("salamence-mega", "Salamencite"),
    ]},
    "F": {"color": (200, 200, 200), "pokemon": [
        ("ceruledge", "Life Orb"),
        ("scizor", "Occa Berry"),
        ("gallade", "Focus Sash"),
        ("blaziken", "Life Orb"),
        ("annihilape", "Assault Vest"),
        ("gyarados", "Life Orb"),
        ("feraligatr", "Life Orb"),
        ("metagross", "Assault Vest"),
        ("dondozo", "Assault Vest"),
        ("corviknight", "Rocky Helmet"),
        ("dragonite", "Yache Berry"),
        ("salamence", "Yache Berry"),
        ("baxcalibur", "Haban Berry"),
        ("umbreon", "Leftovers"),
    ]},
}

# Image settings
SPRITE_SIZE = 68
ITEM_SIZE = 24  # Size of item icon overlay
TIER_LABEL_WIDTH = 60
PADDING = 4
SPRITES_PER_ROW = 8
IMAGE_DIR = "images"
ITEM_DIR = "images/items"

# Item name to filename mapping
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
    # Mega Stones
    "Charizardite X": "charizardite-x",
    "Charizardite Y": "charizardite-y",
    "Blastoisinite": "blastoisinite",
    "Mewtwonite X": "mewtwonite-x",
    "Mewtwonite Y": "mewtwonite-y",
    "Tyranitarite": "tyranitarite",
    "Salamencite": "salamencite",
    "Metagrossite": "metagrossite",
    "Garchompite": "garchompite",
    "Lucarionite": "lucarionite",
    "Scizorite": "scizorite",
    "Gyaradosite": "gyaradosite",
    "Blazikenite": "blazikenite",
    "Swampertite": "swampertite",
    "Gardevoirite": "gardevoirite",
    "Galladite": "galladite",
    "Latiosite": "latiosite",
    "Latiasite": "latiasite",
    "Dragon Ascent": None,  # No item image for Rayquaza mega
}

def load_sprite(pokemon_name, size=SPRITE_SIZE):
    """Load and resize a Pokemon sprite"""
    path = os.path.join(IMAGE_DIR, f"{pokemon_name}.png")
    if not os.path.exists(path):
        # Create placeholder
        img = Image.new('RGBA', (size, size), (128, 128, 128, 255))
        draw = ImageDraw.Draw(img)
        draw.text((5, size//2 - 5), pokemon_name[:6], fill=(255, 255, 255))
        return img

    try:
        img = Image.open(path).convert('RGBA')
        # Resize maintaining aspect ratio
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        # Create square canvas
        canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        # Center the image
        x = (size - img.width) // 2
        y = (size - img.height) // 2
        canvas.paste(img, (x, y), img)
        return canvas
    except Exception as e:
        print(f"Error loading {pokemon_name}: {e}")
        img = Image.new('RGBA', (size, size), (128, 128, 128, 255))
        return img


def load_item_sprite(item_name, size=ITEM_SIZE):
    """Load and resize an item sprite"""
    filename = ITEM_FILENAME.get(item_name)
    if not filename:
        return None

    path = os.path.join(ITEM_DIR, f"{filename}.png")
    if not os.path.exists(path):
        return None

    try:
        img = Image.open(path).convert('RGBA')
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        print(f"Error loading item {item_name}: {e}")
        return None


def load_sprite_with_item(pokemon_name, item_name, size=SPRITE_SIZE):
    """Load Pokemon sprite with item overlay in bottom-right corner"""
    pokemon_img = load_sprite(pokemon_name, size)

    item_img = load_item_sprite(item_name)
    if item_img:
        # Position item in bottom-right corner
        item_x = size - item_img.width - 2
        item_y = size - item_img.height - 2

        # Create a semi-transparent background for item visibility
        bg = Image.new('RGBA', (item_img.width + 4, item_img.height + 4), (40, 40, 40, 200))
        pokemon_img.paste(bg, (item_x - 2, item_y - 2), bg)

        # Paste the item
        pokemon_img.paste(item_img, (item_x, item_y), item_img)

    return pokemon_img


def create_tier_row(tier_name, tier_data, width):
    """Create a single tier row with item icons merged into sprites"""
    pokemon_list = tier_data["pokemon"]
    color = tier_data["color"]

    # Calculate rows needed
    num_pokemon = len(pokemon_list)
    rows_needed = max(1, (num_pokemon + SPRITES_PER_ROW - 1) // SPRITES_PER_ROW)
    cell_height = SPRITE_SIZE + PADDING * 2

    # Create row image
    total_height = rows_needed * cell_height
    row_img = Image.new('RGB', (width, total_height), (40, 40, 40))
    draw = ImageDraw.Draw(row_img)

    # Draw tier label background
    draw.rectangle([0, 0, TIER_LABEL_WIDTH, total_height], fill=color)

    # Load fonts
    try:
        tier_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        tier_font = ImageFont.load_default()

    # Center the tier letter
    bbox = draw.textbbox((0, 0), tier_name, font=tier_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (TIER_LABEL_WIDTH - text_width) // 2
    text_y = (total_height - text_height) // 2
    draw.text((text_x, text_y), tier_name, fill=(0, 0, 0), font=tier_font)

    # Draw Pokemon sprites with item icons
    for i, entry in enumerate(pokemon_list):
        # Handle both old format (string) and new format (tuple)
        if isinstance(entry, tuple):
            pokemon, item = entry
        else:
            pokemon, item = entry, ""

        row = i // SPRITES_PER_ROW
        col = i % SPRITES_PER_ROW

        x = TIER_LABEL_WIDTH + PADDING + col * (SPRITE_SIZE + PADDING)
        y = PADDING + row * cell_height

        # Draw sprite with item overlay
        sprite = load_sprite_with_item(pokemon, item)
        row_img.paste(sprite, (x, y), sprite)

    return row_img


def create_tier_list():
    """Create the full tier list image"""
    # Calculate dimensions
    width = TIER_LABEL_WIDTH + PADDING + SPRITES_PER_ROW * (SPRITE_SIZE + PADDING) + PADDING

    # Create header
    header_height = 80
    header = Image.new('RGB', (width, header_height), (30, 30, 30))
    draw = ImageDraw.Draw(header)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    draw.text((20, 15), "Pokemon Legend ZA - No Legendaries Season", fill=(255, 255, 255), font=title_font)
    draw.text((20, 50), "4P Battle Royale | Mega Allowed | Water Meta | Nash Equilibrium", fill=(180, 180, 180), font=subtitle_font)

    # Create tier rows
    tier_rows = []
    for tier_name, tier_data in TIERS.items():
        row = create_tier_row(tier_name, tier_data, width)
        tier_rows.append(row)

    # Calculate total height
    total_height = header_height + sum(row.height for row in tier_rows) + 40  # 40 for footer

    # Create final image
    final_img = Image.new('RGB', (width, total_height), (30, 30, 30))

    # Paste header
    final_img.paste(header, (0, 0))

    # Paste tier rows
    y_offset = header_height
    for row in tier_rows:
        final_img.paste(row, (0, y_offset))
        y_offset += row.height

    # Add footer/disclaimer
    draw = ImageDraw.Draw(final_img)
    try:
        footer_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        footer_font = ImageFont.load_default()

    disclaimer = "Disclaimer: Analysis may not reflect actual game mechanics"
    draw.text((20, total_height - 25), disclaimer, fill=(120, 120, 120), font=footer_font)

    return final_img


def main():
    print("Generating Tier List Image...")

    # Check if images directory exists
    if not os.path.exists(IMAGE_DIR):
        print(f"Error: {IMAGE_DIR} directory not found. Run image_crawler.py first.")
        return

    # Create tier list
    tier_list = create_tier_list()

    # Save
    output_path = "tierlist.png"
    tier_list.save(output_path, "PNG")
    print(f"Saved to {output_path}")

    # Also save a smaller version for README
    small = tier_list.copy()
    small.thumbnail((800, 800), Image.Resampling.LANCZOS)
    small.save("tierlist_preview.png", "PNG")
    print("Saved preview to tierlist_preview.png")


if __name__ == "__main__":
    main()
