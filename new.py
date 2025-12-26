from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random


camera_pos = (-450, -650, 520)
#camera_pos = (0, -650, 520)


fovY = 90
GRID_LENGTH = 600
rand_var = 423

# ---------------- Level Flags ----------------
level_1_active = True
level_2_active = False
level_3_active = False
level_4_active = False



# ---------------- Player ----------------
player_x = -350.0
player_y = -350.0
score = 0

MAX_LIVES = 5
lives = MAX_LIVES

level_start_spawn_x = player_x
level_start_spawn_y = player_y

player_spawn_positions = {
    2: (-350, -350),   # Level 1 spawn
    3: ( -350, -350),   # Level 2 spawn
}

base_player_speed = 18.0
player_speed = base_player_speed

speed_boost_timer = 0

player_z = 0.0
player_r = 18.0        # radius



# ---------------- Rewards ----------------
rewards = []
reward_config = {
    1: {
        "small": 5,
        "medium": 2,
        "big": 1,
        "medium_positions": [
            (-480,  300),
            ( 480, -300)
        ],
        "big_positions": [
            (500,  500)
        ]
    },
    2: {
        "small": 10,
        "medium": 4,
        "big": 1,
        "medium_positions": [
            (-500,  500),
            ( 500,  500),
            (-500, -500),
            ( 500, -500)
        ],
        "big_positions": [
            (500, 350)
        ]
    },
    3: {
        "small": 15,
        "medium": 8,
        "big": 1,
        "medium_positions": [
            (143,  352),
            ( 191,  -232),
            (119, 520),
            ( 425, -548),
            (-262,  222),
            ( -136,  52),
            (-116, -218),
            ( -116, -520)
        ],
        
        "big_positions": [
            (113, 392)
        ]
    }
    
}

# ---------------- World Building ----------------
L = 600

# ---------------- Level 2 Grid ----------------
LEVEL2_PATTERN = [
    [1, 1, 2, 2, 2, 1, 1],
    [1, 1, 3, 3, 3, 1, 1],
    [2, 3, 3, 3, 3, 3, 2],
    [2, 3, 3, 3, 3, 3, 2],
    [2, 3, 3, 3, 3, 3, 2],
    [1, 1, 3, 3, 3, 1, 1],
    [1, 1, 2, 2, 2, 1, 1]
]
LEVEL2_ROWS = 7
LEVEL2_COLS = 7

L2 = 1000
hazard_half_width = 130
wall_thickness = 5
wall_height = 180


# ---------------- Level 3 Grid ----------------
LEVEL3_PATTERN = [
    # 1 = green (walk + portal allowed)
    # 2 = yellow (walk allowed, portal NOT allowed)
    # 3 = red (blocked)
    [1,1,1,1,1,3,3,1,1,3,1,1],
    [3,3,3,3,3,3,3,1,1,3,1,1],
    [1,1,1,1,1,3,3,1,1,3,1,1],
    [1,1,1,1,1,3,3,1,1,3,1,1],
    [2,3,3,3,3,3,3,3,3,3,3,2],
    [2,1,1,1,1,3,3,1,1,1,1,1],
    [1,1,1,1,1,3,3,1,1,1,1,2],
    [2,3,3,3,3,3,3,3,3,3,3,2],
    [1,1,3,1,1,3,3,1,1,1,1,1],
    [1,1,3,1,1,3,3,1,1,1,1,1],
    [1,1,3,1,1,3,3,3,3,3,3,3],
    [1,1,3,1,1,3,3,1,1,1,1,1],
]
LEVEL3_ROWS=12
LEVEL3_COLS=12


left_inner_x  = -L + wall_thickness
right_inner_x =  L - wall_thickness


portal_lr_active = False   # left , right
portal_ud_active = False   # up , down

portal_r = 45.0
portal_z_center = 25.0
portal_left = {"x": left_inner_x, "y": 0.0, "z": portal_z_center}
portal_right = {"x": right_inner_x, "y": 0.0, "z": portal_z_center}
portal_top = {"x": 0.0, "y": L - wall_thickness, "z": portal_z_center}
portal_bottom = {"x": 0.0, "y": -L + wall_thickness, "z": portal_z_center}

portal_plane_eps = 6.0
portal_cooldown = 0


# ----------------Level 1 Enemies ----------------
enemy1 = {
    "x": 350.0,     # opposite green lane
    "y": -300.0,
    "z": 18.0,
    "r": 18.0,
    "speed":0.1,
    "dir": 1,       # +1 or -1 for patrol direction
    "active": True
}
def on_left_lane(x):
    return x < -hazard_half_width

def on_right_lane(x):
    return x > hazard_half_width

def player_on_enemy_side():
    if on_left_lane(enemy1["x"]):
        return on_left_lane(player_x)
    else:
        return on_right_lane(player_x)


# ---------------- Level 2 Enemies----------------
enemy_L2_type1 = []   # TL and BR
enemy_L2_type2 = None # TR turret

bullets = []          # bullets shot by type2 enemy


def spawn_level2_enemies():
    global enemy_L2_type1, enemy_L2_type2, bullets
    enemy_L2_type1 = []
    bullets = []

    # Type-1 enemy in TOP-LEFT green block
    sx, sy =level2_world_center_of_cell(6, 0)
    enemy_L2_type1.append({
        "type": 1,
        "home": "TL",
        "x": sx, "y": sy,
        "z": player_r + 10,
        "r": 18.0,
        "speed": 0.2,
        "dir": 1
    })

    # Type-1 enemy in BOTTOM-RIGHT green block
    sx2, sy2 = level2_world_center_of_cell(0, 6)
    enemy_L2_type1.append({
        "type": 1,
        "home": "BR",
        "x": sx2, "y": sy2,
        "z": player_r + 10,
        "r": 18.0,
        "speed": 0.2,
        "dir": -1
    })



    # Type-2 enemy in TOP-RIGHT green block (fixed turret)
    enemy_L2_type2 = {
        "type": 2,
        "home": "TR",
        "x": 520, "y": 520,
        "r": 18.0,
        "angle": 0.0,        # spinning angle in degrees
        "spin_speed": 0.5,   # degrees per frame
        "fire_cd": 0         # cooldown frames
    }

