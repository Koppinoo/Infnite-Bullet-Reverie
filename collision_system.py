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
