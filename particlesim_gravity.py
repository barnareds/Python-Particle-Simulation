import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Simulation')

BOUNCE_STOP = 1.5

FPS = 60
G = .1
XBORDER = (40, WIDTH - 40)
YBORDER = (40, HEIGHT - 40)


class Particle:

  def __init__(self, x, y, vx, vy, ax, ay, r, id):
    self.x = x
    self.y = y
    self.vx = vx
    self.vy = vy
    self.ax = ax
    self.ay = ay
    self.m = r * 10
    self.radius = r
    self.id = id
    self.color = 'blue'
    self.circle = ''
    self.selected = False
    self.friction = 0.01

  def update(self):

    self.ax = -self.vx * self.friction
    self.ay = -self.vy * self.friction

    self.vx += self.ax
    self.vy += self.ay

    self.x += self.vx
    self.y += self.vy

  def render(self, mouse_pos):
    self.circle = pygame.draw.circle(screen,
                                     self.color, (self.x, self.y),
                                     self.radius,
                                     width=5)

    if self.selected:
      pygame.draw.line(screen, 'red', (self.x, self.y), mouse_pos, width=5)

  def launchParticle(self, mouse_pos):

    self.vx = (self.x - mouse_pos[0]) / 10
    self.vy = (self.y - mouse_pos[1]) / 10

  def update_color(self):
    
    vel = math.sqrt(self.vx**2 + self.vy**2)
    self.color = get_color(vel)


def clamp(n, min, max):
  if min < n < max:
    return n
  elif n >= max:
    return max
  else:
    return min

def mixrgb(fac, rgb1, rgb2):
  return tuple([c2 * fac + c1 * (1 - fac) for c1, c2 in zip(rgb1, rgb2)])

def get_color(speed):
  return mixrgb(clamp(speed / 10, 0, 1), (0, 0, 255), (255, 0, 0))


class Box:

  def __init__(self, bx, by, line_width):

    self.xborder = bx
    self.yborder = by
    self.line_width = line_width
    self.elasticitat = 1
    self.half_width = (self.line_width + 1) / 2

  def boxCollision(self, p):

    if p.x <= self.xborder[0] + p.radius + self.half_width:
      p.x = self.xborder[0] + p.radius + self.half_width
      p.vx = p.vx * -self.elasticitat

    elif p.x >= self.xborder[1] - p.radius - self.half_width:
      p.x = self.xborder[1] - p.radius - self.half_width
      p.vx = p.vx * - self.elasticitat

    if p.y <= self.yborder[0] + p.radius + self.half_width:
      p.y = self.yborder[0] + p.radius + self.half_width + 1
      p.vy = p.vy * -self.elasticitat

    elif p.y >= self.yborder[1] - p.radius - self.half_width:
      p.y = self.yborder[1] - p.radius - self.half_width
      
      if math.sqrt(p.vy**2 + p.vx**2) <= BOUNCE_STOP:
        p.vy = 0
        p.vx = 0

      else:
        p.vy = p.vy * -self.elasticitat

    else:
        p.vy += G

  def render(self):
    pygame.draw.line(screen,
                     'white', (XBORDER[0], YBORDER[0]),
                     (XBORDER[1], YBORDER[0]),
                     width=self.line_width)
    pygame.draw.line(screen,
                     'white', (XBORDER[0],YBORDER[1]),
                     (XBORDER[1], YBORDER[1]),
                     width=self.line_width)

    pygame.draw.line(screen,
                     'white', (XBORDER[0], YBORDER[0]),
                     (XBORDER[0], YBORDER[1]),
                     width=self.line_width)
    pygame.draw.line(screen,
                     'white', (XBORDER[1], YBORDER[0]),
                     (XBORDER[1], YBORDER[1]),
                     width=self.line_width)


def particleCollision(p1, p2):

  dx, dy = p1.x - p2.x, p1.y - p2.y
  d = math.sqrt(dx**2 + dy**2)

  # Has collided
  if (d <= (p1.radius + p2.radius)):

    overlap = (d - p1.radius - p2.radius) * 0.5

    p1.x -= overlap * (p1.x - p2.x) / d
    p1.y -= overlap * (p1.y - p2.y) / d

    p2.x += overlap * (p1.x - p2.x) / d
    p2.y += overlap * (p1.y - p2.y) / d

    d = math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

    nx = (p2.x - p1.x) / d
    ny = (p2.y - p1.y) / d

    tx = -ny
    ty = nx

    dpTan1 = p1.vx * tx + p1.vy * ty
    dpTan2 = p2.vx * tx + p2.vy * ty

    dpNorm1 = p1.vx * nx + p1.vy * ny
    dpNorm2 = p2.vx * nx + p2.vy * ny

    m1 = (dpNorm1 * (p1.m - p2.m) + 2 * p2.m * dpNorm2) / (p1.m + p2.m)
    m2 = (dpNorm2 * (p2.m - p1.m) + 2 * p1.m * dpNorm1) / (p1.m + p2.m)

    p1.vx = tx * dpTan1 + nx * m1
    p1.vy = ty * dpTan1 + ny * m1
    p2.vx = tx * dpTan2 + nx * m2
    p2.vy = ty * dpTan2 + ny * m2
    
def createParticle(mouse_pos, particles, id_count):

  id_count += 1
  p = Particle(mouse_pos[0], mouse_pos[1], 0, 0, 0, 0, 40, id_count)
  particles.append(p)
  
  return particles, id_count

def createParticlesInit(particles, id_count):
  
  for i in range(3):
    id_count += 1

    xv = random.randint(-5,5)
    yv = random.randint(-5,5)
    p = Particle(random.randint(XBORDER[0],XBORDER[1]), random.randint(YBORDER[0],YBORDER[1]), xv, yv, 0, 0, 20, id_count)
    particles.append(p)
  
  return particles, id_count

def main():

  running = True
  clock = pygame.time.Clock()

  particles = []
  box = Box(XBORDER, YBORDER, 5)
  id_count = 0
  
  particles, id_count = createParticlesInit(particles, id_count)

  while running:

    screen.fill('black')
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:
      #if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
        particles, id_count = createParticle(mouse_pos, particles, id_count)
        
      if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for p in particles:
          if p.circle.collidepoint(mouse_pos):
            p.selected = True

      if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
        for p in particles:
          if p.selected:
            p.launchParticle(mouse_pos)
            p.selected = False


    for p in particles:
      for p2 in particles:
        if p.id != p2.id:
          particleCollision(p, p2)

      p.update()
      box.boxCollision(p)

      p.update_color()
      p.render(mouse_pos)

    box.render()
    # Update the game state

    # Draw the game screen
    pygame.display.update()
    pygame.display.flip()

    clock.tick(FPS)
  
  pygame.quit()


if __name__ == "__main__":
    main()
