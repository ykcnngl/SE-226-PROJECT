import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from imdb import Cinemagoer


genai.configure(api_key="YOUR-API-KEY") #REPLACE WITH YOUR API KEY
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







model = genai.GenerativeModel('gemini-2.0-flash-lite')



def get_movie_storyline(title):
     ia = Cinemagoer()
     movies = ia.search_movie(title)
     if movies:
         movie = ia.get_movie(movies[0].movieID)
         if 'plot outline' in movie:
             return movie['plot outline']
     return "No storyline"


def recommend_movies(genre, mood):
    prompt = f"I want to watch a movie.  I'm in the mood for something {mood} and in the {genre} genre. Please give me three movie recommendations."
    try:
        responses = model.generate_content(prompt)
        return responses.text
    except Exception as e:
        print(f"Error generating recommendation: {e}")
        return "Sorry, I could not generate movie recommendations at this time."

# Example usage:
genre = "comedy"
mood = "lighthearted"
recommendations = recommend_movies(genre, mood)
print(recommendations)

