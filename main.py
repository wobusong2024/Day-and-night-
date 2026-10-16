
import tkinter as tk
import math
import random

# ---------------- WINDOW SETUP ----------------

root = tk.Tk()
root.title("Day-to-Night Simulator")
root.geometry("1000x760")
root.configure(bg="#edf3f8")
root.resizable(False, False)

WIDTH = 900
HEIGHT = 450

progress = 0.0
playing = False
animation_job = None

# 0 = Morning, 1 = Afternoon, 2 = Sunset, 3 = Night

PHASES = ["Morning", "Afternoon", "Sunset", "Night"]

DESCRIPTIONS = [
    "The sun rises and the sky becomes brighter.",
    "The sun shines high in the afternoon sky.",
    "The sun moves towards the horizon at sunset.",
    "The moon appears and the stars light up the sky."
]

SKY_TOP = ["#F8C47B", "#48B9F0", "#FF783F", "#151A4B"]
SKY_BOTTOM = ["#FFE6AC", "#C8F1FF", "#FFD18B", "#51417C"]

# ---------------- CANVAS ----------------

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="white",
    highlightthickness=0
)
canvas.pack(pady=12)


# ---------------- COLOUR FUNCTIONS ----------------

def hex_to_rgb(colour):
    colour = colour.lstrip("#")
    return tuple(
        int(colour[i:i + 2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(
        *[max(0, min(255, int(v))) for v in rgb]
    )


def blend_colour(colour1, colour2, amount):
    c1 = hex_to_rgb(colour1)
    c2 = hex_to_rgb(colour2)

    result = tuple(
        c1[i] + (c2[i] - c1[i]) * amount
        for i in range(3)
    )

    return rgb_to_hex(result)


def get_colour(colours, value):
    index = min(2, int(value))
    fraction = value - index

    return blend_colour(
        colours[index],
        colours[index + 1],
        fraction
    )


# ---------------- LANDSCAPE ----------------

def draw_mountains():
    # Distant mountains
    canvas.create_polygon(
        0, 320,
        130, 155,
        280, 320,
        430, 190,
        600, 335,
        760, 170,
        900, 320,
        900, 450,
        0, 450,
        fill="#507AA8",
        outline=""
    )

    # Foreground mountains
    canvas.create_polygon(
        0, 385,
        100, 300,
        260, 375,
        430, 290,
        620, 390,
        770, 305,
        900, 380,
        900, 450,
        0, 450,
        fill="#28466F",
        outline=""
    )

    # Horizon and ground
    canvas.create_rectangle(
        0, 435, WIDTH, HEIGHT,
        fill="#233B52",
        outline=""
    )


def draw_cloud(x, y, colour, scale=1):
    canvas.create_oval(
        x, y + 10 * scale,
        x + 40 * scale, y + 35 * scale,
        fill=colour, outline=""
    )
    canvas.create_oval(
        x + 12 * scale, y,
        x + 45 * scale, y + 30 * scale,
        fill=colour, outline=""
    )
    canvas.create_oval(
        x + 30 * scale, y + 8 * scale,
        x + 65 * scale, y + 35 * scale,
        fill=colour, outline=""
    )


# ---------------- SUN ----------------

def draw_sun():
    if progress >= 2.9:
        return

    # Horizontal movement from left to right
    x = 65 + (progress / 3) * 770

    # Sun rises, reaches its highest point, then sets
    y = 320 - 230 * math.sin(math.pi * progress / 3)

    # Sun glow
    canvas.create_oval(
        x - 55, y - 55,
        x + 55, y + 55,
        fill="#FBE6A0",
        outline=""
    )

    canvas.create_oval(
        x - 38, y - 38,
        x + 38, y + 38,
        fill="#FFE36E",
        outline=""
    )


# ---------------- MOON AND STARS ----------------

random.seed(10)

STARS = [
    (
        random.randint(20, 880),
        random.randint(15, 230),
        random.choice([2, 3, 4])
    )
    for _ in range(75)
]


def draw_stars():
    if progress < 2.6:
        return

    # Stars gradually appear as night approaches
    visibility = min(1, (progress - 2.6) / 0.4)

    for i, (x, y, size) in enumerate(STARS):
        if (i % 4) / 4 < visibility:
            colour = random.choice(
                ["#FFFFFF", "#FFF2B0", "#D8E6FF"]
            )

            canvas.create_oval(
                x, y, x + size, y + size,
                fill=colour,
                outline=""
            )


def draw_moon():
    if progress < 2.6:
        return

    x = 735
    y = 95

    # Moon
    canvas.create_oval(
        x - 28, y - 28,
        x + 28, y + 28,
        fill="#FFF4BD",
        outline=""
    )

    # Cover part of the moon to create a crescent
    cover_colour = get_colour(SKY_TOP, progress)

    canvas.create_oval(
        x - 8, y - 36,
        x + 42, y + 14,
        fill=cover_colour,
        outline=""
    )


# ---------------- DRAW THE SCENE ----------------

def draw_scene():
    canvas.delete("all")

    top_colour = get_colour(SKY_TOP, progress)
    bottom_colour = get_colour(SKY_BOTTOM, progress)

    # Draw a vertical gradient using coloured strips
    for y in range(HEIGHT):
        amount = y / HEIGHT
        colour = blend_colour(
            top_colour,
            bottom_colour,
            amount
        )

        canvas.create_line(
            0, y, WIDTH, y,
            fill=colour,
            tags="sky"
        )

    draw_stars()
    draw_moon()

    cloud_colour = (
        "#DCA16D" if progress >= 2
        else "#FFFFFF"
    )

    draw_cloud(160, 120, cloud_colour, 0.8)
    draw_cloud(580, 155, cloud_colour, 0.65)
    draw_cloud(400, 75, cloud_colour, 0.5)

    draw_sun()
    draw_mountains()

    update_information()


# ---------------- INFORMATION PANEL ----------------

phase_label = tk.Label(
    root,
    text="Morning",
    font=("Arial", 19, "bold"),
    bg="#edf3f8",
    fg="#234E70"
)
phase_label.pack()

description_label = tk.Label(
    root,
    text=DESCRIPTIONS[0],
    font=("Arial", 11),
    bg="#edf3f8",
    fg="#40566B"
)
description_label.pack(pady=4)

clock_label = tk.Label(
    root,
    text="Simulation time: 6:00 AM",
    font=("Arial", 11, "bold"),
    bg="#edf3f8",
    fg="#234E70"
)
clock_label.pack(pady=3)


def update_information():
    phase_index = min(3, int(progress))

    phase_label.config(text=PHASES[phase_index])
    description_label.config(
        text=DESCRIPTIONS[phase_index]
    )

    # Simulated time: 6 AM to 9 PM
    total_minutes = round(360 + (progress / 3) * 900)

    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60

    period = "AM" if hours < 12 else "PM"
    display_hour = hours % 12 or 12

    clock_label.config(
        text=(
            f"Simulation time: "
            f"{display_hour}:{minutes:02d} {period}"
        )
    )


# ---------------- PHASE CONTROLS ----------------

def set_phase(value):
    global progress

    stop_animation()
    progress = float(value)
    draw_scene()


def animate():
    global progress, animation_job, playing

    if not playing:
        return

    progress += 0.012

    if progress >= 3:
        progress = 3
        playing = False
        animation_job = None
        draw_scene()
        return

    draw_scene()

    animation_job = root.after(50, animate)


def play_animation():
    global playing, progress

    if playing:
        return

    if progress >= 3:
        progress = 0

    playing = True
    animate()


def stop_animation():
    global playing, animation_job

    playing = False

    if animation_job is not None:
        root.after_cancel(animation_job)
        animation_job = None


def reset_animation():
    global progress

    stop_animation()
    progress = 0
    draw_scene()


# ---------------- BUTTONS ----------------

phase_frame = tk.Frame(root, bg="#edf3f8")
phase_frame.pack(pady=12)

phases = [
    ("Morning", 0),
    ("Afternoon", 1),
    ("Sunset", 2),
    ("Night", 3)
]

for name, value in phases:
    tk.Button(
        phase_frame,
        text=name,
        width=12,
        font=("Arial", 10, "bold"),
        bg="#2878B5",
        fg="white",
        activebackground="#E99A43",
        activeforeground="white",
        relief="flat",
        command=lambda v=value: set_phase(v)
    ).pack(side="left", padx=5)


action_frame = tk.Frame(root, bg="#edf3f8")
action_frame.pack(pady=3)

tk.Button(
    action_frame,
    text="▶ Play Animation",
    width=17,
    font=("Arial", 10, "bold"),
    bg="#27834D",
    fg="white",
    relief="flat",
    command=play_animation
).pack(side="left", padx=6)

tk.Button(
    action_frame,
    text="⏸ Pause",
    width=12,
    font=("Arial", 10, "bold"),
    bg="#D98B26",
    fg="white",
    relief="flat",
    command=stop_animation
).pack(side="left", padx=6)

tk.Button(
    action_frame,
    text="↺ Reset",
    width=12,
    font=("Arial", 10, "bold"),
    bg="#596A7A",
    fg="white",
    relief="flat",
    command=reset_animation
).pack(side="left", padx=6)


# ---------------- LEARNING CHALLENGE ----------------

challenge = tk.Label(
    root,
    text=(
        "Gallery Challenge: Which variable controls the time of day?\n"
        "What condition determines when the moon and stars appear?"
    ),
    font=("Arial", 10),
    bg="#edf3f8",
    fg="#34495E",
    justify="center"
)
challenge.pack(pady=12)


# Start the application
draw_scene()
root.mainloop()
