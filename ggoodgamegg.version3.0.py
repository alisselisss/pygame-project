import pygame
import sys
import os
import random
from progress import *

WIDTH = 1000
HEIGHT = 800

FPS = 60

# player_coins = 0  # Сколько монет у игрока, по сути вносится во время UPDATE у игрока или из БД
choosen_price = 0  # Цена предположительно-выбираемого персонажа, нужна для сравнения кол-ва денег и покупки
choosen_character = 1  # условно выбранный персонаж!
choosen_character_to_play = 1  # номер выбранного персонажа, 1 - дефолтный
choosen_level = 1


def load_image(name, colorkey=None):
    # загружаем изображения
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    # загружаем уровень
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    for i in range(len(level_map)):
        level_map[i] = list(level_map[i].ljust(max_width, '.'))
    return level_map


def generate_level(level):
    # генерируем уровень, расставляем платформы, монетки, врагов
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            if level[y][x] == '/':
                Tile('surface', x, y)
            if level[y][x] == '#':
                Tile('beautiful_surface', x, y)
            if level[y][x] == '1':
                Enemy_1(x, y)
            if level[y][x] == '2':
                Enemy_2(x, y)
            if level[y][x] == '?':
                Tile('enemy', x, y)
            if level[y][x] == ',':
                Tile('coin', x, y)
            if level[y][x] == "s":
                Tile("start_table", x, y)
            if level[y][x] == "e":
                Tile("end_table", x, y)
            if level[y][x] == "h":
                Decorative(x, y, tile_images['dec_heart'])
            if level[y][x] == "d":
                Decorative(x, y, tile_images['dec_dragonfly'])
            if level[y][x] == '@':
                new_player = Player(x, y)
    return new_player


def draw_hearts(lives):
    global hearts_group
    hearts_group = pygame.sprite.Group()
    for i in range(lives):
        heart = pygame.sprite.Sprite()
        heart.image = heart_image
        heart.rect = heart.image.get_rect()
        heart.rect.top = 25
        heart.rect.left = i * 50 + 50
        heart.add(hearts_group)


def terminate():
    pygame.quit()
    # write_progress()
    sys.exit()


