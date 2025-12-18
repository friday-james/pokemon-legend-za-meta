#!/usr/bin/env python3
"""
Pokemon Meta Analyzer v5 - Real-Time 4-Player Battle Royale
Rules:
- 4-player battle royale format
- Real-time combat (sniping, dodging, hiding)
- Kill-based scoring (most last hits wins)
- Pokemon can respawn
- Physical attacks: FAST cast but must move to target (RISKY - can be sniped/ganked)
- Special attacks: RANGED/safe but SLOW cast (can be dodged/interrupted)
- NO priority moves exist
- 3 Pokemon per team
- Only ONE legendary permitted per team
- No native abilities (items OK)
- Items permitted (no repeats)
"""

import csv
from collections import defaultdict

# =============================================================================
# CONFIGURATION
# =============================================================================
TEAM_SIZE = 3

# Real-time battle weights
WEIGHTS = {
    'burst_damage': 0.30,      # Kill-stealing potential (single big hit)
    'range_safety': 0.20,      # Can attack without being ganked
    'aoe_potential': 0.20,     # Hit multiple enemies at once = GOOD
    'mobility': 0.15,          # Repositioning, escape, dodging
    'survivability': 0.10,     # Survive third-party attacks
    'type_matchup': 0.05,      # Type coverage
}
# NOTE: AoE = valuable (hits one area, can catch grouped enemies), Multi-hit = BAD (can dodge between hits)

# Physical vs Special trade-off
# Physical: 1.3x cast speed multiplier (fast) but 0.6x safety (must approach)
# Special:  0.7x cast speed multiplier (slow) but 1.0x safety (ranged)
PHYSICAL_SPEED_MULT = 1.3
PHYSICAL_SAFETY_MULT = 0.6
SPECIAL_SPEED_MULT = 0.7
SPECIAL_SAFETY_MULT = 1.0

# Power vs Cast Time trade-off
# Higher power moves take longer to cast (can be dodged/interrupted)
# Base cast time at 80 power, scales up with power
BASE_POWER = 80
POWER_CAST_PENALTY = 0.005  # 0.5% slower per power point above 80

# AoE Size vs Power
# Higher power AoE = larger radius = more likely to hit clustered enemies
# But also slower cast = can be dodged
# AoE doesn't guarantee multi-hit - enemies can still dodge, hits one area only
# Average hits: 1-2 enemies (when grouped fighting), sometimes 3 if clustered
AOE_SIZE_SCALING = 0.008  # 0.8% larger AoE per power point above base

# =============================================================================
# POKEMON SIZE (affects movement speed - larger = slower, easier to hit)
# =============================================================================
# Size categories: 1=tiny, 2=small, 3=medium, 4=large, 5=huge
# Larger Pokemon: slower movement, bigger hitbox (easier to hit)
POKEMON_SIZE = {
    # Huge (5) - Very slow, easy target
    "Groudon": 5, "Kyogre": 5, "Rayquaza": 5, "Zygarde": 5, "Dondozo": 5,
    "Wailord": 5, "Steelix": 5, "Melmetal": 5, "Rayquaza-Mega": 5,
    # Large (4) - Slow, notable hitbox
    "Tyranitar": 4, "Metagross": 4, "Salamence": 4, "Dragonite": 4, "Garchomp": 4,
    "Gyarados": 4, "Aggron": 4, "Xerneas": 4, "Yveltal": 4,
    "Goodra": 4, "Goodra-Hisui": 4, "Baxcalibur": 4, "Volcanion": 4,
    "Corviknight": 4, "Feraligatr": 4, "Swampert": 4, "Hoopa": 4,
    "Clefable": 4,  # Large in-game model
    # Mega evolutions - Large
    "Tyranitar-Mega": 4, "Metagross-Mega": 4, "Salamence-Mega": 4, "Garchomp-Mega": 4,
    "Gyarados-Mega": 4, "Swampert-Mega": 4, "Mewtwo-Mega-X": 4, "Mewtwo-Mega-Y": 3,
    # Medium (3) - Average
    "Mewtwo": 3,  # Medium sized, not large
    "Blastoise": 3, "Charizard": 3, "Venusaur": 3, "Slowbro": 3, "Slowking": 3,
    "Machamp": 3, "Milotic": 3, "Blaziken": 3, "Lucario": 3, "Gallade": 3,
    "Gardevoir": 3, "Magearna": 3, "Genesect": 3, "Armarouge": 3, "Ceruledge": 3,
    "Heatran": 3, "Excadrill": 3, "Annihilape": 3, "Gholdengo": 3, "Latias": 3,
    "Latios": 3, "Cobalion": 3, "Terrakion": 3, "Virizion": 3, "Keldeo": 3,
    "Scizor": 3, "Skarmory": 3, "Toxtricity": 3, "Dragalge": 3, "Noivern": 3,
    "Marshadow": 3, "Darkrai": 3,
    # Small (2) - Fast, hard to hit
    "Greninja": 2, "Zeraora": 2, "Sylveon": 2, "Vaporeon": 2, "Jolteon": 2,
    "Flareon": 2, "Espeon": 2, "Glaceon": 2, "Umbreon": 2,
    "Tinkaton": 2, "Glimmora": 2, "Eelektross": 2,
    # Tiny (1) - Very fast, very hard to hit
    "Dedenne": 1, "Clefairy": 1,
}
DEFAULT_SIZE = 3  # Medium

# Size multipliers for mobility and hitbox
SIZE_MOBILITY_MULT = {1: 1.4, 2: 1.2, 3: 1.0, 4: 0.8, 5: 0.6}  # Smaller = faster
SIZE_HITBOX_MULT = {1: 0.6, 2: 0.8, 3: 1.0, 4: 1.2, 5: 1.5}    # Larger = easier to hit (bad)

# =============================================================================
# ITEMS (No Choice Band/Specs/Scarf)
# =============================================================================
ITEMS = {
    "Red Orb": {"holder": "Groudon", "effect": "primal", "description": "Primal Groudon"},
    "Blue Orb": {"holder": "Kyogre", "effect": "primal", "description": "Primal Kyogre"},
    "Life Orb": {"effect": "damage_boost", "value": 1.3, "description": "+30% damage"},
    "Expert Belt": {"effect": "super_effective_boost", "value": 1.2, "description": "+20% SE"},
    "Assault Vest": {"effect": "stat_mult", "stat": "SpD", "value": 1.5, "description": "+50% SpD"},
    "Leftovers": {"effect": "recovery", "value": 0.0625, "description": "6.25% HP/turn"},
    "Rocky Helmet": {"effect": "contact_damage", "value": 0.167, "description": "Contact recoil"},
    "Focus Sash": {"effect": "survive_ohko", "description": "Survive OHKO once"},
    "Wide Lens": {"effect": "accuracy", "value": 1.1, "description": "+10% accuracy"},
    "Scope Lens": {"effect": "crit", "value": 1.5, "description": "+crit rate"},
    "Shell Bell": {"effect": "lifesteal", "value": 0.125, "description": "Heal on damage"},
    # Type-resist berries (negate super effective ONCE per spawn)
    "Yache Berry": {"effect": "resist_once", "type": "Ice", "description": "Resist Ice once"},
    "Shuca Berry": {"effect": "resist_once", "type": "Ground", "description": "Resist Ground once"},
    "Charti Berry": {"effect": "resist_once", "type": "Rock", "description": "Resist Rock once"},
    "Chople Berry": {"effect": "resist_once", "type": "Fighting", "description": "Resist Fighting once"},
    "Kasib Berry": {"effect": "resist_once", "type": "Ghost", "description": "Resist Ghost once"},
    "Haban Berry": {"effect": "resist_once", "type": "Dragon", "description": "Resist Dragon once"},
    "Colbur Berry": {"effect": "resist_once", "type": "Dark", "description": "Resist Dark once"},
    "Roseli Berry": {"effect": "resist_once", "type": "Fairy", "description": "Resist Fairy once"},
    "Occa Berry": {"effect": "resist_once", "type": "Fire", "description": "Resist Fire once"},
    "Passho Berry": {"effect": "resist_once", "type": "Water", "description": "Resist Water once"},
    "Rindo Berry": {"effect": "resist_once", "type": "Grass", "description": "Resist Grass once"},
    "Wacan Berry": {"effect": "resist_once", "type": "Electric", "description": "Resist Electric once"},
}

