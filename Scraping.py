import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
import google.generativeai as genai
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# --- API Config ---
genai.configure(api_key="AIzaSyCJM-AzGpg_ey8mE8V7sOJTvUCh12Ygq-0")
vertexai.init(project="mercurial-time-459907-r1", location="us-central1")
gen_model = genai.GenerativeModel('gemini-2.0-flash-lite')
image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

# --- Global Data ---
movie_links = {}
dialogue_text = ""
scene_description = ""

# --- IMDb Data Fetch ---
def fetch_top_movies():
    url = "https://www.imdb.com/chart/top/"
    headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US,en;q=0.5"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    movie_rows = soup.select("li.ipc-metadata-list-summary-item")[:10]

    movies = []
    for row in movie_rows:
        title = row.select_one("h3").text.strip()
        a_tag = row.select_one("a.ipc-title-link-wrapper")
        full_link = "https://www.imdb.com" + a_tag.get("href")
        movie_links[title] = full_link
        movies.append(title)
    return movies

# --- Storyline Fetch ---
def get_movie_storyline(title):
    ia = Cinemagoer()
    movies = ia.search_movie(title)
    if movies:
        movie = ia.get_movie(movies[0].movieID)
        if 'plot outline' in movie:
            return movie['plot outline']
        elif 'plot' in movie and movie['plot']:
            return movie['plot'][0]
    return "No storyline available."

# --- Gemini: Dialogue Generation ---
def generate_dialogue(storyline, characters, length):
    prompt = f"Write a dialogue using the following plot: {storyline}. It should have {characters} characters and max {length} words."
    try:
        response = gen_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# --- Gemini: Scene Description ---
def generate_scene_description(title, chars, storyline):
    prompt = f"Generate a scene description for the movie '{title}' with {chars} characters. Plot: {storyline}"
    try:
        response = gen_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Scene error: {e}"

# --- Vertex AI: Image Generation ---
def generate_image(prompt, location, style):
    full_prompt = f"{prompt}\nLocation: {location}\nStyle: {style}"
    try:
        response = image_model.generate_images(prompt=full_prompt, number_of_images=1)
        return response.images[0]._image_bytes
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None

# --- GUI Callback ---
def on_generate():
    global dialogue_text, scene_description

    selected = movie_combo.get()
    if not selected:
        messagebox.showerror("Error", "Please select a movie.")
        return

    chars = char_spinbox.get()
    length = length_entry.get()
    location = location_entry.get()
    style = style_combo.get()

    storyline = get_movie_storyline(selected)
    summary_label.config(text=f"{storyline}")

    scene_description = generate_scene_description(selected, chars, storyline)
    scene_label.config(text=scene_description)

    dialogue_text = generate_dialogue(storyline, chars, length)
    dialogue_box.delete("1.0", tk.END)
    dialogue_box.insert(tk.END, dialogue_text)

    image_bytes = generate_image(scene_description, location, style)
    if image_bytes:
        with open("generated_image.jpg", "wb") as f:
            f.write(image_bytes)
        img = Image.open("generated_image.jpg").resize((300, 300))
        photo = ImageTk.PhotoImage(img)
        image_label.config(image=photo)
        image_label.image = photo

# --- Save to File ---
def save_dialogue():
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Generated Dialogue:\n\n")
            f.write(dialogue_text)
            f.write("\n\nScene Description:\n\n")
            f.write(scene_description)
        messagebox.showinfo("Success", "Dialogue saved successfully.")

# --- GUI Setup ---
root = tk.Tk()
root.title("PDA-226 IMDB Movie Dialogue Generator")
root.geometry("1000x700")

tk.Label(root, text="Top 10 IMDb Movies").pack()
movie_combo = ttk.Combobox(root, values=fetch_top_movies(), width=80)
movie_combo.pack()

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Number of Characters (2-4):").grid(row=0, column=0)
char_spinbox = ttk.Spinbox(frame, from_=2, to=4, width=5)
char_spinbox.grid(row=0, column=1)

tk.Label(frame, text="Max Dialogue Length:").grid(row=0, column=2)
length_entry = ttk.Entry(frame, width=10)
length_entry.insert(0, "500")
length_entry.grid(row=0, column=3)

tk.Label(frame, text="Location:").grid(row=1, column=0)
location_entry = ttk.Entry(frame, width=30)
location_entry.insert(0, "New York")
location_entry.grid(row=1, column=1)

tk.Label(frame, text="Style:").grid(row=1, column=2)
style_combo = ttk.Combobox(frame, values=["Marvel", "Futuristic", "Cartoon", "Realistic"], width=15)
style_combo.current(0)
style_combo.grid(row=1, column=3)

tk.Button(root, text="Generate Dialogue & Image", command=on_generate).pack(pady=10)

tk.Label(root, text="Storyline:").pack()
summary_label = tk.Label(root, text="", wraplength=900, justify="left")
summary_label.pack()

tk.Label(root, text="Scene Description:").pack()
scene_label = tk.Label(root, text="", wraplength=900, justify="left")
scene_label.pack()

tk.Label(root, text="Generated Dialogue:").pack()
dialogue_box = tk.Text(root, height=10, width=110)
dialogue_box.pack()

tk.Button(root, text="Save Dialogue to File", command=save_dialogue).pack(pady=5)

image_label = tk.Label(root)
image_label.pack()

root.mainloop()
