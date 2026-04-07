# =================
# import
# ==================

import pygame
import math
import random
import sys
import json
import os

import cv2
import mediapipe as mp
import time

import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)
# =============================
# Initialize Pygame
# =============================


cap = cv2.VideoCapture(0)
pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))

timer_started = False
start_time = 0
elapsed_time = 0
last_switch_time = pygame.time.get_ticks()
TUTORIAL_DELAY = 2  # seconds
tutorial_index = 0
in_transition = False

leaderboard_file = "leaderboard.json"
leaderboard = {}

guess_chance = False

show_popup_small_option = False


def load_animation(folder, scale=None):
    frames = []

    files = sorted(
        [f for f in os.listdir(folder) if f.lower().endswith(".jpg")]
    )

    for file in files:
        path = os.path.join(folder, file)
        img = pygame.image.load(path).convert_alpha()

        if scale:
            img = pygame.transform.scale(img, scale)

        frames.append(img)

    print("Loaded frames:", len(frames))  # DEBUG
    return frames


def load_leaderboard():
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as f:
            return json.load(f)
    return {}


def save_leaderboard(data):
    with open(leaderboard_file, "w") as f:
        json.dump(data, f, indent=4)


def print_leaderboard():
    if not leaderboard:
        print("=== LEADERBOARD EMPTY ===")
        return

    print("\n=== LEADERBOARD (BEST TIMES) ===")
    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1])

    for i, (name, time_) in enumerate(sorted_lb, start=1):
        print(f"{i}. {name} - {time_:.2f}s")


def draw_leaderboard(screen, leaderboard, font, x, y, max_entries=8):
    """
    Draws the top leaderboard entries on the screen.
    screen : Pygame screen
    leaderboard : dict {player_name: time}
    font : Pygame font object
    x, y : starting position to draw
    max_entries : maximum number of entries to show
    """

    # Sort by fastest time
    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1])

    # Draw the title

    offset_y = y + 100

    # Draw top entries
    for i, (name, time_) in enumerate(sorted_lb[:max_entries], start=1):
        entry_text = f"{i}. {name} - {time_:.2f}s"
        entry_surface = font.render(entry_text, True, (240, 240, 240))
        screen.blit(entry_surface, (x, offset_y))
        offset_y += 50


def draw_leaderboard_shadow(screen, leaderboard, font, x, y, max_entries=8):
    """
    Draws the top leaderboard entries on the screen.
    screen : Pygame screen
    leaderboard : dict {player_name: time}
    font : Pygame font object
    x, y : starting position to draw
    max_entries : maximum number of entries to show
    """
    if not leaderboard:
        text_surface = font.render("Leaderboard is empty", True, (255, 255, 255))
        screen.blit(text_surface, (x, y))
        return

    # Sort by fastest time
    sorted_lb = sorted(leaderboard.items(), key=lambda x: x[1])

    # Draw the title

    offset_y = y + 100

    # Draw top entries
    for i, (name, time_) in enumerate(sorted_lb[:max_entries], start=1):
        entry_text = f"{i}. {name} - {time_:.2f}s"
        entry_surface = font.render(entry_text, True, (20, 20, 20))
        screen.blit(entry_surface, (x, offset_y))
        offset_y += 50


decorated_on = True

show_popup_info = False

show_popup_option = False

in_game = False

show_popup_name_menu = False

player_name = ""
number_input_active = False
name_input_active = False

selection_box = False
attempt = []
user_text = ""

options = ["EASY", "MEDIUM", "HARD"]
selected_index = 0

# Position of the selector bar
selector_x = 700
selector_y = 620
# Size of each option box
option_width = 300
option_height = 55

# Animation
slide_pos = selector_x
slide_speed = 12

# Whether the text box is active

cursor_visible = True
cursor_timer = 0

x1 = "EASY"


tutorial_screen =False
ai_gameMode = False
tutorial_screen_end = False

pygame.display.set_caption("Guess Number Game")
clock = pygame.time.Clock()

# =============================
# Load assets
# =============================
bg_img = pygame.image.load(resource_path("assest/pixel_land.png")).convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

pixel_sky_bg = pygame.image.load(resource_path("assest/pixel_sky.png")).convert()
pixel_sky_bg = pygame.transform.scale(pixel_sky_bg, (1920, 1080))

paper_img = pygame.image.load(resource_path("assest/pixel_paper.png")).convert_alpha()
paper_img = pygame.transform.scale(paper_img, (700, 600))

liquid_block = pygame.image.load(resource_path("assest/game menu/name menu/block.png")).convert_alpha()
liquid_block = pygame.transform.scale(liquid_block, (1900, 1500))

liquid_block_rect = pygame.Rect((25, -10), (1900, 1300))

enter_your_name_text = pygame.image.load(resource_path("assest/game menu/name menu/enter your name.png")).convert_alpha()
#enter_your_name_text = pygame.transform.scale(enter_your_name_text,(800,400))

name_text_box = pygame.image.load(resource_path("assest/game menu/name menu/name text box.png")).convert_alpha()

cloud_img = pygame.image.load(resource_path("assest/cloud.png")).convert_alpha()

blank_paper = pygame.image.load(resource_path("assest/pixel_paper.png")).convert_alpha()

game_title = pygame.image.load(resource_path("assest/main menu/game title text.png")).convert_alpha()

flip_blank_paper = pygame.image.load(resource_path("assest/pixel_paper fliped.png"))

option_title = pygame.image.load(resource_path("assest/option menu/option white.png")).convert_alpha()

music_text = pygame.image.load(resource_path("assest/option menu/music.png"))

sfx_text = pygame.image.load(resource_path("assest/option menu/sfx.png"))

ai_mode_text = pygame.image.load(resource_path("assest/option menu/ai mOde.png"))

shaded_text_box = pygame.image.load(resource_path("assest/game menu/name menu/shaded text_box.png")).convert_alpha()

difficulty_text = pygame.image.load(resource_path("assest/game menu/name menu/difficulty.png"))

difficulty_selection = pygame.image.load(resource_path("assest/game menu/name menu/shape 31.png"))

difficulty_selection_box = pygame.image.load(resource_path("assest/game menu/name menu/difficulty_selection_box.png")).convert_alpha()

normal_default = pygame.image.load(
    resource_path("assest/game menu/name menu/NORMAL.png")).convert_alpha()

sep_line = pygame.image.load(resource_path("assest/game menu/name menu/sep_line.png"))

easy_text = pygame.image.load(
    resource_path("assest/game menu/name menu/EASY .png")).convert_alpha()