def set_active_level(level_num):
    global level_1_active, level_2_active, level_3_active, level_4_active
    global lives

    level_1_active = level_num == 1
    level_2_active = level_num == 2
    level_3_active = level_num == 3
    level_4_active = level_num == 4

    lives = MAX_LIVES
    spawn_player_for_level(level_num)
    
    global level_start_spawn_x, level_start_spawn_y
    level_start_spawn_x, level_start_spawn_y = player_x, player_y


    if level_num == 2:
        spawn_level2_enemies()



    
def promote_level():
    if level_1_active:
        set_active_level(2)
        reset_player_for_level(2)
    elif level_2_active:
        set_active_level(3)
        reset_player_for_level(3)
    elif level_3_active:
        set_active_level(1)
        
    spawn_rewards_for_level()


def reset_player_for_level(level):
    global player_x, player_y, player_z

    if level in player_spawn_positions:
        player_x, player_y = player_spawn_positions[level]
    else:
        player_x, player_y = 0, 0

    player_z = 0



def get_active_level():
    if level_1_active:
        return 1
    elif level_2_active:
        return 2
    elif level_3_active:
        return 3
    elif level_4_active:
        return 4
    return 1


def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def allowed_on_green(nx, ny):
    
    if nx < -L + player_r or nx > L - player_r:
        return False
    if ny < -L + player_r or ny > L - player_r:
        return False

    left_ok  = nx <= (-hazard_half_width - player_r)
    right_ok = nx >= ( hazard_half_width + player_r)
    
    if not (left_ok or right_ok):
        return False

    if nx < left_inner_x + player_r:
        return False
    
    if nx > right_inner_x - player_r:
        return False

    return True


def level2_cell_at(wx, wy):
    # Convert world coords (-L..L) to grid cell indices
    cell_w = (2 * L) / LEVEL2_COLS
    cell_h = (2 * L) / LEVEL2_ROWS

    col = int((wx + L) / cell_w)
    row = int((wy + L) / cell_h)

    # clamp to [0..6] so edge cases don't crash
    col = clamp(col, 0, LEVEL2_COLS - 1)
    row = clamp(row, 0, LEVEL2_ROWS - 1)

    return LEVEL2_PATTERN[row][col]   # 1/2/3

def level2_world_center_of_cell(row, col):
    cell_w = (2 * L) / LEVEL2_COLS
    cell_h = (2 * L) / LEVEL2_ROWS

    cx = -L + (col + 0.5) * cell_w
    cy = -L + (row + 0.5) * cell_h
    return cx, cy

def find_green_spawn_in_block(home):
    # home is "TL", "TR", "BL", "BR"
    mid_r = LEVEL2_ROWS // 2
    mid_c = LEVEL2_COLS // 2

    if home == "TL":
        r_range = range(mid_r, LEVEL2_ROWS)
        c_range = range(0, mid_c)
    elif home == "TR":
        r_range = range(mid_r, LEVEL2_ROWS)
        c_range = range(mid_c, LEVEL2_COLS)
    elif home == "BL":
        r_range = range(0, mid_r)
        c_range = range(0, mid_c)
    else:  # "BR"
        r_range = range(0, mid_r)
        c_range = range(mid_c, LEVEL2_COLS)

    # Find any green cell (assuming 2 = green in your level2 pattern)
    for r in r_range:
        for c in c_range:
            if LEVEL2_PATTERN[r][c] == 1:
                return level2_world_center_of_cell(r, c)

    # fallback: center of the block if no green found
    rr = (mid_r + LEVEL2_ROWS - 1) // 2 if home in ("TL", "TR") else (0 + mid_r - 1) // 2
    cc = (0 + mid_c - 1) // 2 if home in ("TL", "BL") else (mid_c + LEVEL2_COLS - 1) // 2
    return level2_world_center_of_cell(rr, cc)



def level2_rc_at(wx, wy):
    cell_w = (2 * L) / LEVEL2_COLS
    cell_h = (2 * L) / LEVEL2_ROWS

    col = int((wx + L) / cell_w)
    row = int((wy + L) / cell_h)
    col = clamp(col, 0, LEVEL2_COLS - 1)
    row = clamp(row, 0, LEVEL2_ROWS - 1)
    return row, col

def level2_block_bounds(home):
    # Green corner blocks are 2x2:
    # TL: rows 5-6, cols 0-1
    # BR: rows 0-1, cols 5-6

    cell_w = (2 * L) / LEVEL2_COLS
    cell_h = (2 * L) / LEVEL2_ROWS
    start_x = -L
    start_y = -L

    if home == "TL":
        c0, c1 = 0, 1
        r0, r1 = 5, 6
    elif home == "BR":
        c0, c1 = 5, 6
        r0, r1 = 0, 1
    else:
        return None  # not needed for your two type-1 enemies

    xmin = start_x + c0 * cell_w
    xmax = start_x + (c1 + 1) * cell_w
    ymin = start_y + r0 * cell_h
    ymax = start_y + (r1 + 1) * cell_h

    # keep some margin so the sphere doesn't clip outside
    margin = 25
    return xmin + margin, xmax - margin, ymin + margin, ymax - margin



def level2_green_block(px, py):
    # Return which CORNER GREEN block this point is in: "TL","TR","BL","BR" or None
    # Only consider if tile is GREEN (==1)
    if level2_cell_at(px, py) != 1:
        return None

    row, col = level2_rc_at(px, py)

    # Using your LEVEL2_PATTERN, the corner green regions are 2x2 blocks:
    # TL: rows 5-6, cols 0-1  (top in +y direction)
    # TR: rows 5-6, cols 5-6
    # BL: rows 0-1, cols 0-1
    # BR: rows 0-1, cols 5-6

    if row >= 5 and col <= 1:
        return "TL"
    if row >= 5 and col >= 5:
        return "TR"
    if row <= 1 and col <= 1:
        return "BL"
    if row <= 1 and col >= 5:
        return "BR"
    return None


