from flask import Flask, render_template
import requests
import joblib

app = Flask(__name__)

# Load your trained model and vectorizer
model = joblib.load('model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

def fetch_tech_news():
    api_url = "https://newsapi.org/v2/top-headlines?category=technology&apiKey=680e232fbbab48cd8a633909d3ced6eb"
    
    start_time = time.time()  # Start the timer
    response = requests.get(api_url)
    end_time = time.time()  # End the timer
    
    print(f"API Request Time: {end_time - start_time} seconds")  # Print time taken to fetch data
    
    if response.status_code == 200:  # Check if the request was successful
        articles = response.json().get('articles', [])
        print(f"Received {len(articles)} articles")
        for article in articles:
            print(article)  # Inspect the article data
        return articles
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []


@app.route('/')
def home():
    print("Home route accessed")  # This will tell you if the route is being accessed
    try:
        articles = fetch_tech_news()
        print(f"Fetched {len(articles)} articles")  # Check how many articles were fetched
        real_news = []

        for article in articles:
            title = article['title'] or ''
            description = article['description'] or ''
            content = f"{title} {description}"

            # Predict authenticity using the model
            transformed_content = vectorizer.transform([content])
            prediction = model.predict(transformed_content)

            print(f"Prediction: {prediction[0]}")  # Check prediction result

            if prediction[0] == 'REAL':  # If it's classified as real
                real_news.append(article)

        print(f"Found {len(real_news)} real articles.")  # Check how many real articles
        return render_template('news.html', articles=real_news)
    except Exception as e:
        print(f"Error in home route: {e}")
        return "Error occurred while processing news."


if __name__ == "__main__":
    app.run(debug=True)
