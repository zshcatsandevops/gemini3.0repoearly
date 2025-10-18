#!/usr/bin/env python3
"""
Samsoft Tetris — Windows 11 (25H2) Port — Accurate 23HT Build
-------------------------------------------------------------
This version introduces a full rotation system, wall kicks, and refined
gameplay mechanics for a more authentic experience.

(C) 2025 Flames Co. / Samsoft Interactive
"""

import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import pygame
import collections
import io
import wave

# --- Constants ------------------------------------------------------------
CVS_WIDTH = 600
CVS_HEIGHT = 440  # Increased height for better layout
BOX_L = 20
W_BOX_NUM = 10
H_BOX_NUM = 20
SCORES = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
FONT = f'Fixedsys {int(BOX_L / 2)} bold'
TITLE_FONT = 'Fixedsys 24 bold'
DELAY_BASE = 500
DELAY_DECREMENT = 25
KILL_SCREEN_LEVEL = 29
KILL_SCREEN_DELAY = 16

# Shape definitions now include all rotation states. Coords are relative to a pivot.
FIGURE_SHAPES = collections.OrderedDict([
    ('t', {
        'color': 'purple',
        'states': [[(0, 0), (-1, 0), (1, 0), (0, -1)],
                   [(0, 0), (0, -1), (0, 1), (1, 0)],
                   [(0, 0), (-1, 0), (1, 0), (0, 1)],
                   [(0, 0), (0, -1), (0, 1), (-1, 0)]],
        'pivot': (4, 1)
    }),
    ('line', {
        'color': 'cyan',
        'states': [[(-1, 0), (0, 0), (1, 0), (2, 0)],
                   [(0, -1), (0, 0), (0, 1), (0, 2)]],
        'pivot': (4, 0)
    }),
    ('left_l', {
        'color': 'orange',
        'states': [[(0, 0), (-1, 0), (1, 0), (-1, -1)],
                   [(0, 0), (0, -1), (0, 1), (1, -1)],
                   [(0, 0), (1, 0), (-1, 0), (1, 1)],
                   [(0, 0), (0, 1), (0, -1), (-1, 1)]],
        'pivot': (4, 1)
    }),
    ('right_l', {
        'color': 'blue',
        'states': [[(0, 0), (-1, 0), (1, 0), (1, -1)],
                   [(0, 0), (0, -1), (0, 1), (1, 1)],
                   [(0, 0), (1, 0), (-1, 0), (-1, 1)],
                   [(0, 0), (0, 1), (0, -1), (-1, -1)]],
        'pivot': (4, 1)
    }),
    ('left_z', {
        'color': 'green',
        'states': [[(0, 0), (-1, 0), (0, -1), (1, -1)],
                   [(0, 0), (1, 0), (0, 1), (1, -1)]],
        'pivot': (4, 1)
    }),
    ('right_z', {
        'color': 'red',
        'states': [[(0, 0), (1, 0), (0, -1), (-1, -1)],
                   [(0, 0), (-1, 0), (0, 1), (-1, -1)]],
        'pivot': (4, 1)
    }),
    ('square', {
        'color': 'yellow',
        'states': [[(0, 0), (1, 0), (0, 1), (1, 1)]],
        'pivot': (4, 0)
    })
])

SHAPE_KEYS = list(FIGURE_SHAPES.keys())

NOTES = {
    'G3S': 207.65, 'A3': 220.00, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66,
    'E4': 329.63, 'G4S': 415.30, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
    'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00,
    'REST': 0
}

