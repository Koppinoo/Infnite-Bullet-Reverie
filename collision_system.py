# collision_system.py
def check_collision(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
    """
    Returns True if two rectangular objects are colliding.
    """
    return (
        obj1_x < obj2_x + obj2_w and
        obj1_x + obj1_w > obj2_x and
        obj1_y < obj2_y + obj2_h and
        obj1_y + obj1_h > obj2_y
    )


# --- Player hitbox ---
HITBOX_RADIUS = 4  # Small visual hitbox for precision dodging

import math

def circle_rect_collision(cx, cy, radius, rx, ry, rw, rh):
    """
    Checks collision between a circle (player hitbox)
    and a rectangle (enemy or bullet).
    """
    # Clamp circle centre to rectangle bounds
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))

    # Calculate distance from circle centre to closest point
    dx = cx - closest_x
    dy = cy - closest_y

    return (dx * dx + dy * dy) <= (radius * radius)
