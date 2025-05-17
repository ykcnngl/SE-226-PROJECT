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
    if title =="The Dark Knight" : title = "Batman The Dark Knight"
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
    prompt = f"Write a from a plot from some of top 10 imdb movies using: {storyline}. It should have {characters} characters and max {length} words."
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
        img = Image.open("generated_image.jpg")
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

# Create Notebook (tab container)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# --- Tab Frames ---
# 1. Settings Tab
settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text='Settings')

# 2. Storyline Tab
story_tab = ttk.Frame(notebook)
notebook.add(story_tab, text='Storyline')

# 3. Scene Description Tab
scene_tab = ttk.Frame(notebook)
notebook.add(scene_tab, text='Scene')

# 4. Dialogue Tab
dialogue_tab = ttk.Frame(notebook)
notebook.add(dialogue_tab, text='Dialogue')

# 5. Image Tab
image_tab = ttk.Frame(notebook)
notebook.add(image_tab, text='Image')

# --- Settings Tab Widgets ---
tk.Label(settings_tab, text="Top 10 IMDb Movies").pack(pady=(10,5))
movie_combo = ttk.Combobox(settings_tab, values=fetch_top_movies(), width=80)
movie_combo.pack()

frame = ttk.Frame(settings_tab)
frame.pack(pady=10)

# Number of Characters
ttk.Label(frame, text="Number of Characters (2-4):").grid(row=0, column=0, padx=5, pady=5)
char_spinbox = ttk.Spinbox(frame, from_=2, to=4, width=5)
char_spinbox.grid(row=0, column=1, padx=5, pady=5)

# Max Dialogue Length
ttk.Label(frame, text="Max Dialogue Length:").grid(row=0, column=2, padx=5, pady=5)
length_entry = ttk.Entry(frame, width=10)
length_entry.insert(0, "500")
length_entry.grid(row=0, column=3, padx=5, pady=5)

# Location
ttk.Label(frame, text="Location:").grid(row=1, column=0, padx=5, pady=5)
location_entry = ttk.Entry(frame, width=30)
location_entry.insert(0, "New York")
location_entry.grid(row=1, column=1, padx=5, pady=5)

# Style
ttk.Label(frame, text="Style:").grid(row=1, column=2, padx=5, pady=5)
style_combo = ttk.Combobox(frame, values=["Marvel", "Futuristic", "Cartoon", "Realistic"], width=15)
style_combo.current(0)
style_combo.grid(row=1, column=3, padx=5, pady=5)

# Generate Button
ttk.Button(settings_tab, text="Generate Dialogue & Image", command=on_generate).pack(pady=10)

# --- Storyline Tab Widgets ---
tk.Label(story_tab, text="Storyline:").pack(anchor='nw', padx=10, pady=(10,5))
summary_label = tk.Label(story_tab, text="", wraplength=900, justify="left")
summary_label.pack(fill='both', expand=True, padx=10)

# --- Scene Description Tab Widgets ---
tk.Label(scene_tab, text="Scene Description:").pack(anchor='nw', padx=10, pady=(10,5))
scene_label = tk.Label(scene_tab, text="", wraplength=900, justify="left")
scene_label.pack(fill='both', expand=True, padx=10)

# --- Dialogue Tab Widgets ---
tk.Label(dialogue_tab, text="Generated Dialogue:").pack(anchor='nw', padx=10, pady=(10,5))
# Scrollable Text
text_frame = tk.Frame(dialogue_tab)
text_frame.pack(fill='both', expand=True, padx=10)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

dialogue_box = tk.Text(text_frame, height=15, width=110, yscrollcommand=scrollbar.set, wrap="word")
dialogue_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar.config(command=dialogue_box.yview)

# Save Button
ttk.Button(dialogue_tab, text="Save Dialogue to File", command=save_dialogue).pack(pady=5)

# --- Image Tab Widgets ---
image_label = tk.Label(image_tab)
image_label.pack(fill='both', expand=True)

root.mainloop()