# Full Korobeiniki "Type A" theme
MELODY = [
    # Section A
    ('E5', 0.2), ('B4', 0.1), ('C5', 0.1), ('D5', 0.2), ('C5', 0.1), ('B4', 0.1),
    ('A4', 0.2), ('A4', 0.1), ('C5', 0.1), ('E5', 0.2), ('D5', 0.1), ('C5', 0.1),
    ('B4', 0.3), ('C5', 0.1), ('D5', 0.2), ('E5', 0.2),
    ('C5', 0.2), ('A4', 0.2), ('A4', 0.4), ('REST', 0.1),

    ('D5', 0.3), ('F5', 0.1), ('A5', 0.2), ('G5', 0.1), ('F5', 0.1),
    ('E5', 0.3), ('C5', 0.1), ('E5', 0.2), ('D5', 0.1), ('C5', 0.1),
    ('B4', 0.3), ('C5', 0.1), ('D5', 0.2), ('E5', 0.2),
    ('C5', 0.2), ('A4', 0.2), ('A4', 0.4), ('REST', 0.1),

    # Section B
    ('E4', 0.4), ('C4', 0.4),
    ('D4', 0.4), ('B3', 0.4),
    ('C4', 0.4), ('A3', 0.4),
    ('G3S', 0.4), ('B3', 0.4),

    ('E4', 0.4), ('C4', 0.4),
    ('D4', 0.4), ('B3', 0.4),
    ('C4', 0.2), ('E4', 0.2), ('A4', 0.4),
    ('G4S', 0.4), ('REST', 0.4)
]


# --- NES Square Wave Synth -----------------------------------------------
def generate_square_wave(frequency, duration, sample_rate=44100):
    if frequency == 0:
        return np.zeros(int(duration * sample_rate), dtype=np.int16)
    t = np.arange(int(duration * sample_rate))
    wave = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t / sample_rate))
    return (wave * 32767).astype(np.int16)

def generate_music_track():
    sample_rate = 44100
    song = [generate_square_wave(NOTES[n], d, sample_rate) for n, d in MELODY]
    sound = np.concatenate(song)
    stereo = np.column_stack((sound, sound))

    # Save the generated audio to an in-memory WAV file
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)  # 16-bit = 2 bytes
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo.tobytes())
    buffer.seek(0)
    return buffer

# --- Utility Classes ------------------------------------------------------
class Utils:
    @staticmethod
    def convert_coords(x, y, x_size=1, y_size=1):
        return BOX_L * x, BOX_L * y, BOX_L * (x + x_size), BOX_L * (y + y_size)

    @staticmethod
    def find_overlaps(x, y, x_size, y_size, canvas, excluded_items):
        x1, y1, x2, y2 = Utils.convert_coords(x, y, x_size, y_size)
        all_overlaps = canvas.find_enclosed(x1 - 1, y1 - 1, x2 + 1, y2 + 1)
        return list(set(all_overlaps) - set(excluded_items))

    @staticmethod
    def tgm_randomizer():
        """TGM-style randomizer to prevent piece droughts."""
        pool = list(range(len(SHAPE_KEYS))) * 5
        history = [4, 5, 4, random.choice([0, 1, 2, 3, 6])]
        while True:
            for _ in range(6):
                idx = random.randrange(len(pool))
                piece_idx = pool[idx]
                if piece_idx not in history:
                    break
            pool.remove(piece_idx)
            if not pool:
                pool = list(range(len(SHAPE_KEYS))) * 5
            history = history[1:] + [piece_idx]
            yield SHAPE_KEYS[piece_idx]

