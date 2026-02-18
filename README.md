# ADWBALL 2026 — Desktop Career Mode (Pygame)

This project is now a **desktop game** (not web, not CLI-only) built with Python + Pygame.

## What you get
- Multi-screen UI: Hub, Squad, Market, Standings, and Live Match.
- Real gameplay during matches:
  - Move your controlled player (WASD/Arrow keys).
  - Shoot the ball (Space).
  - Score in real time against AI defender/keeper behavior.
- Career systems:
  - XI + Bench swapping.
  - Harder training progression (cost scales + success chance drops near 99).
  - Transfers from market.
  - Full 20-team LaLiga table simulation.
  - Golden Boot race with all teams.

## Install
```bash
python3 -m pip install pygame
```

## Run
```bash
python3 main.py
```

## Controls
- **Top buttons**: switch screens with mouse.
- **Squad screen**:
  - Up/Down = select XI player
  - Left/Right = select bench player
  - `T` = targeted training
  - `Space` = swap bench player into XI
- **Market screen**:
  - Up/Down = select player
  - `Enter` = sign player
- **Match screen**:
  - WASD / Arrow keys = move
  - `Space` = shoot (when near ball)