def allowed_on_level_2(nx, ny):
    # boundaries (same as your old function)
    if nx < -L + player_r or nx > L - player_r:
        return False
    if ny < -L + player_r or ny > L - player_r:
        return False

    # tile = level2_cell_at(nx, ny)

    # # walkable = green(1) and yellow(2)
    # return tile in (1, 2)
    
    if ny >= 432 or ny <= -432 :
        return True
    
    if ny < 432 and ny > 270:
           if nx < -265 or nx > 265:
            return True
        
    if ny < 270 and ny > -270:
        if nx < -435 or nx > 435:
            return True
        
    if ny < -270 and ny > -432:
        if nx < -265 or nx > 265:
            return True
        
def level3_cell_at(wx, wy):
    cell_w = (2 * L) / LEVEL3_COLS
    cell_h = (2 * L) / LEVEL3_ROWS

    col = int((wx + L) / cell_w)
    row = int((wy + L) / cell_h)

    col = clamp(col, 0, LEVEL3_COLS - 1)
    row = clamp(row, 0, LEVEL3_ROWS - 1)

    return LEVEL3_PATTERN[row][col]


def allowed_on_level_3(nx, ny):
    if nx < -L + player_r or nx > L - player_r:
        return False
    if ny < -L + player_r or ny > L - player_r:
        return False

    tile = level3_cell_at(nx, ny)

    # walkable = green(1) and yellow(2)
    return tile in (1, 2)


def is_green_for_current_level(x, y):
    if level_1_active:
        return allowed_on_green(x, y)
    elif level_2_active:
        return allowed_on_level_2(x, y)
    elif level_3_active:
        return allowed_on_green_level_3(x, y)
    elif level_4_active:
        return allowed_on_green_level_4(x, y)
    return False

def allowed_on_green_level_3(nx, ny):
    return allowed_on_level_3(nx, ny)

def random_green_position():
    for _ in range(200):   # safety limit
        x = random.uniform(-L + 40, L - 40)
        y = random.uniform(-L + 40, L - 40)

        if is_green_for_current_level(x, y):
            return x, y

    return 0, 0


def spawn_rewards_for_level():
    global rewards , reward_phase
    rewards.clear()
    reward_phase = 1
    spawn_current_reward_phase()
    
        
def spawn_current_reward_phase():
    global rewards

    level = get_active_level()
    cfg = reward_config[level]

    # ---------- Phase 1 ----------
    if reward_phase == 1:
        for _ in range(cfg["small"]):
            x, y = random_green_position()
            rewards.append({
                "x": x,
                "y": y,
                "z": 10,
                "type": 1,
                "r": 12
            })

    # ---------- Phase 2 ----------
    elif reward_phase == 2:
        for (x, y) in cfg["medium_positions"]:
            rewards.append({
                "x": x,
                "y": y,
                "z": 10,
                "type": 2,
                "r": 16
            })

    # ---------- Phase 3 ----------
    elif reward_phase == 3:
        for (x, y) in cfg["big_positions"]:
            rewards.append({
                "x": x,
                "y": y,
                "z": 10,
                "type": 3,
                "r": 20
            })

def can_place_portal_here(px, py):
    if level_1_active:
        return True
    if level_2_active:
        return level2_cell_at(px, py) == 1
    if level_3_active:
        return level3_cell_at(px, py) == 1
    return True

def spawn_player_for_level(level):
    global player_x, player_y

    if level == 1:
        player_x, player_y = -350, -350 

    elif level == 2:
        player_x, player_y = -520, -520


    elif level == 3:
        player_x, player_y = random_green_position()

def advance_reward_phase():
    global reward_phase

    if reward_phase < 3:
        reward_phase += 1
        spawn_current_reward_phase()

def can_place_portal_here(px, py):
    if level_1_active:
        return True
    if level_2_active:
        return level2_cell_at(px, py) == 1
    if level_3_active:
        return level3_cell_at(px, py) == 1
    return True

def spawn_player_for_level(level):
    global player_x, player_y

    if level == 1:
        player_x, player_y = -350, -350 

    elif level == 2:
        player_x, player_y = -520, -520


    elif level == 3:
        player_x, player_y = random_green_position()


def try_move(dx, dy):
    
    global player_x, player_y
    
    nx = player_x + dx
    ny = player_y + dy
    if level_1_active:
        if allowed_on_green(nx, ny):
            player_x, player_y = nx, ny

    if level_2_active:
        if allowed_on_level_2(nx, ny):
            player_x, player_y = nx, ny
            
    if level_3_active:
        if allowed_on_level_3(nx, ny):
            player_x, player_y = nx, ny
            
    if level_3_active:
        if allowed_on_level_3(nx, ny):
            player_x, player_y = nx, ny