# --- Figure (Tetromino) ---------------------------------------------------
class Figure:
    def __init__(self, canvas, shape_key, background_items, limit_coords):
        self.canvas = canvas
        self.shape_key = shape_key
        self.shape_data = FIGURE_SHAPES[shape_key]
        self.color = self.shape_data['color']
        self.pivot = list(self.shape_data['pivot'])
        self.rotation_state = 0
        self.limit_coords = limit_coords
        self.background_items = background_items
        self.blocks = []
        self.stopped = False

    def get_coords_for_state(self, state_index, current_pivot):
        """Returns absolute grid coordinates for a given rotation state."""
        state_coords = self.shape_data['states'][state_index]
        return [(current_pivot[0] + x, current_pivot[1] + y) for x, y in state_coords]

    def create(self, next_area=False):
        offset_x = 12 if next_area else 0
        self.pivot[0] += offset_x
        
        coords = self.get_coords_for_state(self.rotation_state, self.pivot)
        
        # Pre-check for collision on spawn (game over condition)
        if not next_area and self._is_colliding(coords):
            return False

        for px, py in coords:
            rect = self.canvas.create_rectangle(
                Utils.convert_coords(px, py),
                fill=self.color, outline='gray', width=2
            )
            self.blocks.append(rect)

        return True

    def _is_colliding(self, coords_to_check):
        """Checks if a set of coordinates collides with walls or background blocks."""
        for x, y in coords_to_check:
            if not (0 <= x < W_BOX_NUM and y < H_BOX_NUM):
                return True # Wall collision
            
            x1, y1, x2, y2 = Utils.convert_coords(x, y)
            overlaps = self.canvas.find_enclosed(x1 - 1, y1 - 1, x2 + 1, y2 + 1)
            if any(item in self.background_items for item in overlaps):
                return True # Collision with a landed block
        return False

    def move(self, delta):
        dx, dy = delta
        new_pivot = [self.pivot[0] + dx, self.pivot[1] + dy]
        new_block_coords = self.get_coords_for_state(self.rotation_state, new_pivot)

        if self._is_colliding(new_block_coords):
            if dy > 0:  # If moving down caused the collision, lock the piece
                self.stopped = True
            return

        # Execute move if no collision
        self.pivot = new_pivot
        for i, block in enumerate(self.blocks):
            nx, ny = new_block_coords[i]
            self.canvas.coords(block, Utils.convert_coords(nx, ny))

    def rotate(self):
        num_states = len(self.shape_data['states'])
        next_state = (self.rotation_state + 1) % num_states
        
        # Test rotations with standard wall kick offsets
        kick_offsets = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in kick_offsets:
            test_pivot = [self.pivot[0] + dx, self.pivot[1] + dy]
            new_coords = self.get_coords_for_state(next_state, test_pivot)
            
            if not self._is_colliding(new_coords):
                # Valid rotation found
                self.pivot = test_pivot
                self.rotation_state = next_state
                for i, block in enumerate(self.blocks):
                    nx, ny = new_coords[i]
                    self.canvas.coords(block, Utils.convert_coords(nx, ny))
                return

    def drop(self):
        while not self.stopped:
            self.move((0, 1))

