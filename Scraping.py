from vertexai.preview.vision_models import ImageGenerationModel
import vertexai
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from imdb import Cinemagoer
from PIL import Image
import io

#yıldızlanmış yerler guı de değiştirilmesi gereken yerler(button tıklanınca gelen özellik gibi)
#yıldızlar da yorum satırlarıyla atılacaktır



genai.configure(api_key="AIzaSyBG3-_ftoEVqejYJQAWezZCWmMjSSBD-M8") #REPLACE WITH YOUR API KEY
model = genai.GenerativeModel('gemini-2.0-flash-lite')

url = "https://www.imdb.com/chart/top/"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.5"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Select top 10 movie rows
movie_rows = soup.select("li.ipc-metadata-list-summary-item")[:10]

movie_links = {}


for i, row in enumerate(movie_rows, start=1):

    title = row.select_one("h3").text.strip()
    year = row.select_one("span.sc-4b408797-8.iurwGb").text.strip()
    rating = row.select_one("span.ipc-rating-star.ipc-rating-star--base.ipc-rating-star--imdb.ratingGroup--imdb-rating").text.strip()

    a_tag = row.select_one("a.ipc-title-link-wrapper")
    full_link = "https://www.imdb.com" + a_tag.get("href")

    movie_links[title] = full_link


    print(f" {title} ({year}) - Rating: {rating}")
    print(f"   Here is the link: {full_link}\n")

print(movie_links)

selected_movie_name = input("select a movie: ")

main_chars = input("how many main characters u need ? ")
maxlength_of_dialog =1500

length_of_dialogue = int(input("How long you want the dialogue ? "))

while(True):
    if length_of_dialogue < 1500:break
    else:
        int(input("enter new Length for dialogue: "))


def get_movie_storyline(title):
    ia = Cinemagoer()
    movies = ia.search_movie(title)

    if movies:
        movie_id = movies[0].movieID
        movie = ia.get_movie(movie_id)

        if 'plot outline' in movie:
            return movie['plot outline']
        elif 'plot' in movie and movie['plot']:
            return movie['plot'][0]

    return "No storyline available"

storyline = get_movie_storyline(selected_movie_name)
print(storyline)





def recommend_movies(storyline,number):
    prompt = f"Write me a new dialogue using {storyline} and {number} main characters to speak between their selfs."
    try:
        responses = model.generate_content(prompt)
        return responses.text
    except Exception as e:
        print(f"Error generating recommendation: {e}")
        return "Sorry, I could not generate movie recommendations at this time."


location = "Where the story lands" #***************
style = "Marvel"#**********************
scene_description = "random atmosphere choices"

stored_dialogue = recommend_movies(storyline, main_chars)
print(stored_dialogue)


#image kısmı kaldı yapman lazım !!!!!!!!!!!!!!

