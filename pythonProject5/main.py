import math
import pygame
import sys
import pygame.mixer
import os
import time
import json

from constants import *
from random import randint, choice
from pygame.locals import *


class GameObject(object):
    def __init__(self, x, y):
        self._set_coords(x, y)
        self._width = 0
        self._height = 0

    def _set_coords(self, x, y):
        self._x = x
        self._y = y

    def get_coords(self):
        return self._x, self._y

    def get_round_coords(self):
        return int(round(self._x)), int(round(self._y))

    def get_size(self):
        return self._width, self._height


class Player(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, x, y)
        self._move_directions = []
        self.shooting = False
        self._width, self._height = PLAYER_IMG.get_size()
        self._hp = PLAYERHITPOINTS

    def start_move(self, direction):
        self._move_directions.append(direction)

    def end_move(self, direction):
        if direction in self._move_directions:
            self._move_directions.remove(direction)

    def move(self):
        x, y = self.get_coords()
        self._dx = 0
        self._dy = 0
        for direction in self._move_directions:
            if direction == 'up':
                self._dy = -PLAYERSPEED
            if direction == 'down':
                self._dy = PLAYERSPEED
            if direction == 'left':
                self._dx = -PLAYERSPEED
            if direction == 'right':
                self._dx = PLAYERSPEED
        self._set_coords(x + self._dx, y + self._dy)

    def set_shooting(self, status):
        self.shooting = status

    def get_shooting(self):
        return self.shooting

    def take_damage(self, damage):
        self._hp -= damage

    def is_alive(self):
        return self._hp > 0


class Enemy(GameObject):
    def __init__(self, x, y, hp, speed, dmg, img):
        GameObject.__init__(self, x, y)
        self._dx = 0
        self._dy = 0
        self._hit_target = False
        self._hp = hp
        self._speed = speed
        self._dmg = dmg
        self._img = img
        self._width, self._height = img.get_size()

    def set_move_target(self, targetx, targety):
        self._move_tx = targetx
        self._move_ty = targety

    def move(self):
        x, y = self.get_coords()
        if abs((self._move_tx - x) * (self._move_ty - y)) < self._width:
            self._hit_target = True
            self._dx = 0
            self._dy = 0
        else:
            self._hit_target = False
        if not self._hit_target:
            angle = math.atan2(self._move_ty - y, self._move_tx - x)
            self._dx = self._speed * math.cos(angle)
            self._dy = self._speed * math.sin(angle)
        self._set_coords(x + self._dx, y + self._dy)

    def take_damage(self, damage):
        self._hp -= damage


class Bullet(GameObject):
    def __init__(self, playerx, playery, targetx, targety, dmg, speed):
        self._set_coords(playerx, playery)
        self._width, self._height = BULLETSIZE, BULLETSIZE
        self._tx = targetx
        self._ty = targety
        self._speed = speed
        angle = math.atan2(self._ty - playery, self._tx - playerx)
        self._dx = int(round(self._speed * math.cos(angle)))
        self._dy = int(round(self._speed * math.sin(angle)))
        self._hit_target = False
        self.dmg = dmg

    def move(self):
        x, y = self.get_coords()
        if abs((self._tx - x) * (self._ty - y)) < self._speed * self._speed:
            self._hit_target = True
        if not self._hit_target:
            angle = math.atan2(self._ty - y, self._tx - x)
            self._dx = int(round(self._speed * math.cos(angle)))
            self._dy = int(round(self._speed * math.sin(angle)))
        self._set_coords(x + self._dx, y + self._dy)


