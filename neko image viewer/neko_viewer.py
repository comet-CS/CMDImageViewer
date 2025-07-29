import sys
import os
import time
import shutil
from PIL import Image, ImageSequence
import msvcrt

MAX_WIDTH = 400
MAX_HEIGHT = 400
MIN_FRAME_DELAY = 0.05  # seconds = 50ms

def pixel_to_half_block(top, bottom):
    return f"\x1b[38;2;{top[0]};{top[1]};{top[2]}m\x1b[48;2;{bottom[0]};{bottom[1]};{bottom[2]}m▀"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_size():
    size = shutil.get_terminal_size(fallback=(80, 25))
    return size.columns, size.lines

def resize_high_res(img):
    width, height = img.size
    if height % 2 != 0:
        height -= 1
        img = img.crop((0, 0, width, height))

    if width > MAX_WIDTH or height > MAX_HEIGHT:
        scale = min(MAX_WIDTH / width, MAX_HEIGHT / height)
        width = int(width * scale)
        height = int(height * scale)
        if height % 2 != 0:
            height -= 1
        img = img.resize((width, height))
    return img

def render_image(img):
    img = resize_high_res(img)
    output_lines = []
    for y in range(0, img.height - 1, 2):
        line = ""
        for x in range(img.width):
            top = img.getpixel((x, y))
            bottom = img.getpixel((x, y + 1))
            line += pixel_to_half_block(top, bottom)
        output_lines.append(line + "\x1b[0m")
    return output_lines

def render_image_static_centered(img):
    term_width, term_height = get_terminal_size()
    char_ratio = 0.5  # Character height compensation
    max_width = int(term_width)
    max_height = int(term_height / char_ratio)

    img = resize_high_res(img)

    new_img = Image.new("RGB", (max_width, max_height), color=(0, 0, 0))
    x_offset = (max_width - img.width) // 2
    y_offset = (max_height - img.height) // 2
    new_img.paste(img, (x_offset, y_offset))

    return render_image(new_img)

def frames_are_identical(frame1, frame2):
    if frame1.size != frame2.size:
        return False
    return list(frame1.getdata()) == list(frame2.getdata())

def show_animated_gif(path):
    img = Image.open(path)
    frames = []
    durations = []

    previous_frame = None
    for frame in ImageSequence.Iterator(img):
        current_frame = frame.convert('RGB')
        if previous_frame and frames_are_identical(current_frame, previous_frame):
            continue
        rendered = render_image(current_frame)  # not centered
        frames.append(rendered)
        delay = frame.info.get('duration', 100) / 1000
        durations.append(max(delay, MIN_FRAME_DELAY))
        previous_frame = current_frame

    if not frames:
        print("❌ No valid frames found in GIF.")
        return

    print("🔁 Playing GIF (Press ENTER or ESC to stop)")
    i = 0
    while True:
        frame_data = "\x1b[H"
        frame_data += '\n'.join(frames[i]) + "\x1b[0m\n"
        sys.stdout.write(frame_data)
        sys.stdout.flush()

        time.sleep(durations[i])
        i = (i + 1) % len(frames)

        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in (b'\r', b'\x1b'):
                sys.stdout.write("\x1b[0m\x1b[2J\x1b[H")
                sys.stdout.flush()
                return

def show_static_image(path):
    img = Image.open(path).convert('RGB')
    lines = render_image_static_centered(img)
    for line in lines:
        print(line)

def show_image(path):
    if not os.path.exists(path):
        print("❌ Image not found:", path)
        return
    try:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".gif":
            show_animated_gif(path)
        else:
            show_static_image(path)
    except Exception as e:
        print(f"❌ Error rendering image: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: neko_viewer.py <image>")
        sys.exit(1)
    show_image(sys.argv[1])