hard_text = pygame.image.load(
    resource_path("assest/game menu/name menu/HARD .png")).convert_alpha()

start_button = pygame.image.load(
    resource_path("assest/game menu/name menu/Start_Button.png")).convert_alpha()
hovered_start_button = pygame.image.load(
    "assest/game menu/name menu/hovered_start.png").convert_alpha()
hovered_start_button1 = pygame.image.load(
    "assest/game menu/name menu/hovered_start.png").convert_alpha()
hovered_start_button1.set_alpha(128)
hovered_start_button_rect = hovered_start_button.get_rect(topleft=(800, 700))

reset_button_rect = hovered_start_button.get_rect(topleft=(770, 600))

hightlighted_start_button = pygame.image.load(
    "assest/game menu/name menu/highlighted start_button.png")

blue_back_button = pygame.image.load(
    "assest/button/normal/blue_normal_back.png")

blue_back_button = pygame.transform.scale(blue_back_button, (80, 60))

blue_highlighted_back_button = pygame.image.load(
    "assest/button/highlighted/blue_highlighted back.png")

blue_highlighted_back_button = pygame.transform.scale(blue_highlighted_back_button, (80, 60))

leaderboard_text_title = pygame.image.load(
    "assest/game menu/in_game/leaderboard_title.png")
information_text_title = pygame.image.load(
    "assest/game menu/in_game/info_title.png")
attempt_text_x = pygame.image.load("assest/game menu/in_game/attempt.png")
hint_text = pygame.image.load("assest/game menu/in_game/hint_ .png")
guess_text_title = pygame.image.load("assest/game menu/in_game/guess_title.png")
player_text = pygame.image.load("assest/game menu/in_game/player.png")
time_text = pygame.image.load("assest/game menu/in_game/time.png")

normal_reset_button = pygame.image.load("assest/button/normal/reset_button.png")
highlighted_reset_button = pygame.image.load(
    "assest/button/highlighted/highlighted reset button.png")
dark_reset_button = pygame.image.load(
    "assest/button/darker/dark reset button.png")

green_highlight = pygame.image.load(
    "assest/game menu/in_game/green highlight.png").convert_alpha()
yellow_highlight = pygame.image.load(
    "assest/game menu/in_game/yellow highlight.png").convert_alpha()
red_highlight = pygame.image.load(
    "assest/game menu/in_game/red highlight.png").convert_alpha()
green_highlight.set_alpha(50)
red_highlight.set_alpha(50)
yellow_highlight.set_alpha(50)

WIN_CHANNEL = pygame.mixer.Channel(7)
WIN_CHANNEL.set_volume(1.0)


#tutorial_images = [pygame.transform.scale(pygame.image.load("assest/tutorial/tutorial{i}.png").convert_alpha(), (WIDTH, HEIGHT)) for i in range(1, 10)]


