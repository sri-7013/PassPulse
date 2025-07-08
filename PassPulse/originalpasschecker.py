import customtkinter as ctk
import tkinter.messagebox as messagebox
import math
import re
import random
import string

# === Password Strength Evaluation ===

def evaluate_strength(password):
    strength = 0
    suggestions = []

    rules = {
        "length": (len(password) >= 8, "Use at least 8 characters."),
        "lower": (re.search(r"[a-z]", password), "Add lowercase letters."),
        "upper": (re.search(r"[A-Z]", password), "Add uppercase letters."),
        "digit": (re.search(r"\d", password), "Add digits."),
        "special": (re.search(r"[@$!%*#?&]", password), "Add special characters.")
    }

    for passed, msg in rules.values():
        if passed:
            strength += 1
        else:
            suggestions.append(msg)

    if password.lower() in ['password', '123456', 'qwerty', 'admin', 'letmein']:
        suggestions.append("Avoid common passwords.")
        strength = 1

    if strength <= 2:
        return "Weak", suggestions, 25, "#e74c3c"
    elif strength == 3:
        return "Moderate", suggestions, 50, "#f39c12"
    elif strength == 4:
        return "Strong", suggestions, 75, "#2980b9"
    else:
        return "Very Strong", suggestions, 100, "#27ae60"

def calc_entropy(password):
    pool = 0
    if re.search(r"[a-z]", password): pool += 26
    if re.search(r"[A-Z]", password): pool += 26
    if re.search(r"\d", password): pool += 10
    if re.search(r"[@$!%*#?&]", password): pool += 32

    if pool == 0: return 0, "—"

    entropy = len(password) * math.log2(pool)
    time_sec = 0.5 * (2 ** entropy) / 1e10
    return entropy, human_readable(time_sec)

def human_readable(seconds):
    for name, sec in [("years", 31536000), ("days", 86400), ("hours", 3600), ("minutes", 60), ("seconds", 1)]:
        if seconds >= sec:
            return f"{seconds / sec:.1f} {name}"
    return "less than a second"

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "@$!%*#?&"
    return ''.join(random.choice(chars) for _ in range(length))

# === NEW: Generate Secure Passphrase ===
word_pool = [
    "Shadow", "Echo", "Storm", "Nebula", "Falcon", "Quantum",
    "Sparrow", "Tiger", "Phoenix", "Blade", "Nova", "Vortex",
    "Sky", "River", "Stone", "Magic", "Wolf", "Blade"
]

def generate_passphrase():
    words = random.sample(word_pool, 3)
    symbols = random.choices("!@#$%&*", k=2)
    digits = random.choices("0123456789", k=2)
    combined = words + symbols + digits
    random.shuffle(combined)
    return ''.join(combined)

# === GUI Setup ===

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("PASSWORD STRENGTH CHECKER - SRIKAR")
app.geometry("620x750")

title = ctk.CTkLabel(app, text="PASSWORD STRENGTH CHECKER", font=("Segoe UI", 22, "bold"))
title.pack(pady=15)

# === Entry + Show Button ===
entry_frame = ctk.CTkFrame(app, fg_color="transparent")
entry_frame.pack(pady=10)

password_var = ctk.StringVar()
entry = ctk.CTkEntry(entry_frame, width=320, height=40, font=("Segoe UI", 14), textvariable=password_var, show="*", corner_radius=15)
entry.grid(row=0, column=0, padx=(0, 10))

def toggle_visibility():
    if entry.cget("show") == "":
        entry.configure(show="*")
        toggle_btn.configure(text="Show")
    else:
        entry.configure(show="")
        toggle_btn.configure(text="Hide")

toggle_btn = ctk.CTkButton(entry_frame, text="Show", command=toggle_visibility, width=70, corner_radius=15)
toggle_btn.grid(row=0, column=1)

# === Strength Bar under Entry ===
strength_bar = ctk.CTkProgressBar(entry_frame, width=400, height=20, corner_radius=10)
strength_bar.grid(row=1, column=0, columnspan=2, pady=(10, 0))
strength_bar.set(0)
strength_bar.grid_remove()

# === Result & Entropy Labels ===
result_label = ctk.CTkLabel(app, text="", font=("Segoe UI", 15, "bold"))
result_label.pack()

entropy_label = ctk.CTkLabel(app, text="", font=("Segoe UI", 12))
entropy_label.pack(pady=2)

# === Suggestion Box (Read-Only) ===
ctk.CTkLabel(app, text="Suggestions", font=("Segoe UI", 14, "bold")).pack(pady=(15, 5))
suggestion_box = ctk.CTkTextbox(app, width=500, height=100, font=("Segoe UI", 12), corner_radius=12)
suggestion_box.pack()
suggestion_box.configure(state="disabled")

# === Animate Progress Bar ===
def animate_progress(target_value, color):
    current = getattr(animate_progress, "current_value", 0.0)
    steps = 20
    step = (target_value - current) / steps

    def update(i=0):
        val = current + step * i
        strength_bar.set(val)
        strength_bar.configure(progress_color=color)
        if i < steps:
            app.after(20, update, i + 1)
        else:
            animate_progress.current_value = target_value

    update()

# === Check Password Strength ===
def check_password(event=None):
    pwd = password_var.get().strip()

    if not pwd:
        strength_bar.grid_remove()
        result_label.configure(text="")
        entropy_label.configure(text="")
        strength_bar.set(0)
        animate_progress.current_value = 0.0
        suggestion_box.configure(state="normal")
        suggestion_box.delete("0.0", "end")
        suggestion_box.configure(state="disabled")
        return

    strength_bar.grid()
    rating, suggestions, score, color = evaluate_strength(pwd)
    entropy, crack_time = calc_entropy(pwd)

    result_label.configure(text=f"Strength: {rating}")
    entropy_label.configure(text=f"≈ {entropy:.1f} bits | Crack time: {crack_time}")
    animate_progress(score / 100, color)

    suggestion_box.configure(state="normal")
    suggestion_box.delete("0.0", "end")
    for s in suggestions:
        suggestion_box.insert("end", f"• {s}\n")
    suggestion_box.configure(state="disabled")

entry.bind("<KeyRelease>", check_password)
entry.bind("<Return>", check_password)

# === Use Passphrase Checkbox ===
passphrase_var = ctk.BooleanVar()
passphrase_checkbox = ctk.CTkCheckBox(app, text="Use Passphrase Mode", variable=passphrase_var)
passphrase_checkbox.pack(pady=8)

# === Generate Button ===
def generate_and_check():
    if passphrase_var.get():
        pwd = generate_passphrase()
    else:
        pwd = generate_password()
    entry.delete(0, "end")
    entry.insert(0, pwd)
    check_password()

generate_btn = ctk.CTkButton(app, text="Generate Password", command=generate_and_check, width=420, height=40, corner_radius=20)
generate_btn.pack(pady=10)

# === Copy Button ===
def copy_to_clipboard():
    app.clipboard_clear()
    app.clipboard_append(entry.get())
    messagebox.showinfo("Copied", "Password copied to clipboard!")

copy_btn = ctk.CTkButton(app, text="Copy to Clipboard", command=copy_to_clipboard, width=420, height=40, corner_radius=20)
copy_btn.pack(pady=5)

# === Footer ===
footer = ctk.CTkLabel(app, text="Developed by Srikar", font=("Segoe UI", 12, "bold"))
footer.pack(pady=20)

app.mainloop()