# Pokemon with special abilities that work in this game
SPECIAL_ABILITIES = {
    # Rayquaza's Delta Stream: Flying-type loses weaknesses to Ice, Electric, Rock
    "Rayquaza": {"ability": "Delta Stream", "effect": "remove_flying_weakness"},
}

ITEM_SYNERGIES = {
    "Groudon": ["Red Orb", "Passho Berry", "Assault Vest"],  # 4x Water
    "Kyogre": ["Blue Orb", "Life Orb", "Assault Vest"],
    "Magearna": ["Assault Vest", "Leftovers", "Life Orb"],
    "Mewtwo": ["Life Orb", "Expert Belt", "Focus Sash"],
    "Goodra": ["Assault Vest", "Leftovers", "Life Orb"],
    "Goodra-Hisui": ["Assault Vest", "Leftovers", "Life Orb"],
    "Metagross": ["Assault Vest", "Life Orb", "Expert Belt"],
    "Tyranitar": ["Assault Vest", "Chople Berry", "Life Orb"],  # 4x Fighting
    "Dragonite": ["Yache Berry", "Life Orb", "Assault Vest"],  # 4x Ice
    "Salamence": ["Yache Berry", "Life Orb", "Assault Vest"],  # 4x Ice
    "Garchomp": ["Yache Berry", "Life Orb", "Expert Belt"],  # 4x Ice
    "Rayquaza": ["Life Orb", "Expert Belt", "Assault Vest"],  # Delta Stream removes 4x Ice!
    "Zygarde": ["Yache Berry", "Leftovers", "Assault Vest"],  # 4x Ice
    "Baxcalibur": ["Haban Berry", "Life Orb", "Assault Vest"],  # 4x weakness options
    "Charizard": ["Charti Berry", "Life Orb", "Expert Belt"],  # 4x Rock
    "Volcanion": ["Shuca Berry", "Life Orb", "Assault Vest"],  # 4x Ground (if not for unique typing)
    "Heatran": ["Shuca Berry", "Assault Vest", "Life Orb"],  # 4x Ground
    "Toxtricity": ["Shuca Berry", "Life Orb", "Expert Belt"],  # 4x Ground
    "Swampert": ["Rindo Berry", "Assault Vest", "Life Orb"],  # 4x Grass
}

PRIMAL_STATS = {
    "Groudon": (100, 180, 160, 150, 90, 90),
    "Kyogre": (100, 150, 90, 180, 160, 90),
}

PRIMAL_TYPES = {
    "Groudon": ("Ground", "Fire"),
    "Kyogre": ("Water", None),
}

# Mega Evolution Data
MEGA_STATS = {
    # (HP, Atk, Def, SpA, SpD, Spe)
    "Charizard-Mega-X": (78, 130, 111, 130, 85, 100),  # Dragon/Fire
    "Charizard-Mega-Y": (78, 104, 78, 159, 115, 100),  # Fire/Flying
    "Blastoise-Mega": (79, 103, 120, 135, 115, 78),   # Water
    "Mewtwo-Mega-X": (106, 190, 100, 154, 100, 130),  # Psychic/Fighting
    "Mewtwo-Mega-Y": (106, 150, 70, 194, 120, 140),   # Psychic
    "Tyranitar-Mega": (100, 164, 150, 95, 120, 71),   # Rock/Dark
    "Salamence-Mega": (95, 145, 130, 120, 90, 120),   # Dragon/Flying
    "Metagross-Mega": (80, 145, 150, 105, 110, 110),  # Steel/Psychic
    "Garchomp-Mega": (108, 170, 115, 120, 95, 92),    # Dragon/Ground
    "Lucario-Mega": (70, 145, 88, 140, 70, 112),      # Fighting/Steel
    "Scizor-Mega": (70, 150, 140, 65, 100, 75),       # Bug/Steel
    "Gyarados-Mega": (95, 155, 109, 70, 130, 81),     # Water/Dark
    "Blaziken-Mega": (80, 160, 80, 130, 80, 100),     # Fire/Fighting
    "Swampert-Mega": (100, 150, 110, 95, 110, 70),    # Water/Ground
    "Gardevoir-Mega": (68, 85, 65, 165, 135, 100),    # Psychic/Fairy
    "Gallade-Mega": (68, 165, 95, 65, 115, 110),      # Psychic/Fighting
    "Latios-Mega": (80, 130, 100, 160, 120, 110),     # Dragon/Psychic
    "Latias-Mega": (80, 100, 120, 140, 150, 110),     # Dragon/Psychic
    "Rayquaza-Mega": (105, 180, 100, 180, 100, 115),  # Dragon/Flying (via Dragon Ascent)
}

MEGA_TYPES = {
    "Charizard-Mega-X": ("Fire", "Dragon"),
    "Charizard-Mega-Y": ("Fire", "Flying"),
    "Blastoise-Mega": ("Water", None),
    "Mewtwo-Mega-X": ("Psychic", "Fighting"),
    "Mewtwo-Mega-Y": ("Psychic", None),
    "Tyranitar-Mega": ("Rock", "Dark"),
    "Salamence-Mega": ("Dragon", "Flying"),
    "Metagross-Mega": ("Steel", "Psychic"),
    "Garchomp-Mega": ("Dragon", "Ground"),
    "Lucario-Mega": ("Fighting", "Steel"),
    "Scizor-Mega": ("Bug", "Steel"),
    "Gyarados-Mega": ("Water", "Dark"),
    "Blaziken-Mega": ("Fire", "Fighting"),
    "Swampert-Mega": ("Water", "Ground"),
    "Gardevoir-Mega": ("Psychic", "Fairy"),
    "Gallade-Mega": ("Psychic", "Fighting"),
    "Latios-Mega": ("Dragon", "Psychic"),
    "Latias-Mega": ("Dragon", "Psychic"),
    "Rayquaza-Mega": ("Dragon", "Flying"),
}

MEGA_ITEMS = {
    "Charizard-Mega-X": "Charizardite X",
    "Charizard-Mega-Y": "Charizardite Y",
    "Blastoise-Mega": "Blastoisinite",
    "Mewtwo-Mega-X": "Mewtwonite X",
    "Mewtwo-Mega-Y": "Mewtwonite Y",
    "Tyranitar-Mega": "Tyranitarite",
    "Salamence-Mega": "Salamencite",
    "Metagross-Mega": "Metagrossite",
    "Garchomp-Mega": "Garchompite",
    "Lucario-Mega": "Lucarionite",
    "Scizor-Mega": "Scizorite",
    "Gyarados-Mega": "Gyaradosite",
    "Blaziken-Mega": "Blazikenite",
    "Swampert-Mega": "Swampertite",
    "Gardevoir-Mega": "Gardevoirite",
    "Gallade-Mega": "Galladite",
    "Latios-Mega": "Latiosite",
    "Latias-Mega": "Latiasite",
    "Rayquaza-Mega": "Dragon Ascent",  # No item needed, just the move
}

