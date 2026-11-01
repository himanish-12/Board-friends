# 🎯 Board Friends

A 2D tabletop Carrom game built from scratch in Python and Pygame. 

No external sprites, no image assets, and no bloat—every piece of wood grain, brass rivet, pocket net, and glossy text popup is drawn procedurally in code. It pairs a classic rosewood-and-birch Carrom board with a clean, Chess.com-inspired dark/green sidebar and arcade-style physics.

---

## ✨ What's Inside

* **Zero External Assets:** Everything is rendered via Pygame surfaces. You can clone the repo and play immediately without worrying about broken image paths.
* **Sub-Stepped 2D Physics:** Runs 8 physics sub-steps per frame to handle high-speed break shots cleanly. No coins tunneling through cushions or clipping into each other.
* **Raycast Aiming & Deflection Guide:** Pulling back the striker shows a live trajectory line, a "ghost striker" at the exact point of impact, and the predicted deflection vector of the target coin.
* **Full Tournament Carrom Rules:**
  * **White (South)** vs. **Black (North)**.
  * **Red Queen (+3 Bonus):** Sink the Queen and cover it with one of your own coins on the same shot (or the very next stroke) to claim the bonus. Fail to cover it, and it goes right back to the center.
  * **Striker Fouls:** Sinking the striker costs you 1 point, returns one of your pocketed coins to the center of the board, and passes the turn.
* **Custom Candy Typography & FX:** Features a custom 3D gradient text renderer for arcade callouts (*"Sodalicious!"*, *"Juicy!"*, *"Crush!"*, *"Divine!"*), particle sparks on heavy impacts, pocket ripples, and screen shake.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/board-friends.git](https://github.com/YOUR_USERNAME/board-friends.git)
cd board-friends
python -m venv .venv
pip install -r requirements.txt
python main.py
```
#tweaking physics
TO change physics go to settings.py and change values like
```bash
BOARD_DRAG = 0.986        # Closer to 1.0 = slicker, freshly powdered board
COIN_BOUNCE = 0.88        # Elasticity between colliding coins
CUSHION_BOUNCE = 0.80     # Rebound speed off the wooden frame
MAX_STRIKE_POWER = 32.0   # Top speed of a full-power break shot
```

#playable link from itch.io

[Link text](https://himanish-12.itch.io/board-friends)