def draw_player():
    """
    Draw player like Player.png using ONLY cubes (scaled).
    Local coordinates: +X right, +Y forward, +Z up.
    """
    glPushMatrix()

    # Place character at player position
    glTranslatef(player_x, player_y, player_z + player_r)

    # ---------------- helpers ----------------
    def cube(x, y, z, sx, sy, sz, r, g, b):
        """Draw a scaled cube centered at (x,y,z) in local space."""
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(sx, sy, sz)
        glColor3f(r, g, b)
        glutSolidCube(1.0)
        glPopMatrix()

    # ---------------- colors (approx Player.png) ----------------
    SKIN  = (1.0, 0.80, 0.80)
    SHIRT = (1.0, 0.00, 0.00)
    PANTS = (0.00, 0.45, 0.75)
    BLACK = (0.0, 0.0, 0.0)

    # Scale of the whole avatar (tweak if you want bigger/smaller)
    S = 6.0

    # ---------------- build model ----------------
    # HEAD (skin)
    cube(0*S, 0*S, 13*S, 6*S, 4*S, 6*S, *SKIN)

    # EYES / GLASSES stripe (black) across upper head
    cube(0*S, 0*S, 15*S, 6*S, 4.2*S, 0.4*S, *BLACK)


    # LEFT EYE block (black square on stripe)
    cube(-1.5*S, -2.10*S, 14.8*S, 1.1*S, 0.25*S, 1.1*S, *BLACK)

    # NECK (skin)
    cube(0*S, 0*S, 10.0*S, 2.0*S, 2.0*S, 1.5*S, *SKIN)

    # TORSO (shirt red)
    cube(0*S, 0*S, 6.0*S, 8.0*S, 4.5*S, 7.0*S, *SHIRT)

    # ARMS (skin)
    cube(-6.0*S, 0*S, 6.0*S, 3.0*S, 4.0*S, 7.0*S, *SKIN)  # left arm
    cube( 6.0*S, 0*S, 6.0*S, 3.0*S, 4.0*S, 7.0*S, *SKIN)  # right arm

    # PANTS block (blue)
    cube(0*S, 0*S, 0.5*S, 8.0*S, 4.5*S, 7.0*S, *PANTS)

    # LEGS (two blue columns with a gap in middle)
    cube(-2.0*S, 0*S, -6.5*S, 4.0*S, 4.0*S, 8.0*S, *PANTS)  # left leg
    cube( 2.0*S, 0*S, -6.5*S, 4.0*S, 4.0*S, 8.0*S, *PANTS)  # right leg

    glPopMatrix()


def draw_enemy_level_1():
    if not enemy1["active"]:
        return

    glPushMatrix()
    glTranslatef(enemy1["x"], enemy1["y"], enemy1["z"])
    glColor3f(0.2, 0.2, 0.8)  # blue enemy
    glutSolidSphere(enemy1["r"], 16, 16)
    glPopMatrix()


def draw_rewards():
    for r in rewards:
        glPushMatrix()
        glTranslatef(r["x"], r["y"], r["z"])

        if r["type"] == 1:
            # Core energy sphere
            glColor3f(255/255, 128/255, 128/255)
            glPushMatrix()
            glutSolidSphere(8, 16, 16)
            glPopMatrix()

            # Upper energy band
            glColor3f(38/255, 49/255, 150/255)
            glPushMatrix()
            glTranslatef(0, 0, 6)
            glRotatef(90, 1, 0, 0)
            glutSolidTorus(1.5, 10, 10, 24)
            glPopMatrix()

        elif r["type"] == 2:
            # medium reward shape
        
            # core energy sphere
            glColor3f(163/255, 0/255, 102/255)
            glColor3f(0, 1, 1)
            glutSolidSphere(10, 16, 16)

            # Frame cube
            glColor3f(0,0,0)
            glColor3f(1, 0, 1)
            glPushMatrix()
            glScalef(1.8, 1.8, 1.8)
            glutWireCube(12)
            glPopMatrix()

            # Energy ring
            glColor3f(1,1,1)
            glColor3f(255/255, 255/255, 255/255)
            glPushMatrix()
            glRotatef(90, 1, 0, 0)
            glutSolidTorus(2, 16, 10, 24)
            glPopMatrix()
            
        else:

            # big reward shape
            glColor3f(250/255, 250/255, 250/255)
            glPushMatrix()
            glScalef(2.2, 2.2, 0.6)
            glutSolidCube(10)
            glPopMatrix()

            # Crystal spike
            # glColor3f(20/255, 128/255, 93/255)
            glColor3f(0,0,0)            
            glPushMatrix()
            glTranslatef(0, 0, 8)
            glutSolidCone(10, 32, 20, 20)
            glPopMatrix()

            # Portal ring
            glPushMatrix()
            glTranslatef(0, 0, 20)
            glRotatef(90, 1, 0, 0)
            glutSolidTorus(2.5, 18, 12, 32)
            glPopMatrix()

            # Energy orb
            glPushMatrix()
            glTranslatef(0, 0, 36)
            glutSolidSphere(6, 16, 16)
            glPopMatrix()
            

        glPopMatrix()

def check_enemy_collision():
    global lives

    if not level_1_active:
        return

    ex, ey = enemy1["x"], enemy1["y"]
    px, py = player_x, player_y

    dx = px - ex
    dy = py - ey

    if dx*dx + dy*dy <= (player_r + enemy1["r"])**2:
        player_hit_by_enemy()

def update_bullets_level2():
    global bullets

    new_list = []
    for b in bullets:
        b["x"] += b["vx"]
        b["y"] += b["vy"]

        # bullet exists only inside its own green block (TR)
        if level2_green_block(b["x"], b["y"]) != b["home"]:
            continue

        # collision with player only if player also in TR block
        if level2_green_block(player_x, player_y) == b["home"]:
            dx = player_x - b["x"]
            dy = player_y - b["y"]
            if dx*dx + dy*dy <= (player_r + b["r"])**2:
                player_hit_by_enemy()
                continue

        new_list.append(b)

    bullets = new_list

def draw_level2_enemies_and_bullets():
    # type1 enemies
    for e in enemy_L2_type1:
        glPushMatrix()
        glTranslatef(e["x"], e["y"], e.get("z", player_r + 10))
        glColor3f(0.2, 0.2, 0.8)  # blue
        glutSolidSphere(e["r"], 16, 16)
        glPopMatrix()

    # type2 turret
    if enemy_L2_type2 is not None:
        t = enemy_L2_type2
        glPushMatrix()
        glTranslatef(t["x"], t["y"], player_r)
        glColor3f(0.9, 0.3, 0.1)  # orange turret
        glutSolidSphere(t["r"], 16, 16)
        glPopMatrix()

    # bullets
    for b in bullets:
        glPushMatrix()
        glTranslatef(b["x"], b["y"], player_r)
        glColor3f(1.0, 1.0, 0.2)  # yellow bullet
        glutSolidSphere(b["r"], 10, 10)
        glPopMatrix()

