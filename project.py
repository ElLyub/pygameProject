import os, sys, pygame, random


pygame.init()
pygame.font.init()

FPS = 50
WIDTH = 650
HEIGHT = 450
STEP = 50
SCORE = 0
gravity = 0.25
speed = 200
fps = 60
sound1 = pygame.mixer.Sound('data/water2.wav')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
screen_rect = (0, 0, WIDTH - 150, HEIGHT)


def score_to_screen(score):
    global SCORE
    SCORE = score
    myfont = pygame.font.Font('data/14210.ttf', 16)
    textsurface = myfont.render('Score:' + str(score)+'/' + str(4), False, (0, 0, 0))
    screen.fill((48, 214, 177))
    screen.blit(textsurface,(555,20))

def borders(x, y):
    if x < 0 or x > 550 or y < 0 or y > 450:
        return False
    else:
        return True

def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
 
    # и подсчитываем максимальную длину    
    max_width = max(map(len, level_map))
 
    # дополняем каждую строку пустыми клетками ('.')    
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Box('wall', x, y)
            elif level[y][x] == 'w':
                Water('water', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(load_image('sheep.png', -1), 4, 1, x, y)
            elif level[y][x] == '+':
                Tile('empty', x, y)
                carrot = Carrot('carrot', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y, carrot

def terminate():
    pygame.quit()
    sys.exit()
    
# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
box_group = pygame.sprite.Group()
carrot_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
bubbles_group = pygame.sprite.Group()
button_group = pygame.sprite.Group()
over_group = pygame.sprite.Group()

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'carrot': load_image('carrot.png'),
    'water': load_image('water.png')
}
 
tile_width = tile_height = 50
 
class OverG(pygame.sprite.Sprite):
    image = load_image("gameover.png")
 
    def __init__(self):
        super().__init__(over_group, all_sprites)
        self.image = OverG.image
        self.rect = self.image.get_rect()
        self.rect.x -= self.rect.width
        
 
    def update(self):
        self.rect.x = WIDTH // 2 - 100
        self.rect.y = HEIGHT // 2 - 100
            
            
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Box(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(box_group, tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Carrot(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(carrot_group, tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 4, tile_height * pos_y + 5)

   
class Water(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(water_group, tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)     


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("babbl.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))
 
    def __init__(self, pos, dx, dy):
        super().__init__(bubbles_group, all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
 
        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos
 
        # гравитация будет одинаковой
        self.gravity = gravity
 
    def update(self):
        # применяем гравитационный эффект: 
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()

 
def create_particles(position):
    # количество создаваемых частиц
    particle_count = 215
    # возможные скорости
    numbers = range(-3, 11)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))         

 
class Player(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(pos_x, pos_y)
        self.flip = pygame.transform.flip(self.image, 1, 0)
        self.score = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
 
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


    def move(self, event):
        event = event
        if event == pygame.K_LEFT and borders(self.rect.x - STEP, self.rect.y):
            self.image = self.flip
            self.rect.x -= STEP
            if pygame.sprite.spritecollideany(self, box_group):
               self.rect.x += STEP
            elif pygame.sprite.spritecollideany(self, water_group):
               create_particles((self.rect.x, self.rect.y))
               sound1.play()
               over_group.update()
        if event == pygame.K_RIGHT and borders(self.rect.x + STEP, self.rect.y):
            self.rect.x += STEP
            self.update()
            if pygame.sprite.spritecollideany(self, box_group):
                self.rect.x -= STEP
            elif pygame.sprite.spritecollideany(self, water_group):
               create_particles((self.rect.x, self.rect.y))
               sound1.play()
               over_group.update()
        if event == pygame.K_DOWN and borders(self.rect.x, self.rect.y + STEP):
            self.rect.y += STEP
            if pygame.sprite.spritecollideany(self, box_group):
                self.rect.y -= STEP
            elif pygame.sprite.spritecollideany(self, water_group):
               create_particles((self.rect.x, self.rect.y))
               sound1.play()
               over_group.update()
        if event == pygame.K_UP and borders(self.rect.x, self.rect.y - STEP):
            self.rect.y -= STEP
            if pygame.sprite.spritecollideany(self, box_group):
                self.rect.y += STEP
            elif pygame.sprite.spritecollideany(self, water_group):
               create_particles((self.rect.x, self.rect.y))
               sound1.play()
               over_group.update()
        if event == pygame.K_SPACE:
            if pygame.sprite.spritecollideany(self, carrot_group):
                pygame.sprite.spritecollideany(self, carrot_group).kill()
                self.score += 1
                score_to_screen(self.score)

               
class Restart(pygame.sprite.Sprite):
    image = load_image("replay.png")
 
    def __init__(self):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно!!!
        super().__init__(button_group, all_sprites)
        self.image = Restart.image
        self.rect = self.image.get_rect()
        self.rect.x = 560
        self.rect.y = 50         
 
    def update(self, pl):
        if self.rect.collidepoint(event.pos):
            player, level_x, level_y, carrot = generate_level(load_level('level_1.txt'))
            player.kill()
            score_to_screen(0)
            end.kill()
            pl.rect.x = 0
            pl.rect.y = 0
             

player = None

def start_screen():
    intro_text = ["CARROT SHEEP", "",
                  "Правила игры:",
                  "Соберите всю морковь (для этого нажмите на пробел),",
                  "Обходите коробки и остерегайтесь воды.",
                  "Для начала игры нажмите здесь, удачи!"]
 
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('data/14646.otf', 12)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
                
        pygame.display.flip()
        clock.tick(FPS)

start_screen()
screen.fill(pygame.Color('white'))

 
player, level_x, level_y, carrot = generate_level(load_level('level_1.txt'))
button = Restart()
end = OverG()

score_to_screen(0)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #движение player'а
        if event.type == pygame.KEYDOWN: 
            player.move(event.key)
        if event.type == pygame.MOUSEBUTTONDOWN:
            button_group.update(player)

            
    if SCORE == 4:
        player.kill()
        player, level_x, level_y, carrot = generate_level(load_level('level_1.2.txt'))
        SCORE = 0
        score_to_screen(0)

    tiles_group.draw(screen)
    carrot_group.draw(screen)
    player_group.draw(screen)
    button_group.draw(screen)
    bubbles_group.draw(screen)
    over_group.draw(screen)
    bubbles_group.update()
    pygame.display.flip()
    clock.tick(35)
pygame.quit()
 
 

