#!/usr/bin/env python3
"""
Pokemon Tier List Image Generator
Creates a visual tier list from meta analysis data
"""

from PIL import Image, ImageDraw, ImageFont
import os
import csv

# Tier list configuration (based on meta_analyzer.py output)
# Updated with: AoE size scales with power (Eruption = huge radius)
# Format: (pokemon_name, recommended_item)
TIERS = {
    "S": {"color": (255, 127, 127), "pokemon": [
        ("kyogre", "Blue Orb"),
        ("volcanion", "Life Orb"),
    ]},
    "A": {"color": (255, 191, 127), "pokemon": [
        ("groudon", "Red Orb"),
        ("armarouge", "Life Orb"),
        ("keldeo", "Life Orb"),
        ("vaporeon", "Life Orb"),
        ("greninja", "Assault Vest"),
        ("milotic", "Assault Vest"),
        ("blastoise", "Assault Vest"),
        ("slowbro", "Assault Vest"),
        ("slowking", "Assault Vest"),
        ("xerneas", "Life Orb"),
        ("heatran", "Shuca Berry"),
    ]},
    "B": {"color": (255, 255, 127), "pokemon": [
        ("charizard", "Charti Berry"),
        ("sylveon", "Assault Vest"),
        ("darkrai", "Life Orb"),
        ("mewtwo", "Life Orb"),
        ("glimmora", "Shuca Berry"),
        ("clefable", "Life Orb"),
        ("glaceon", "Life Orb"),
        ("jolteon", "Life Orb"),
        ("rayquaza", "Life Orb"),
        ("toxtricity", "Shuca Berry"),
        ("gardevoir", "Focus Sash"),
        ("excadrill", "Life Orb"),
    ]},
    "C": {"color": (191, 255, 127), "pokemon": [
        ("espeon", "Life Orb"),
        ("gholdengo", "Assault Vest"),
        ("yveltal", "Life Orb"),
        ("magearna", "Assault Vest"),
        ("genesect", "Occa Berry"),
        ("dragalge", "Assault Vest"),
        ("lucario", "Life Orb"),
        ("latios", "Life Orb"),
        ("latias", "Assault Vest"),
    ]},
    "D": {"color": (127, 255, 255), "pokemon": [
        ("garchomp", "Yache Berry"),
        ("zygarde", "Yache Berry"),
        ("swampert", "Rindo Berry"),
        ("hoopa", "Kasib Berry"),
        ("zeraora", "Life Orb"),
        ("marshadow", "Life Orb"),
        ("goodra", "Assault Vest"),
        ("noivern", "Life Orb"),
        ("cobalion", "Shuca Berry"),
        ("terrakion", "Chople Berry"),
        ("virizion", "Life Orb"),
        ("blaziken", "Life Orb"),
        ("gallade", "Focus Sash"),
        ("ceruledge", "Life Orb"),
    ]},
    "F": {"color": (200, 200, 200), "pokemon": [
        ("tyranitar", "Chople Berry"),
        ("dragonite", "Yache Berry"),
        ("salamence", "Yache Berry"),
        ("annihilape", "Assault Vest"),
        ("baxcalibur", "Life Orb"),
        ("dondozo", "Assault Vest"),
        ("melmetal", "Assault Vest"),
        ("steelix", "Shuca Berry"),
        ("aggron", "Shuca Berry"),
        ("corviknight", "Rocky Helmet"),
        ("feraligatr", "Life Orb"),
        ("metagross", "Assault Vest"),
        ("scizor", "Occa Berry"),
        ("umbreon", "Leftovers"),
    ]},
}

# Image settings
SPRITE_SIZE = 68
ITEM_LABEL_HEIGHT = 14
TIER_LABEL_WIDTH = 60
PADDING = 4
SPRITES_PER_ROW = 8  # Reduced to fit item labels
IMAGE_DIR = "images"

# Item short names for display
ITEM_SHORT = {
    "Blue Orb": "BlueOrb",
    "Red Orb": "RedOrb",
    "Life Orb": "LifeOrb",
    "Assault Vest": "AV",
    "Focus Sash": "Sash",
    "Yache Berry": "Yache",
    "Shuca Berry": "Shuca",
    "Charti Berry": "Charti",
    "Chople Berry": "Chople",
    "Kasib Berry": "Kasib",
    "Occa Berry": "Occa",
    "Rindo Berry": "Rindo",
    "Rocky Helmet": "Helmet",
    "Leftovers": "Lefties",
    "Expert Belt": "ExBelt",
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


def create_tier_row(tier_name, tier_data, width):
    """Create a single tier row with item labels"""
    pokemon_list = tier_data["pokemon"]
    color = tier_data["color"]

    # Calculate rows needed
    num_pokemon = len(pokemon_list)
    rows_needed = max(1, (num_pokemon + SPRITES_PER_ROW - 1) // SPRITES_PER_ROW)
    cell_height = SPRITE_SIZE + ITEM_LABEL_HEIGHT + PADDING * 2

    # Create row image
    total_height = rows_needed * cell_height
    row_img = Image.new('RGB', (width, total_height), (40, 40, 40))
    draw = ImageDraw.Draw(row_img)

    # Draw tier label background
    draw.rectangle([0, 0, TIER_LABEL_WIDTH, total_height], fill=color)

    # Load fonts
    try:
        tier_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        item_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
    except:
        tier_font = ImageFont.load_default()
        item_font = ImageFont.load_default()

    # Center the tier letter
    bbox = draw.textbbox((0, 0), tier_name, font=tier_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (TIER_LABEL_WIDTH - text_width) // 2
    text_y = (total_height - text_height) // 2
    draw.text((text_x, text_y), tier_name, fill=(0, 0, 0), font=tier_font)

    # Draw Pokemon sprites with item labels
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

        # Draw sprite
        sprite = load_sprite(pokemon)
        row_img.paste(sprite, (x, y), sprite)

        # Draw item label below sprite
        if item:
            item_short = ITEM_SHORT.get(item, item[:8])
            item_bbox = draw.textbbox((0, 0), item_short, font=item_font)
            item_width = item_bbox[2] - item_bbox[0]
            item_x = x + (SPRITE_SIZE - item_width) // 2
            item_y = y + SPRITE_SIZE + 1
            draw.text((item_x, item_y), item_short, fill=(200, 200, 200), font=item_font)

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

    draw.text((20, 15), "Pokemon Legend ZA - 4P Battle Royale Meta", fill=(255, 255, 255), font=title_font)
    draw.text((20, 50), "Real-time | Kill-based | AoE favored | Size matters", fill=(180, 180, 180), font=subtitle_font)

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
