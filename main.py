from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Camera-related variables (better viewing angle)
# (x, y, z) -> x sideways, y forward/back, z height
camera_pos = (-450, -650, 520)

fovY = 95
GRID_LENGTH = 600
rand_var = 423

# ---------------- Player ----------------
player_x = -350.0
player_y = 0.0
player_z = 0.0
player_r = 18.0
player_speed = 18.0

# ---------------- World params (keep consistent with draw_environment) ----------------
L = 600
road_half_width = 130
wall_thickness = 45
wall_height = 380

left_inner_x  = -L + wall_thickness
right_inner_x =  L - wall_thickness

# ---------------- Portal ----------------
portal_active = False
portal_r = 55.0
portal_z_center = 25.0  # height center of portal on the wall
portal_left = {"x": left_inner_x, "y": 0.0, "z": portal_z_center}
portal_right = {"x": right_inner_x, "y": 0.0, "z": portal_z_center}
portal_plane_eps = 6.0  # how close to the wall plane counts as "enter"
portal_cooldown = 0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def allowed_on_green(nx, ny):
    # Inside plane bounds (leave a margin for player radius)
    if nx < -L + player_r or nx > L - player_r:
        return False
    if ny < -L + player_r or ny > L - player_r:
        return False

    # Can't cross road: must stay fully on left strip OR fully on right strip
    left_ok  = nx <= (-road_half_width - player_r)
    right_ok = nx >= ( road_half_width + player_r)
    if not (left_ok or right_ok):
        return False

    # Can't go into the walls thickness area (inner face boundary)
    if nx < left_inner_x + player_r:
        return False
    if nx > right_inner_x - player_r:
        return False

    return True

def try_move(dx, dy):
    global player_x, player_y
    nx = player_x + dx
    ny = player_y + dy
    if allowed_on_green(nx, ny):
        player_x, player_y = nx, ny

def draw_player():
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z + player_r)

    # Contrasty color vs green: orange-red
    glColor3f(1.0, 0.25, 0.10)
    glutSolidSphere(player_r, 16, 16)

    # tiny "cap" cube to look like a character
    glTranslatef(0, 0, player_r + 8)
    glColor3f(1.0, 0.85, 0.10)
    glutSolidCube(14)

    glPopMatrix()

def spawn_portals():
    global portal_active, portal_left, portal_right

    # portal appears on both walls at the player's current Y (clamped)
    y_on_wall = clamp(player_y, -L + portal_r, L - portal_r)

    portal_left  = {"x": left_inner_x,  "y": y_on_wall, "z": portal_z_center}
    portal_right = {"x": right_inner_x, "y": y_on_wall, "z": portal_z_center}

    portal_active = True




def draw_portal_at(x_plane, cy, cz):
    # circle in the Y-Z plane at fixed X (wall plane)
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x_plane, cy, cz)
    for i in range(0, 41):
        ang = (2.0 * math.pi * i) / 40.0
        yy = cy + portal_r * math.cos(ang)
        zz = cz + portal_r * math.sin(ang)
        glVertex3f(x_plane, yy, zz)
    glEnd()

def draw_portals():
    if not portal_active:
        return

    # draw on inner faces; add a tiny epsilon so it doesn't z-fight with wall
    draw_portal_at(left_inner_x + 0.2,  portal_left["y"],  portal_left["z"])
    draw_portal_at(right_inner_x - 0.2, portal_right["y"], portal_right["z"])


def try_teleport():
    global player_x, player_y, portal_cooldown

    if not portal_active:
        return

    if portal_cooldown > 0:
        return

    pz = player_z + player_r

    entry_left_x  = left_inner_x + player_r
    entry_right_x = right_inner_x - player_r

    # ✅ tolerance must be >= movement jump size, otherwise you may never "hit" it
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
    global portal_cooldown

    # decrease cooldown over keypresses
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
        spawn_portals()

    # check teleport after moving (or even after spawning)
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


def draw_environment():

    L = 600  # half length (matches your GRID_LENGTH usage style)

    # Road settings
    road_half_width = 130  # road width = 260
    road_z = 0.02           # tiny lift to avoid z-fighting with ground

    # Wall settings
    wall_height = 380
    wall_thickness = 45

    glBegin(GL_QUADS)

    # ---------- Ground (green) ----------
    glColor3f(0.44, 0.67, 0.29)

    # left green strip
    glVertex3f(-L, -L, 0)
    glVertex3f(-road_half_width, -L, 0)
    glVertex3f(-road_half_width, L, 0)
    glVertex3f(-L, L, 0)

    # right green strip
    glVertex3f(road_half_width, -L, 0)
    glVertex3f(L, -L, 0)
    glVertex3f(L, L, 0)
    glVertex3f(road_half_width, L, 0)

    # ---------- Road (dark grey strip in middle) ----------
    glColor3f(0.30, 0.30, 0.30)  # dark grey
    glVertex3f(-road_half_width, -L, road_z)
    glVertex3f(road_half_width, -L, road_z)
    glVertex3f(road_half_width, L, road_z)
    glVertex3f(-road_half_width, L, road_z)

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

    # Wall top
    glVertex3f(left_outer_x, -L, wall_height)
    glVertex3f(left_outer_x, L, wall_height)
    glVertex3f(left_inner_x, L, wall_height)
    glVertex3f(left_inner_x, -L, wall_height)

    # Wall outer face (optional but makes it look like a slab)
    glColor3f(0.60, 0.70, 0.88)
    glVertex3f(left_outer_x, -L, 0)
    glVertex3f(left_outer_x, L, 0)
    glVertex3f(left_outer_x, L, wall_height)
    glVertex3f(left_outer_x, -L, wall_height)

    # ---------- Right wall (bluish) ----------
    glColor3f(0.70, 0.78, 0.92)
    right_outer_x = L
    right_inner_x = L - wall_thickness

    # Wall face (inner face visible from center)
    glVertex3f(right_inner_x, -L, 0)
    glVertex3f(right_inner_x, L, 0)
    glVertex3f(right_inner_x, L, wall_height)
    glVertex3f(right_inner_x, -L, wall_height)

    # Wall top
    glVertex3f(right_inner_x, -L, wall_height)
    glVertex3f(right_inner_x, L, wall_height)
    glVertex3f(right_outer_x, L, wall_height)
    glVertex3f(right_outer_x, -L, wall_height)

    # Wall outer face
    glColor3f(0.60, 0.70, 0.88)
    glVertex3f(right_outer_x, -L, 0)
    glVertex3f(right_outer_x, L, 0)
    glVertex3f(right_outer_x, L, wall_height)
    glVertex3f(right_outer_x, -L, wall_height)

    glEnd()


def idle():
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()

    draw_environment()

    # portals should be drawn after walls exist
    draw_portals()

    # draw player on top
    draw_player()

    draw_text(10, 770, "WASD move | 1 spawn portals")
    draw_text(10, 740, f"Player: ({player_x:.1f}, {player_y:.1f})")

    glutSwapBuffers()



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Environment (Template Style)")

    glEnable(GL_DEPTH_TEST)  # IMPORTANT: depth on (your template clears depth buffer)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
