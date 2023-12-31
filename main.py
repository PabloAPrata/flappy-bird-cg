import pygame
from sys import exit
import random

pygame.init()
clock = pygame.time.Clock()

x_speed = 1
y_speed = 1

# Definições da Janela
win_height = 720
win_width = 551
window = pygame.display.set_mode((win_width, win_height))

# Carregando imagens
bird_images = [pygame.image.load("assets/bird_down.png"),
               pygame.image.load("assets/bird_mid.png"),
               pygame.image.load("assets/bird_up.png")]
skyline_image = pygame.image.load("assets/background.png")
ground_image = pygame.image.load("assets/ground.png")
top_pipe_image = pygame.image.load("assets/pipe_top.png")
bottom_pipe_image = pygame.image.load("assets/pipe_bottom.png")
game_over_image = pygame.image.load("assets/game_over.png")
start_image = pygame.image.load("assets/start.png")

# Definições gerais do Game
scroll_speed = 3
bird_start_position = (100, 250)
score = 0
font = pygame.font.SysFont('Arial', 20)
game_stopped = True
player_record = 0

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = bird_images[0]
        self.rect = self.image.get_rect()
        self.rect.center = bird_start_position
        self.image_index = 0
        self.vel = 0
        self.alive = True
        self.delta_x = 0
        self.delta_y = 0

    def update(self, user_input):
        # Animação do pássaro
        if self.alive:
            self.image_index += 3
        if self.image_index >= 30:
            self.image_index = 0
        self.image = bird_images[self.image_index // 10]

        self.vel = -7

        # Movimento horizontal
        if user_input[pygame.K_LEFT]:
            self.delta_x = self.delta_x - 0.8
        elif user_input[pygame.K_RIGHT]:
            self.delta_x = self.delta_x + 0.8
        else:
            self.delta_x = 0

        # Movimento vertical
        if user_input[pygame.K_UP]:
            self.delta_y = self.delta_y - 0.8
            self.image = pygame.transform.rotate(self.image, self.vel * -7)
        elif user_input[pygame.K_DOWN]:
            self.delta_y = self.delta_y + 0.8
            self.image = pygame.transform.rotate(self.image, self.vel * +7)
        else:
            self.delta_y = 0

        # Atualize a posição do pássaro
        self.rect.x += self.delta_x
        self.rect.y += self.delta_y

        # Garanta que o pássaro não saia da tela
        self.rect.x = max(0, min(self.rect.x, win_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, win_height - self.rect.height))



class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, image, pipe_type):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enter, self.exit, self.passed = False, False, False
        self.pipe_type = pipe_type

    def update(self):
        # Move Pipe
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()

        # Score
        global score
        global player_record

        if self.pipe_type == 'bottom':
            if bird_start_position[0] > self.rect.topleft[0] and not self.passed:
                self.enter = True
            if bird_start_position[0] > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.enter and self.exit and not self.passed:
                self.passed = True
                score += 1
                if score > player_record:
                    player_record = score



class Ground(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = ground_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        # Move Ground
        self.rect.x -= scroll_speed
        if self.rect.x <= -win_width:
            self.kill()


def quit_game():
    # Exit Game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def main():
    global score

    # Instancia o Pássaro
    bird = pygame.sprite.GroupSingle()
    bird.add(Bird())

    # Setup Canos
    pipe_timer = 0
    pipes = pygame.sprite.Group()

    # Chão Inicial
    x_pos_ground, y_pos_ground = 0, 520
    ground = pygame.sprite.Group()
    ground.add(Ground(x_pos_ground, y_pos_ground))

    run = True
    while run:
        # Quit
        quit_game()

        # Reset Frame
        window.fill((0, 0, 0))

        # User Input
        user_input = pygame.key.get_pressed()

        # Desenha Background
        window.blit(skyline_image, (0, 0))

        # Spawn Ground
        if len(ground) <= 2:
            ground.add(Ground(win_width, y_pos_ground))

        # Desenha - Canos, Chão e Pássaro
        pipes.draw(window)
        ground.draw(window)
        bird.draw(window)

        # Mostra Score
        score_text = font.render('Score: ' + str(score), True, pygame.Color(255, 255, 255))
        window.blit(score_text, (20, 45))

        # Mostra Record
        player_record_text = font.render('Record: ' + str(player_record), True, pygame.Color(255, 255, 255))
        window.blit(player_record_text, (20, 20))

        # Update - Pipes, Ground and Bird
        if bird.sprite.alive:
            pipes.update()
            ground.update()
            bird.update(user_input)

        # Detecção de colisão
        collision_pipes = pygame.sprite.spritecollide(bird.sprites()[0], pipes, False)
        collision_ground = pygame.sprite.spritecollide(bird.sprites()[0], ground, False)
        if collision_pipes or collision_ground:
            bird.sprite.alive = False
            if collision_ground:
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                              win_height // 2 - game_over_image.get_height() // 2))
            if collision_pipes:
                window.blit(game_over_image, (win_width // 2 - game_over_image.get_width() // 2,
                                              win_height // 2 - game_over_image.get_height() // 2))
            if user_input[pygame.K_r]:
                    score = 0
                    break

        # Spawn Pipes
        if pipe_timer <= 0 and bird.sprite.alive:
            x_top, x_bottom = 550, 550
            y_top = random.randint(-800, -350)
            y_bottom = y_top + random.randint(80, 150) + bottom_pipe_image.get_height()
            pipes.add(Pipe(x_top, y_top, top_pipe_image, 'top'))
            pipes.add(Pipe(x_bottom, y_bottom, bottom_pipe_image, 'bottom'))
            pipe_timer = random.randint(60, 100) #Range do tempo de criação dos canos
        pipe_timer -= 1

        clock.tick(60)
        pygame.display.update()


# Menu
def menu():
    global game_stopped

    while game_stopped:
        quit_game()

        # Draw Menu
        window.fill((0, 0, 0))
        window.blit(skyline_image, (0, 0))
        window.blit(ground_image, Ground(0, 520))
        window.blit(bird_images[0], (100, 250))
        window.blit(start_image, (win_width // 2 - start_image.get_width() // 2,
                                  win_height // 2 - start_image.get_height() // 2))

        # User Input
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            main()

        pygame.display.update()


menu()