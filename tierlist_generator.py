#!/usr/bin/env python3
"""
Pokemon Tier List Image Generator
Creates a visual tier list from meta analysis data
"""

from PIL import Image, ImageDraw, ImageFont
import os
import csv

# Tier list configuration (based on meta_analyzer.py output)
# Updated with: Berries counter 4x weakness once, Rayquaza Delta Stream
TIERS = {
    "S": {"color": (255, 127, 127), "pokemon": ["kyogre"]},
    "A": {"color": (255, 191, 127), "pokemon": ["groudon", "volcanion", "keldeo", "vaporeon", "greninja", "milotic", "xerneas", "blastoise"]},
    "B": {"color": (255, 255, 127), "pokemon": ["armarouge", "darkrai", "sylveon", "excadrill", "mewtwo", "clefable", "glimmora", "jolteon", "rayquaza", "glaceon", "gardevoir", "espeon", "slowbro", "slowking", "gholdengo"]},
    "C": {"color": (191, 255, 127), "pokemon": ["yveltal", "magearna", "heatran", "genesect", "dragalge", "lucario", "latios", "latias", "toxtricity", "charizard"]},
    "D": {"color": (127, 255, 255), "pokemon": ["garchomp", "zygarde", "swampert", "hoopa", "zeraora", "marshadow", "goodra", "noivern", "cobalion", "terrakion", "virizion", "blaziken", "gallade", "ceruledge"]},
    "F": {"color": (200, 200, 200), "pokemon": ["tyranitar", "dragonite", "salamence", "annihilape", "baxcalibur", "dondozo", "melmetal", "steelix", "aggron", "corviknight", "feraligatr", "metagross", "scizor", "umbreon"]},
}

# Image settings
SPRITE_SIZE = 68
TIER_LABEL_WIDTH = 60
PADDING = 4
SPRITES_PER_ROW = 10
IMAGE_DIR = "images"

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
    """Create a single tier row"""
    pokemon_list = tier_data["pokemon"]
    color = tier_data["color"]

    # Calculate rows needed
    num_pokemon = len(pokemon_list)
    rows_needed = max(1, (num_pokemon + SPRITES_PER_ROW - 1) // SPRITES_PER_ROW)
    row_height = SPRITE_SIZE + PADDING * 2

    # Create row image
    total_height = rows_needed * row_height
    row_img = Image.new('RGB', (width, total_height), (40, 40, 40))
    draw = ImageDraw.Draw(row_img)

    # Draw tier label background
    draw.rectangle([0, 0, TIER_LABEL_WIDTH, total_height], fill=color)

    # Draw tier label text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
    except:
        font = ImageFont.load_default()

    # Center the tier letter
    bbox = draw.textbbox((0, 0), tier_name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (TIER_LABEL_WIDTH - text_width) // 2
    text_y = (total_height - text_height) // 2
    draw.text((text_x, text_y), tier_name, fill=(0, 0, 0), font=font)

    # Draw Pokemon sprites
    for i, pokemon in enumerate(pokemon_list):
        row = i // SPRITES_PER_ROW
        col = i % SPRITES_PER_ROW

        x = TIER_LABEL_WIDTH + PADDING + col * (SPRITE_SIZE + PADDING)
        y = PADDING + row * row_height

        sprite = load_sprite(pokemon)
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
