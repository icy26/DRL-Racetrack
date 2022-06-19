import pygame
import math

RED = (255,0,0)
x = 200
y = 200

vel = 0
steeringangle = 0
quadrantangle = 0
quadrant = 0

def draw_car():
    pos = (x, y)
    pygame.draw.circle(screen, RED, pos, 12)

#Simple speed mechanics, acceleration curves, power band, gears etc to be added over iterations
def accelerate():
    global vel
    vel += 0.05

def deccelerate():
    global vel
    if vel > 0.025:
        vel -= 0.025
    else:
        vel = 0

def brake():
    global vel
    if vel > 0.05:
        vel -= 0.05
    else:
        vel = 0

def steer_left():
    global steeringangle
    if steeringangle == 0:
        steeringangle = 359
    else:
        steeringangle -= 1


def steer_right():
    global steeringangle
    if steeringangle == 359:
        steeringangle = 0
    else:
        steeringangle += 1


def convert_steeringangle_to_quadrantangle(steerangle):
    global quadrantangle, quadrant
    if 0 <= steerangle < 90:
        quadrant = 0
        quadrantangle = 90 - steerangle
    elif 90 <= steerangle < 180:
        quadrant = 1
        quadrantangle = steerangle - 90
    elif 180 <= steerangle < 270:
        quadrant = 2
        quadrantangle = 270 - steerangle
    else:
        quadrant = 3
        quadrantangle = steerangle - 270

def movement(quad, angle):
    global x, y, vel

    angleRad = math.radians(angle)

    #Top right quad (moving north east)
    if quad == 0:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y -= oppo
        x += adj
    # Bottom right quad (moving south east)
    elif quad == 1:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y += oppo
        x += adj
    # Bottom left quad (moving south west)
    elif quad == 2:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y += oppo
        x -= adj
    #Top left quad (moving north west)
    else:
        hypo = vel
        oppo = math.sin(angleRad) * hypo
        adj = math.cos(angleRad) * hypo

        y -= oppo
        x -= adj

def main():
    global screen, x, y, vel, quadrant, quadrantangle, steeringangle

    pygame.init()

    (width, height) = (900, 720)
    background_colour = (245, 225, 169)
    name = 'The Screen'

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(name)
    screen.fill(background_colour)

    font = pygame.font.SysFont('Comic Sans', 15)


    running = True
    while running:

        velText = font.render('vel: ' + str(vel), False, (0, 0, 0))
        steerText = font.render('steeringangle: ' + str(steeringangle), False, (0, 0, 0))
        quadangleText = font.render('quadrantangle: ' + str(quadrant), False, (0, 0, 0))
        quadText = font.render('quadrant: ' + str(quadrantangle), False, (0, 0, 0))
        xcoord = font.render('x: ' + str(x), False, (0, 0, 0))
        ycoord = font.render('y: ' + str(y), False, (0, 0, 0))

        #move
        convert_steeringangle_to_quadrantangle(steeringangle)
        movement(quadrant, quadrantangle)

        ev = pygame.event.get()

        for event in ev:
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        # if left arrow key is pressed
        if keys[pygame.K_LEFT]:
            # decrease steeringangle
            steer_left()

        # if left arrow key is pressed
        if keys[pygame.K_RIGHT]:
            # increase steeringangle
            steer_right()

        # if left arrow key is pressed
        if keys[pygame.K_UP]:
            # increase velocity
            accelerate()
        else:
            deccelerate()

        # if left arrow key is pressed
        if keys[pygame.K_DOWN]:
            #decrease velocity
            brake()


        screen.fill(background_colour)

        draw_car()

        screen.blit(velText, (30, 15))
        screen.blit(steerText, (30, 30))
        screen.blit(quadangleText, (30, 45))
        screen.blit(quadText, (30, 60))
        screen.blit(xcoord, (30, 75))
        screen.blit(ycoord, (30,90))

        pygame.display.update()

if __name__ == '__main__':
    main()