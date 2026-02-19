# ADWBALL 2026 — Advanced Desktop Career Mode

This is now a **full desktop football career game** with richer graphics, deeper systems, and active match gameplay.

## Major upgrades
- New designed UI with multiple scenes:
  - Hub
  - Squad Management
  - Transfer Market
  - Standings + Awards
  - Live Match
- Improved visuals:
  - Gradient stadium backdrop
  - Pitch striping, lines, goals, crowd strip
  - Styled cards/panels and overlays
  - Mini-map during matches
- Deeper gameplay systems:
  - Real-time movement with sprint and stamina impact
  - Shot charge mechanic (hold + release)
  - Passing, tackling, AI support/chase behavior
  - Weather effects (Clear/Rain/Windy) affecting gameplay feel
  - Match timeline/event feed
- Career complexity:
  - Negotiation-based transfers (not guaranteed)
  - Scouting action generating new market players
  - Harder training progression (higher cost + lower success near 99)
  - Board confidence and development points
  - Full 20-team LaLiga simulation and Golden Boot race
  - Persistent season progression and rewards

## Install
```bash
python3 -m pip install pygame
```

## Run
```bash
python3 main.py
```

## Controls
### Global
- Mouse: top navigation buttons

### Hub
- Click tactic buttons to change tactical mode

### Squad
- `UP / DOWN`: select XI player
- `LEFT / RIGHT`: select bench player
- `SPACE`: swap selected bench player into XI
- `T`: targeted training on selected XI player

### Market
- `UP / DOWN`: choose player
- `ENTER`: negotiate and sign selected player
- `S`: scout and add 3 new prospects

### Live Match
- `WASD` or Arrow Keys: move
- `SHIFT`: sprint
- Hold + release `SPACE`: charged shot
- `Q`: pass
- `E`: tackle
