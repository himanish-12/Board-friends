# settings.py
# Board dimensions, physics tuning, and color palette for Board Friends

WIN_W, WIN_H = 1140, 840
BOARD_SIZE = 740
BOARD_X = 42
BOARD_Y = (WIN_H - BOARD_SIZE) // 2
FRAME_WIDTH = 52

# Playable wood area inside the rosewood frame
PLAY_X = BOARD_X + FRAME_WIDTH
PLAY_Y = BOARD_Y + FRAME_WIDTH
PLAY_SIZE = BOARD_SIZE - 2 * FRAME_WIDTH
CENTER_X = PLAY_X + PLAY_SIZE // 2
CENTER_Y = PLAY_Y + PLAY_SIZE // 2

FPS = 60
SUBSTEPS = 8

# Chess.com Dark Theme & Signature Green UI Palette
BG_DARK = (22, 21, 18)              # Deep warm charcoal background (#161512)
PANEL_BG = (38, 36, 33)             # Chess.com dark panel (#262421)
CARD_BG = (30, 28, 26)              # Recessed dark card (#1E1C1A)
CARD_ACTIVE = (44, 52, 36)          # Subtle green-tinted active card
BORDER_SUBTLE = (58, 55, 50)        # Clean dark divider border

CHESS_GREEN = (129, 182, 76)        # Chess.com primary green (#81B64C)
CHESS_GREEN_DARK = (83, 113, 51)    # 3D button bottom shadow (#537133)
CHESS_GREEN_LIGHT = (163, 209, 110) # Soft green highlight

# Classic Wooden Carrom Board Colors (Restored from v4)
FRAME_OUTER = (68, 38, 22)          # Rosewood outer frame
FRAME_INNER = (98, 56, 32)          # Inner wood bevel
BRASS = (212, 168, 76)              # Corner brass rivets
BOARD_WOOD = (236, 206, 160)        # Birchwood playing surface
BOARD_WOOD_DARK = (222, 190, 142)   # Center mandala shade
INK_LINE = (56, 34, 20)             # Traditional dark brown board markings
CRIMSON = (192, 44, 44)             # Traditional red accents
POCKET_HOLE = (16, 15, 15)          # Deep pocket holes
POCKET_NET = (38, 34, 30)           # Woven pocket net rings

# Carrommen & Striker Colors (Classic Wood & Acrylic)
IVORY = (244, 239, 226)             # White carrommen
CHARCOAL = (40, 42, 46)             # Black carrommen
QUEEN_RED = (208, 34, 52)           # Red Queen
STRIKER_TEAL = (52, 158, 218)       # Tournament blue striker
GOLD = (238, 188, 64)               # Gold accents
CREAM_TEXT = (242, 240, 236)        # Crisp off-white UI text
MUTED_TEXT = (158, 154, 148)        # Secondary muted gray text

# Sodalicious Candy-Style Text Palette (for Title & Popups)
CANDY_TOP = (255, 228, 95)          # Bright golden yellow top
CANDY_BOT = (235, 120, 20)          # Rich orange-amber bottom
CANDY_OUTLINE = (72, 26, 6)         # Thick chocolate brown outline
CANDY_HIGHLIGHT = (255, 250, 200)   # Glossy top-edge shine

# Physics tuning
BOARD_DRAG = 0.986
COIN_BOUNCE = 0.88
CUSHION_BOUNCE = 0.80
STOP_SPEED = 0.06
MAX_STRIKE_POWER = 32.0

COIN_R = 16
STRIKER_R = 22
POCKET_R = 30