def check_enemy_collision():
    # -------- Level 1 collision --------
    if level_1_active:
        ex, ey = enemy1["x"], enemy1["y"]
        dx = player_x - ex
        dy = player_y - ey
        if dx*dx + dy*dy <= (player_r + enemy1["r"])**2:
            player_hit_by_enemy()
        return

    # -------- Level 2 collision (type-1 enemies) --------
    if level_2_active:
        for e in enemy_L2_type1:
            # only collide if player is inside that enemy's green block
            if level2_green_block(player_x, player_y) != e["home"]:
                continue

            dx = player_x - e["x"]
            dy = player_y - e["y"]
            if dx*dx + dy*dy <= (player_r + e["r"])**2:
                player_hit_by_enemy()
                return


def update_bullets_level2():
    global bullets

    new_list = []
    for b in bullets:
        b["x"] += b["vx"]
        b["y"] += b["vy"]

        # bullet exists only inside its own green block (TR)
        if level2_green_block(b["x"], b["y"]) != b["home"]:
            continue

        # collision with player only if player also in TR block
        if level2_green_block(player_x, player_y) == b["home"]:
            dx = player_x - b["x"]
            dy = player_y - b["y"]
            if dx*dx + dy*dy <= (player_r + b["r"])**2:
                player_hit_by_enemy()
                continue

        new_list.append(b)

    bullets = new_list

def draw_level2_enemies_and_bullets():
    # type1 enemies
    for e in enemy_L2_type1:
        glPushMatrix()
        glTranslatef(e["x"], e["y"], e.get("z", player_r + 10))
        glColor3f(0.2, 0.2, 0.8)  # blue
        glutSolidSphere(e["r"], 16, 16)
        glPopMatrix()

    # type2 turret
    if enemy_L2_type2 is not None:
        t = enemy_L2_type2
        glPushMatrix()
        glTranslatef(t["x"], t["y"], player_r)
        glColor3f(0.9, 0.3, 0.1)  # orange turret
        glutSolidSphere(t["r"], 16, 16)
        glPopMatrix()

    # bullets
    for b in bullets:
        glPushMatrix()
        glTranslatef(b["x"], b["y"], player_r)
        glColor3f(1.0, 1.0, 0.2)  # yellow bullet
        glutSolidSphere(b["r"], 10, 10)
        glPopMatrix()



def player_hit_by_enemy():
    global lives

    lives -= 1

    if lives <= 0:
        lives = 0
        # later: game over logic
        print("GAME OVER")
        spawn_player_for_level(get_active_level())
        return

    # respawn player
    spawn_player_for_level(get_active_level())



def player_hit_by_enemy():
    global lives, player_x, player_y, level_start_spawn_x, level_start_spawn_y

    lives -= 1

    if lives <= 0:
        lives = 0
        print("GAME OVER")
        player_x, player_y = level_start_spawn_x, level_start_spawn_y
        return

    # respawn player at the original level-start spawn
    player_x, player_y = level_start_spawn_x, level_start_spawn_y



def check_reward_collision():
    
    global rewards
    to_remove = []

    px, py = player_x, player_y
    pz = player_z + player_r

    for r in rewards:
        dx = px - r["x"]
        dy = py - r["y"]
        dz = pz - r["z"]

        if dx*dx + dy*dy + dz*dz <= (player_r + r["r"])**2:
            apply_reward(r["type"])
            to_remove.append(r)
            break  # still stop on level change

    for r in to_remove:
        if r in rewards:
            rewards.remove(r)
    
    # ---------- Phase progression ----------
    if not rewards:
        advance_reward_phase()

def apply_reward(r_type):
    global score, lives, player_speed, speed_boost_timer

    if r_type == 1:
        score += 10
        player_speed += 2

    elif r_type == 2:
        score += 25
        lives += 1
        player_speed = base_player_speed + 12
        speed_boost_timer = 720

    elif r_type == 3:
        score += 50
        promote_level()


def spawn_horizontal_portals():
    global portal_lr_active, portal_left, portal_right

    y_on_wall = clamp(player_y, -L + portal_r, L - portal_r)

    if not (
        is_valid_portal_terrain(left_inner_x + player_r + 8, y_on_wall) and
        is_valid_portal_terrain(right_inner_x - player_r - 8, y_on_wall)
    ):
        portal_lr_active = False
        return

    portal_left  = {"x": left_inner_x,  "y": y_on_wall, "z": portal_z_center}
    portal_right = {"x": right_inner_x, "y": y_on_wall, "z": portal_z_center}

    portal_lr_active = True


def spawn_vertical_portals():
    global portal_ud_active, portal_top, portal_bottom

    x_on_wall = clamp(player_x, -L + portal_r, L - portal_r)

    if not (
        is_valid_portal_terrain(x_on_wall, L - player_r - 8) and
        is_valid_portal_terrain(x_on_wall, -L + player_r + 8)
    ):
        portal_ud_active = False
        return

    portal_top    = {"x": x_on_wall, "y": L - wall_thickness, "z": portal_z_center}
    portal_bottom = {"x": x_on_wall, "y": -L + wall_thickness, "z": portal_z_center}

    portal_ud_active = True


def is_valid_portal_terrain(x, y):
    
    if level_1_active and allowed_on_green(x, y):
        return True

    if level_2_active and allowed_on_level_2(x, y):
        return True

    if level_3_active and allowed_on_level_3(x, y):
        return True

    return False


def toggle_horizontal_portals():
    global portal_lr_active, portal_ud_active, portal_cooldown

    if portal_lr_active:
        portal_lr_active = False
        portal_cooldown = 0
    else:
        portal_ud_active = False
        spawn_horizontal_portals()