# Base Pokemon for each mega
MEGA_BASE = {
    "Charizard-Mega-X": "Charizard",
    "Charizard-Mega-Y": "Charizard",
    "Blastoise-Mega": "Blastoise",
    "Mewtwo-Mega-X": "Mewtwo",
    "Mewtwo-Mega-Y": "Mewtwo",
    "Tyranitar-Mega": "Tyranitar",
    "Salamence-Mega": "Salamence",
    "Metagross-Mega": "Metagross",
    "Garchomp-Mega": "Garchomp",
    "Lucario-Mega": "Lucario",
    "Scizor-Mega": "Scizor",
    "Gyarados-Mega": "Gyarados",
    "Blaziken-Mega": "Blaziken",
    "Swampert-Mega": "Swampert",
    "Gardevoir-Mega": "Gardevoir",
    "Gallade-Mega": "Gallade",
    "Latios-Mega": "Latios",
    "Latias-Mega": "Latias",
    "Rayquaza-Mega": "Rayquaza",
}

# =============================================================================
# POKEMON DATA
# =============================================================================
POKEMON_TYPES = {
    "Zygarde": ("Dragon", "Ground"),
    "Dondozo": ("Water", None),
    "Melmetal": ("Steel", None),
    "Vaporeon": ("Water", None),
    "Xerneas": ("Fairy", None),
    "Yveltal": ("Dark", "Flying"),
    "Baxcalibur": ("Dragon", "Ice"),
    "Excadrill": ("Ground", "Steel"),
    "Annihilape": ("Fighting", "Ghost"),
    "Garchomp": ("Dragon", "Ground"),
    "Mewtwo": ("Psychic", None),
    "Rayquaza": ("Dragon", "Flying"),
    "Tyranitar": ("Rock", "Dark"),
    "Swampert": ("Water", "Ground"),
    "Kyogre": ("Water", None),
    "Groudon": ("Ground", None),
    "Corviknight": ("Flying", "Steel"),
    "Clefable": ("Fairy", None),
    "Slowbro": ("Water", "Psychic"),
    "Gyarados": ("Water", "Flying"),
    "Umbreon": ("Dark", None),
    "Slowking": ("Water", "Psychic"),
    "Milotic": ("Water", None),
    "Salamence": ("Dragon", "Flying"),
    "Sylveon": ("Fairy", None),
    "Dragonite": ("Dragon", "Flying"),
    "Heatran": ("Fire", "Steel"),
    "Goodra": ("Dragon", None),
    "Goodra-Hisui": ("Dragon", "Steel"),  # Only 2 weaknesses!
    "Marshadow": ("Fighting", "Ghost"),
    "Gholdengo": ("Steel", "Ghost"),
    "Feraligatr": ("Water", None),
    "Eelektross": ("Electric", None),
    "Noivern": ("Flying", "Dragon"),
    "Armarouge": ("Fire", "Psychic"),
    "Tinkaton": ("Fairy", "Steel"),
    "Glimmora": ("Rock", "Poison"),
    "Metagross": ("Steel", "Psychic"),
    "Latias": ("Dragon", "Psychic"),
    "Latios": ("Dragon", "Psychic"),
    "Magearna": ("Steel", "Fairy"),
    "Volcanion": ("Fire", "Water"),
    "Blastoise": ("Water", None),
    "Charizard": ("Fire", "Flying"),
    "Greninja": ("Water", "Dark"),
    "Genesect": ("Bug", "Steel"),
    "Lucario": ("Fighting", "Steel"),
    "Darkrai": ("Dark", None),
    "Zeraora": ("Electric", None),
    "Gardevoir": ("Psychic", "Fairy"),
    "Gallade": ("Psychic", "Fighting"),
    "Dragalge": ("Poison", "Dragon"),
    "Espeon": ("Psychic", None),
    "Jolteon": ("Electric", None),
    "Glaceon": ("Ice", None),
    "Steelix": ("Steel", "Ground"),
    "Aggron": ("Steel", "Rock"),
    "Skarmory": ("Steel", "Flying"),
    "Scizor": ("Bug", "Steel"),
    "Ceruledge": ("Fire", "Ghost"),
    "Toxtricity": ("Electric", "Poison"),
    "Blaziken": ("Fire", "Fighting"),
    "Hoopa": ("Psychic", "Ghost"),
    "Cobalion": ("Steel", "Fighting"),
    "Terrakion": ("Rock", "Fighting"),
    "Virizion": ("Grass", "Fighting"),
    "Keldeo": ("Water", "Fighting"),
}

LEGENDARY_POKEMON = {
    "Zygarde", "Xerneas", "Yveltal", "Mewtwo", "Rayquaza", "Kyogre", "Groudon",
    "Latias", "Latios", "Heatran", "Cobalion", "Terrakion", "Virizion",
    "Keldeo", "Darkrai", "Marshadow", "Zeraora", "Hoopa", "Volcanion", "Magearna",
    "Genesect", "Melmetal"
}

BASE_STATS = {
    # (HP, Atk, Def, SpA, SpD, Spe)
    "Zygarde": (216, 100, 121, 91, 95, 95),
    "Dondozo": (150, 100, 115, 65, 65, 35),
    "Melmetal": (135, 143, 143, 80, 65, 34),
    "Vaporeon": (130, 65, 60, 110, 95, 65),
    "Xerneas": (126, 131, 95, 131, 98, 99),
    "Yveltal": (126, 131, 95, 131, 98, 99),
    "Baxcalibur": (115, 145, 92, 75, 86, 87),
    "Excadrill": (110, 135, 60, 50, 65, 88),
    "Annihilape": (110, 115, 80, 50, 90, 90),
    "Garchomp": (108, 130, 95, 80, 85, 102),
    "Mewtwo": (106, 110, 90, 154, 90, 130),
    "Rayquaza": (105, 150, 90, 150, 90, 95),
    "Tyranitar": (100, 134, 110, 95, 100, 61),
    "Swampert": (100, 110, 90, 85, 90, 60),
    "Kyogre": (100, 100, 90, 150, 140, 90),
    "Groudon": (100, 150, 140, 100, 90, 90),
    "Corviknight": (98, 87, 105, 53, 85, 67),
    "Clefable": (95, 70, 73, 95, 90, 60),
    "Slowbro": (95, 75, 110, 100, 80, 30),
    "Gyarados": (95, 125, 79, 60, 100, 81),
    "Umbreon": (95, 65, 110, 60, 130, 65),
    "Slowking": (95, 75, 80, 100, 110, 30),
    "Milotic": (95, 60, 79, 100, 125, 81),
    "Salamence": (95, 135, 80, 110, 80, 100),
    "Sylveon": (95, 65, 65, 110, 130, 60),
    "Dragonite": (91, 134, 95, 100, 100, 80),
    "Heatran": (91, 90, 106, 130, 106, 77),
    "Goodra": (90, 100, 70, 110, 150, 80),
    "Goodra-Hisui": (80, 100, 100, 110, 150, 60),  # Dragon/Steel
    "Marshadow": (90, 125, 80, 90, 90, 125),
    "Gholdengo": (87, 60, 95, 133, 91, 84),
    "Feraligatr": (85, 105, 100, 79, 83, 78),
    "Eelektross": (85, 115, 80, 105, 80, 50),
    "Noivern": (85, 70, 80, 97, 80, 123),
    "Armarouge": (85, 60, 100, 125, 80, 75),
    "Tinkaton": (85, 75, 77, 70, 105, 94),
    "Glimmora": (83, 55, 90, 130, 81, 86),
    "Metagross": (80, 135, 130, 95, 90, 70),
    "Latias": (80, 80, 90, 110, 130, 110),
    "Latios": (80, 90, 80, 130, 110, 110),
    "Magearna": (80, 95, 115, 130, 115, 65),
    "Volcanion": (80, 110, 120, 130, 90, 70),
    "Blastoise": (79, 83, 100, 85, 105, 78),
    "Charizard": (78, 84, 78, 109, 85, 100),
    "Greninja": (72, 95, 67, 103, 71, 122),
    "Genesect": (71, 120, 95, 120, 95, 99),
    "Lucario": (70, 110, 70, 115, 70, 90),
    "Darkrai": (70, 90, 90, 135, 90, 125),
    "Zeraora": (88, 112, 75, 102, 80, 143),
    "Gardevoir": (68, 65, 65, 125, 115, 80),
    "Gallade": (68, 125, 65, 65, 115, 80),
    "Dragalge": (65, 75, 90, 97, 123, 44),
    "Espeon": (65, 65, 60, 130, 95, 110),
    "Jolteon": (65, 65, 60, 110, 95, 130),
    "Glaceon": (65, 60, 110, 130, 95, 65),
    "Steelix": (75, 85, 200, 55, 65, 30),
    "Aggron": (70, 110, 180, 60, 60, 50),
    "Skarmory": (65, 80, 140, 40, 70, 70),
    "Scizor": (70, 130, 100, 55, 80, 65),
    "Ceruledge": (75, 125, 80, 60, 100, 85),
    "Toxtricity": (75, 98, 70, 114, 70, 75),
    "Blaziken": (80, 120, 70, 110, 70, 80),
    "Hoopa": (80, 110, 60, 150, 130, 70),
    "Cobalion": (91, 90, 129, 90, 72, 108),
    "Terrakion": (91, 129, 90, 72, 90, 108),
    "Virizion": (91, 90, 72, 90, 129, 108),
    "Keldeo": (91, 72, 90, 129, 90, 108),
}