# ==========================
# classes
# ===========================
class PixelSlider:
    def __init__(self, x, y, width, min_val=0, max_val=100, start_val=50, sound=None):
        self.x = x
        self.y = y
        self.width = width

        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val

        # Chunky pixel‑style sizes
        self.height = 28
        self.handle_w = 28
        self.handle_h = 39

        self.handle_x = self.value_to_pos(start_val)

        self.dragging = False
        self.hovered = False
        self.sound = sound

    # Convert value → pixel position
    def value_to_pos(self, value):
        return self.x + (value - self.min_val) / (self.max_val - self.min_val) * self.width

    # Convert pixel position → value
    def pos_to_value(self, pos):
        return int(self.min_val + (pos - self.x) / self.width * (self.max_val - self.min_val))

    def update(self, events):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Handle rectangle
        hx = int(self.handle_x - self.handle_w // 2)
        hy = int(self.y + self.height // 2 - self.handle_h // 2)
        handle_rect = pygame.Rect(hx, hy, self.handle_w, self.handle_h)

        hovering_now = handle_rect.collidepoint(mouse_x, mouse_y)

        # Hover sound
        if hovering_now and not self.hovered and self.sound:
            self.sound.play()
        self.hovered = hovering_now

        # Drag logic
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and hovering_now:
                self.dragging = True
                if self.sound:
                    self.sound.play()

            if event.type == pygame.MOUSEBUTTONUP and self.dragging:
                self.dragging = False
                if self.sound:
                    self.sound.play()

        # Update handle position while dragging
        if self.dragging:
            self.handle_x = max(self.x, min(mouse_x, self.x + self.width))

            # Convert to raw value
            raw_value = self.pos_to_value(self.handle_x)

            # Snap to steps
            step = 10  # snap every 5 units
            self.value = round(raw_value / step) * step

            # Recalculate handle position after snapping
            self.handle_x = self.value_to_pos(self.value)

        return self.value

    def draw(self, screen):
        border_color = (0, 0, 0)
        bar_bg = (60, 60, 60)  # empty bar color
        start_color = (255, 230, 80)  # yellow
        end_color = (255, 120, 0)  # orange

        # --- EMPTY BAR BACKGROUND ---
        pygame.draw.rect(
            screen,
            bar_bg,
            (self.x, self.y, self.width, self.height),
            border_radius=10
        )

        # --- BAR BORDER ---
        pygame.draw.rect(
            screen,
            border_color,
            (self.x, self.y, self.width, self.height),
            3,
            border_radius=10
        )

        # --- FILLED GRADIENT PART ONLY ---
        # --- FILLED GRADIENT PART ONLY (CLIPPED TO ROUNDED BAR) ---
        fill_width = max(0, min(self.width, int(self.handle_x - self.x)))

        if fill_width > 0:
            # Create a surface for the filled part
            gradient_surf = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)

            # Draw gradient onto that surface
            for i in range(fill_width):
                t = i / fill_width
                r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * t)

                pygame.draw.line(
                    gradient_surf,
                    (r, g, b, 255),
                    (i, 0),
                    (i, self.height)
                )

            # Create a mask with rounded corners
            mask = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, fill_width, self.height), border_radius=10)

            # Apply mask (clip gradient to rounded shape)
            gradient_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            # Draw clipped gradient onto screen
            screen.blit(gradient_surf, (self.x, self.y))

            # Border for filled part
            pygame.draw.rect(
                screen,
                border_color,
                (self.x, self.y, fill_width, self.height),
                3,
                border_radius=10
            )

        # --- HANDLE POSITION ---
        hx = int(self.handle_x - self.handle_w // 2)
        hy = int(self.y + self.height // 2 - self.handle_h // 2)

        # --- HANDLE ---
        pygame.draw.rect(
            screen,
            (255, 200, 120),
            (hx, hy, self.handle_w, self.handle_h),
            border_radius=6
        )

        pygame.draw.rect(
            screen,
            border_color,
            (hx, hy, self.handle_w, self.handle_h),
            4,
            border_radius=6
        )

        # --- HOVER HIGHLIGHT ---
        if self.hovered:
            pygame.draw.rect(
                screen,
                (255, 240, 180),
                (hx, hy, self.handle_w, self.handle_h),
                3,
                border_radius=6
            )


class PixelSwitchSlider:
    def __init__(self, x, y, width=120, height=28, start_state=False, sound=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.state = start_state  # False = OFF, True = ON
        self.handle_w = 28
        self.handle_h = 39

        self.sound = sound

        # Animation
        self.handle_x = self.get_target_x()

        self.hovered = False

    def get_target_x(self):
        if self.state:
            return self.x + self.width - self.handle_w
        else:
            return self.x

    def update(self, events):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        switch_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        hovering_now = switch_rect.collidepoint(mouse_x, mouse_y)
        self.hovered = hovering_now

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and hovering_now:
                self.state = not self.state
                if self.sound:
                    self.sound.play()

        # Smooth slide animation
        target = self.get_target_x()
        self.handle_x += (target - self.handle_x) * 0.25

        return self.state

    def draw(self, screen):
        border_color = (0, 0, 0)

        # Colors
        bar_bg = (60, 60, 60)
        start_color = (255, 230, 80)
        end_color = (255, 120, 0)

        # --- EMPTY BAR ---
        pygame.draw.rect(
            screen,
            bar_bg,
            (self.x, self.y, self.width, self.height),
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            border_color,
            (self.x, self.y, self.width, self.height),
            3,
            border_radius=10
        )

        # --- FILLED GRADIENT ONLY IF ON ---
        if self.state:
            gradient_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

            for i in range(self.width):
                t = i / self.width
                r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * t)

                pygame.draw.line(
                    gradient_surf,
                    (r, g, b, 255),
                    (i, 0),
                    (i, self.height)
                )

            # Clip to rounded bar
            mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, self.width, self.height), border_radius=10)
            gradient_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            screen.blit(gradient_surf, (self.x, self.y))

            pygame.draw.rect(
                screen,
                border_color,
                (self.x, self.y, self.width, self.height),
                3,
                border_radius=10
            )

        # --- HANDLE ---
        hx = int(self.handle_x)
        hy = int(self.y + self.height // 2 - self.handle_h // 2)

        pygame.draw.rect(
            screen,
            (255, 200, 120),
            (hx, hy, self.handle_w, self.handle_h),
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            border_color,
            (hx, hy, self.handle_w, self.handle_h),
            4,
            border_radius=6
        )

        if self.hovered:
            pygame.draw.rect(
                screen,
                (255, 240, 180),
                (hx, hy, self.handle_w, self.handle_h),
                3,
                border_radius=6
            )


class TutorialGestureController:
    def __init__(self, hold_time=0.8, cooldown=0.7, max_hands=1):
        self.HOLD_TIME = hold_time
        self.COOLDOWN = cooldown

        self.last_gesture = None
        self.gesture_start_time = None
        self.last_action_time = 0

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0)

    def get_gesture(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        gesture = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

            lm = hand_landmarks.landmark

            # 1. FIST DETECTION
            # Check if tips of Index(8), Middle(12), Ring(16), and Pinky(20)
            # are below their MCP joints (5, 9, 13, 17)
            is_fist = (lm[8].y > lm[6].y and
                       lm[12].y > lm[10].y and
                       lm[16].y > lm[14].y and
                       lm[20].y > lm[18].y)

            if is_fist:
                gesture = "FIST"
            else:
                # 2. THUMB GESTURE (Your existing logic)
                # dx = Tip - MCP
                dx = lm[4].x - lm[2].x
                if dx > 0.05:  # increased threshold slightly for stability
                    gesture = "THUMB_RIGHT"
                elif dx < -0.05:
                    gesture = "THUMB_LEFT"

        # Debug overlay
        cv2.putText(frame, f"Gesture: {gesture}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Gesture Feed", frame)
        cv2.waitKey(1)

        return gesture, frame

    def handle_tutorial_gesture(self, gesture, tutorial_index, max_index):
        """
        Returns: (new_tutorial_index, should_close_tutorial)
        """
        now = time.time()
        should_close = False

        if gesture is None:
            return tutorial_index, False

        # Reset timer if gesture changed
        if gesture != self.last_gesture:
            self.last_gesture = gesture
            self.gesture_start_time = now
            return tutorial_index, False

        # Check if held long enough
        if now - self.gesture_start_time >= self.HOLD_TIME:
            # Check cooldown
            if now - self.last_action_time < self.COOLDOWN:
                return tutorial_index, False

            # Perform Action
            if gesture == "FIST":
                should_close = True
            elif gesture == "THUMB_RIGHT" and tutorial_index < max_index:
                tutorial_index += 1
            elif gesture == "THUMB_LEFT" and tutorial_index > 0:
                tutorial_index -= 1

            self.last_action_time = now
            self.last_gesture = None
            self.gesture_start_time = None

        return tutorial_index, should_close

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()



# ===========================
# set dimentions
# ===========================
paper_pmin = (600, 250)



paper_pmax = (1300, 850)
slider = PixelSlider(750, 475, 400, min_val=0, max_val=100, start_val=20, sound=None)
slider_sfx = PixelSlider(750, 600, 400, min_val=0, max_val=50, start_val=10, sound=None)

ai_switch = PixelSwitchSlider(735, 675, 75, start_state=False, sound=None)

# ==================================================================
# load sound effects
# ==================================================================

pygame.mixer.pre_init(44100, -16, 2, 128)
pygame.init()

intro_frames = load_animation("assest/transition/Comp 1", (1920, 1080))
print("FIRST FRAME:", intro_frames[0])
intro_index = 0
intro_speed = 0.4  # lower = slower animation
intro_timer = 0
intro_playing = False

leaderboard = load_leaderboard()

click_sound = pygame.mixer.Sound("assest/sound/button.wav")
click_sound.set_volume(slider_sfx.value / 100)

main_menu_theme = pygame.mixer.music.load(
    "assest/sound/main_music_theme (Cover).mp3")
pygame.mixer.music.set_volume(slider.value / 100)

win_audio = pygame.mixer.Sound("assest/sound/win.wav")
win_audio.set_volume(1)

pygame.mixer.music.play(-1)
paper_x, paper_y = paper_pmin
paper_w = paper_pmax[0] - paper_pmin[0]  # 1300 - 600 = 700
paper_h = paper_pmax[1] - paper_pmin[1]  # 850 - 250 = 600

paper_rect = pygame.Rect(paper_x, paper_y, paper_w, paper_h)

input_box = pygame.Rect(650, 400, 580, 55)

difficulty_selection_box_rect = pygame.Rect(698, 582, 515, 45)

difficulty_selection_box_liq_rect = pygame.Rect(700, 575, 515, 250)

easy_hover_difficulty_rect = pygame.Rect(700, 628, 515, 50)
normal_hover_difficulty_rect = pygame.Rect(700, 682, 515, 70)

hard_hover_difficulty_rect = pygame.Rect(700, 757, 515, 60)

print(paper_rect.center)

# ================================================================
# play_button
# =================================================================
play_button = pygame.image.load("assest/button/normal/normal play.png")
play_button = pygame.transform.scale(play_button, (300, 80))

play_button_hover = pygame.image.load(
    "assest/button/highlighted/highlighted play.png")
play_button_hover = pygame.transform.scale(play_button_hover, (300, 80))

play_button_pressed = pygame.image.load("assest/button/darker/dark play.png")
play_button_pressed = pygame.transform.scale(play_button_pressed, (300, 80))

# ==================================================================
# online_button
# ==================================================================

online_button = pygame.image.load("assest/button/normal/normal online.png")
online_button = pygame.transform.scale(online_button, (300, 155))

online_button_hover = pygame.image.load(
    "assest/button/highlighted/highlighted online.png")
online_button_hover = pygame.transform.scale(online_button_hover, (300, 155))

online_button_pressed = pygame.image.load(
    "assest/button/darker/dark online.png")
online_button_pressed = pygame.transform.scale(online_button_pressed, (300, 155))

# ==================================================================
# option button
# ==================================================================

option_button = pygame.image.load("assest/button/normal/normal option.png")
option_button = pygame.transform.scale(option_button, (300, 80))

option_button_hover = pygame.image.load(
    "assest/button/highlighted/highlighted option.png")
option_button_hover = pygame.transform.scale(option_button_hover, (300, 80))

option_button_pressed = pygame.image.load(
    "assest/button/darker/dark option.png")
option_button_pressed = pygame.transform.scale(option_button_pressed, (300, 80))

# ==================================================================
# exit button
# ==================================================================

exit_button = pygame.image.load("assest/button/normal/normal exit.png")
exit_button = pygame.transform.scale(exit_button, (50, 55))

exit_button_hover = pygame.image.load(
    "assest/button/highlighted/highlighted exit.png")
exit_button_hover = pygame.transform.scale(exit_button_hover, (50, 55))

exit_button_pressed = pygame.image.load("assest/button/darker/dark exit.png")
exit_button_pressed = pygame.transform.scale(exit_button_pressed, (50, 55))

# ==================================================================
# info button
# ==================================================================

info_button = pygame.image.load("assest/button/normal/normal info.png")
info_button = pygame.transform.scale(info_button, (50, 55))

info_button_hover = pygame.image.load(
    "assest/button/highlighted/highlighted info.png")
info_button_hover = pygame.transform.scale(info_button_hover, (50, 55))

info_button_pressed = pygame.image.load("assest/button/darker/dark info.png")
info_button_pressed = pygame.transform.scale(info_button_pressed, (50, 55))

# ==================================================================
# info back_button
# ==================================================================

back_button = pygame.image.load("assest/button/normal/normal back.png")
back_button = pygame.transform.scale(back_button, (80, 60))

back_button_hover = pygame.image.load(
    "assest/button/highlighted/highlighted back.png")
back_button_hover = pygame.transform.scale(back_button_hover, (80, 60))

back_button_pressed = pygame.image.load("assest/button/darker/dark back.png")
back_button_pressed = pygame.transform.scale(back_button_pressed, (80, 60))

# ================================================================
# button_rect
# ==================================================================

play_button_rect = play_button.get_rect(center=(paper_rect.centerx, paper_rect.centery - 140))

online_button_rect = online_button.get_rect(center=(paper_rect.centerx, paper_rect.centery - 20))

option_button_rect = option_button.get_rect(center=(paper_rect.centerx, paper_rect.centery + 100))

exit_button_rect = exit_button.get_rect(center=(paper_rect.centerx - 220, paper_rect.centery + 200))

info_button_rect = info_button.get_rect(center=(paper_rect.centerx + 220, paper_rect.centery + 205))

back_button_rect = back_button.get_rect(center=(paper_rect.centerx - 220, paper_rect.centery - 200))

back_button_rect_option = back_button.get_rect(center=(623, 345))
blue_back_button_rect = blue_back_button.get_rect(center=(171, 115))

# =============================
# Font
# =============================
title_font = pygame.font.Font("assest/PixelGameFont.ttf", 80)

info_font = pygame.font.Font("assest/LowresPixel-Regular.otf", 18)

info_title_font = pygame.font.Font("assest/PixelGameFont.ttf", 36)

info_seg_font = pygame.font.Font("assest/PixelGameFont.ttf", 20)

info_title_font.set_bold(True)
info_seg_font.set_bold(True)

win_sound_played = False

# =============================
# Cloud setup
# =============================
clouds = []
for i in range(5):
    sx = random.randint(0, 2000)
    sy = random.randint(120, 300)
    w = random.randint(350, 450)
    h = int(w * 0.5)
    speed = random.uniform(0.1, 0.3)
    phase = random.random() * math.pi
    cloud_surface = pygame.transform.scale(cloud_img, (w, h))
    clouds.append([sx, sy, w, h, speed, phase, cloud_surface])

# =============================
# Paper bounds
# =============================
paper_rect = pygame.Rect(600, 250, 700, 600)

blank_paper_rect = pygame.Rect(600, 250, 700, 600)

flip_blank_paper_rect = pygame.Rect(600, 250, 700, 600)
t = True
random.seed(random.randint(0, 100000000000000))
sec_num_easy = random.randint(1, 50)
sec_num_normal = random.randint(1, 100)
sec_num_hard = random.randint(1, 500)
back_col = ""
hint = ""
secret = sec_num_easy

# =============================
# Main loop
# =============================
click_used = False

frame = 0
running = True
while running:
    frame += 1
    # Read a frame from webcam




    # Optional: print for debug

    cursor_timer += clock.get_time()
    if cursor_timer >= 500:
        cursor_visible = not cursor_visible
        cursor_timer = 0



    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if in_game:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos) and not guess_chance:
                    number_input_active = True
                else:
                    number_input_active = False

            if event.type == pygame.KEYDOWN and number_input_active:
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN and user_text != "":
                    if user_text.isdigit():
                        guess = int(user_text)

                        # START TIMER ON FIRST GUESS
                        if not timer_started and not guess_chance:
                            start_time = pygame.time.get_ticks()
                            timer_started = True

                        # =========================
                        # EASY MODE LOGIC
                        # =========================

                        if x1 == "EASY" and guess == secret:
                            if not win_sound_played:
                                pygame.mixer.music.set_volume(slider.value / 100 * 0.25)  # lower music
                                WIN_CHANNEL.play(win_audio)
                                win_sound_played = True

                            timer_started = False

                            guess_chance = True
                            number_input_active = False
                            final_time = round(elapsed_time, 2)
                            back_col = "green"

                            if player_name not in leaderboard or final_time < leaderboard[player_name]:
                                leaderboard[player_name] = final_time
                                save_leaderboard(leaderboard)

                            hint = "YOU GOT IT!"
                            print_leaderboard()  # 👈 PRINT HERE


                        elif x1 == "EASY" and guess < secret:
                            hint = "TRY HIGHER"

                        elif x1 == "EASY" and guess > secret:
                            hint = "TRY LOWER"

                        elif x1 == "NORMAL" and guess == secret:
                            if not win_sound_played:
                                pygame.mixer.music.set_volume(slider.value / 100 * 0.25)  # lower music
                                WIN_CHANNEL.play(win_audio)
                                win_sound_played = True
                            guess_chance = True
                            timer_started = False
                            number_input_active = False
                            final_time = round(elapsed_time, 2)

                            if player_name not in leaderboard or final_time < leaderboard[player_name]:
                                leaderboard[player_name] = final_time
                                save_leaderboard(leaderboard)

                            hint = "YOU GOT IT!"

                            print_leaderboard()  # 👈 PRINT HERE

                        elif x1 == "NORMAL" and guess < secret:
                            hint = "TRY HIGHER"

                        elif x1 == "NORMAL" and guess > secret:
                            hint = "TRY LOWER"


                        elif x1 == "HARD" and guess == secret:
                            if not win_sound_played:
                                pygame.mixer.music.set_volume(slider.value / 100 * 0.25)  # lower music
                                WIN_CHANNEL.play(win_audio)
                                win_sound_played = True
                            guess_chance = True
                            timer_started = False
                            number_input_active = False
                            final_time = round(elapsed_time, 2)

                            if player_name not in leaderboard or final_time < leaderboard[player_name]:
                                leaderboard[player_name] = final_time
                                save_leaderboard(leaderboard)

                            hint = "YOU GOT IT!"

                            print_leaderboard()  # 👈 PRINT HERE

                        elif x1 == "HARD" and guess < secret:
                            hint = "TRY HIGHER"

                        elif x1 == "HARD" and guess > secret:

                            hint = "TRY LOWER"
                        different = abs(guess - secret)

                        if different == 0:
                            back_col = "green"

                        elif different <= 5:
                            back_col = "yellow"
                        else:
                            back_col = "red"

                        attempt.append(guess)

                        # clear input no matter what
                    user_text = ""
                elif event.unicode.isdigit():
                    user_text += event.unicode

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Toggle fullscreen/windowed
                decorated_on = not decorated_on
                if decorated_on:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                show_popup_small_option = not show_popup_small_option

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if info_button_rect.collidepoint(event.pos):
                show_popup = True  # toggle popup on click
            if exit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if info_button_rect.collidepoint(event.pos):
                show_popup_info = True
            if exit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

        if show_popup_name_menu:
            # Click to activate

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if input_box.collidepoint(mx, my):
                    screen.blit(shaded_text_box, (0, 60))
                    name_input_active = True

                else:
                    screen.blit(name_text_box, (0, 60))
                    name_input_active = False

            # Keyboard input
            if event.type == pygame.KEYDOWN and name_input_active:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    print("Name entered:", player_name)
                    name_input_active = False
                else:
                    if len(player_name) < 16:
                        player_name += event.unicode


        screen.blit(name_text_box, (0, 60))

    # ==================================================================

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    temp_surface = pygame.Surface((1920, 1080), pygame.SRCALPHA)

    screen.blit(bg_img, (0, 0))
    # ==================================================================
    # Animate clouds
    # ==================================================================
    for i, cloud in enumerate(clouds):
        x, y_base, w, h, speed, phase, cloud_surface = cloud
        x += speed
        y = y_base + 15 * math.sin(frame * 0.01 + phase)
        if x > WIDTH:
            x = -w
            y_base = random.randint(80, 250)
            clouds[i][1] = y_base
        clouds[i][0] = x
        screen.blit(cloud_surface, (x, y))

    # =====================================
    # FULL FLY ANIMATION (BLOCKS ALL UI)
    # =====================================
    if intro_playing and intro_frames:
        intro_timer += intro_speed

        if intro_timer >= 1:
            intro_timer = 0

            if intro_index < len(intro_frames) - 1:
                intro_index += 1
            else:
                intro_playing = False
                in_transition = False
                show_popup_name_menu = True  # ✅ NEXT STATE
        # stop safely

        frames = intro_frames[intro_index]
        x = WIDTH // 2 - frames.get_width() // 2
        y = HEIGHT // 2 - frames.get_height() // 2

        screen.blit(frames, (x, y))
        pygame.display.flip()
        clock.tick(60)
        continue

    # ==================================================================
    # infromaion menu display
    # ==================================================================
    if show_popup_info:
        # Draw blank popup paper

        popup_surface = pygame.transform.scale(paper_img, (700, 600))
        screen.blit(popup_surface, paper_rect.topleft)

        # ==================================================================
        # infromation_text
        # ==================================================================

        info_title = info_title_font.render("GUESS THE NUMBER GAME", True, (255, 255, 255))
        screen.blit(info_title, (paper_x + 110, paper_y + 140))
        info_title = info_title_font.render("GUESS THE NUMBER GAME", True, (20, 20, 20, 70))
        screen.blit(info_title, (paper_x + 107, paper_y + 138))

        info_l1 = info_font.render("this is a simple yet fun game built in python.", True, (20, 20, 20))

        screen.blit(info_l1, (paper_x + 112, paper_y + 190))

        info_l2 = info_font.render("the goal is straightforward: the computer picks a", True, (20, 20, 20))
        screen.blit(info_l2, (paper_x + 112, paper_y + 220))

        info_l3 = info_font.render("random number, and you must guess it correctly.", True, (20, 20, 20))
        screen.blit(info_l3, (paper_x + 112, paper_y + 250))

        info_l4 = info_font.render("each attempt brings you closer to discovering the", True, (20, 20, 20))
        screen.blit(info_l4, (paper_x + 112, paper_y + 280))

        info_l5 = info_font.render("hidden number, testing both your intuition and logic.", True, (20, 20, 20))
        screen.blit(info_l5, (paper_x + 112, paper_y + 310))

        info_l6 = info_font.render("the game was designed to demonstrate how python", True, (20, 20, 20))
        screen.blit(info_l6, (paper_x + 112, paper_y + 350))

        info_l7 = info_font.render("can be used for interactive projects, combining", True, (20, 20, 20))
        screen.blit(info_l7, (paper_x + 112, paper_y + 380))

        info_l8 = info_font.render("graphics, user input, and game logic in one place.", True, (20, 20, 20))
        screen.blit(info_l8, (paper_x + 112, paper_y + 410))

        creat_name = info_seg_font.render("CREATED BY : HAMZA HAIDER ", True, (255, 255, 255, 40))
        screen.blit(creat_name, (paper_x + 278, paper_y + 471))

        std_num = info_seg_font.render("STUDENT_ID :202411751 ", True, (255, 255, 255, 40))
        screen.blit(std_num, (paper_x + 278, paper_y + 501))

        creat_name = info_seg_font.render("CREATED BY : HAMZA HAIDER ", True, (20, 20, 20))
        screen.blit(creat_name, (paper_x + 275, paper_y + 470))

        std_num = info_seg_font.render("STUDENT_ID :202411751 ", True, (20, 20, 20))
        screen.blit(std_num, (paper_x + 275, paper_y + 500))

        # ==================================================================
        # back_Button_func
        # ==================================================================

        if back_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                screen.blit(back_button_pressed, back_button_rect.topleft)
                pygame.time.delay(75)
                click_sound.play()
                show_popup_info = False
                show_popup_option = False
            else:
                screen.blit(back_button_hover, back_button_rect.topleft)
        else:
            screen.blit(back_button, back_button_rect.topleft)

        if (back_button_rect.collidepoint(mouse_pos)):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    # ===============================================================
    # option menu display
    # ===============================================================

    elif show_popup_option:

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        screen.blit(option_title, (610, 120))

        fliped_paper_surfec = pygame.transform.scale(flip_blank_paper, (1350, 700))
        screen.blit(fliped_paper_surfec, (300, 200))

        music_text_sur = pygame.transform.scale(music_text, (180, 80))
        screen.blit(music_text_sur, (560, 450))

        sfx_text_sur = pygame.transform.scale(sfx_text, (140, 70))
        screen.blit(sfx_text_sur, (575, 575))

        ai_mode_text_sur = pygame.transform.scale(ai_mode_text, (170, 70))
        screen.blit(ai_mode_text_sur, (565, 650))
        # ✅ Update slider
        slider.update(events)
        slider.draw(screen)
        volume = slider.value / 100
        pygame.mixer.music.set_volume(volume)

        slider_sfx.update(events)
        slider_sfx.draw(screen)
        volume = slider_sfx.value / 100

        ai_switch.update(events)
        ai_switch.draw(screen)
        click_sound.set_volume(volume)

        # ✅ Button logic
        if back_button_rect_option.collidepoint(mouse_pos):
            if mouse_pressed:
                click_sound.play()
                show_popup_info = False
                show_popup_option = False
                menu = False
            else:
                screen.blit(back_button_hover, (600, 325))
        else:
            screen.blit(back_button, (600, 325))

        pygame.display.update()


    # ===================================================================
    # SMALL OPTION MENU
    # ===================================================================

    elif show_popup_small_option:

        screen.blit(pixel_sky_bg, (0, 0))

        for i, cloud in enumerate(clouds):
            x, y_base, w, h, speed, phase, cloud_surface = cloud
            x += speed
            y = y_base + 15 * math.sin(frame * 0.01 + phase)
            if x > WIDTH:
                x = -w
                y_base = random.randint(80, 250)
                clouds[i][1] = y_base
            clouds[i][0] = x
            screen.blit(cloud_surface, (x, y))
        screen.blit(option_title, (610, 120))

        fliped_paper_surfec = pygame.transform.scale(flip_blank_paper, (1350, 700))
        screen.blit(fliped_paper_surfec, (300, 200))

        music_text_sur = pygame.transform.scale(music_text, (180, 80))
        screen.blit(music_text_sur, (560, 450))

        sfx_text_sur = pygame.transform.scale(sfx_text, (140, 70))
        screen.blit(sfx_text_sur, (575, 575))

        ai_mode_text_sur = pygame.transform.scale(ai_mode_text, (170, 70))
        screen.blit(ai_mode_text_sur, (565, 650))
        #Update slider
        slider.update(events)
        slider.draw(screen)
        volume = slider.value / 100
        pygame.mixer.music.set_volume(volume)

        slider_sfx.update(events)
        slider_sfx.draw(screen)
        volume = slider_sfx.value / 100

        ai_switch.update(events)
        ai_switch.draw(screen)
        click_sound.set_volume(volume)

        if blue_back_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                click_sound.play()
                show_popup_info = False
                show_popup_option = False
                menu = False
                in_game = False
                show_popup_name_menu = False
                show_popup_small_option = False

            else:
                screen.blit(blue_highlighted_back_button, (150, 100))
        else:
            screen.blit(blue_back_button, (150, 100))

        pygame.display.update()

    #===================================================================
    #game menu
    #===================================================================

    elif show_popup_name_menu:

        screen.blit(pixel_sky_bg, (0, 0))

        for i, cloud in enumerate(clouds):
            x, y_base, w, h, speed, phase, cloud_surface = cloud
            x += speed
            y = y_base + 15 * math.sin(frame * 0.01 + phase)
            if x > WIDTH:
                x = -w
                y_base = random.randint(80, 250)
                clouds[i][1] = y_base
            clouds[i][0] = x
            screen.blit(cloud_surface, (x, y))

            screen.blit(liquid_block, (25, -10))
            screen.blit(enter_your_name_text, (600, 300))
            screen.blit(difficulty_text, (780, 500))
            screen.blit(name_text_box, (0, 60))

            easy_text_f = info_title_font.render("EASY: GUESS A NUMBER FORM 1-50", True, (25, 25, 25))
            easy_text_fs = info_font.render("EASY: GUESS A NUMBER FORM 1-50", True, (25, 25, 25))
            normal_text_f = info_title_font.render("NORMAL: GUESS A NUMBER FORM 1-100", True, (25, 25, 25))
            normal_text_fs = info_font.render("NORMAL: GUESS A NUMBER FORM 1-100", True, (25, 25, 25))
            hard_text_fs = info_font.render("HARD: GUESS A NUMBER FORM 1-500", True, (25, 25, 25))
            hard_text_f = info_title_font.render("HARD: GUESS A NUMBER FORM 1-500", True, (25, 25, 25))

        if not selection_box:
            # screen.blit(hovered_start_button_rect,(800,700))
            if hovered_start_button_rect.collidepoint(mouse_pos):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if hovered_start_button_rect.collidepoint(event.pos):
                        click_sound.play()

                        # reset game state
                        in_game = True
                        show_popup_name_menu = False
                        show_popup_option = False
                        show_popup_small_option = False
                        guess_chance = False
                        back_col = ""
                        pygame.mixer.music.set_volume(slider.value / 100)
                        win_sound_played = False
                        hint = ""
                        attempt.clear()
                        elapsed_time = 0
                        timer_started = False
                        tutorial_screen = ai_switch.state

                else:
                    screen.blit(hovered_start_button, (800, 700))


            else:
                screen.blit(start_button, (805, 703))

        #pygame.draw.rect(screen,(0,0,0,60),blue_back_button_rect)
        target_y = selector_y + selected_index * 70
        slide_pos += (target_y - slide_pos) * 0.2
        if selection_box:
            screen.blit(difficulty_selection_box, (700, 578))

            difficulty_selection = pygame.transform.scale(difficulty_selection, (515, 58))
            screen.blit(difficulty_selection, (700, 574))

            screen.blit(sep_line, (700, 675))
            screen.blit(sep_line, (700, 750))
            # pygame.draw.rect(screen,(0,0,0,50),hard_hover_difficulty_rect)

            if easy_hover_difficulty_rect.collidepoint(mouse_pos):

                temp_surface.fill((0, 0, 0, 0))

                # Draw rectangle with RGBA (last value = opacity)
                pygame.draw.rect(temp_surface, (0, 71, 171, 25), (550, 425, 515, 50))

                # Blit onto main screen
                screen.blit(temp_surface, (150, 200))
                screen.blit(easy_text_fs, (900, 640))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if easy_hover_difficulty_rect.collidepoint(event.pos):
                        click_used = True
                        x1 = "EASY"
                        secret = sec_num_easy


            elif normal_hover_difficulty_rect.collidepoint(mouse_pos):

                temp_surface.fill((0, 0, 0, 0))
                pygame.draw.rect(temp_surface, (0, 71, 171, 25), (550, 480, 515, 75))
                screen.blit(temp_surface, (150, 200))
                screen.blit(normal_text_fs, (900, 700))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if normal_hover_difficulty_rect.collidepoint(event.pos):
                        click_used = True
                        x1 = "NORMAL"
                        secret = sec_num_normal

            elif hard_hover_difficulty_rect.collidepoint(mouse_pos):

                temp_surface.fill((0, 0, 0, 0))

                pygame.draw.rect(temp_surface, (0, 71, 171, 25), (550, 560, 515, 63))
                screen.blit(temp_surface, (150, 200))
                screen.blit(hard_text_fs, (900, 777))
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hard_hover_difficulty_rect.collidepoint(event.pos):
                        click_used = True
                        x1 = "HARD"
                        secret = sec_num_hard
            #pygame.draw.rect(screen, (0, 71, 171, 128), blue_highlighted_back_button)

            screen.blit(easy_text, (725, 640))
            screen.blit(normal_default, (715, 700))
            screen.blit(hard_text, (725, 775))

        screen.blit(difficulty_selection, (700, 575))
        if x1 == "NORMAL":

            screen.blit(normal_default, (730, 590))
            screen.blit(normal_text_f, (625, 850))
        elif x1 == "EASY":
            screen.blit(easy_text, (730, 590))
            screen.blit(easy_text_f, (625, 850))
        elif x1 == "HARD":
            screen.blit(hard_text, (730, 590))
            screen.blit(hard_text_f, (625, 850))

        if difficulty_selection_box_rect.collidepoint(mouse_pos):

            if mouse_pressed:
                selection_box = True


        elif difficulty_selection_box_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                selection_box = False
        elif liquid_block_rect.collidepoint(mouse_pos):

            if mouse_pressed:
                selection_box = False

        #============================
        # DRAW INPUT TEXT
        text_surface = info_title_font.render(player_name, True, (50, 50, 50))
        screen.blit(text_surface, (input_box.x + 20, input_box.y + 15))

        # Draw blinking cursor
        if name_input_active and cursor_visible:
            cursor_x = input_box.x + 20 + text_surface.get_width() + 3
            cursor_y = input_box.y + 7
            cursor_h = text_surface.get_height()
            pygame.draw.rect(screen, (100, 100, 100), (cursor_x, cursor_y, 4, cursor_h))

        if ((input_box.collidepoint(mouse_pos)) or hovered_start_button_rect.collidepoint(mouse_pos)) or (
                difficulty_selection_box_rect.collidepoint(mouse_pos) or blue_back_button_rect.collidepoint(mouse_pos)
                or hovered_start_button_rect.collidepoint(mouse_pos) and not selection_box) or (

                difficulty_selection_box_rect.collidepoint(mouse_pos) or easy_hover_difficulty_rect.collidepoint(
                mouse_pos) or normal_hover_difficulty_rect.collidepoint(
                 mouse_pos) or hard_hover_difficulty_rect.collidepoint(mouse_pos)) and selection_box:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)



    elif tutorial_screen:

        screen.blit(pixel_sky_bg, (0, 0))




    elif in_game and not ai_switch.state:

        screen.blit(pixel_sky_bg, (0, 0))

        for i, cloud in enumerate(clouds):
            x, y_base, w, h, speed, phase, cloud_surface = cloud
            x += speed
            y = y_base + 15 * math.sin(frame * 0.01 + phase)
            if x > WIDTH:
                x = -w
                y_base = random.randint(80, 250)
                clouds[i][1] = y_base
            clouds[i][0] = x

            screen.blit(cloud_surface, (x, y))

            green_highlight = pygame.transform.scale(green_highlight, (1000, 705))
            yellow_highlight = pygame.transform.scale(yellow_highlight, (1000, 705))


            red_highlight = pygame.transform.scale(red_highlight, (1000, 705))

            if back_col == "green":

                screen.blit(green_highlight, (400, 180))
                green_text_number = info_title_font.render("green color means that your right", True, (0,0,0))
                screen.blit(green_text_number, (615, 700))
            elif back_col == "red":

                screen.blit(red_highlight, (400, 180))

                red_text_number = info_title_font.render("red color means that you are far", True, (0,0,0))
                screen.blit(red_text_number, (625, 700))
            elif back_col == "yellow":

                screen.blit(yellow_highlight, (400, 180))

                text_number = info_title_font.render("yellow color means that you are close",True,(0,0,0))
                screen.blit(text_number,(615,700))

            liquid_block4 = pygame.transform.scale(liquid_block, (1500, 1000))
            screen.blit(liquid_block4, (185, 125))

            liquid_block1 = pygame.transform.scale(liquid_block, (800, 1000))
            screen.blit(liquid_block1, (-175, 125))

            liquid_block2 = pygame.transform.scale(liquid_block, (800, 1000))
            screen.blit(liquid_block2, (1300, 125))
            screen.blit(name_text_box, (0, 60))
        #if x1 == "EASY":
        if timer_started:
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000  # seconds

        cursor_timer += 1
        if cursor_timer % 30 == 0:
            cursor_visible = not cursor_visible

        # Draw
        txt_surface = info_title_font.render(user_text, True, (20, 20, 20))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 15))

        screen.blit(information_text_title, (125, 225))
        screen.blit(guess_text_title, (775, 225))

        screen.blit(leaderboard_text_title, (1440, 225))

        screen.blit(hint_text, (725, 475))

        screen.blit(player_text, (50, 325))

        player_name_text = info_title_font.render(player_name, True, (0, 0, 0))
        screen.blit(player_name_text, (50, 400))

        screen.blit(attempt_text_x, (50, 475))

        screen.blit(time_text, (50, 580))

        if reset_button_rect.collidepoint(mouse_pos) and not timer_started:
            if mouse_pressed:
                screen.blit(dark_reset_button, (775, 600))
                sec_num_easy = random.randint(1, 50)
                sec_num_normal = random.randint(1, 100)
                sec_num_hard = random.randint(1, 500)
                guess_chance = False
                hint = ""
                back_col = ""
                attempt.clear()

                pygame.mixer.music.set_volume(slider.value / 100)
                win_sound_played = False
                elapsed_time = 0
                click_sound.play()
                if x1 == "EASY":
                    secret = random.randint(1, 50)
                elif x1 == "NORMAL":
                    secret = random.randint(1, 100)
                elif x1 == "HARD":
                    secret = random.randint(1, 500)


            else:
                screen.blit(highlighted_reset_button, (775, 600))
        else:
            screen.blit(normal_reset_button, (775, 600))

        #pygame.draw.rect(screen,(0,0,0,60),reset_button_rect)

        # screen.blit(normal_reset_button,(775,600))

        # Draw input box border on screen (not liquid_block)

        timer_text_t = info_title_font.render(
            f"TIME: {elapsed_time:.1f}S", True, (255, 255, 255)
        )
        hint_txt = info_title_font.render(hint, True, (0, 0, 0))
        screen.blit(hint_txt, (900, 485))

        attempt_text = info_title_font.render(str(attempt[-4:]), True, (255, 255, 255))

        screen.blit(attempt_text, (50, 525))

        draw_leaderboard(screen, leaderboard, info_title_font, 1530, 250)

        draw_leaderboard_shadow(screen, leaderboard, info_title_font, 1525, 247)

        screen.blit(timer_text_t, (50, 650))  # change position if you want

        # Draw blinking cursor
        if number_input_active and cursor_visible:
            cursor_x = input_box.x + 5 + txt_surface.get_width() + 2
            cursor_y = input_box.y + 5
            cursor_h = txt_surface.get_height()
            pygame.draw.rect(screen, (100, 100, 100), (cursor_x, cursor_y, 4, cursor_h))

        if input_box.collidepoint(mouse_pos) or reset_button_rect.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)





    # ==================================================================
    # main menu display
    # ==================================================================
    else:
        # Draw main paper
        screen.blit(game_title, (380, 120))
        screen.blit(paper_img, paper_rect.topleft)

        # Title text
        #  title_surface = title_font.render("GUESS NUMBER", True, (20, 20, 20))
        # screen.blit(title_surface, (600, 60))

        # PLAY button
        if play_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                screen.blit(play_button_pressed, play_button_rect.topleft)
                click_sound.play()
                in_transition = True
                intro_playing = True
                intro_index = 0
                intro_timer = 0



            else:
                screen.blit(play_button_hover, play_button_rect.topleft)
        else:
            screen.blit(play_button, play_button_rect.topleft)

        # ONLINE button
        if online_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                screen.blit(online_button_pressed, online_button_rect.topleft)
                click_sound.play()
            else:
                screen.blit(online_button_hover, online_button_rect.topleft)
        else:
            screen.blit(online_button, online_button_rect.topleft)

        # OPTIONS button
        if option_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                screen.blit(option_button_pressed, option_button_rect.topleft)

                click_sound.play()
                pygame.time.delay(75)
                show_popup_option = True
            else:
                screen.blit(option_button_hover, option_button_rect.topleft)
        else:
            screen.blit(option_button, option_button_rect.topleft)

        # EXIT button
        if exit_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                screen.blit(exit_button_pressed, exit_button_rect.topleft)
                click_sound.play()
                pygame.time.delay(75)
            else:
                screen.blit(exit_button_hover, exit_button_rect.topleft)
        else:
            screen.blit(exit_button, exit_button_rect.topleft)

        # INFO button
        if info_button_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                screen.blit(info_button_pressed, info_button_rect.topleft)
                click_sound.play()
                pygame.time.delay(75)
                show_popup_info = True
            else:
                screen.blit(info_button_hover, info_button_rect.topleft)
        else:
            screen.blit(info_button, info_button_rect.topleft)

        # ✅ Cursor handling (once per frame)
        if (play_button_rect.collidepoint(mouse_pos) or
                online_button_rect.collidepoint(mouse_pos) or
                option_button_rect.collidepoint(mouse_pos) or
                exit_button_rect.collidepoint(mouse_pos) or
                info_button_rect.collidepoint(mouse_pos)):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # Update display




    pygame.display.flip()
    clock.tick(60)