def toggle_vertical_portals():
    global portal_lr_active, portal_ud_active, portal_cooldown

    if portal_ud_active:
        portal_ud_active = False
        portal_cooldown = 0
    else:
        portal_lr_active = False
        spawn_vertical_portals()


def draw_portal_at(x_plane, cy, cz):
    
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x_plane, cy, cz)
    for i in range(0, 41):
        ang = (2.0 * math.pi * i) / 40.0
        yy = cy + portal_r * math.cos(ang)
        zz = cz + portal_r * math.sin(ang)
        glVertex3f(x_plane, yy, zz)
    glEnd()
    
    
def draw_portal_at_y(y_plane, cx, cz):
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(cx, y_plane, cz)
    for i in range(0, 41):
        ang = (2.0 * math.pi * i) / 40.0
        xx = cx + portal_r * math.cos(ang)
        zz = cz + portal_r * math.sin(ang)
        glVertex3f(xx, y_plane, zz)
    glEnd()


def draw_portals():
    
    if portal_lr_active:
        draw_portal_at(left_inner_x + 0.2,  portal_left["y"],  portal_left["z"])
        draw_portal_at(right_inner_x - 0.2, portal_right["y"], portal_right["z"])

    if portal_ud_active:
        draw_portal_at_y(L - wall_thickness - 0.2, portal_top["x"], portal_top["z"])
        draw_portal_at_y(-L + wall_thickness + 0.2, portal_bottom["x"], portal_bottom["z"])


def in_minor_hazard_zone(px, py):
    # block teleporting unless player stands on GREEN (tile == 1)
    if level_2_active:
        return level2_cell_at(px, py) != 1
    if level_3_active:
        return level3_cell_at(px, py) != 1
    return False



def try_teleport():
    
    global player_x, player_y, portal_cooldown

    if  portal_cooldown > 0:
        return
    
    if (level_2_active or level_3_active or level_4_active) and in_minor_hazard_zone(player_x, player_y):
        return


    if portal_cooldown > 0:
        return
    
    pz = player_z + player_r

    if portal_lr_active:
        
        entry_left_x  = left_inner_x + player_r
        entry_right_x = right_inner_x - player_r
        x_tol = player_speed  # 18.0

        # ---- Enter LEFT portal -> Exit RIGHT portal ----
        if abs(player_x - entry_left_x) <= x_tol:
            dy = player_y - portal_left["y"]
            dz = pz - portal_left["z"]
            if (dy * dy + dz * dz) <= (portal_r * portal_r):
                player_x = right_inner_x - player_r - 8
                player_y = portal_right["y"]
                portal_cooldown = 6
                return

        # ---- Enter RIGHT portal -> Exit LEFT portal ----
        if abs(player_x - entry_right_x) <= x_tol:
            dy = player_y - portal_right["y"]
            dz = pz - portal_right["z"]
            if (dy * dy + dz * dz) <= (portal_r * portal_r):
                player_x = left_inner_x + player_r + 8
                player_y = portal_left["y"]
                portal_cooldown = 6
                return

    if portal_ud_active:            
        entry_top_y = L - player_r
        entry_bottom_y = -L + player_r
        y_tol = player_speed

        # ---- Enter TOP portal -> Exit BOTTOM ----
        if abs(player_y - entry_top_y) <= y_tol:
            dx = player_x - portal_top["x"]
            dz = pz - portal_top["z"]
            if (dx * dx + dz * dz) <= (portal_r * portal_r):
                player_y = -L + player_r + 8
                player_x = portal_bottom["x"]
                portal_cooldown = 6
                return

        # ---- Enter BOTTOM portal -> Exit TOP ----
        if abs(player_y - entry_bottom_y) <= y_tol:
            dx = player_x - portal_bottom["x"]
            dz = pz - portal_bottom["z"]
            if (dx * dx + dz * dz) <= (portal_r * portal_r):
                player_y = L - player_r - 8
                player_x = portal_top["x"]
                portal_cooldown = 6
                return


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)






def keyboardListener(key, x, y):
    global portal_cooldown , player_x, player_y

    if portal_cooldown > 0:
        portal_cooldown -= 1

    # movement
    if key == b'w':
        try_move(0, player_speed)
    elif key == b's':
        try_move(0, -player_speed)
    elif key == b'a':
        try_move(-player_speed, 0)
    elif key == b'd':
        try_move(player_speed, 0)

    # spawn portal pair
    elif key == b'1':
        if can_place_portal_here(player_x, player_y):
            toggle_horizontal_portals()

    elif key == b'2':
        if can_place_portal_here(player_x, player_y):
            toggle_vertical_portals()


    
    
    elif key == b'0':
        set_active_level(1)
    elif key == b'9':
        set_active_level(2)
    elif key == b'8':
        set_active_level(3)
    elif key == b'7':
        set_active_level(4)
    
    
    try_teleport()

    glutPostRedisplay()


def specialKeyListener(key, x, y):
    global camera_pos
    cx, cy, cz = camera_pos

    if key == GLUT_KEY_LEFT:
        cx -= 10
    if key == GLUT_KEY_RIGHT:
        cx += 10
    if key == GLUT_KEY_UP:
        cz += 10
    if key == GLUT_KEY_DOWN:
        cz -= 10

    camera_pos = (cx, cy, cz)


def mouseListener(button, state, x, y):
    pass


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x, y, z = camera_pos
    gluLookAt(
        x, y, z,      # camera position
        0, 120, 0,    # look-at target (slightly forward so ground looks nicer)
        0, 0, 1       # up vector
    )


