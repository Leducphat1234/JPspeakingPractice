import tkinter as tk
from tkinter import messagebox
import random
import os
import tempfile
import time
from gtts import gTTS
# from playsound import playsound
import pygame


# ======================
# Load sentences
# ======================
def load_sentences(filename="JPspeaking.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if not lines:
            raise ValueError("File rỗng")
        return lines
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể đọc file {filename}\n{e}")
        return []
def load_answers(filename="JPanswer.txt"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f]
    except:
        return []

sentences = load_sentences()
n = len(sentences)
answers = load_answers()

# ======================
# App state
# ======================
played = [False] * n
current_index = None
slow_mode = False
showing_answer = False


# ======================
# Tkinter root
# ======================
root = tk.Tk()
root.title("Japanese Speaking Practice")
root.geometry("900x500")

# ======================
# pygame mixer init
# ======================
pygame.mixer.init()

# ======================
# Layout containers
# ======================
control_frame = tk.Frame(root, width=160)
control_frame.pack(side="right", fill="y", padx=10, pady=10)
control_frame.pack_propagate(False)

progress_frame = tk.Frame(root, height=130)
progress_frame.pack(side="bottom", fill="x")
progress_frame.pack_propagate(False)
reset_frame = tk.Frame(root)
reset_frame.pack(side="bottom", pady=5)
speed_text = tk.StringVar(value="Speed: NORMAL")

def reset_progress():
    global played, current_index, showing_answer
    played = [False] * n
    current_index = None
    set_slow_mode(False)
    current_sentence.set("Nhấn Continue để bắt đầu")
    reset_button.pack_forget()
    refresh_progress()
    answer_label.pack_forget()
    showing_answer = False


def toggle_answer():
    global showing_answer

    if current_index is None:
        return

    if not showing_answer:
        if current_index < len(answers) and answers[current_index]:
            answer_text.set(answers[current_index])
        else:
            answer_text.set("(Chưa có câu trả lời)")

        answer_label.pack(pady=6)
        showing_answer = True
    else:
        answer_label.pack_forget()
        showing_answer = False


reset_button = tk.Button(
    reset_frame,
    text="Reset",
    width=12,
    command=lambda: reset_progress()
)
reset_button.pack()
reset_button.pack_forget()  # Ẩn ban đầu

main_frame = tk.Frame(root)
main_frame.pack(expand=True, fill="both")
answer_button = tk.Button(
    main_frame,
    text="Câu trả lời",
    width=14,
    command=lambda: toggle_answer()
)
answer_button.pack(pady=6)

answer_text = tk.StringVar(value="")

answer_label = tk.Label(
    main_frame,
    textvariable=answer_text,
    font=("Arial", 16),
    fg="#444",
    wraplength=600,
    justify="center"
)
answer_label.pack()
answer_label.pack_forget()  # Ẩn ban đầu


# ======================
# Colors
# ======================
COLOR_DEFAULT = "#f0f0f0"
COLOR_PLAYED  = "#b3d9ff"
COLOR_CURRENT = "#ffcc80"

# ======================
# Sentence display
# ======================
current_sentence = tk.StringVar(value="Nhấn Continue để bắt đầu")

sentence_label = tk.Label(
    main_frame,
    textvariable=current_sentence,
    font=("Arial", 22),
    wraplength=600,
    justify="center"
)
sentence_label.pack(expand=True)

speed_label = tk.Label(
    main_frame,
    textvariable=speed_text,
    font=("Arial", 12),
    fg="#555"
)
speed_label.pack(pady=6)


# ======================
# gTTS
# ======================

def play_audio(text):
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)

    tts = gTTS(text, lang="ja", slow=slow_mode)
    tts.save(tmp_path)

    pygame.mixer.music.load(tmp_path)
    pygame.mixer.music.play()

    # chờ phát xong
    while pygame.mixer.music.get_busy():
        root.update()
        time.sleep(0.05)

    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    os.remove(tmp_path)

# ======================
# Logic
# ======================
def refresh_progress():
    for i, btn in enumerate(progress_buttons):
        if i == current_index:
            btn.config(bg=COLOR_CURRENT)
        elif played[i]:
            btn.config(bg=COLOR_PLAYED)
        else:
            btn.config(bg=COLOR_DEFAULT)

def show_sentence(idx, speak=True):
    global current_index, showing_answer

    current_index = idx
    current_sentence.set(sentences[idx])

    # Ẩn đáp án khi sang câu mới
    answer_label.pack_forget()
    showing_answer = False

    refresh_progress()
    if speak:
        play_audio(sentences[idx])



def continue_random():
    remaining = [i for i, p in enumerate(played) if not p]
    if not remaining:
        messagebox.showinfo("Hoàn thành", "Bạn đã nghe hết các câu!")
        reset_button.pack()
        return
    idx = random.choice(remaining)
    played[idx] = True
    show_sentence(idx, speak=True)


def repeat_sentence():
    if current_index is not None:
        show_sentence(current_index, speak=True)

# ======================
# Control buttons
# ======================
tk.Button(control_frame, text="Continue (space)", width=14, command=continue_random).pack(pady=6)
tk.Button(control_frame, text="Repeat (R)", width=14, command=repeat_sentence).pack(pady=6)
tk.Button(
    control_frame, text="Slow (-)", width=14,
    command=lambda: set_slow_mode(True)
).pack(pady=6)

tk.Button(
    control_frame, text="Normal (+)", width=14,
    command=lambda: set_slow_mode(False)
).pack(pady=6)

# ======================
# Progress bar
# ======================
progress_inner = tk.Frame(progress_frame)
progress_inner.pack(anchor="center")

progress_buttons = []
MAX_COL = 10

for i in range(n):
    row = i // MAX_COL
    col = i % MAX_COL
    btn = tk.Label(
        progress_inner,
        text=str(i + 1),
        width=4,
        bg=COLOR_DEFAULT,
        fg="black",
        relief="raised",
        cursor="hand2"
    )
    btn.grid(row=row, column=col, padx=3, pady=3)
    btn.bind("<Button-1>", lambda e, idx=i: show_sentence(idx))
    progress_buttons.append(btn)

# ======================
# Keyboard shortcuts
# ======================
def on_key(event):
    key = event.keysym.lower()

    if key == "space":
        continue_random()

    elif key == "r":
        repeat_sentence()

    elif key in ("plus", "equal"):  # + hoặc =
        set_slow_mode(True)

    elif key == "minus":
        set_slow_mode(False)

    elif key == "escape":
        root.quit()


def set_slow_mode(value):
    global slow_mode
    slow_mode = value

    if slow_mode:
        speed_text.set("Speed: SLOW")
        root.title("Japanese Speaking Practice  [SLOW]")
    else:
        speed_text.set("Speed: NORMAL")
        root.title("Japanese Speaking Practice")


root.bind("<Key>", on_key)


# ======================
# Start app
# ======================
root.mainloop()
