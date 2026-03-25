import struct

def get_stl_bounding_box(filepath):
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    try:
        with open(filepath, 'rb') as f:
            f.read(80) # Skip the 80-byte header
            num_triangles = struct.unpack('<I', f.read(4))[0]

            for _ in range(num_triangles):
                f.read(12) # Skip the face normal
                for _ in range(3): # Loop through the 3 vertices
                    x, y, z = struct.unpack('<fff', f.read(12))
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
                f.read(2) # Skip the 2-byte attribute

        # Small buffer still added
        print(f"EXCLUDE_MIN_X, EXCLUDE_MAX_X = {min_x-0.5:.2f}, {max_x+0.5:.2f}")
        print(f"EXCLUDE_MIN_Y, EXCLUDE_MAX_Y = {min_y-0.5:.2f}, {max_y+0.5:.2f}")
        
    except Exception as e:
        print(f"Error reading STL: {e}")

get_stl_bounding_box('five_maze.stl')