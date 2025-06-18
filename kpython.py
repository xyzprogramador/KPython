import os
import sys
import shutil
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Label
from PIL import Image, ImageTk
from tkvideo import tkvideo
import random 
# === ANSI Colors ===
COLOR_CYAN = '\033[96m'
COLOR_GREEN = '\033[92m'
COLOR_RESET = '\033[0m'

# === ASCII Banner ===
ASCII_LOGO = r"""
 ▄▀▀▄ █  ▄▀▀▄▀▀▀▄  ▄▀▀▄ ▀▀▄  ▄▀▀▀█▀▀▄  ▄▀▀▄ ▄▄   ▄▀▀▀▀▄   ▄▀▀▄ ▀▄ 
█  █ ▄▀ █   █   █ █   ▀▄ ▄▀ █    █  ▐ █  █   ▄▀ █      █ █  █ █ █ 
▐  █▀▄  ▐  █▀▀▀▀  ▐     █   ▐   █     ▐  █▄▄▄█  █      █ ▐  █  ▀█ 
  █   █    █            █      █         █   █  ▀▄    ▄▀   █   █  
▄▀   █   ▄▀           ▄▀     ▄▀         ▄▀  ▄▀    ▀▀▀▀   ▄▀   █   
█    ▐  █             █     █          █   █             █    ▐   
▐       ▐             ▐     ▐          ▐   ▐             ▐        
"""

# === Menu ===
OPTIONS = [
    "[1] Search by tag (XVideos Video)",
    "[2] Show by tag (Local Image Preview)",
    "[98] Search image by tag",
    "[99] Exit"
]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def center_text(text, width=None):
    if width is None:
        width = shutil.get_terminal_size().columns
    return text.center(width)

def show_banner():
    clear_screen()
    for line in ASCII_LOGO.strip().splitlines():
        print(COLOR_CYAN + center_text(line) + COLOR_RESET)
    print(COLOR_GREEN + center_text("Welcome to XPYTHON") + COLOR_RESET)
    print()

def show_menu():
    for option in OPTIONS:
        print(center_text(option))
    print()

# === [1] Search by tag & Play Video ===
def search_by_tag():
    tag = input("\nEnter tag to search on XVideos: ").replace(' ', '+')
    print(f"[+] Searching for: {tag}...")

    url = f"https://www.xvideos.com/?k={tag}"
    headers = { "User-Agent": "Mozilla/5.0" }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Coleta todos os links válidos
    video_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith("/video") and "video" in href and "profiles" not in href and "like" not in href:
            candidate = "https://www.xvideos.com" + href
            if "/videos-i-like" not in candidate:
                video_links.append(candidate)

    if not video_links:
        print("[X] No valid videos found for this tag.")
        input("Press Enter to continue...")
        return

    # Escolhe um vídeo aleatório
    video_link = random.choice(video_links)
    print(f"[+] Found: {video_link}")
    play_video(video_link)


# === Video Preview ===
def play_video(video_url):
    print("[+] Fetching video source...")
    headers = { "User-Agent": "Mozilla/5.0" }
    r = requests.get(video_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    script = soup.find("script", string=lambda t: t and 'setVideoUrlHigh' in t)

    if not script:
        print("[X] Failed to extract video.")
        input("Press Enter to continue...")
        return

    # Extract .mp4 URL from JS
    start = script.text.find("setVideoUrlHigh('") + len("setVideoUrlHigh('")
    end = script.text.find("')", start)
    mp4_url = script.text[start:end]

    if not mp4_url:
        print("[X] Video URL not found.")
        return

    print(f"[+] Video URL: {mp4_url}")

    # Download video temporarily
    temp_video = "temp_video.mp4"
    try:
        with open(temp_video, "wb") as f:
            f.write(requests.get(mp4_url).content)
    except Exception as e:
        print(f"[X] Error downloading video: {e}")
        return

    # Play in tkinter
    root = Tk()
    root.title("XPYTHON - Video Preview")
    lbl = Label(root)
    lbl.pack()
    player = tkvideo(temp_video, lbl, loop=1, size=(640, 360))
    player.play()
    root.mainloop()

    os.remove(temp_video)

# === [2] Show image by tag ===
def show_by_tag():
    tag = input("\nEnter tag to preview image: ")
    matches = [f for f in os.listdir("images") if f.lower().startswith(tag.lower()) and f.endswith(".jpg")]

    if not matches:
        print(f"[X] No image found for tag '{tag}'")
        input("Press Enter to return...")
        return

    image_path = os.path.join("images", random.choice(matches))
    show_image(image_path, f"Preview: {tag}")


# === [99] Search image by tag ===
def search_image_by_tag():
    tag = input("\nSearch tag for image: ")
    matches = [f for f in os.listdir("images") if f.lower().startswith(tag.lower()) and f.endswith(".jpg")]

    if matches:
        image_path = os.path.join("images", random.choice(matches))
        print("[✓] Image found. Showing preview...")
        show_image(image_path, f"Found: {tag}")
    else:
        print("[X] No image found.")
    input("Press Enter to continue...")

# === Image Preview ===
def show_image(path, title="Image Preview"):
    root = Tk()
    root.title(title)
    img = Image.open(path)
    tk_img = ImageTk.PhotoImage(img)
    lbl = Label(root, image=tk_img)
    lbl.pack()
    root.mainloop()

# === Main Loop ===
def main():
    while True:
        show_banner()
        show_menu()
        choice = input("\n> ").strip()
        if choice == '1':
            search_by_tag()
        elif choice == '2':
            show_by_tag()
        elif choice == '98':
            search_image_by_tag()
        elif choice == '99':
            sys.exit(1)
        else:
            print("[X] Invalid option.")
            input("Press Enter to retry...")
if __name__ == "__main__":
    main()
