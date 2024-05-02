# Crimsoland

Цель: Изучить событийно-ориентированное программирование с использованиембиблиотеки на языке  Python при помощи библиотеки Pygame

### Класс Enemy(GameObject):

- `__init__(self, x, y, hp, speed, dmg, img)`: Инициализирует врага с заданными параметрами: координаты (x, y), количество жизней (hp), скорость (speed), урон (dmg), и изображение (img).
- `set_move_target(self, targetx, targety)`: Устанавливает целевое положение для движения врага.
- `move(self)`: Определяет логику движения врага к целевой позиции.
- `take_damage(self, damage)`: Наносит урон врагу, уменьшая его количество жизней.

### Класс Bullet(GameObject):

- `__init__(self, playerx, playery, targetx, targety, dmg, speed)`: Инициализирует пулю с заданными параметрами: начальное положение игрока (playerx, playery), целевое положение (targetx, targety), урон (dmg) и скорость (speed).
- `move(self)`: Определяет логику движения пули в направлении цели.

### Класс GameLogic:

- `handle_events(self)`: Обрабатывает события в игре, такие как нажатия клавиш и мыши.
- `show_menu(self, state="init")`: Отображает главное меню игры или меню паузы в зависимости от состояния.
- `show_weapon_selection(self)`: Отображает меню выбора оружия для игрока.
- `show_leaderboard(self)`: Отображает таблицу лидеров.
- `input_box(self, prompt)`: Отображает окно ввода для получения текстового ввода от пользователя.
- `update_leaderboard(self)`: Обновляет таблицу лидеров с текущими результатами игрока.
- `load_rules_from_json(self, file_path)`: Загружает правила игры из файла JSON.
- `show_rules(self)`: Отображает правила игры.
- `play_game(self, level)`: Запускает игровой процесс для указанного уровня.
- `start(self)`: Начинает игру и управляет ее ходом.
- `mouse_in_rect(self, mouse, rect)`: Проверяет, находится ли курсор мыши в прямоугольнике.
- `is_obj_collision(self, obj1, obj2)`: Проверяет столкновение двух объектов.
- `check_hits(self)`: Проверяет попадания пуль во врагов и обновляет количество убитых врагов.
- `check_player_get_damage(self)`: Проверяет, получил ли игрок урон от врагов.
- `is_out_of_window(self, obj)`: Проверяет, находится ли объект за пределами игрового окна.
- `enemy_placing(self)`: Генерирует случайные координаты для появления врагов на экране.
- `show_level_selection(self)`: Отображает меню выбора уровня игры.


# Главное меню

![2024-05-02](https://github.com/NikitaGryn/game1/assets/114168438/c8b1eba1-9684-4399-86e3-4afb97921f98)

# Таблица рекордов

![2024-05-02 (1)](https://github.com/NikitaGryn/game1/assets/114168438/509ff10d-6e39-47e2-8372-93cd9dd22857)

# Выбор оружия

![2024-05-02 (3)](https://github.com/NikitaGryn/game1/assets/114168438/8fb75d78-4af0-4277-ba5d-dbb9cbc7c642)

# 20 уровней

![2024-05-02 (2)](https://github.com/NikitaGryn/game1/assets/114168438/abfb95e2-bd41-47e0-9699-a84f6431076d)

# Сама игра

![2024-05-02 (4)](https://github.com/NikitaGryn/game1/assets/114168438/4916d56d-fe74-47b7-9e89-863745a2cbdb)
![2024-05-02 (5)](https://github.com/NikitaGryn/game1/assets/114168438/c2eb4c26-75c1-473e-885d-eae40847d6f1)