TYPE_DEFENSE = {
    "Normal": {"weak": ["Fighting"], "resist": [], "immune": ["Ghost"]},
    "Fire": {"weak": ["Water", "Ground", "Rock"], "resist": ["Fire", "Grass", "Ice", "Bug", "Steel", "Fairy"], "immune": []},
    "Water": {"weak": ["Electric", "Grass"], "resist": ["Fire", "Water", "Ice", "Steel"], "immune": []},
    "Electric": {"weak": ["Ground"], "resist": ["Electric", "Flying", "Steel"], "immune": []},
    "Grass": {"weak": ["Fire", "Ice", "Poison", "Flying", "Bug"], "resist": ["Water", "Electric", "Grass", "Ground"], "immune": []},
    "Ice": {"weak": ["Fire", "Fighting", "Rock", "Steel"], "resist": ["Ice"], "immune": []},
    "Fighting": {"weak": ["Flying", "Psychic", "Fairy"], "resist": ["Bug", "Rock", "Dark"], "immune": []},
    "Poison": {"weak": ["Ground", "Psychic"], "resist": ["Grass", "Fighting", "Poison", "Bug", "Fairy"], "immune": []},
    "Ground": {"weak": ["Water", "Grass", "Ice"], "resist": ["Poison", "Rock"], "immune": ["Electric"]},
    "Flying": {"weak": ["Electric", "Ice", "Rock"], "resist": ["Grass", "Fighting", "Bug"], "immune": ["Ground"]},
    "Psychic": {"weak": ["Bug", "Ghost", "Dark"], "resist": ["Fighting", "Psychic"], "immune": []},
    "Bug": {"weak": ["Fire", "Flying", "Rock"], "resist": ["Grass", "Fighting", "Ground"], "immune": []},
    "Rock": {"weak": ["Water", "Grass", "Fighting", "Ground", "Steel"], "resist": ["Normal", "Fire", "Poison", "Flying"], "immune": []},
    "Ghost": {"weak": ["Ghost", "Dark"], "resist": ["Poison", "Bug"], "immune": ["Normal", "Fighting"]},
    "Dragon": {"weak": ["Ice", "Dragon", "Fairy"], "resist": ["Fire", "Water", "Electric", "Grass"], "immune": []},
    "Dark": {"weak": ["Fighting", "Bug", "Fairy"], "resist": ["Ghost", "Dark"], "immune": ["Psychic"]},
    "Steel": {"weak": ["Fire", "Fighting", "Ground"], "resist": ["Normal", "Grass", "Ice", "Flying", "Psychic", "Bug", "Rock", "Dragon", "Steel", "Fairy"], "immune": ["Poison"]},
    "Fairy": {"weak": ["Poison", "Steel"], "resist": ["Fighting", "Bug", "Dark"], "immune": ["Dragon"]},
}

# Meta-relevant attack types (for coverage value)
META_ATTACK_TYPES = {
    "Ice": 1.5, "Fighting": 1.4, "Ground": 1.3, "Fire": 1.2, "Fairy": 1.2,
    "Rock": 1.1, "Electric": 1.0, "Water": 1.0, "Dark": 1.0, "Ghost": 1.0,
    "Psychic": 0.9, "Steel": 0.9, "Dragon": 0.9, "Grass": 0.8, "Flying": 0.8,
    "Poison": 0.7, "Bug": 0.6, "Normal": 0.5,
}

# =============================================================================
# HIGH-POWER MOVES (for burst damage calculation)
# In real-time:
#   - AoE = valuable (hits one area, can catch 1-3 enemies if grouped/fighting)
#   - Multi-hit = BAD (same target, multiple hits = can dodge between)
#   - Single big hit = GOOD (instant burst for kill-steal)
# =============================================================================
# Format: (Move, Power, is_aoe, is_multi_hit)
# is_aoe=True = hits multiple enemies = BONUS
# is_multi_hit=True = multiple hits on same target = PENALTY
SPECIAL_MOVES = {
    "Psychic": [("Psystrike", 100, False, False), ("Psychic", 90, False, False), ("Psyshock", 80, False, False)],
    "Water": [("Origin Pulse", 110, True, False), ("Surf", 90, True, False), ("Hydro Pump", 110, False, False), ("Scald", 80, False, False)],
    "Fire": [("Eruption", 150, True, False), ("Heat Wave", 95, True, False), ("Lava Plume", 80, True, False), ("Fire Blast", 110, False, False), ("Overheat", 130, False, False), ("Flamethrower", 90, False, False)],
    "Electric": [("Discharge", 80, True, False), ("Thunder", 110, False, False), ("Thunderbolt", 90, False, False)],
    "Ice": [("Blizzard", 110, True, False), ("Ice Beam", 90, False, False), ("Freeze-Dry", 70, False, False)],
    "Dragon": [("Draco Meteor", 130, False, False), ("Dragon Pulse", 85, False, False)],
    "Ghost": [("Shadow Ball", 80, False, False), ("Hex", 65, False, False)],
    "Dark": [("Dark Pulse", 80, False, False), ("Snarl", 55, True, False)],
    "Fairy": [("Dazzling Gleam", 80, True, False), ("Moonblast", 95, False, False)],
    "Ground": [("Earth Power", 90, False, False), ("Scorching Sands", 70, False, False)],
    "Grass": [("Leaf Storm", 130, False, False), ("Energy Ball", 90, False, False), ("Giga Drain", 75, False, False)],
    "Steel": [("Flash Cannon", 80, False, False), ("Steel Beam", 140, False, False)],
    "Fighting": [("Focus Blast", 120, False, False), ("Aura Sphere", 80, False, False)],
    "Poison": [("Sludge Wave", 95, True, False), ("Sludge Bomb", 90, False, False)],
    "Rock": [("Power Gem", 80, False, False), ("Meteor Beam", 120, False, False)],
    "Flying": [("Hurricane", 110, False, False), ("Air Slash", 75, False, False)],
    "Bug": [("Bug Buzz", 90, False, False)],
    "Normal": [("Boomburst", 140, True, False), ("Hyper Voice", 90, True, False), ("Hyper Beam", 150, False, False)],
}