def draw_level_1():
    global  L, hazard_half_width, wall_height, wall_height
    # L = 600  # half length (matches your GRID_LENGTH usage style)

    # Hazard settings
    # hazard_half_width = 130  # hazard zone width = 260
    hazard_z = 0.02          

    glBegin(GL_QUADS)

    # ---------- Ground (green) ----------
    glColor3f(0.44, 0.67, 0.29)

    # left green strip
    glVertex3f(-L, -L, 0)
    glVertex3f(-hazard_half_width, -L, 0)
    glVertex3f(-hazard_half_width, L, 0)
    glVertex3f(-L, L, 0)

    # right green strip
    glVertex3f(hazard_half_width, -L, 0)
    glVertex3f(L, -L, 0)
    glVertex3f(L, L, 0)
    glVertex3f(hazard_half_width, L, 0)

    # ---------- Hazardous Zone  ----------
    glColor3f(0.8, 0.0, 0.0)
    glVertex3f(-hazard_half_width, -L, hazard_z)
    glVertex3f(hazard_half_width, -L, hazard_z)
    glVertex3f(hazard_half_width, L, hazard_z)
    glVertex3f(-hazard_half_width, L, hazard_z)

    # ---------- Left wall (bluish) ----------
    # A rectangular vertical wall along the left side of the plane.
    glColor3f(0.70, 0.78, 0.92)  # bluish
    left_outer_x = -L
    left_inner_x = -L + wall_thickness

    # Wall face (inner face visible from center)
    glVertex3f(left_inner_x, -L, 0)
    glVertex3f(left_inner_x, L, 0)
    glVertex3f(left_inner_x, L, wall_height)
    glVertex3f(left_inner_x, -L, wall_height)

    # # Wall top
    # glVertex3f(left_outer_x, -L, wall_height)
    # glVertex3f(left_outer_x, L, wall_height)
    # glVertex3f(left_inner_x, L, wall_height)
    # glVertex3f(left_inner_x, -L, wall_height)

    # # Wall outer face (optional but makes it look like a slab)
    # glColor3f(0.60, 0.70, 0.88)
    # glVertex3f(left_outer_x, -L, 0)
    # glVertex3f(left_outer_x, L, 0)
    # glVertex3f(left_outer_x, L, wall_height)
    # glVertex3f(left_outer_x, -L, wall_height)

    # ---------- Right wall (bluish) ----------
    glColor3f(0.70, 0.78, 0.92)
    
    right_outer_x = L
    right_inner_x = L #- wall_thickness

    # Wall face (inner face visible from center)
    glVertex3f(right_inner_x, -L, 0)
    glVertex3f(right_inner_x, L, 0)
    glVertex3f(right_inner_x, L, wall_height)
    glVertex3f(right_inner_x, -L, wall_height)

    # # Wall top
    # glVertex3f(right_inner_x, -L, wall_height)
    # glVertex3f(right_inner_x, L, wall_height)
    # glVertex3f(right_outer_x, L, wall_height)
    # glVertex3f(right_outer_x, -L, wall_height)

    # # Wall outer face
    # glColor3f(0.60, 0.70, 0.88)
    # glVertex3f(right_outer_x, -L, 0)
    # glVertex3f(right_outer_x, L, 0)
    # glVertex3f(right_outer_x, L, wall_height)
    # glVertex3f(right_outer_x, -L, wall_height)

    glEnd()


def draw_level_2():

    # Colors
    color_map = {
        1: (0.44, 0.67, 0.29),  # green
        2: (0.95, 0.85, 0.10),  # yellow
        3: (0.85, 0.10, 0.10),  # red
    }

    # Cell geometry
    cols = 7
    rows = 7
    cell_w = (2 * L) / cols
    cell_h = (2 * L) / rows
    start_x = -L
    start_y = -L

    
    
    glBegin(GL_QUADS)

    def draw_cell(col, row, val):
        x0 = start_x + col * cell_w
        x1 = x0 + cell_w
        y0 = start_y + row * cell_h
        y1 = y0 + cell_h
        glColor3f(*color_map[val])
        glVertex3f(x0, y0, 0)
        glVertex3f(x1, y0, 0)
        glVertex3f(x1, y1, 0)
        glVertex3f(x0, y1, 0)

    for row in range(rows):
        for col in range(cols):
            draw_cell(col, row, LEVEL2_PATTERN[row][col])

    
    glColor3f(0.70, 0.78, 0.92)
    
    # ---------- Top wall  ----------
    glVertex3f(-left_inner_x, L, 0)
    glVertex3f(left_inner_x, L, 0)
    glVertex3f(left_inner_x, L, wall_height)
    glVertex3f(-left_inner_x, L, wall_height)
    
    
    # ---------- Left wall 
    glVertex3f(-L, -L, 0)
    glVertex3f(-L, L, 0)
    glVertex3f(-L, L, wall_height)
    glVertex3f(-L, -L, wall_height)
    
    
    # ---------- Right wall
    glVertex3f(right_inner_x, -L, 0)
    glVertex3f(right_inner_x, L, 0)
    glVertex3f(right_inner_x, L, wall_height)
    glVertex3f(right_inner_x, -L, wall_height)
    
    
     # ---------- Bottom wall  ----------
    glVertex3f(-left_inner_x, -L, 0)
    glVertex3f(left_inner_x, -L, 0)
    glVertex3f(left_inner_x, -L, wall_height)
    glVertex3f(-left_inner_x, -L, wall_height)
    
    glEnd()


