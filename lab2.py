import pygame
import math

pygame.init()
W, H = 900, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Удаление невидимых ребер")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)  

depth = 0.3

front = [
    (0.0, 0.0, depth),
    (0.0, 1.0, depth),
    (0.0, -1.0, depth),
    (1.0, 1.0, depth),
    (1.0, -1.0, depth),
]

back = [
    (0.0, 0.0, -depth),
    (0.0, 1.0, -depth),
    (0.0, -1.0, -depth),
    (1.0, 1.0, -depth),
    (1.0, -1.0, -depth),
]

vertices = front + back
cx = sum(v[0] for v in vertices) / len(vertices)
cy = sum(v[1] for v in vertices) / len(vertices)
cz = sum(v[2] for v in vertices) / len(vertices)

print("Центр буквы:", cx, cy, cz)

edges = [
    (0,1), (0,2), (0,3), (0,4),
    (5,6), (5,7), (5,8), (5,9),
    (0,5), (1,6), (2,7), (3,8), (4,9),
]

#вращение
angle_z = 0.0
angle_x = 0.0
angle_y = 0.0
#перемещение
tx, ty, tz = 0.0, 0.0, 0.0
change = 0.02
scale = 200
#масштаб
scale_factor = 1.0
#длина осей
len = 1.5
cam1 = math.radians(-30)   
cam2 = math.radians(20)  

#матрица перемещения
def transfer_matr(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ]

#матрица вращения по z
def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1],
    ]

#врещение вокруг x
def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1],
    ]

#вращение вокруг y
def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1],
    ]

#перемещение
def transfer(M, v):
    x, y, z = v
    vec = [x, y, z, 1.0]
    out = [0.0, 0.0, 0.0, 0.0]
    for i in range(4):
        for j in range(4):
            out[i] += M[i][j] * vec[j]
    return (out[0], out[1], out[2])

#проекция
def to_screen(p):
    x, y, z = p

    cy, sy = math.cos(cam1), math.sin(cam1)
    x1 =  x * cy + z * sy
    z1 = -x * sy + z * cy
    y1 =  y

    cp, sp = math.cos(cam2), math.sin(cam2)
    x2 = x1
    y2 = y1 * cp - z1 * sp

    return (int(W // 2 + x2 * scale),
            int(H // 2 - y2 * scale))

#переножение матриц
def mul(A, B):
    result = [[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            for k in range(4):
                result[i][j] += A[i][k] * B[k][j]
    return result

#приведение к градусам
def norm_angle_deg(rad):
    deg = math.degrees(rad) % 360
    if deg > 180:
        deg -= 360
    return deg

running = True
auto_rotating = False
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()

    ctrl  = keys[pygame.K_LCTRL]
    shift = keys[pygame.K_LSHIFT]
    z_key = keys[pygame.K_z]
    if z_key and ctrl:
        angle_z += change    
    if z_key and shift:
        angle_z -= change

    x_key = keys[pygame.K_x]
    if x_key and ctrl:
        angle_x += change    
    if x_key and shift:
        angle_x -= change

    y_key = keys[pygame.K_y]
    if y_key and ctrl:
        angle_y += change    
    if y_key and shift:
        angle_y -= change

    R = mul(rot_z(angle_z), mul(rot_y(angle_y), rot_x(angle_x)))
    T_plus  = transfer_matr( cx,  cy,  cz)
    T_minus = transfer_matr(-cx, -cy, -cz)

    M = mul(T_plus, mul(R, T_minus))

    transformed = []
    for v in vertices:
        transformed.append(transfer(M, v))
    screen.fill((255, 255, 255))

    axis_points = [
        ((0, 0, 0), (len, 0, 0), (255, 0, 0), "X"),
        ((0, 0, 0), (0, len, 0), (0, 180, 0), "Y"),
        ((0, 0, 0), (0, 0, len), (0, 0, 255), "Z"),
    ]
    for p1, p2, color, name in axis_points:
        q1 = to_screen(p1)
        q2 = to_screen(p2)
        pygame.draw.line(screen, color, q1, q2, 2)
        text = font.render(name, True, color)
        screen.blit(text, (q2[0] + 5, q2[1] - 5))

    dot = to_screen((0, 0, 0))
    pygame.draw.circle(screen, (0, 0, 0), dot, 4)

    for a, b in edges:
        pa = to_screen(transformed[a])
        pb = to_screen(transformed[b])
        pygame.draw.line(screen, (0, 0, 0), pa, pb, 3)

    info = [
        f"rot:  X={norm_angle_deg(angle_x):+7.1f}  Y={norm_angle_deg(angle_y):+7.1f}  Z={norm_angle_deg(angle_z):+7.1f}",
        "Ctrl + Z/X/Y - вращение +",
        "Shift + Z/X/Y - вращение -",
        "ESC - выход",
    ]
    
    for i, line in enumerate(info):
        text = font.render(line, True, (0, 0, 0))
        screen.blit(text, (10, 10 + i * 24))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()