PHYSICAL_MOVES = {
    # Format: (Move, Power, is_aoe, is_multi_hit, is_gap_closer)
    # Gap closers: moves that help close distance safely (Dig, Fly, Phantom Force, etc.)
    # AoE physical = good, Multi-hit = bad, Gap closer = safer approach
    "Dragon": [("Outrage", 120, False, False, False), ("Dragon Claw", 80, False, False, False), ("Glaive Rush", 120, False, False, True), ("Scale Shot", 75, False, True, False)],
    "Fighting": [("Close Combat", 120, False, False, False), ("Superpower", 120, False, False, False), ("Drain Punch", 75, False, False, False)],
    "Ground": [("Earthquake", 100, True, False, False), ("Precipice Blades", 120, True, False, False), ("Bulldoze", 60, True, False, False), ("High Horsepower", 95, False, False, False), ("Dig", 80, False, False, True)],
    "Steel": [("Meteor Mash", 90, False, False, False), ("Iron Head", 80, False, False, False), ("Heavy Slam", 100, False, False, True)],  # Heavy Slam = gap closer (body slam style)
    "Rock": [("Rock Slide", 75, True, False, False), ("Stone Edge", 100, False, False, False), ("Head Smash", 150, False, False, True)],  # Head Smash = charge in
    "Dark": [("Knock Off", 97, False, False, False), ("Crunch", 80, False, False, False), ("Throat Chop", 80, False, False, False), ("Sucker Punch", 70, False, False, True)],
    "Fire": [("Flare Blitz", 120, False, False, True), ("Fire Punch", 75, False, False, False)],  # Flare Blitz = charge in
    "Ice": [("Icicle Crash", 85, False, False, False), ("Ice Punch", 75, False, False, False), ("Triple Axel", 120, False, True, False)],
    "Ghost": [("Poltergeist", 110, False, False, False), ("Phantom Force", 90, False, False, True), ("Shadow Claw", 70, False, False, False)],  # Phantom Force = vanish then hit
    "Bug": [("Megahorn", 120, False, False, False), ("X-Scissor", 80, False, False, False), ("Lunge", 80, False, False, True)],  # Lunge = gap closer
    "Flying": [("Brave Bird", 120, False, False, True), ("Acrobatics", 110, False, False, True), ("Fly", 90, False, False, True), ("Dual Wingbeat", 80, False, True, False)],  # Flying moves = gap closers
    "Electric": [("Wild Charge", 90, False, False, True), ("Thunder Punch", 75, False, False, False)],  # Wild Charge = charge in
    "Grass": [("Wood Hammer", 120, False, False, False), ("Leaf Blade", 90, False, False, False), ("Power Whip", 120, False, False, False), ("Bullet Seed", 75, False, True, False)],
    "Poison": [("Gunk Shot", 120, False, False, False), ("Poison Jab", 80, False, False, False)],
    "Psychic": [("Zen Headbutt", 80, False, False, True)],  # Headbutt = charge in
    "Fairy": [("Play Rough", 90, False, False, False)],
    "Water": [("Wave Crash", 120, False, False, True), ("Liquidation", 85, False, False, False), ("Waterfall", 80, False, False, True), ("Aqua Jet", 40, False, False, True)],  # Wave Crash/Waterfall = charge in
    "Normal": [("Double-Edge", 120, False, False, True), ("Body Slam", 85, False, False, True), ("Return", 102, False, False, False), ("Extreme Speed", 80, False, False, True)],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_type_weaknesses(type1, type2=None, pokemon_name=None):
    """Calculate all type weaknesses, resistances, and immunities
    Also considers special abilities like Rayquaza's Delta Stream
    """
    weaknesses, resistances, immunities = {}, {}, set()

    # Check for special abilities
    has_delta_stream = False
    if pokemon_name and pokemon_name in SPECIAL_ABILITIES:
        ability = SPECIAL_ABILITIES[pokemon_name]
        if ability.get("effect") == "remove_flying_weakness":
            has_delta_stream = True

    for attack_type in TYPE_DEFENSE.keys():
        mult = 1.0
        if attack_type in TYPE_DEFENSE[type1]["weak"]: mult *= 2
        elif attack_type in TYPE_DEFENSE[type1]["resist"]: mult *= 0.5
        elif attack_type in TYPE_DEFENSE[type1]["immune"]: mult = 0

        if type2:
            if attack_type in TYPE_DEFENSE[type2]["weak"]: mult *= 2
            elif attack_type in TYPE_DEFENSE[type2]["resist"]: mult *= 0.5
            elif attack_type in TYPE_DEFENSE[type2]["immune"]: mult = 0

        # Delta Stream: Flying-type loses weakness to Ice, Electric, Rock
        if has_delta_stream and type2 == "Flying":
            if attack_type in ["Ice", "Electric", "Rock"]:
                # Remove the 2x from Flying weakness
                if mult >= 2:
                    mult /= 2  # Neutralize the Flying weakness portion

        if mult == 0: immunities.add(attack_type)
        elif mult >= 4: weaknesses[attack_type] = 4
        elif mult >= 2: weaknesses[attack_type] = 2
        elif mult <= 0.25: resistances[attack_type] = 0.25
        elif mult <= 0.5: resistances[attack_type] = 0.5

    return weaknesses, resistances, immunities


def get_best_moves(pokemon_types, is_physical):
    """Get best moves for a Pokemon based on its type and attack style
    Returns: list of (move_name, type, effective_power, is_aoe, is_multi_hit, role, raw_power)

    Power vs Cast Time: Higher power = longer cast = easier to dodge
    Sweet spot is medium power moves (80-100) that balance damage and speed
    """
    moves = PHYSICAL_MOVES if is_physical else SPECIAL_MOVES
    best_moves = []

    def calc_effective_power(power, is_aoe, is_multi_hit, is_stab, is_gap_closer=False, is_physical=False):
        """Calculate effective power considering cast time penalty, AoE size scaling, and gap closer"""
        eff_power = power

        # STAB bonus
        if is_stab:
            eff_power *= 1.5

        # AoE calculation with size scaling
        # AoE hits one area - doesn't auto-hit everyone, people can dodge
        # Avg case: 1-2 targets when enemies are grouped/fighting
        # Best case: 3 targets if cramped together
        if is_aoe:
            # Base AoE bonus (average 1.5 targets, not guaranteed)
            aoe_bonus = 1.15
            # Higher power = larger AoE radius = more likely to catch grouped enemies
            if power > BASE_POWER:
                aoe_size_bonus = 1.0 + (power - BASE_POWER) * AOE_SIZE_SCALING
                aoe_bonus *= min(1.3, aoe_size_bonus)  # Cap at 30% extra
            elif power < BASE_POWER:
                # Smaller AoE = harder to hit multiple targets
                aoe_size_penalty = 1.0 - (BASE_POWER - power) * 0.004
                aoe_bonus *= max(0.85, aoe_size_penalty)
            eff_power *= aoe_bonus

        # Multi-hit penalty (can be dodged between hits)
        if is_multi_hit:
            eff_power *= 0.5

        # Gap closer bonus for physical moves (Dig, Fly, Phantom Force, Body Slam, etc.)
        # These moves help close distance safely, reducing the risk of physical attacks
        if is_gap_closer and is_physical:
            eff_power *= 1.2  # 20% bonus for safer approach

        # Cast time penalty for high power moves
        # Higher power = longer cast = more dodgeable
        if power > BASE_POWER:
            cast_penalty = 1.0 - (power - BASE_POWER) * POWER_CAST_PENALTY
            eff_power *= max(0.7, cast_penalty)  # Cap at 30% penalty
        elif power < BASE_POWER:
            # Slight bonus for faster low-power moves
            cast_bonus = 1.0 + (BASE_POWER - power) * 0.002
            eff_power *= min(1.1, cast_bonus)

        return eff_power

    # STAB moves first
    for ptype in pokemon_types:
        if ptype and ptype in moves:
            for move_data in moves[ptype]:
                if isinstance(move_data, tuple) and len(move_data) >= 4:
                    move, power, is_aoe, is_multi_hit = move_data[:4]
                    is_gap_closer = move_data[4] if len(move_data) > 4 else False
                    eff_power = calc_effective_power(power, is_aoe, is_multi_hit, is_stab=True,
                                                     is_gap_closer=is_gap_closer, is_physical=is_physical)
                    best_moves.append((move, ptype, eff_power, is_aoe, is_multi_hit, "STAB", power, is_gap_closer))

    # Coverage moves
    for ctype in ["Ice", "Fighting", "Ground", "Fire", "Electric", "Ghost", "Dark"]:
        if ctype in moves and ctype not in pokemon_types:
            for move_data in moves[ctype]:
                if isinstance(move_data, tuple) and len(move_data) >= 4:
                    move, power, is_aoe, is_multi_hit = move_data[:4]
                    is_gap_closer = move_data[4] if len(move_data) > 4 else False
                    if is_multi_hit:
                        continue  # Skip multi-hit moves for coverage
                    eff_power = calc_effective_power(power, is_aoe, is_multi_hit, is_stab=False,
                                                     is_gap_closer=is_gap_closer, is_physical=is_physical)
                    best_moves.append((move, ctype, eff_power, is_aoe, is_multi_hit, "Coverage", power, is_gap_closer))
                    break  # Only one per type

    return sorted(best_moves, key=lambda x: x[2], reverse=True)[:6]


def calculate_burst_score(stats, is_physical):
    """Calculate burst damage potential"""
    hp, atk, def_, spa, spd, spe = stats

    if is_physical:
        # Physical: Fast cast (1.3x) but risky (0.6x safety)
        raw_burst = atk * PHYSICAL_SPEED_MULT * PHYSICAL_SAFETY_MULT
    else:
        # Special: Slow cast (0.7x) but safe (1.0x ranged)
        raw_burst = spa * SPECIAL_SPEED_MULT * SPECIAL_SAFETY_MULT

    return raw_burst


def calculate_mobility_score(stats, pokemon_name):
    """Calculate mobility for repositioning
    Affected by: Speed stat + Size (smaller = faster)
    """
    hp, atk, def_, spa, spd, spe = stats
    size = POKEMON_SIZE.get(pokemon_name, DEFAULT_SIZE)
    size_mult = SIZE_MOBILITY_MULT.get(size, 1.0)
    # Speed matters for dodging and repositioning, size affects movement
    return spe * size_mult


def calculate_survivability(stats, weaknesses, pokemon_name):
    """Calculate ability to survive third-party attacks
    Affected by: Bulk + Size (larger = bigger hitbox = easier to hit = worse)
    """
    hp, atk, def_, spa, spd, spe = stats

    bulk = hp * (def_ + spd) / 200

    # Penalty for weaknesses (more dangerous in 4-player)
    weakness_penalty = 0
    for wtype, mult in weaknesses.items():
        meta_weight = META_ATTACK_TYPES.get(wtype, 1.0)
        if mult == 4:
            weakness_penalty += 50 * meta_weight  # 4x weakness is devastating
        else:
            weakness_penalty += 20 * meta_weight

    # Size penalty: larger = bigger hitbox = easier to hit
    size = POKEMON_SIZE.get(pokemon_name, DEFAULT_SIZE)
    hitbox_mult = SIZE_HITBOX_MULT.get(size, 1.0)
    # Larger Pokemon take more "effective" damage due to being hit more often
    size_penalty = (hitbox_mult - 1.0) * 30  # 0 for medium, negative for small, positive for large

    return max(10, bulk - weakness_penalty - size_penalty)


def calculate_aoe_score(moves):
    """Calculate AoE potential for hitting clustered enemies
    AoE = hits one area, average 1-2 targets when enemies fight each other
    Best case: 3 targets if cramped together
    Multi-hit = BAD (penalized in move selection already)
    """
    aoe_score = 0
    for move_data in moves:
        if len(move_data) >= 5:
            # Format: (move_name, type, eff_power, is_aoe, is_multi_hit, role)
            is_aoe = move_data[3]
            is_multi_hit = move_data[4]
            eff_power = move_data[2]
            if is_aoe and not is_multi_hit:
                # AoE bonus: potential to hit grouped enemies during fights
                aoe_score += eff_power * 0.6
    return aoe_score


# =============================================================================
# MAIN SCORING
# =============================================================================

def comprehensive_score(pokemon_name, base_stats, item_name=None):
    """Calculate comprehensive score for real-time 4-player battle"""

    types = POKEMON_TYPES.get(pokemon_name, ("Normal", None))
    stats = list(base_stats)

    # Apply primal transformation
    if pokemon_name == "Groudon" and item_name == "Red Orb":
        stats = list(PRIMAL_STATS["Groudon"])
        types = PRIMAL_TYPES["Groudon"]
    elif pokemon_name == "Kyogre" and item_name == "Blue Orb":
        stats = list(PRIMAL_STATS["Kyogre"])
        types = PRIMAL_TYPES["Kyogre"]

    # Determine physical vs special
    is_physical = stats[1] > stats[3]

    # Get best moves
    best_moves = get_best_moves(types, is_physical)

    # Calculate sub-scores (pass pokemon_name for special abilities like Delta Stream)
    weaknesses, resistances, immunities = calculate_type_weaknesses(types[0], types[1], pokemon_name)

    burst = calculate_burst_score(stats, is_physical)
    mobility = calculate_mobility_score(stats, pokemon_name)
    survivability = calculate_survivability(stats, weaknesses, pokemon_name)
    aoe = calculate_aoe_score(best_moves)

    # Get size for display
    size = POKEMON_SIZE.get(pokemon_name, DEFAULT_SIZE)
    size_names = {1: "Tiny", 2: "Small", 3: "Medium", 4: "Large", 5: "Huge"}

    # Check if using a resist berry (reduces 4x weakness impact)
    has_resist_berry = False
    if item_name and ITEMS.get(item_name, {}).get("effect") == "resist_once":
        berry_type = ITEMS[item_name].get("type")
        if berry_type in weaknesses:
            has_resist_berry = True

    # Range/safety score
    if is_physical:
        range_safety = 40  # Must approach = risky in 4-player
    else:
        range_safety = 100  # Ranged = safe positioning

    # Type coverage score
    type_score = len(resistances) * 5 + len(immunities) * 15 - len(weaknesses) * 10
    four_x_penalty = sum(50 for m in weaknesses.values() if m == 4)
    # Berry reduces 4x weakness penalty (can survive one hit)
    if has_resist_berry and four_x_penalty > 0:
        four_x_penalty *= 0.5  # Berry halves the penalty
    type_score -= four_x_penalty

    # Special ability bonus
    ability_bonus = 0
    has_special_ability = pokemon_name in SPECIAL_ABILITIES
    if has_special_ability:
        ability_bonus = 30  # Delta Stream etc. are very valuable

    # Item bonus
    item = ITEMS.get(item_name, {})
    item_bonus = 0
    if item.get("effect") == "primal":
        item_bonus = 80
    elif item.get("effect") == "damage_boost":
        item_bonus = 40
    elif item.get("effect") == "survive_ohko":
        item_bonus = 30
    elif item.get("effect") == "stat_mult":
        item_bonus = 25

    # Weighted final score
    final_score = (
        burst * WEIGHTS['burst_damage'] * 2.5 +
        range_safety * WEIGHTS['range_safety'] * 1.5 +
        aoe * WEIGHTS['aoe_potential'] * 1.5 +  # AoE is valuable for 4-player
        mobility * WEIGHTS['mobility'] * 1.0 +
        survivability * WEIGHTS['survivability'] * 1.2 +
        type_score * WEIGHTS['type_matchup'] +
        item_bonus +
        ability_bonus  # Special abilities like Delta Stream
    )

    # Determine best item if not specified
    if not item_name:
        synergies = ITEM_SYNERGIES.get(pokemon_name, ["Life Orb", "Assault Vest", "Expert Belt"])
        item_name = synergies[0]
        item = ITEMS.get(item_name, {})

    has_4x = any(m == 4 for m in weaknesses.values())
    four_x_types = [t for t, m in weaknesses.items() if m == 4]

    # Get special ability info
    special_ability = SPECIAL_ABILITIES.get(pokemon_name, {}).get("ability", None)

    return {
        'name': pokemon_name,
        'score': final_score,
        'stats': tuple(stats),
        'types': types,
        'is_physical': is_physical,
        'size': size,
        'size_name': size_names.get(size, "Medium"),
        'burst': burst,
        'mobility': mobility,
        'survivability': survivability,
        'range_safety': range_safety,
        'aoe': aoe,
        'weaknesses': weaknesses,
        'resistances': resistances,
        'immunities': immunities,
        'has_4x': has_4x,
        'four_x_types': four_x_types,
        'has_resist_berry': has_resist_berry,
        'special_ability': special_ability,
        'is_legendary': pokemon_name in LEGENDARY_POKEMON,
        'item': item_name,
        'item_desc': item.get("description", ""),
        'best_moves': best_moves,
    }


def comprehensive_score_mega(pokemon_name, base_stats, types, item_name, is_legendary):
    """Calculate comprehensive score for mega evolutions"""
    stats = list(base_stats)

    # Determine physical vs special
    is_physical = stats[1] > stats[3]

    # Get best moves
    best_moves = get_best_moves(types, is_physical)

    # Calculate sub-scores
    weaknesses, resistances, immunities = calculate_type_weaknesses(types[0], types[1], pokemon_name)

    burst = calculate_burst_score(stats, is_physical)
    mobility = calculate_mobility_score(stats, pokemon_name)
    survivability = calculate_survivability(stats, weaknesses, pokemon_name)
    aoe = calculate_aoe_score(best_moves)

    # Get size for display
    size = POKEMON_SIZE.get(pokemon_name, DEFAULT_SIZE)
    size_names = {1: "Tiny", 2: "Small", 3: "Medium", 4: "Large", 5: "Huge"}

    # Range/safety score
    if is_physical:
        range_safety = 40  # Must approach = risky in 4-player
    else:
        range_safety = 100  # Ranged = safe positioning

    # Type coverage score
    type_score = len(resistances) * 5 + len(immunities) * 15 - len(weaknesses) * 10
    four_x_penalty = sum(50 for m in weaknesses.values() if m == 4)
    type_score -= four_x_penalty

    # Mega stone = locked item, but gets mega boost
    mega_bonus = 60  # Stat boost from mega evolution

    # Weighted final score
    final_score = (
        burst * WEIGHTS['burst_damage'] * 2.5 +
        range_safety * WEIGHTS['range_safety'] * 1.5 +
        aoe * WEIGHTS['aoe_potential'] * 1.5 +
        mobility * WEIGHTS['mobility'] * 1.0 +
        survivability * WEIGHTS['survivability'] * 1.2 +
        type_score * WEIGHTS['type_matchup'] +
        mega_bonus
    )

    has_4x = any(m == 4 for m in weaknesses.values())
    four_x_types = [t for t, m in weaknesses.items() if m == 4]

    return {
        'name': pokemon_name,
        'score': final_score,
        'stats': tuple(stats),
        'types': types,
        'is_physical': is_physical,
        'size': size,
        'size_name': size_names.get(size, "Medium"),
        'burst': burst,
        'mobility': mobility,
        'survivability': survivability,
        'range_safety': range_safety,
        'aoe': aoe,
        'weaknesses': weaknesses,
        'resistances': resistances,
        'immunities': immunities,
        'has_4x': has_4x,
        'four_x_types': four_x_types,
        'has_resist_berry': False,  # Can't use berry with mega stone
        'special_ability': None,
        'is_legendary': is_legendary,
        'item': item_name,
        'item_desc': "Mega Stone",
        'best_moves': best_moves,
    }


def assign_tier(score, max_score):
    """Assign tier based on score"""
    ratio = score / max_score if max_score > 0 else 0
    if ratio >= 0.90: return "S"
    elif ratio >= 0.75: return "A"
    elif ratio >= 0.60: return "B"
    elif ratio >= 0.45: return "C"
    elif ratio >= 0.30: return "D"
    else: return "F"


def build_optimal_team(pokemon_scores, team_size=3):
    """Build optimal team with unique items"""
    sorted_pokemon = sorted(pokemon_scores, key=lambda x: x['score'], reverse=True)

    team = []
    legendary_used = False
    used_items = set()

    for pokemon in sorted_pokemon:
        if len(team) >= team_size:
            break

        if pokemon['is_legendary']:
            if legendary_used:
                continue
            legendary_used = True

        # Find available item
        item = pokemon['item']
        if item in used_items:
            synergies = ITEM_SYNERGIES.get(pokemon['name'], ["Life Orb", "Assault Vest", "Expert Belt", "Focus Sash"])
            found = False
            for alt in synergies:
                if alt not in used_items:
                    # Recalculate with new item
                    pokemon = comprehensive_score(pokemon['name'], BASE_STATS.get(pokemon['name'], pokemon['stats']), alt)
                    item = alt
                    found = True
                    break
            if not found:
                continue

        team.append(pokemon)
        used_items.add(item)

    return team, used_items


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 90)
    print("POKEMON META ANALYZER v5 - REAL-TIME 4-PLAYER BATTLE ROYALE")
    print("=" * 90)
    print("\nRules:")
    print("  - 4-player battle royale format")
    print("  - Kill-based scoring (most last hits wins)")
    print("  - Pokemon can respawn")
    print("  - Physical: FAST cast but must approach (RISKY - can be ganked)")
    print("  - Special:  RANGED/safe but SLOW cast (can be dodged)")
    print("  - NO priority moves exist")
    print("  - 3 Pokemon per team, max 1 legendary")
    print("  - Items allowed (no duplicates)")
    print()

    # Score all Pokemon
    pokemon_scores = []

    for name, stats in BASE_STATS.items():
        # Try with best item
        synergies = ITEM_SYNERGIES.get(name, ["Life Orb"])
        item = synergies[0]
        score = comprehensive_score(name, stats, item)
        pokemon_scores.append(score)

    # Add Primal forms
    if "Groudon" in BASE_STATS:
        primal_g = comprehensive_score("Groudon", BASE_STATS["Groudon"], "Red Orb")
        primal_g['name'] = "Primal Groudon"
        pokemon_scores.append(primal_g)

    if "Kyogre" in BASE_STATS:
        primal_k = comprehensive_score("Kyogre", BASE_STATS["Kyogre"], "Blue Orb")
        primal_k['name'] = "Primal Kyogre"
        pokemon_scores.append(primal_k)

    # Add Mega Evolutions
    for mega_name, mega_stats in MEGA_STATS.items():
        mega_item = MEGA_ITEMS.get(mega_name, "Life Orb")
        mega_types = MEGA_TYPES.get(mega_name)
        base_name = MEGA_BASE.get(mega_name)

        # Check if base Pokemon is legendary
        is_mega_legendary = base_name in LEGENDARY_POKEMON

        # Create a modified comprehensive_score for mega
        score = comprehensive_score_mega(mega_name, mega_stats, mega_types, mega_item, is_mega_legendary)
        pokemon_scores.append(score)

    sorted_pokemon = sorted(pokemon_scores, key=lambda x: x['score'], reverse=True)
    max_score = sorted_pokemon[0]['score'] if sorted_pokemon else 100

    # Print tier list
    print("=" * 100)
    print("TIER LIST - 4-PLAYER BATTLE ROYALE META")
    print("=" * 100)
    print(f"{'Tier':<4} {'Pokemon':<18} {'Score':>7} | {'Type':<15} | {'Size':<6} | {'Style':<7} | Key Strengths")
    print("-" * 100)

    current_tier = None
    for p in sorted_pokemon[:35]:
        tier = assign_tier(p['score'], max_score)
        types_str = f"{p['types'][0]}" + (f"/{p['types'][1]}" if p['types'][1] else "")
        atk_style = "Phys" if p['is_physical'] else "Spec"
        leg = "★" if p['is_legendary'] else " "
        four_x = f" [4x:{','.join(p['four_x_types'])}]" if p['four_x_types'] else ""
        size_str = p.get('size_name', 'Med')[:5]

        # Key strengths
        strengths = []
        if p['aoe'] > 50: strengths.append("AoE")
        if p['range_safety'] > 80: strengths.append("Ranged")
        if p['mobility'] > 100: strengths.append("Fast")
        elif p['mobility'] < 60: strengths.append("Slow")
        if p['survivability'] > 80: strengths.append("Tanky")
        if p['burst'] > 100: strengths.append("Burst")
        if p['size'] <= 2: strengths.append("SmallHitbox")
        if p['immunities']: strengths.append(f"Imm:{list(p['immunities'])[0][:3]}")

        tier_str = tier if tier != current_tier else " "
        current_tier = tier

        print(f"{tier_str:<3}{leg} {p['name']:<18} {p['score']:>6.1f} | {types_str:<15} | {size_str:<6} | {atk_style:<7} | {', '.join(strengths[:4])}{four_x}")

    # Analysis by category
    print("\n" + "=" * 90)
    print("ANALYSIS: PHYSICAL VS SPECIAL IN 4-PLAYER")
    print("=" * 90)

    physical = [p for p in sorted_pokemon if p['is_physical']]
    special = [p for p in sorted_pokemon if not p['is_physical']]

    print(f"\nBest PHYSICAL attackers (fast cast, but must approach = RISKY):")
    for p in sorted(physical, key=lambda x: x['score'], reverse=True)[:5]:
        print(f"  {p['name']:<18} Score: {p['score']:>6.1f} | Burst: {p['burst']:.0f} | Risk: Must close distance")

    print(f"\nBest SPECIAL attackers (ranged/safe, but slow cast):")
    for p in sorted(special, key=lambda x: x['score'], reverse=True)[:5]:
        print(f"  {p['name']:<18} Score: {p['score']:>6.1f} | Burst: {p['burst']:.0f} | Advantage: Can snipe safely")

    # AoE specialists
    print("\n" + "=" * 90)
    print("AOE SPECIALISTS (Hit multiple players at once)")
    print("=" * 90)

    aoe_sorted = sorted([p for p in sorted_pokemon if p['aoe'] > 30], key=lambda x: x['aoe'], reverse=True)
    for p in aoe_sorted[:10]:
        aoe_moves = [m[0] for m in p['best_moves'] if len(m) >= 5 and m[3] and not m[4]][:3]  # is_aoe=True, is_multi_hit=False
        print(f"  {p['name']:<18} AoE Score: {p['aoe']:>6.1f} | Moves: {', '.join(aoe_moves)}")

    # Optimal team
    print("\n" + "=" * 90)
    print("OPTIMAL TEAM (3 Pokemon, 1 Legendary Max, Unique Items)")
    print("=" * 90)

    team, used_items = build_optimal_team(pokemon_scores, TEAM_SIZE)

    for i, p in enumerate(team, 1):
        types_str = f"{p['types'][0]}" + (f"/{p['types'][1]}" if p['types'][1] else "")
        leg = " ★" if p['is_legendary'] else ""
        atk = "Physical" if p['is_physical'] else "Special"
        four_x = f" [4x: {','.join(p['four_x_types'])}]" if p['four_x_types'] else ""
        size_str = p.get('size_name', 'Medium')

        print(f"\n{i}. {p['name']}{leg}")
        print(f"   Type: {types_str}{four_x}")
        print(f"   Size: {size_str} | Attack: {atk} | Item: {p['item']}")
        print(f"   Stats: HP:{p['stats'][0]} Atk:{p['stats'][1]} Def:{p['stats'][2]} SpA:{p['stats'][3]} SpD:{p['stats'][4]} Spe:{p['stats'][5]}")
        print(f"   Burst: {p['burst']:.1f} | Safety: {p['range_safety']} | Mobility: {p['mobility']:.0f} | AoE: {p['aoe']:.1f}")
        if p['best_moves']:
            move_strs = []
            for m in p['best_moves'][:4]:
                aoe_tag = " [AoE]" if (len(m) >= 4 and m[3]) else ""
                move_strs.append(f"{m[0]}({m[1]}){aoe_tag}")
            print(f"   Moves: {', '.join(move_strs)}")

    print(f"\nTeam Total Score: {sum(p['score'] for p in team):.1f}")
    print(f"Items Used: {', '.join(used_items)}")

    # Strategic tips
    print("\n" + "=" * 90)
    print("STRATEGIC ANALYSIS FOR 4-PLAYER BATTLE ROYALE")
    print("=" * 90)

    print("""
KEY INSIGHTS:

1. SPECIAL ATTACKERS DOMINATE
   - Can snipe kills from safety without approaching
   - Slower cast time is offset by ranged advantage
   - In 4-player, approaching makes you vulnerable to 3rd party attacks

2. AOE MOVES ARE VALUABLE (different from multi-hit!)
   - AoE = hits one area, people can still dodge
   - Best when enemies are grouped/fighting = avg 1-2 hits, up to 3 if cramped
   - Larger AoE (high power) = easier to catch grouped enemies
   - Earthquake, Surf, Heat Wave, Discharge = good AoE options
   - Multi-hit = same target, multiple hits = BAD (can dodge between)
   - Scale Shot, Triple Axel, Dual Wingbeat = BAD multi-hit

3. PHYSICAL ATTACKERS ARE RISKY
   - Must close distance = can be sniped while approaching
   - Fast cast doesn't help if you get killed moving in
   - Only viable with high speed OR high bulk
   - Best physical: Groudon (Earthquake AoE), Excadrill (EQ)

4. SURVIVAL VS KILL TRADE-OFF
   - Pure tanks can't secure kills = low tier
   - Glass cannons die to 3rd party = risky
   - Sweet spot: Ranged burst damage + AoE + decent bulk

5. 4X WEAKNESSES ARE DEVASTATING
   - In 4-player, someone WILL have coverage
   - Zygarde's 4x Ice makes it easy kill-steal target
   - Dragon/Steel (Goodra-Hisui) = only 2 weaknesses = harder to snipe

6. SIZE MATTERS
   - Larger Pokemon = slower movement + bigger hitbox = easier to hit
   - Smaller Pokemon = faster + smaller hitbox = harder to hit
   - Huge (Groudon, Kyogre) are easy targets despite power
   - Small (Greninja, Jolteon, Sylveon) are nimble and hard to snipe

7. IDEAL POKEMON PROFILE FOR 4-PLAYER:
   - Special attacker (ranged safety)
   - High-power single-hit moves (for kill-stealing)
   - Access to AoE (hit multiple enemies)
   - Few weaknesses (no easy counters)
   - Medium or Small size (not an easy target)
   - Decent HP/bulk (survive third-party attacks)
""")

    # Save to CSV
    output_file = "meta_analysis_v5.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Tier', 'Pokemon', 'Legendary', 'Score', 'Type1', 'Type2',
                        'Attack_Style', 'Burst', 'Safety', 'Mobility', 'AoE', 'Survivability',
                        'Item', '4x_Weak', 'Best_Moves'])

        for i, p in enumerate(sorted_pokemon, 1):
            tier = assign_tier(p['score'], max_score)
            moves_str = "; ".join([f"{m[0]}({m[1]})" for m in p['best_moves'][:4]])
            writer.writerow([
                i, tier, p['name'], "Yes" if p['is_legendary'] else "No",
                f"{p['score']:.1f}", p['types'][0], p['types'][1] or "",
                "Physical" if p['is_physical'] else "Special",
                f"{p['burst']:.1f}", p['range_safety'], f"{p['mobility']:.0f}",
                f"{p['aoe']:.1f}", f"{p['survivability']:.1f}",
                p['item'], ",".join(p['four_x_types']) if p['four_x_types'] else "",
                moves_str
            ])

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
