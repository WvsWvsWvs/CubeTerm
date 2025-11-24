import curses
import math
import time

# Global rotation angles
A = B = C = 0

# Screen size and cube parameters
width, height = 160, 44
distance_from_cam = 100
K1 = 40
increment_speed = 0.6
background_ascii = '.'

def calculate_x(i, j, k):
    return (
        j * math.sin(A) * math.sin(B) * math.cos(C)
        - k * math.cos(A) * math.sin(B) * math.cos(C)
        + j * math.cos(A) * math.sin(C)
        + k * math.sin(A) * math.sin(C)
        + i * math.cos(B) * math.cos(C)
    )

def calculate_y(i, j, k):
    return (
        j * math.cos(A) * math.cos(C)
        + k * math.sin(A) * math.cos(C)
        - j * math.sin(A) * math.sin(B) * math.sin(C)
        + k * math.cos(A) * math.sin(B) * math.sin(C)
        - i * math.cos(B) * math.sin(C)
    )

def calculate_z(i, j, k):
    return (
        k * math.cos(A) * math.cos(B)
        - j * math.sin(A) * math.cos(B)
        + i * math.sin(B)
    )

def calculate_surface(cube_x, cube_y, cube_z, ch, buffer, zbuffer, horizontal_offset):
    x = calculate_x(cube_x, cube_y, cube_z)
    y = calculate_y(cube_x, cube_y, cube_z)
    z = calculate_z(cube_x, cube_y, cube_z) + distance_from_cam

    ooz = 1 / z
    xp = int(width / 2 + horizontal_offset + K1 * ooz * x * 2)
    yp = int(height / 2 + K1 * ooz * y)

    if 0 <= xp < width and 0 <= yp < height:
        idx = xp + yp * width
        if ooz > zbuffer.get(idx, 0):
            zbuffer[idx] = ooz
            buffer[idx] = (xp, yp, ch)

def frange(start, stop, step):
    while start < stop:
        yield start
        start += step

def draw_cube(cube_width, char_set, buffer, zbuffer, horizontal_offset):
    for cube_x in frange(-cube_width, cube_width, increment_speed):
        for cube_y in frange(-cube_width, cube_width, increment_speed):
            calculate_surface(cube_x, cube_y, -cube_width, char_set[0], buffer, zbuffer, horizontal_offset)
            calculate_surface(cube_width, cube_y, cube_x, char_set[1], buffer, zbuffer, horizontal_offset)
            calculate_surface(-cube_width, cube_y, -cube_x, char_set[2], buffer, zbuffer, horizontal_offset)
            calculate_surface(-cube_x, cube_y, cube_width, char_set[3], buffer, zbuffer, horizontal_offset)
            calculate_surface(cube_x, -cube_width, -cube_y, char_set[4], buffer, zbuffer, horizontal_offset)
            calculate_surface(cube_x, cube_width, cube_y, char_set[5], buffer, zbuffer, horizontal_offset)

def main(stdscr):
    global A, B, C
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Make getch() non-blocking

    while True:
        buffer = {}
        zbuffer = {}

        draw_cube(20, b'@$~#;+', buffer, zbuffer, -2 * 20)
        draw_cube(10, b'@$~#;+', buffer, zbuffer, 1 * 10)
        draw_cube(5,  b'@$~#;+', buffer, zbuffer, 8 * 5)

        stdscr.erase()
        for _, (x, y, ch) in buffer.items():
            try:
                stdscr.addch(y, x, ch)
            except curses.error:
                pass  # ignore if off screen

        stdscr.refresh()
        time.sleep(0.016)

        A += 0.05
        B += 0.05
        C += 0.01

        # Optional: press 'q' to quit
        if stdscr.getch() == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