# --- Game Core ------------------------------------------------------------
class TetrisGame:
    def __init__(self):
        self.tk = tk.Tk()
        self.tk.title("Samsoft Tetris – Win11 25H2 Port (23HT Build)")
        
        self.canvas = tk.Canvas(self.tk, width=CVS_WIDTH, height=CVS_HEIGHT, bg='black')
        self.canvas.pack()
        
        self.rand = Utils.tgm_randomizer()
        self.score = 0
        self.lines = 0
        self.level = 1
        self.is_paused = False
        
        self.background_items = []
        self.draw_ui() # This defines limit_coords
        self.curr_figure = None
        self.next_figure = None


    def start(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        print("🎵 Generating Korobeiniki theme (NES version)...")
        music_buffer = generate_music_track()
        pygame.mixer.music.load(music_buffer)
        pygame.mixer.music.play(loops=-1, fade_ms=1000)


        self.spawn_new_figure()

        self.tk.bind("<Key>", self.handle_key)
        self.run()
        self.tk.mainloop()

    def draw_ui(self):
        # Play area
        play_area_coords = Utils.convert_coords(0, 0, W_BOX_NUM, H_BOX_NUM)
        self.canvas.create_rectangle(play_area_coords, outline='gray', tags='bounds')
        self.limit_coords = self.canvas.coords('bounds')

        # UI Panels
        self.canvas.create_rectangle(220, 20, 380, 60, outline='gray')
        self.canvas.create_text(300, 40, text='TETRIS', font=TITLE_FONT, fill='white')
        
        # Next Piece Area
        self.canvas.create_rectangle(240, 80, 360, 160, outline='gray')
        self.canvas.create_text(300, 100, text='NEXT', font=FONT, fill='white')

        # Score Area
        self.canvas.create_rectangle(240, 180, 360, 260, outline='gray')
        self.canvas.create_text(300, 200, text='SCORE', font=FONT, fill='white')
        self.canvas.create_text(300, 230, text='0', font=FONT, fill='white', tags='SCR')
        
        # Level Area
        self.canvas.create_rectangle(240, 280, 360, 360, outline='gray')
        self.canvas.create_text(300, 300, text='LEVEL', font=FONT, fill='white')
        self.canvas.create_text(300, 330, text='1', font=FONT, fill='white', tags='LVL')


    def handle_key(self, event):
        if self.is_paused and event.keysym != "p":
            return
            
        if event.keysym == "Escape": self.tk.quit()
        elif event.keysym == "Left": self.curr_figure.move((-1, 0))
        elif event.keysym == "Right": self.curr_figure.move((1, 0))
        elif event.keysym == "Down": self.curr_figure.move((0, 1))
        elif event.keysym == "Up": self.curr_figure.rotate()
        elif event.keysym == "space": self.curr_figure.drop()
        elif event.keysym == "p": self.toggle_pause()

    def run(self):
        if not self.is_paused:
            if not self.curr_figure.stopped:
                self.curr_figure.move((0, 1))
            else:
                self.lock_and_spawn()
        
        delay = KILL_SCREEN_DELAY if self.level >= KILL_SCREEN_LEVEL else \
                max(50, DELAY_BASE - (self.level - 1) * DELAY_DECREMENT)
        self.tk.after(delay, self.run)

    def lock_and_spawn(self):
        self.background_items.extend(self.curr_figure.blocks)
        self.clear_lines()
        self.spawn_new_figure()

    def spawn_new_figure(self):
        if self.next_figure is None:
            # First piece of the game
            self.curr_figure = Figure(self.canvas, next(self.rand), self.background_items, self.limit_coords)
            if not self.curr_figure.create():
                self.game_over()
                return
        else:
            # Promote next_figure to curr_figure
            self.curr_figure = self.next_figure
            
            # Move its blocks from the 'next' area to the play area start
            self.curr_figure.pivot = list(self.curr_figure.shape_data['pivot'])
            self.curr_figure.rotation_state = 0 # Reset rotation
            
            coords = self.curr_figure.get_coords_for_state(0, self.curr_figure.pivot)
            for i, block in enumerate(self.curr_figure.blocks):
                nx, ny = coords[i]
                self.canvas.coords(block, Utils.convert_coords(nx, ny))
                
            # Check for game over on spawn
            if self.curr_figure._is_colliding(coords):
                self.game_over()
                return

        # Create the new next_figure for display
        self.next_figure = Figure(self.canvas, next(self.rand), self.background_items, self.limit_coords)
        self.next_figure.create(next_area=True)

    def clear_lines(self):
        lines_to_clear = []
        for y in range(H_BOX_NUM):
            overlaps = Utils.find_overlaps(0, y, W_BOX_NUM, 1, self.canvas, [])
            row_blocks = [b for b in overlaps if b in self.background_items]
            if len(row_blocks) == W_BOX_NUM:
                lines_to_clear.append((y, row_blocks))

        if not lines_to_clear: return
        
        for y, blocks in lines_to_clear:
            for block in blocks:
                self.canvas.delete(block)
                self.background_items.remove(block)
        
        # Shift blocks down
        for y_cleared, _ in reversed(lines_to_clear):
            for item in self.background_items:
                x1, y1, x2, y2 = self.canvas.coords(item)
                if y1 < y_cleared * BOX_L:
                    self.canvas.move(item, 0, BOX_L)

        # Update score and level
        num_cleared = len(lines_to_clear)
        self.lines += num_cleared
        self.score += SCORES[num_cleared] * self.level
        self.level = (self.lines // 10) + 1
        
        self.canvas.itemconfig(self.canvas.find_withtag('SCR')[0], text=str(self.score))
        self.canvas.itemconfig(self.canvas.find_withtag('LVL')[0], text=str(self.level))

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            pygame.mixer.music.pause()
            self.canvas.create_text(100, 220, text="PAUSED", font=TITLE_FONT, fill="white", tags="pause_text", anchor="w")
        else:
            pygame.mixer.music.unpause()
            self.canvas.delete("pause_text")

    def game_over(self):
        pygame.mixer.music.fadeout(1000)
        messagebox.showinfo("Game Over", f"Score: {self.score}\nLines: {self.lines}\nLevel: {self.level}")
        self.tk.quit()

# --- Entry Point ----------------------------------------------------------
if __name__ == "__main__":
    game = TetrisGame()
    game.start()

