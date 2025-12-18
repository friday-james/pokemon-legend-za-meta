# Pokemon Meta Analyzer - 4-Player Battle Royale

A meta analysis tool for a custom Pokemon real-time 4-player battle royale game mode.

![Tier List](tierlist.png)

## Disclaimer

**The data and analysis in this repository may not be accurate.** The game mechanics modeled here are approximations and do not fully reflect the actual in-game mechanics. This analysis is for reference purposes only and should not be taken as definitive meta guidance.

Key limitations:
- Move data is scraped and may be incomplete
- Real-time mechanics (cast times, hitboxes, movement) are estimated
- Pokemon size categories are approximated
- AoE vs multi-hit classification may not match actual game behavior
- Type effectiveness follows standard Pokemon rules which may differ from the actual game

---

## Meta Report - 4-Player Battle Royale

### Game Rules
- **4-player battle royale** format
- **Real-time combat** - players can dodge, snipe, and hide
- **Kill-based scoring** - most last hits/kills wins
- **Pokemon can respawn**
- **3 Pokemon per team**, max 1 legendary
- **Items allowed** (no duplicates on team)
- **No native abilities** (item abilities like Primal forms OK)
- **No priority moves**

### Key Mechanics

| Mechanic | Physical Attacks | Special Attacks |
|----------|------------------|-----------------|
| Cast Speed | Fast | Slow |
| Range | Must approach target | Ranged (safe) |
| Risk | High (can be ganked) | Low |

| Move Type | Effect | Examples |
|-----------|--------|----------|
| **AoE** | Hits multiple enemies = GOOD | Earthquake, Surf, Heat Wave |
| **Multi-hit** | Multiple hits on same target = BAD (dodgeable) | Scale Shot, Triple Axel |
| **High Power** | More damage but LONGER cast time (dodgeable) | Draco Meteor, Eruption |
| **Medium Power** | Sweet spot - balanced damage and cast speed | Surf, Thunderbolt, Ice Beam |

| Size | Movement | Hitbox | Risk |
|------|----------|--------|------|
| Huge | 0.6x slower | 1.5x larger | Easy target |
| Large | 0.8x slower | 1.2x larger | Notable target |
| Medium | Normal | Normal | Balanced |
| Small | 1.2x faster | 0.8x smaller | Hard to hit |
| Tiny | 1.4x faster | 0.6x smaller | Very hard to hit |

---

## Tier List

### S Tier
| Pokemon | Type | Size | Key Strengths |
|---------|------|------|---------------|
| Primal Kyogre | Water | Huge | Best AoE (Origin Pulse, Surf), 180 SpA burst |
| Volcanion | Fire/Water | Large | Eruption + Origin Pulse AoE combo |

### A Tier
| Pokemon | Type | Size | Key Strengths |
|---------|------|------|---------------|
| Primal Groudon | Ground/Fire | Huge | Earthquake AoE, 180 Atk burst |
| Keldeo | Water/Fighting | Medium | Water AoE + good size balance |
| Vaporeon | Water | Small | Small hitbox + AoE + bulk |
| Greninja | Water/Dark | Small | Fastest mobility, small hitbox |
| Milotic | Water | Medium | Balanced stats + Water AoE |
| Xerneas | Fairy | Large | Fairy AoE, Dragon immunity |
| Heatran | Fire/Steel | Medium | Heat Wave AoE, Poison immunity |
| Blastoise | Water | Medium | Water AoE, balanced bulk |

### B Tier
| Pokemon | Type | Size | Key Strengths |
|---------|------|------|---------------|
| Armarouge | Fire/Psychic | Medium | Fire AoE moves |
| Darkrai | Dark | Medium | Fast + ranged + Psychic immunity |
| Sylveon | Fairy | Small | Small hitbox + Dragon immunity |
| Charizard | Fire/Flying | Medium | Heat Wave AoE |
| Excadrill | Ground/Steel | Medium | Earthquake AoE (physical) |
| Mewtwo | Psychic | Medium | High SpA, ranged, fast |
| Clefable | Fairy | Large | Fairy AoE, Dragon immunity |
| Garchomp | Dragon/Ground | Large | Earthquake AoE, burst damage |

### C Tier
| Pokemon | Type | Size | Key Strengths |
|---------|------|------|---------------|
| Zygarde | Dragon/Ground | Huge | Earthquake AoE, bulk (4x Ice) |
| Slowbro/Slowking | Water/Psychic | Medium | Water AoE, decent bulk |
| Gholdengo | Steel/Ghost | Medium | Immunities, ranged |
| Yveltal | Dark/Flying | Large | Dark AoE, Psychic/Ground immunity |
| Magearna | Steel/Fairy | Medium | Dragon immunity, bulk |

---

## Optimal Team Composition

### Recommended Team
1. **Primal Kyogre** (Blue Orb) - Legendary slot, best overall
2. **Vaporeon** (Life Orb) - Small hitbox, tanky, AoE
3. **Greninja** (Assault Vest) - Fastest, smallest, AoE

**Team Strategy**: All special attackers for ranged safety, all have Water AoE for multi-target damage, mix of sizes for different roles.

### Alternative Teams

**Balanced Size Team**:
1. Keldeo (Legendary) - Medium, balanced
2. Greninja - Small, fast sniper
3. Milotic - Medium, bulky AoE

**Anti-Dragon Team**:
1. Xerneas (Legendary) - Dragon immune
2. Sylveon - Dragon immune, small
3. Clefable - Dragon immune, small

---

## Strategic Insights

### Why Special Attackers Dominate
In a 4-player battle royale, approaching to use physical attacks exposes you to third-party attacks from 2 other players. Special attackers can snipe from safety.

### Why AoE is Premium
With 3 enemies on the field, AoE moves effectively deal 3x damage output. Excellent for kill-stealing when others are fighting.

### Why Size Matters
Larger Pokemon are easier targets in chaotic 4-player fights. Smaller Pokemon can dodge and avoid being focused.

### 4x Weaknesses are Death Sentences
In 4-player, someone WILL have coverage. Zygarde's 4x Ice weakness makes it easy to snipe. Goodra-Hisui (Dragon/Steel) with only 2 weaknesses is much safer.

---

## Files

| File | Description |
|------|-------------|
| `meta_analyzer.py` | Main analysis script |
| `meta_analysis.csv` | Generated tier list and scores |
| `pokemon_crawler.py` | Serebii.net data scraper |
| `pokemon_movesets.csv` | Pokemon moveset summary |
| `pokemon_movesets_detailed.csv` | Detailed move data |

## Usage

```bash
python meta_analyzer.py
```

---

## Data Sources

- Pokemon data scraped from [Serebii.net](https://www.serebii.net/)
- Type effectiveness based on standard Pokemon mechanics
- Size categories estimated from Pokedex height/weight data