def draw_level_3():
    color_map = {
        1: (0.44, 0.67, 0.29),  # green
        2: (0.95, 0.85, 0.10),  # yellow
        3: (0.85, 0.10, 0.10),  # red
    }

    cols = LEVEL3_COLS
    rows = LEVEL3_ROWS
    cell_w = (2 * L) / cols
    cell_h = (2 * L) / rows
    start_x = -L
    start_y = -L

    glBegin(GL_QUADS)

    def draw_cell(col, row, val):
        x0 = start_x + col * cell_w
        x1 = x0 + cell_w
        y0 = start_y + row * cell_h
        y1 = y0 + cell_h
        glColor3f(*color_map[val])
        glVertex3f(x0, y0, 0)
        glVertex3f(x1, y0, 0)
        glVertex3f(x1, y1, 0)
        glVertex3f(x0, y1, 0)

    for row in range(rows):
        for col in range(cols):
            draw_cell(col, row, LEVEL3_PATTERN[row][col])

    # --- Walls (same as level 2) ---
    glColor3f(0.70, 0.78, 0.92)

    # Top wall
    glVertex3f(-left_inner_x, L, 0)
    glVertex3f(left_inner_x, L, 0)
    glVertex3f(left_inner_x, L, wall_height)
    glVertex3f(-left_inner_x, L, wall_height)

    # Left wall
    glVertex3f(-L, -L, 0)
    glVertex3f(-L, L, 0)
    glVertex3f(-L, L, wall_height)
    glVertex3f(-L, -L, wall_height)

    # Right wall
    glVertex3f(right_inner_x, -L, 0)
    glVertex3f(right_inner_x, L, 0)
    glVertex3f(right_inner_x, L, wall_height)
    glVertex3f(right_inner_x, -L, wall_height)

    # Bottom wall
    glVertex3f(-left_inner_x, -L, 0)
    glVertex3f(left_inner_x, -L, 0)
    glVertex3f(left_inner_x, -L, wall_height)
    glVertex3f(-left_inner_x, -L, wall_height)

    glEnd()


def draw_environment():
    
    if level_1_active:
        draw_level_1()
    elif level_2_active:
        draw_level_2()    
    elif level_3_active:
        draw_level_3()


def update_enemy_level_1():
    if not enemy1["active"]:
        return

    ex, ey = enemy1["x"], enemy1["y"]

    # -------- CASE 1: Player NOT on enemy side → patrol --------
    if not player_on_enemy_side():
        enemy1["y"] += enemy1["speed"] * enemy1["dir"]

        # bounce back at lane limits
        if ey > L - 50:
            enemy1["dir"] = -1
        elif ey < -L + 50:
            enemy1["dir"] = 1

    # -------- CASE 2: Player on enemy side → chase --------
    else:
        dx = player_x - ex
        dy = player_y - ey
        dist = math.sqrt(dx*dx + dy*dy)

        if dist > 0:
            enemy1["x"] += enemy1["speed"] * (dx / dist)
            enemy1["y"] += enemy1["speed"] * (dy / dist)

    # ensure enemy never leaves green
    if not allowed_on_green(enemy1["x"], enemy1["y"]):
        enemy1["dir"] *= -1

def update_level2_type1_enemy(e):
    player_block = level2_green_block(player_x, player_y)

    # Always compute bounds once
    bounds = level2_block_bounds(e["home"])
    if bounds is None:
        return
    xmin, xmax, ymin, ymax = bounds

    # ---- PATROL when player is NOT in this enemy's block ----
    if player_block != e["home"]:
        e["y"] += e["speed"] * e["dir"]

        # ✅ bounce inside the block (like level 1)
        if e["y"] >= ymax:
            e["y"] = ymax
            e["dir"] = -1
        elif e["y"] <= ymin:
            e["y"] = ymin
            e["dir"] = 1

    # ---- CHASE when player enters this enemy's block ----
    else:
        dx = player_x - e["x"]
        dy = player_y - e["y"]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            e["x"] += e["speed"] * (dx / dist)
            e["y"] += e["speed"] * (dy / dist)

    # ✅ Clamp always (safety) so chase can't escape the block
    e["x"] = clamp(e["x"], xmin, xmax)
    e["y"] = clamp(e["y"], ymin, ymax)


def fire_bullet_from_turret(turret, vx, vy):
    bullets.append({
        "x": turret["x"],
        "y": turret["y"],
        "r": 6.0,
        "vx": vx,
        "vy": vy,
        "home": turret["home"]   # "TR"
    })


def update_level2_type2_enemy(turret):
    if turret is None:
        return

    # cooldown tick
    if turret["fire_cd"] > 0:
        turret["fire_cd"] -= 1

    player_block = level2_green_block(player_x, player_y)
    player_in_tr = (player_block == turret["home"])  # TR

    # ---- Idle: spin + shoot slowly along spin direction ----
    if not player_in_tr:
        turret["angle"] = (turret["angle"] + turret["spin_speed"]) % 360.0

        if turret["fire_cd"] == 0:
            ang = math.radians(turret["angle"])
            speed = 0.2
            vx = speed * math.cos(ang)
            vy = speed * math.sin(ang)
            fire_bullet_from_turret(turret, vx, vy)
            turret["fire_cd"] = 300  

    # ---- Player in TR: shoot toward player ----
    else:
        if turret["fire_cd"] == 0:
            dx = player_x - turret["x"]
            dy = player_y - turret["y"]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                speed = 0.5
                vx = speed * (dx / dist)
                vy = speed * (dy / dist)
                fire_bullet_from_turret(turret, vx, vy)
                turret["fire_cd"] = 200


def idle():
    global speed_boost_timer, player_speed

    if level_1_active:
        update_enemy_level_1()

    if level_2_active:
        for e in enemy_L2_type1:
            update_level2_type1_enemy(e)
        update_level2_type2_enemy(enemy_L2_type2)
        update_bullets_level2()




    if speed_boost_timer > 0:
        speed_boost_timer -= 1
        if speed_boost_timer == 0:
            player_speed = base_player_speed

    check_reward_collision()
    check_enemy_collision()

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_environment()
    draw_rewards()
    if level_2_active:
        draw_level2_enemies_and_bullets()


    # portals should be drawn after walls exist
    draw_portals()

    # draw player on top
    draw_player()

    # draw_text(10, 770, "WASD move | 1 spawn portals")
    draw_text(10, 740, f"Player: ({player_x:.1f}, {player_y:.1f})")
    draw_text(10, 770, f"Score: {score}")
    hearts = "<3" * lives
    draw_text(10, 710, f"Lives: {hearts}")


    if level_1_active:
        draw_enemy_level_1()


    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Environment (Template Style)")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    spawn_rewards_for_level()
    if level_2_active:
        spawn_level2_enemies()

    
    glutMainLoop()

if __name__ == "__main__":
    main()