def render(intro_text, text_coord):
    for i in range(len(intro_text)):
        font = pygame.font.Font("data/pixel3.ttf", 180 - i * 100)
        string_rendered = font.render(intro_text[i], 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 330 if i == 0 else 240
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def start_screen():
    global start
    start = True
    intro_text = ["THE",
                  "SUITEHEARTS"]

    background_image = load_image("back.png")
    screen.blit(background_image, [0, 0])
    zast = pygame.transform.scale(load_image("dark_zast.png"), (1100, 900))
    screen.blit(zast, (-30, 10))
    decorative_group = pygame.sprite.Group()
    for _ in range(9):
        Decorative(random.randint(0, 1000), random.randint(0, 800), tile_images['dec_fly']).add(decorative_group)

    render(intro_text, 280)

    button_group_start = pygame.sprite.Group()
    play_btn = Button('Go!!!', 430, 550, button_group_start)
    shop_btn = Button('Shop', 230, 550, button_group_start)
    quit_btn = Button('Quit', 630, 550, button_group_start)

    pygame.time.set_timer(pygame.USEREVENT, 50)
    while True:
        screen.blit(background_image, [0, 0])
        decorative_group.draw(screen)
        decorative_group.update()
        screen.blit(zast, (-30, 10))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    for sprite in decorative_group:
                        sprite.kill()
                    level_menu()
                    if choosen_level:
                        return
                if quit_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    terminate()
                if shop_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    shop()  # GO TO THE SHOP!!!
            if event.type == pygame.USEREVENT:
                for btn in button_group_start:
                    if btn.rect.collidepoint(pygame.mouse.get_pos()) and btn.timer < btn.rect.x // 10:
                        btn.timer += 1
                    elif btn.timer > 0:
                        btn.timer -= 1
        for btn in button_group_start:
            btn.highlight()
        my_money()
        render(intro_text, 280)
        button_group_start.update()
        pygame.display.flip()
        clock.tick(FPS)


def my_money():
    ramka = pygame.transform.scale(load_image("card.png"), (800, 40))
    screen.blit(ramka, (-300, 10))
    screen.blit(pygame.transform.scale(tile_images['coin'], (40, 40)), (0, 10))
    text_font = pygame.font.Font('data/pixel3.ttf', 35)
    desc = text_font.render('= ' + str(progress_dict['player_coins']), 1, (255, 255, 255))
    desc_rect = desc.get_rect(left=50, top=20)
    screen.blit(desc, desc_rect)


def level_menu():
    global start, choosen_level
    start = False

    background_image = load_image("back.png")
    map_image = load_image('level_map2.png')

    button_group = pygame.sprite.Group()
    run_btn = Button('Run', 210, 710, button_group, little=1)
    menu_btn = Button('Menu', 410, 710, button_group, little=1)
    quit_btn = Button('Quit', 610, 710, button_group, little=1)

    level_1_rect = pygame.Rect(70, 485, 70, 100)
    level_2_rect = pygame.Rect(130, 600, 70, 100)
    level_3_rect = pygame.Rect(200, 490, 70, 100)
    level_4_rect = pygame.Rect(285, 590, 70, 100)
    level_5_rect = pygame.Rect(355, 480, 70, 100)
    level_6_rect = pygame.Rect(440, 570, 70, 100)
    level_7_rect = pygame.Rect(500, 485, 70, 100)
    level_8_rect = pygame.Rect(570, 595, 70, 100)
    level_9_rect = pygame.Rect(640, 505, 70, 100)
    level_10_rect = pygame.Rect(750, 430, 100, 150)

    hero = load_image(f'dark_hero{choosen_character_to_play}.png')
    frames = []
    for i in range(3):
        frames.append(hero.subsurface(pygame.Rect(
            (hero.get_width() // 3 * i, 0),
            (hero.get_width() // 3, hero.get_height())
        )))
    cur_frame = 1
    pos = [0, 0]
    pos[0] = eval(f'level_{choosen_level if choosen_level else 1}_rect').centerx - 30
    pos[1] = eval(f'level_{choosen_level if choosen_level else 1}_rect').centery - 40
    if choosen_level == 10:
        pos[1] = level_10_rect.centery
    dx = dy = 0


    while True:
        screen.blit(background_image, [0, 0])
        screen.blit(map_image, [40, 10])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if quit_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    terminate()
                if menu_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    choosen_level = 0
                    return
                if run_btn.rect.collidepoint(pygame.mouse.get_pos()) and choosen_level:
                    restart()
                    return
            if event.type == pygame.USEREVENT:
                for btn in button_group:
                    if btn.rect.collidepoint(pygame.mouse.get_pos()) and btn.timer < btn.rect.x // 10:
                        btn.timer += 1
                    elif btn.timer > 0:
                        btn.timer -= 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(1, 11):
                    if eval(f"level_{i}_rect.collidepoint(pygame.mouse.get_pos())") and eval(f'progress_dict["level_{i}"]'):
                        choosen_level = i
                        pos = [round(pos[0] + dx), round(pos[1] + dy)]
                        dx = pos[0] - event.pos[0]
                        dy = pos[1] - event.pos[1]
                        pos[0] = eval(f'level_{i}_rect').centerx - 30
                        pos[1] = eval(f'level_{i}_rect').centery - 40
                        if choosen_level == 10:
                            pos[1] = level_10_rect.centery
        image = frames[round(cur_frame) % len(frames)]
        image = pygame.transform.scale(image, (80, 105))
        if dx > 0:
            dx -= 2
            image = pygame.transform.flip(image, True, False)
        if dx < 0:
            dx += 2
        if dy > 0:
            dy -= 2
        if dy < 0:
            dy += 2
        if abs(dx) >= 2 or abs(dy) >= 2:
            cur_frame += 0.1
        else:
            cur_frame = 1
        for i in range(1, 10):
            if not eval(f'progress_dict["level_{i}"]'):
                screen.blit(load_image('close.png'), eval(f'level_{i}_rect'))
        screen.blit(image, (round(pos[0] + dx), round(pos[1] + dy)))
        for btn in button_group:
            btn.highlight()
        button_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def shop():
    global start
    start = False
    pixel_font = pygame.font.Font('data/pixel3.ttf', 100)
    name_font = pygame.font.Font('data/pixel3.ttf', 30)
    text_font = pygame.font.Font('data/pixel3.ttf', 19)

    background_image = load_image("back.png")
    screen.blit(background_image, [0, 0])

    ramka = pygame.transform.scale(load_image("ramka.png"), (900, 790))
    screen.blit(ramka, (40, 10))

    character_card = pygame.transform.scale(load_image("card.png"), (850, 550))
    screen.blit(character_card, (340, 130))

    title = pixel_font.render('SHOP', 1, (255, 255, 255))
    title_rect = title.get_rect(left=340, top=50)
    screen.blit(title, title_rect)

    charater_card = pygame.transform.scale(load_image("card2.png"), (230, 230))
    screen.blit(charater_card, (60, 119))
    charater_card = pygame.transform.scale(load_image("card2.png"), (230, 230))
    screen.blit(charater_card, (320, 119))
    charater_card = pygame.transform.scale(load_image("card2.png"), (230, 230))
    screen.blit(charater_card, (60, 389))
    charater_card = pygame.transform.scale(load_image("card2.png"), (230, 230))
    screen.blit(charater_card, (320, 389))

    hero_frames = None
    name = None
    result, result_rect = None, None
    cur_frame = 1
    image = None

    button_group = pygame.sprite.Group()
    buy_btn = Button('Buy', 210, 710, button_group, little=1, light=False)
    menu_btn = Button('Menu', 410, 710, button_group, little=1, light=False)
    quit_btn = Button('Quit', 610, 710, button_group, little=1, light=False)

    ben = pygame.transform.scale(load_image("benz.png"), (170, 170))
    screen.blit(ben, (90, 153))
    bnzd_btn = Button('Benzedrine', 100, 350, button_group, little=2, light=False)

    hsc = pygame.transform.scale(load_image("crab.png"), (170, 170))
    screen.blit(hsc, (350, 153))
    hsc_btn = Button('H.Crab', 390, 350, button_group, little=2, light=False)

    dtc = pygame.transform.scale(load_image("donnie.png"), (170, 170))
    screen.blit(dtc, (90, 423))
    dtc_btn = Button('Donnie', 120, 620, button_group, little=2, light=False)

    sd = pygame.transform.scale(load_image("sand.png"), (170, 170))
    screen.blit(sd, (340, 423))
    mrsd_btn = Button('Sandman', 370, 620, button_group, little=2, light=False)

    my_money()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buy_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    result, result_rect = buy_character()  # ВЫБОР ПЕРСОНАЖА!
                    my_money()
                if quit_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    terminate()
                if menu_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    start = True
                    return
                if bnzd_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    hero_frames, description = show_character("Dr Benzedrine", 0, 1)
                    result, result_rect = None, None
                    name = "Dr Benzedrine"
                if hsc_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    hero_frames, description = show_character("HorseShoe Crab", 160, 2)
                    result, result_rect = None, None
                    name = "HorseShoe Crab"
                if dtc_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    hero_frames, description = show_character("Donnie The Catcher", 350, 3)
                    result, result_rect = None, None
                    name = "Donnie The Catcher"
                if mrsd_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    hero_frames, description = show_character("Mr Sandman", 666, 4)
                    result, result_rect = None, None
                    name = "Mr Sandman"

            if event.type == pygame.USEREVENT:
                for btn in button_group:
                    if btn.rect.collidepoint(pygame.mouse.get_pos()) and btn.timer < btn.rect.x // 10:
                        btn.timer += 1
                    elif btn.timer > 0:
                        btn.timer -= 1
        for btn in button_group:
            btn.highlight()
        if not hero_frames is None:
            screen.blit(character_card, (340, 130))
            if not image is None and image.get_rect().move((650, 180)).collidepoint(pygame.mouse.get_pos()):
                cur_frame += 0.1
            else:
                cur_frame = 1
            image = hero_frames[round(cur_frame) % len(hero_frames)]
            image = pygame.transform.scale(image, (160, 210))
            screen.blit(image, (650, 180))

            y_move = 450
            for i in description:
                desc = text_font.render(i, 1, (255, 255, 255))
                desc_rect = desc.get_rect(left=590, top=y_move)
                screen.blit(desc, desc_rect)
                y_move += 30

            title = name_font.render(name, 1, (255, 255, 255))
            title_rect = title.get_rect(left=590, top=400)
            screen.blit(title, title_rect)
        if not result is None:
            screen.blit(result, result_rect)

        if progress_dict[f'hero_{choosen_character}'] and not hero_frames is None:
            bought = text_font.render('you have', 1, (255, 255, 255))
            bought_rect = bought.get_rect(left=790, top=200)
            screen.blit(bought, bought_rect)
            bought = text_font.render('already', 1, (255, 255, 255))
            bought_rect = bought.get_rect(left=790, top=230)
            screen.blit(bought, bought_rect)
            bought = text_font.render('bougth', 1, (255, 255, 255))
            bought_rect = bought.get_rect(left=790, top=260)
            screen.blit(bought, bought_rect)
            bought = text_font.render('this', 1, (255, 255, 255))
            bought_rect = bought.get_rect(left=790, top=290)
            screen.blit(bought, bought_rect)
            bought = text_font.render('character!', 1, (255, 255, 255))
            bought_rect = bought.get_rect(left=790, top=320)
            screen.blit(bought, bought_rect)
        button_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def show_character(name, price, num):
    global choosen_character, choosen_price
    choosen_character = num
    choosen_price = price

    characters = {'Dr Benzedrine': 'hero1.png',
                  'HorseShoe Crab': 'hero2.png',
                  'Donnie The Catcher': 'hero3.png',
                  'Mr Sandman': 'hero4.png'
                  }
    zast = pygame.transform.scale(load_image(characters[name]), (210, 210))
    frames = []
    for i in range(3):
        frames.append(zast.subsurface(pygame.Rect(
            (zast.get_width() // 3 * i, 0),
            (zast.get_width() // 3, zast.get_height()))))

    if num == 1:
        description = ["Dr. Benzedrine - your default",
                       "character, who has a power of",
                       "exploding bullets (he made it",
                       "himself in laboratory!)",
                       "___________________________",
                       f"Price: {str(price)}$"
                       ]
    elif num == 2:
        description = ["HorseShoe Crab - the luckiest",
                       "man ever! You can use it",
                       "in fighting and collect",
                       "more coins from enemies!",
                       "___________________________",
                       f"Price: {str(price)}$"
                       ]
    elif num == 3:
        description = ["Donnie The Catcher - can help",
                       "you to catch an attention!",
                       "Or not... Be invisible for",
                       "enemies one time!",
                       "___________________________",
                       f"Price: {str(price)}$"
                       ]
    else:
        description = ["Mr Sandman - The Suiteheart",
                       "of dreams. Can recreate the",
                       "most powerful things ever! Use",
                       "SuperBeam to defeat everybody!",
                       "___________________________",
                       f"Price: {str(price)}$"
                       ]
    return frames, description


def buy_character():
    global choosen_character, choosen_character_to_play, choosen_price
    text_font = pygame.font.Font('data/pixel3.ttf', 19)
    if progress_dict['player_coins'] >= choosen_price and not\
            progress_dict[f'hero_{choosen_character}']:
        choosen_character_to_play = choosen_character
        desc = text_font.render("Successful!", 1, (255, 255, 255))
        progress_dict['player_coins'] -= choosen_price
        progress_dict[f'hero_{choosen_character_to_play}'] = 1
    elif progress_dict[f'hero_{choosen_character}']:
        desc = text_font.render("Character applied!", 1, (255, 255, 255))
        choosen_character_to_play = choosen_character
    else:
        desc = text_font.render("You need more coins!", 1, (255, 255, 255))
    desc_rect = desc.get_rect(left=700, top=620)
    screen.blit(desc, desc_rect)
    return desc, desc_rect


def end_screen():
    global start, choosen_level, progress_dict
    pixel_font = pygame.font.Font('data/pixel3.ttf', 65)
    pixel_font2 = pygame.font.Font('data/pixel3.ttf', 30)
    zast = pygame.transform.scale(load_image("zast.png"), (1000, 800))
    screen.blit(zast, (30, 0))

    if player.win:
        title = pixel_font.render('Great job!', 1, (255, 255, 255))
        motivation = pixel_font2.render('Now you can feel your heartbeat', 1, (255, 255, 255))
        motivation2 = pixel_font2.render('beating in unison with', 1, (255, 255, 255))
        motivation3 = pixel_font2.render('your power. It becomes stronger...', 1, (255, 255, 255))
        if choosen_character_to_play == 1:
            ramka = pygame.transform.scale(load_image("ramka.png"), (160, 110))
            screen.blit(ramka, (290, 350))
        else:
            ramka = pygame.transform.scale(load_image("ramka.png"), (260, 110))
            screen.blit(ramka, (290, 350))
        result_coin = pygame.transform.scale(tile_images['coin'], (40, 40))
        screen.blit(result_coin, (300, 360))
        result_coins = pixel_font2.render('= ' + str(player.coins), 1, (255, 255, 255))
        coins_rect3 = result_coins.get_rect(left=360, top=370)
        screen.blit(result_coins, coins_rect3)
        for i in range(player.lives):
            screen.blit(heart_image, (310 + i * 40, 410))
    else:
        title = pixel_font.render('you lose =(', 1, (255, 255, 255))
        motivation = pixel_font2.render('But determination is still burning', 1, (255, 255, 255))
        motivation2 = pixel_font2.render('in the depth of your heart', 1, (255, 255, 255))
        motivation3 = pixel_font2.render('Lets try again!', 1, (255, 255, 255))
        skull = pygame.transform.scale(load_image("skull.png"), (130, 130))
        screen.blit(skull, (350, 330))
        screen.blit(skull, (450, 330))
        screen.blit(skull, (550, 330))

    title_rect = title.get_rect(left=340, top=155)
    screen.blit(title, title_rect)

    motivation_rect = motivation.get_rect(left=230, top=250)
    motivation_rect2 = motivation2.get_rect(left=230, top=280)
    motivation_rect3 = motivation3.get_rect(left=230, top=310)
    screen.blit(motivation, motivation_rect)
    screen.blit(motivation2, motivation_rect2)
    screen.blit(motivation3, motivation_rect3)

    button_group = pygame.sprite.Group()
    if player.win and choosen_level != 10:
        restart_btn = Button('Next', 250, 500, button_group)
        menu_btn = Button('Menu', 440, 500, button_group)
        quit_btn = Button('Quit', 650, 500, button_group)
        choosen_level += 1
        progress_dict[f'level_{choosen_level}'] = 1
        progress_dict['player_coins'] += player.coins
    elif player.win and choosen_level == 10:
        restart_btn = None
        choosen_level += 1
        progress_dict[f'level_{choosen_level}'] = 1
        progress_dict['player_coins'] += player.coins
        menu_btn = Button('Menu', 330, 500, button_group)
        quit_btn = Button('Quit', 600, 500, button_group)
    else:
        restart_btn = Button('Restart', 220, 500, button_group)
        menu_btn = Button('Menu', 490, 500, button_group)
        quit_btn = Button('Quit', 670, 500, button_group)
    pygame.time.set_timer(pygame.USEREVENT, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not restart_btn is None and restart_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    restart()
                    return
                if quit_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    terminate()
                if menu_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    restart()
                    start = True
                    start_screen()
                    return
            if event.type == pygame.USEREVENT:
                for btn in button_group:
                    if btn.rect.collidepoint(pygame.mouse.get_pos()) and btn.timer < btn.rect.x // 10:
                        btn.timer += 1
                    elif btn.timer > 0:
                        btn.timer -= 1
        for btn in button_group:
            btn.highlight()
        button_group.update()
        pygame.display.flip()
        clock.tick(FPS)


def restart():
    global player, camera, background, background_rect, start, level_map
    start = False
    for sprite in all_sprites:
        all_sprites.remove(sprite)
    for sprite in enemy_group:
        enemy_group.remove(sprite)
    for sprite in player_group:
        player_group.remove(sprite)
    for sprite in surface_group:
        surface_group.remove(sprite)
    for sprite in coin_group:
        coin_group.remove(sprite)
    try:
        player.kill()
    except Exception:
        pass
    level_map = load_level(eval(f'level_{choosen_level}_dict["level_map"]'))
    player = generate_level(level_map)
    background = load_image(eval(f'level_{choosen_level}_dict["back"]'))
    background_rect = background.get_rect()
    tile_images['surface'] = load_image(eval(f'level_{choosen_level}_dict["surface"]'))
    tile_images['beautiful_surface'] = load_image(eval(f'level_{choosen_level}_dict["beautiful_surface"]'))

    draw_hearts(player.lives)
    camera = Camera()
    camera.update(player)
    pygame.time.set_timer(pygame.USEREVENT, 1500)


def cut_sheet(obj, sheet, columns, rows):
    obj.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                           sheet.get_height() // rows)
    for j in range(rows):
        for i in range(columns):
            frame_location = (obj.rect.w * i, obj.rect.h * j)
            obj.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, obj.rect.size)))


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos_x, pos_y, group, little=0, light=True):
        super().__init__(group)
        self.light = light
        if little:
            if little == 1:
                self.font = pygame.font.Font('data/pixel3.ttf', 50)
            else:
                self.font = pygame.font.Font('data/pixel3.ttf', 30)
        else:
            self.font = pygame.font.Font('data/pixel3.ttf', 60)
        self.text = self.font.render(text, 1, (255, 255, 255))
        self.rect = self.text.get_rect(top=pos_y, left=pos_x)
        self.timer = 0

    def update(self):
        screen.blit(self.text, self.rect)

    def highlight(self):
        if self.light:
            for i in range(self.rect.width // 10):
                if i < self.timer:
                    pygame.draw.rect(screen, (255, 255, 255),
                                     (int(self.rect.left + i * 10), int(self.rect.bottom + 5), 9, 9))


class Decorative(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, img):
        super().__init__(all_sprites)
        self.image = img
        self.img_copy = img
        self.image = pygame.transform.scale(self.image,
                                            (self.img_copy.get_width() // 9, self.img_copy.get_height() // 3))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y]

        self.frames = []
        cut_sheet(self, self.image, 3, 1)
        self.cur_frame = random.randint(0, 2)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image,
                                            (self.img_copy.get_width() // 9, self.img_copy.get_height() // 3))
        self.rect = self.image.get_rect()
        self.step = 0
        if start:
            self.rect.center = (pos_x, pos_y)

    def change_frame(self):
        self.cur_frame = self.cur_frame + 0.1
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.image = pygame.transform.scale(self.image,
                                            (self.img_copy.get_width() // 9, self.img_copy.get_height() // 3))

    def update(self):
        self.step += 1
        self.change_frame()
        if self.step == 10 and not start:
            self.abs_pos[0] += random.randint(-15, 15)
            self.abs_pos[1] += random.randint(-15, 15)
            self.step = 0
        if start and self.step == 10:
            self.rect.x += random.randint(-15, 15)
            self.rect.y += random.randint(-15, 15)
            self.step = 0


class Tile(pygame.sprite.Sprite):
    # отрисовываем объекты
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        if tile_type == 'surface' or tile_type == 'beautiful_surface':
            self.add(surface_group)
        elif tile_type == 'coin':
            self.add(coin_group)
        elif tile_type == 'enemy':
            self.add(enemy_group)
        elif tile_type == 'end_table':
            self.add(end_group)
        self.pos_x = pos_x
        self.image = pygame.transform.scale(tile_images[tile_type], (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)

        if tile_type == 'end_table' or tile_type == 'start_table':
            self.image = pygame.transform.scale(tile_images[tile_type], (100, 100))


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        # изменяем положение обьектов, в соотвествии с камерой
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy


    def update(self, target):
        self.dx = 0
        self.dy = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        if isinstance(self, Enemy_1):
            self.image = tile_images['enemy_1']
        elif isinstance(self, Enemy_2):
            self.image = tile_images['enemy_2']
        self.image = pygame.transform.scale(self.image, (90, 110))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = [self.rect.x, self.rect.y - 20]
        self.speedx = - 80
        self.step = 0
        self.left = True

        self.frames = []
        cut_sheet(self, self.image, 3, 1)
        self.cur_frame = 1
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (97, 130))
        self.enemy_image = self.image
        self.rect = self.image.get_rect()

    def change_frame(self):
        self.cur_frame = self.cur_frame + 0.1
        self.enemy_image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.enemy_image = pygame.transform.scale(self.enemy_image, (97, 130))
        self.image = pygame.transform.flip(self.enemy_image, self.left, False)


class Enemy_1(Enemy):
    def update(self):
        self.step += 1
        self.change_frame()
        if self.step >= 100:
            self.step = 0
            self.speedx = - self.speedx
            self.left = not self.left
        self.abs_pos[0] += self.speedx * FPS / 1000


class Enemy_2(Enemy):
    def update(self):
        self.change_frame()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global choosen_character_to_play
        super().__init__(player_group, all_sprites)
        self.speedx = 0
        self.speedy = 0
        self.start_camera_dy = 0

        self.coins = 0
        if choosen_character_to_play == 1:
            self.lives = 3
            self.transparent_mod = None
        elif choosen_character_to_play == 2:
            self.lives = 4
            self.transparent_mod = None
        elif choosen_character_to_play == 3:
            self.transparent_mod = False   # мод невидимости для Донни
            self.lives = 5
        elif choosen_character_to_play == 4:
            self.lives = 6
            self.transparent_mod = None
        self.timer = 0

        self.damage = False
        self.left = False
        self.bad_moment = False
        self.jump = False
        self.win = False

        self.frames = []

        if choosen_character_to_play == 1:
            cut_sheet(self, load_image('hero1.png'), 3, 1)
        elif choosen_character_to_play == 2:
            cut_sheet(self, load_image('hero2.png'), 3, 1)
        elif choosen_character_to_play == 3:
            cut_sheet(self, load_image('hero3.png'), 3, 1)
        elif choosen_character_to_play == 4:
            cut_sheet(self, load_image('hero4.png'), 3, 1)

        self.cur_frame = 1
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (97, 130))
        self.player_image = self.image  # копия картинки персонажа, нужна для того чтобы по ней переворачивать картинку персонажа при ходьбе
        self.rect = pygame.Rect(0, 0, self.image.get_width() - 20, self.image.get_height())

        self.rect.left = pos_x * tile_width
        self.rect.centery = pos_y * tile_height

    def transparency(self):
        self.transparent_mod = True
        cut_sheet(self, load_image('transparent_hero3.png'), 3, 1)
        self.cur_frame = 1
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (97, 130))
        self.player_image = self.image  # копия картинки персонажа, нужна для того чтобы по ней переворачивать картинку персонажа при ходьбе
        self.rect = pygame.Rect(0, 0, self.image.get_width() - 20, self.image.get_height())
        self.rect.left = self.rect.x * tile_width
        self.rect.centery = self.rect.y * tile_height


    def get_keys(self):
        # проверяем какие клавиши нажаты, задаем скорость ходьбы
        keystate = pygame.key.get_pressed()
        self.speedx = 0
        if keystate[pygame.K_LEFT]:
            self.left = True
            if not self.collision_at_the_left():
                self.speedx = - 5
        if keystate[pygame.K_RIGHT]:
            self.left = False
            if not self.collision_at_the_right():
                self.speedx = 5
        if keystate[pygame.K_UP] and self.on_the_ground() and not self.collision_at_the_top():
            self.speedy = - 8
            if not self.bad_moment:
                # сохраняем начальное положение камеры перед прыжком, чтобы проверять не сместилась ли камера
                self.start_camera_dy = camera.dy
            self.rect.y -= 0.4  # чтобы 3не было пересечений с полом
            self.jump = True
            camera.dy += 0.4
        # анимация ходьбы, если ни одна клавиша не нажата, то оставляем 1 frame
        if any(keystate):
            self.change_frame()
        else:
            self.cur_frame = 1
            self.change_frame()

    def update(self):
        self.get_coins()
        # проверяем падает ли наш персонаж
        if not self.on_the_ground() and not self.collision_at_the_top():
            self.speedy += 0.4
            self.cur_frame = 0
            self.change_frame()
        else:
            self.speedy = 0

        # проверяем, что наш игрок не ушел за границы карты
        if self.rect.left < 300 and camera.dx != 0:
            self.rect.left = 300
        if self.rect.right > WIDTH - 300 and camera.dx != -len(level_map[0]) * tile_width + WIDTH:
            self.rect.right = WIDTH - 300

        # перемещаем игрока с проверкой, не уходит ли он за границы карты
        if self.rect.right + self.speedx <= WIDTH and self.rect.left + self.speedx >= 0:
            self.rect.x += self.speedx
        self.rect.y += self.speedy
        # без этого будет казаться, что где-то он ходит быстрее, а где-то медленнее
        if self.rect.right > WIDTH - 300 or self.rect.left < 300:
            self.speedx *= 1.5
        # перемещаем камеру, если мы не достигли конца/начала карты
        if not (self.rect.right >= WIDTH - 300 and camera.dx == -len(level_map[0]) * tile_width + WIDTH) and not \
                (self.rect.left < 300 and camera.dx == 0):
            camera.dx -= self.speedx
        camera.dy -= self.speedy
        # self.bad_moment - отвечает за смещение камеры, когда наш персонаж стукается о платформу сверху,
        # чтобы камера возвращалась в положение до прыжка
        if self.bad_moment and self.on_the_ground():
            camera.dy = self.start_camera_dy
            self.bad_moment = False
        # проверяем, чтобы наша камера не уходила за границы уровня
        if camera.dx > 0:
            camera.dx = 0
        if camera.dx < -len(level_map[0]) * tile_width + WIDTH:
            camera.dx = -len(level_map[0]) * tile_width + WIDTH
        if camera.dy < tile_height * 2:
            camera.dy = tile_height * 2
        # изменяем положение объектов относительно камеры
        for sprite in all_sprites:
            if sprite != self and sprite not in player_group:
                camera.apply(sprite)
        # проверяем столкновение с врагом
        if self.timer == 1:
            self.damage = False
        for sprite in pygame.sprite.spritecollide(self, enemy_group, False):
            if self.transparent_mod:
                self.transparent_mod = False
            else:
                if not self.damage:
                    self.lives -= 1
                    self.damage = True
                    self.timer = 0
                    pygame.time.set_timer(pygame.USEREVENT, 1500)
                    draw_hearts(self.lives)
        if self.lives == 0:
            self.end_of_level()
        if pygame.sprite.spritecollide(self, end_group, False):
            self.win = True
            self.end_of_level()

    def drop(self):
        if self.transparent_mod:
            pass
        else:
            for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    r = self.image.get_at((x, y))[0]
                    r = r + 50 if r < 205 else 255
                    g = self.image.get_at((x, y))[1]
                    g -= 50 if g > 50 else 0
                    b = self.image.get_at((x, y))[2]
                    b -= 50 if b > 50 else 0
                    a = self.image.get_at((x, y))[3]
                    self.image.set_at((x, y), pygame.Color(r, g, b, a))
                    self.player_image = self.image


    def change_frame(self):
        # анимация ходьбы
        self.cur_frame = self.cur_frame + 0.1
        self.player_image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.player_image = pygame.transform.scale(self.player_image, (97, 130))
        self.image = pygame.transform.flip(self.player_image, self.left, False)
        if self.damage:
            self.drop()

    def on_the_ground(self):
        # проверка стоит ли наш персонаж на земле
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.top - 23 > self.rect.centery:
                # if not self.bad_moment:
                self.start_camera_dy = camera.dy
                self.rect.bottom = sprite.rect.top + 1
                self.jump = False
                return True
        return False

    def collision_at_the_top(self):
        # столкновение с блоками сверху
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.top <= self.rect.top and abs(self.rect.centerx - sprite.rect.centerx) < 50:
                self.rect.top = sprite.rect.bottom + 1
                if self.jump:
                    self.bad_moment = True
                return True
        return False

    def collision_at_the_right(self):
        # столкновение с блоками справа
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.left <= self.rect.right and not self.rect.bottom == sprite.rect.top + 1:
                if sprite.rect.left < self.rect.left:
                    self.rect.right += 2
                return True
        return False

    def collision_at_the_left(self):
        # столкновение с блоками слева
        for sprite in pygame.sprite.spritecollide(self, surface_group, False):
            if sprite.rect.right <= self.rect.right and not self.rect.bottom == sprite.rect.top + 1:
                return True
        return False

    def get_coins(self):
        # собираем монетки
        for sprite in pygame.sprite.spritecollide(self, coin_group, True):
            self.coins += 1

    def end_of_level(self):
        end_screen()

    def shoot(self):
        Bullet(self.rect.centerx - camera.dx, self.rect.centery - camera.dy)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        global choosen_character_to_play
        super().__init__(all_sprites)
        self.image = load_image(f'fire{choosen_character_to_play}.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.bottom = pos_y
        self.rect.centerx = pos_x

        self.starting_pos = pos_x
        self.speedx = 13 if not player.left else -13

        self.abs_pos = [self.rect.x, self.rect.y]

        self.collision = False
        self.cur_frame = 0
        self.boom_image = load_image('boom.png')
        self.frames = []
        cut_sheet(self, self.boom_image, 7, 1)

    def update(self):
        global choosen_character_to_play
        for sprite in pygame.sprite.spritecollide(self, enemy_group, True):
            self.abs_pos = sprite.abs_pos
            self.collision = True
            if choosen_character_to_play == 2:  # Если персонаж HShoeCrab - монет выпадает вдвое больше!!!
                player.coins += random.randint(16, 30)
            else:
                player.coins += random.randint(8, 15)
            self.speedx = 0
        if self.collision:
            self.boom()
        else:
            self.abs_pos[0] += self.speedx
            if abs(self.abs_pos[0] - self.starting_pos) == 500:
                self.kill()

    def boom(self):
        self.cur_frame = self.cur_frame + 0.22
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.image = pygame.transform.scale(self.image, (64, 64))
        if self.cur_frame > 7:
            self.kill()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((0, 0, 0))
    pygame.display.set_caption('TheSTHR')
    clock = pygame.time.Clock()
    pygame.time.set_timer(pygame.USEREVENT, 1500)
    load_progress()

    tile_width = tile_height = 50
    tile_images = {
        'surface': load_image('ground.jpg'),
        'beautiful_surface': load_image('grass.png'),
        'coin': load_image('coins.png'),
        'enemy': load_image('enemy1.png'),
        'enemy_1': load_image('enemy_1.png'),
        'enemy_2': load_image('enemy_2.png'),
        'start_table': load_image('table.png'),
        'end_table': load_image('table.png'),
        'dec_heart': load_image('dec_1.png'),
        'dec_dragonfly': load_image('dec_2.png'),
        'dec_fly': load_image('fly.png')
    }
    heart_image = load_image('heart.png')

    # прописываем группы спрайтов
    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    surface_group = pygame.sprite.Group()
    coin_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    end_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()

    start = True
    start_screen()

    pixel_font = pygame.font.Font('data/pixel1.ttf', 48)
    coins = pixel_font.render('0', 1, (255, 255, 255))
    coins_rect = coins.get_rect(center=(900, 50))

    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(background, background_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                write_progress()
                running = False
            if event.type == pygame.USEREVENT:
                if player.damage:
                    player.timer += 1
                else:
                    pygame.time.set_timer(pygame.USEREVENT, 0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # здесь выстрел по нажатию пробела
                    player.shoot()
                if event.key == pygame.K_z and choosen_character_to_play == 3:  # здесь если персонаж Donnie - делаем его невидимым
                    player.transparency()

        player.get_keys()
        coins = pixel_font.render(str(player.coins), 1, (255, 255, 255))
        hearts_group.draw(screen)
        all_sprites.draw(screen)
        all_sprites.update()
        screen.blit(coins, coins_rect)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