class GameLogic(object):
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.enemy_kill_sound = pygame.mixer.Sound('enemy_kill_sound.mp3')
        self.displaysurf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.fpsclock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', BASICFONTSIZE)
        pygame.display.set_caption('Simple shooting')
        self.game_time = 0
        self.time_text = '0:00'
        self.enemy_kills = 0
        self.leaderboard = {}
        self.BULLETSPEED = 10

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key in (K_UP, K_w):
                    self.player.start_move('up')
                if event.key in (K_DOWN, K_s):
                    self.player.start_move('down')
                if event.key in (K_LEFT, K_a):
                    self.player.start_move('left')
                if event.key in (K_RIGHT, K_d):
                    self.player.start_move('right')
            elif event.type == KEYUP:
                if event.key == K_ESCAPE:
                    self.show_menu(state="pause")
                if event.key in (K_UP, K_w):
                    self.player.end_move('up')
                if event.key in (K_DOWN, K_s):
                    self.player.end_move('down')
                if event.key in (K_LEFT, K_a):
                    self.player.end_move('left')
                if event.key in (K_RIGHT, K_d):
                    self.player.end_move('right')
            elif event.type == MOUSEBUTTONDOWN:
                self.player.set_shooting(True)
            elif event.type == MOUSEBUTTONUP:
                self.player.set_shooting(False)
            elif event.type == USEREVENT + 1:
                self.update_timer()

    def show_menu(self, state="init"):
        self.displaysurf.blit(TERRAIN_IMG, (0, 0))
        text_exit = "EXIT"
        if state == "init":
            text_play = "PLAY"
            text_leaderboard = "LEADERBOARD"
            text_help = "HELP"
            text_levels = "LEVELS"
            text_weapon = "WEAPON"
        elif state == "pause":
            text_play = "RESUME"
            text_leaderboard = "LEADERBOARD"
            text_help = "HELP"
            text_levels = "LEVELS"
            text_weapon = "WEAPON"
        elif state == "end":
            text_play = "SCORE: %s" % (self.game_time * self.enemy_kills)
            text_exit = "GAME OVER"
            text_leaderboard = "LEADERBOARD"
            text_help = "HELP"
            text_levels = "LEVELS"
            text_weapon = "WEAPON"

        button_spacing_play_leaderboard = 3
        button_spacing_leaderboard_help = 18
        button_spacing_help_exit = 25
        button_spacing_exit_levels = 38
        button_spacing_levels_weapon = 50

        pw, ph = self.font.render(text_play, True, YELLOW).get_size()
        px = WINDOWWIDTH / 2 - pw / 2
        py = WINDOWHEIGHT / 2 - ph - button_spacing_play_leaderboard

        lw, lh = self.font.render(text_leaderboard, True, YELLOW).get_size()
        lx = WINDOWWIDTH / 2 - lw / 2
        ly = WINDOWHEIGHT / 2 + lh + 2 * button_spacing_play_leaderboard

        hw, hh = self.font.render(text_help, True, YELLOW).get_size()
        hx = WINDOWWIDTH / 2 - hw / 2
        hy = WINDOWHEIGHT / 2 + hh + 3 * button_spacing_leaderboard_help

        ew, eh = self.font.render(text_exit, True, YELLOW).get_size()
        ex = WINDOWWIDTH / 2 - ew / 2
        ey = WINDOWHEIGHT / 2 + eh + 4 * button_spacing_help_exit

        aw, ah = self.font.render(text_levels, True, YELLOW).get_size()
        ax = WINDOWWIDTH / 2 - aw / 2
        ay = WINDOWHEIGHT / 2 + ah + 4 * button_spacing_exit_levels

        ww, wh = self.font.render(text_weapon, True, YELLOW).get_size()
        wx = WINDOWWIDTH / 2 - ww / 2
        wy = WINDOWHEIGHT / 2 + wh + 4 * button_spacing_levels_weapon

        self.displaysurf.blit(self.font.render(text_play, True, YELLOW), (px, py))
        self.displaysurf.blit(self.font.render(text_leaderboard, True, YELLOW), (lx, ly))
        self.displaysurf.blit(self.font.render(text_help, True, YELLOW), (hx, hy))
        self.displaysurf.blit(self.font.render(text_exit, True, YELLOW), (ex, ey))
        self.displaysurf.blit(self.font.render(text_levels, True, YELLOW), (ax, ay))
        self.displaysurf.blit(self.font.render(text_weapon, True, YELLOW), (wx, wy))

        pygame.display.update()

        while True:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                mousex, mousey = pygame.mouse.get_pos()
                if self.mouse_in_rect((mousex, mousey), (px, py, pw, ph)):
                    self.enemy_kills = 0
                    return "play"
                elif self.mouse_in_rect((mousex, mousey), (lx, ly, lw, lh)):
                    self.show_leaderboard()
                elif self.mouse_in_rect((mousex, mousey), (hx, hy, hw, hh)):
                    self.show_rules()
                elif self.mouse_in_rect((mousex, mousey), (ax, ay, aw, ah)):
                    self.enemy_kills = 0
                    level = self.show_level_selection()
                    self.play_game(level)
                elif self.mouse_in_rect((mousex, mousey), (ex, ey, ew, eh)):
                    terminate()
                elif self.mouse_in_rect((mousex, mousey), (wx, wy, ww, wh)):
                    self.show_weapon_selection()
            self.fpsclock.tick(FPS)

    def show_weapon_selection(self):
        self.displaysurf.blit(TERRAIN_IMG, (0, 0))
        text_exit = "BACK"
        text_weapon1 = "Normal Weapon"
        text_weapon2 = "Dual Direction Weapon"
        text_weapon3 = "Triple Bullet Weapon"

        button_spacing_weapon1_weapon2 = 10
        button_spacing_weapon2_weapon3 = 20

        w1w, w1h = self.font.render(text_weapon1, True, YELLOW).get_size()
        w1x = WINDOWWIDTH / 2 - w1w / 2
        w1y = WINDOWHEIGHT / 2 - w1h / 2

        w2w, w2h = self.font.render(text_weapon2, True, YELLOW).get_size()
        w2x = WINDOWWIDTH / 2 - w2w / 2
        w2y = WINDOWHEIGHT / 2 - w2h / 2 + w1h + button_spacing_weapon1_weapon2

        w3w, w3h = self.font.render(text_weapon3, True, YELLOW).get_size()
        w3x = WINDOWWIDTH / 2 - w3w / 2
        w3y = WINDOWHEIGHT / 2 - w3h / 2 + w1h + button_spacing_weapon1_weapon2 + w2h + button_spacing_weapon2_weapon3

        ew, eh = self.font.render(text_exit, True, YELLOW).get_size()
        ex = WINDOWWIDTH - ew - 10
        ey = 10

        self.displaysurf.blit(self.font.render(text_weapon1, True, YELLOW), (w1x, w1y))
        self.displaysurf.blit(self.font.render(text_weapon2, True, YELLOW), (w2x, w2y))
        self.displaysurf.blit(self.font.render(text_weapon3, True, YELLOW), (w3x, w3y))
        self.displaysurf.blit(self.font.render(text_exit, True, YELLOW), (ex, ey))

        pygame.display.update()
        while True:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                mousex, mousey = pygame.mouse.get_pos()
                if self.mouse_in_rect((mousex, mousey), (w1x, w1y, w1w, w1h)):
                    self.BULLETSPEED = 10  # Change bullet speed based on selection
                    self.show_menu()
                elif self.mouse_in_rect((mousex, mousey), (w2x, w2y, w2w, w2h)):
                    self.BULLETSPEED = 25  # Change bullet speed based on selection
                    self.show_menu()
                elif self.mouse_in_rect((mousex, mousey), (w3x, w3y, w3w, w3h)):
                    self.BULLETSPEED = 50  # Change bullet speed based on selection
                    self.show_menu()
                elif self.mouse_in_rect((mousex, mousey), (ex, ey, ew, eh)):
                    self.show_menu()
            self.fpsclock.tick(FPS)

    def show_leaderboard(self):
        self.displaysurf.fill(BLACK)

        filename = "leaderboard.json"
        try:
            with open(filename, 'r') as file:
                leaderboard = json.load(file)
        except FileNotFoundError:
            leaderboard = {}

        title_text = self.font.render("Leaderboard", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOWWIDTH // 2, 50))
        self.displaysurf.blit(title_text, title_rect)

        if self.enemy_kills > 0:
            new_record = False
            for name, score in leaderboard.items():
                if self.enemy_kills > score:
                    new_record = True
                    break
            if new_record:
                name_input = self.input_box("Enter your name: ")
                leaderboard[name_input] = self.enemy_kills

                leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))

                with open(filename, 'w') as file:
                    json.dump(leaderboard, file)

        y_offset = 100
        for idx, (player_name, score) in enumerate(leaderboard.items(), start=1):
            player_text = f"{idx}. {player_name}: {score}"
            player_rendered = self.font.render(player_text, True, YELLOW)
            player_rect = player_rendered.get_rect(center=(WINDOWWIDTH // 2, y_offset))
            self.displaysurf.blit(player_rendered, player_rect)
            y_offset += 30

        back_button = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(self.displaysurf, BLACK, back_button, border_radius=5)
        back_text = self.font.render("Back", True, YELLOW)
        text_rect = back_text.get_rect(center=back_button.center)
        self.displaysurf.blit(back_text, text_rect)

        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        waiting = False
                        self.show_menu(state="init")
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def input_box(self, prompt):
        input_rect = pygame.Rect(0, 0, 200, 32)
        input_rect.center = (WINDOWWIDTH // 4, 250)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        font = pygame.font.Font(None, 32)
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        active = not active
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            return text
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            self.displaysurf.fill(BLACK)
            pygame.draw.rect(self.displaysurf, color, input_rect, 2)
            text_surface = font.render(text, True, color)
            self.displaysurf.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            input_rect.w = max(200, text_surface.get_width() + 10)
            pygame.display.flip()
            clock.tick(30)

    def update_leaderboard(self):
        score = self.game_time * self.enemy_kills
        if score > 0:
            self.leaderboard[time.time()] = score

    def load_rules_from_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                rules_data = json.load(file)
                return rules_data.get("rules", [])
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return []

    def show_rules(self):

        rules_window = pygame.Surface((WINDOWWIDTH, WINDOWHEIGHT))

        image_path = os.path.join("img.png")
        ground1 = pygame.image.load(image_path)
        rules_window.blit(ground1, (0, 0))

        font = pygame.font.Font(None, 20)

        rules = self.load_rules_from_json("rules.json")

        y_offset = 30
        for line in rules:
            text_surface = font.render(line, True, BLACK)
            rules_window.blit(text_surface, (10, y_offset))
            y_offset += 20

        back_button = pygame.Rect(WINDOWWIDTH - 120, 10, 110, 40)
        pygame.draw.rect(rules_window, GRAY, back_button, border_radius=5)
        back_text = font.render("Back", True, BLACK)
        text_rect = back_text.get_rect(center=back_button.center)
        rules_window.blit(back_text, text_rect)

        self.displaysurf.blit(rules_window, (0, 0))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button.collidepoint(mouse_pos):
                        waiting = False
                        self.show_menu(state="init")
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def play_game(self, level):
        self.enemies = []
        speed = (ENEMYSPEED + level) / FPS
        for i in range(ENEMY_INITIAL_COUNT):
            x, y = self.enemy_placing()
            self.enemies.append(Enemy(x, y, ENEMYHITPOINTS, speed,
                                      ENEMY_DAMAGE, ENEMY_IMG))
        self.bullets = []
        self.player = Player(PLAYERSTARTPOSITION[0], PLAYERSTARTPOSITION[1])
        clock_enemies_spawn = 0
        firerate_counter = FIRERATE
        pygame.time.set_timer(USEREVENT + 1, 1000)
        while True:
            self.handle_events()
            clock_enemies_spawn += 1
            if clock_enemies_spawn >= ENEMY_SPAWN_TIME:
                clock_enemies_spawn = 0
                for counter in range(ENEMY_SPAWN_COUNT):
                    x, y = self.enemy_placing()
                    self.enemies.append(Enemy(x, y, ENEMYHITPOINTS, speed,
                                              ENEMY_DAMAGE, ENEMY_IMG))

            self.displaysurf.blit(TERRAIN_IMG, (0, 0))

            playerx, playery = self.player.get_coords()
            if self.player.get_shooting():
                if firerate_counter >= FIRERATE:
                    firerate_counter = 0
                    mousex, mousey = pygame.mouse.get_pos()
                    self.bullets.append(Bullet(playerx, playery, mousex, mousey, BULLETDAMAGE, self.BULLETSPEED))
            for bullet in self.bullets:
                bullet.move()
                pygame.draw.circle(self.displaysurf, BLUE, (bullet.get_coords()), BULLETSIZE)
                if self.is_out_of_window(bullet):
                    self.bullets.remove(bullet)
            self.player.move()
            for enemy in self.enemies:
                enemy.set_move_target(playerx, playery)
                enemy.move()
                self.displaysurf.blit(ENEMY_IMG, (enemy.get_round_coords()))
            self.check_hits()
            self.check_player_get_damage()
            self.displaysurf.blit(PLAYER_IMG, (self.player.get_coords()))
            self.displaysurf.blit(self.font.render(self.time_text, True,
                                                   (YELLOW)), (20, 10))
            text_kills = 'Kills: %s' % self.enemy_kills
            self.displaysurf.blit(self.font.render(text_kills, True,
                                                   (YELLOW)),
                                  (WINDOWWIDTH - 100, 10))
            pygame.display.update()
            if not self.player.is_alive():
                self.show_menu()
                break
            firerate_counter += 1
            if firerate_counter > FIRERATE:
                firerate_counter = FIRERATE
            self.fpsclock.tick(FPS)

    def start(self):
        while True:
            self.enemy_kills = 0
            self.game_time = 0
            menu_result = self.show_menu()
            if menu_result == "play":
                self.play_game(1)
            else:
                break
        terminate()
        self.show_menu()
        self.enemies = []
        speed = ENEMYSPEED / FPS
        for i in range(ENEMY_INITIAL_COUNT):
            x, y = self.enemy_placing()
            self.enemies.append(Enemy(x, y, ENEMYHITPOINTS, speed,
                                      ENEMY_DAMAGE, ENEMY_IMG))
        self.bullets = []
        self.player = Player(PLAYERSTARTPOSITION[0], PLAYERSTARTPOSITION[1])
        clock_enemies_spawn = 0
        firerate_counter = FIRERATE
        pygame.time.set_timer(USEREVENT + 1, 1000)
        while True:
            self.handle_events()
            clock_enemies_spawn += 1
            if clock_enemies_spawn >= ENEMY_SPAWN_TIME:
                clock_enemies_spawn = 0
                for counter in range(ENEMY_SPAWN_COUNT):
                    x, y = self.enemy_placing()
                    self.enemies.append(Enemy(x, y, ENEMYHITPOINTS, speed,
                                              ENEMY_DAMAGE, ENEMY_IMG))

            self.displaysurf.blit(TERRAIN_IMG, (0, 0))

            # move player, enemies, bullets
            playerx, playery = self.player.get_coords()
            if self.player.get_shooting():
                if firerate_counter >= FIRERATE:
                    firerate_counter = 0
                    mousex, mousey = pygame.mouse.get_pos()
                    self.bullets.append(Bullet(playerx, playery, mousex, mousey, BULLETDAMAGE))
            for bullet in self.bullets:
                bullet.move()
                pygame.draw.circle(self.displaysurf, BLUE, (bullet.get_coords()), BULLETSIZE)
                if self.is_out_of_window(bullet):
                    self.bullets.remove(bullet)
            self.player.move()
            for enemy in self.enemies:
                enemy.set_move_target(playerx, playery)
                enemy.move()
                self.displaysurf.blit(ENEMY_IMG, (enemy.get_round_coords()))
            self.check_hits()
            self.check_player_get_damage()
            # draw player, stats, etc.
            self.displaysurf.blit(PLAYER_IMG, (self.player.get_coords()))
            self.displaysurf.blit(self.font.render(self.time_text, True,
                                                   (YELLOW)), (20, 10))
            text_kills = 'Kills: %s' % self.enemy_kills
            self.displaysurf.blit(self.font.render(text_kills, True,
                                                   (YELLOW)),
                                  (WINDOWWIDTH - 100, 10))
            pygame.display.update()
            if not self.player.is_alive():
                self.show_menu()
                break
            firerate_counter += 1
            if firerate_counter > FIRERATE:
                firerate_counter = FIRERATE
            self.fpsclock.tick(FPS)

    def update_timer(self):
        self.game_time += 1
        mm = self.game_time / 60
        ss = self.game_time % 60
        self.time_text = '%s:%s' % (mm, str(ss).zfill(2))

    def mouse_in_rect(self, mouse, rect):
        mousex, mousey = mouse
        x, y, w, h = rect
        return x <= mousex <= x + w and \
            y <= mousey <= y + h

    def is_obj_collision(self, obj1, obj2):
        x1, y1 = obj1.get_coords()
        w1, h1 = obj1.get_size()
        x2, y2 = obj2.get_coords()
        w2, h2 = obj2.get_size()

        distance = (w1 + w2) * 0.8
        x1 = x1 + w1 / 2
        y1 = y1 + h1 / 2
        x2 = x2 + w2 / 2
        y2 = y2 + h2 / 2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) < distance

    def check_hits(self):
        bullets_to_remove = []
        enemies_to_remove = []
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet not in bullets_to_remove and \
                        enemy not in enemies_to_remove and \
                        self.is_obj_collision(bullet, enemy):
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
                    self.enemy_kills += 1
                    self.update_leaderboard()
        for bullet in bullets_to_remove:
            self.bullets.remove(bullet)
        for enemy in enemies_to_remove:
            self.enemies.remove(enemy)
            self.enemy_kill_sound.play()

    def check_player_get_damage(self):
        for enemy in self.enemies:
            if self.is_obj_collision(enemy, self.player):
                self.player.take_damage(ENEMY_DAMAGE)

    def is_out_of_window(self, obj):
        x, y = obj.get_coords()
        if x < 0 or x > WINDOWWIDTH or y < 0 or y > WINDOWHEIGHT:
            return True
        return False

    def enemy_placing(self):
        GRID_SIZE = 15
        CELL_WIDTH = int(WINDOWWIDTH / GRID_SIZE)
        CELL_HEIGHT = int(WINDOWHEIGHT / GRID_SIZE)

        places = ('topleft', 'topmid', 'topright',
                  'midleft', 'midright',
                  'bottomleft', 'bottommid', 'bottomright')
        place = choice(places)
        if place == 'topleft':
            x = randint(0, CELL_WIDTH)
            y = randint(0, CELL_HEIGHT)
        if place == 'topmid':
            x = randint(CELL_WIDTH, WINDOWWIDTH - CELL_WIDTH)
            y = randint(0, CELL_HEIGHT)
        if place == 'topright':
            x = randint(WINDOWWIDTH - CELL_WIDTH, WINDOWWIDTH)
            y = randint(0, CELL_HEIGHT)
        if place == 'midleft':
            x = randint(0, CELL_WIDTH)
            y = randint(CELL_HEIGHT, WINDOWHEIGHT - CELL_HEIGHT)
        if place == 'midright':
            x = randint(WINDOWWIDTH - CELL_WIDTH, WINDOWWIDTH)
            y = randint(CELL_HEIGHT, WINDOWHEIGHT - CELL_HEIGHT)
        if place == 'bottomleft':
            x = randint(0, CELL_WIDTH)
            y = randint(WINDOWHEIGHT - CELL_HEIGHT, WINDOWHEIGHT)
        if place == 'bottommid':
            x = randint(CELL_WIDTH, WINDOWWIDTH - CELL_WIDTH)
            y = randint(WINDOWHEIGHT - CELL_HEIGHT, WINDOWHEIGHT)
        if place == 'bottomright':
            x = randint(WINDOWWIDTH - CELL_WIDTH, WINDOWWIDTH)
            y = randint(WINDOWHEIGHT - CELL_HEIGHT, WINDOWHEIGHT)
        return (x, y)

    def show_level_selection(self):
        self.displaysurf.fill(BLACK)
        title_text = self.font.render("Select Level", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOWWIDTH // 2, 50))
        self.displaysurf.blit(title_text, title_rect)

        level_buttons = []
        button_width = 100
        button_height = 50
        button_spacing = 20

        for i in range(20):
            row = i // 5
            col = i % 5
            x = (WINDOWWIDTH - 5 * button_width - 4 * button_spacing) // 2 + col * (button_width + button_spacing)
            y = (WINDOWHEIGHT - 4 * button_height - 3 * button_spacing) // 2 + row * (button_height + button_spacing)
            button_rect = pygame.Rect(x, y, button_width, button_height)
            level_buttons.append(button_rect)
            pygame.draw.rect(self.displaysurf, YELLOW, button_rect)

            button_text = self.font.render(f"Level {i + 1}", True, BLACK)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.displaysurf.blit(button_text, text_rect)

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button_rect in enumerate(level_buttons):
                        if button_rect.collidepoint(mouse_pos):
                            return i + 1
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


def terminate():
    pygame.quit()
    sys.exit()


def main():
    game = GameLogic()
    game.start()


if __name__ == '__main__':
    main()
