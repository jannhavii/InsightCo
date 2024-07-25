import json
from flask import Flask, render_template, request, jsonify 
import pandas as pd  
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  
from wordcloud import WordCloud  
import matplotlib.pyplot as plt 
import numpy as np  
import io 
import base64 
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.support.ui import WebDriverWait 
from dotenv import load_dotenv
import os  
import time  
from openai import OpenAI  

app = Flask(__name__)  
static_folder='BE_project//static'  

#Scrapping function
def scrape_youtube_details(url, callback):
    options = webdriver.ChromeOptions()  
    options.add_argument('--headless') 
    driver = webdriver.Chrome(service=Service(executable_path=r"chromedriver-win64\chromedriver-win64\chromedriver.exe"), options=options) 

    driver.get(url)  
    wait = WebDriverWait(driver, 30)  
    time.sleep(2) 

    try:
        pause_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'ytp-play-button')))
        pause_button.click()
        time.sleep(1) 
        pause_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"Error pausing video: {str(e)}")
 
    last_height = 0  
    while True:  
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);") 
        time.sleep(3) 
        new_height = driver.execute_script("return document.documentElement.scrollHeight")  
        if new_height == last_height:  
            break
        last_height = new_height 

    # extract video details 
    video_title_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="title"]/h1/yt-formatted-string')))
    video_title = video_title_element.text
    video_owner_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="text"]/a')))
    video_owner = video_owner_element.text
    comment_count_element = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]')))
    comment_count = comment_count_element.text

    # dataframe to store video details
    video_details_df = pd.DataFrame({
        'Video_Title': [video_title],
        'Video_Owner': [video_owner],
        'Comment_Count': [comment_count]
    })

    # save video details to csv
    desired_directory = r"BE_project\csv_files"
    video_details_file_path = os.path.join(desired_directory, 'youtube_video_details.csv') 
    video_details_df.to_csv(video_details_file_path, index=False)  

    # extract comments
    comments = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content-text"]')))
    comment_list = [comment.text for comment in comments] 

    # store comments in df
    comments_df = pd.DataFrame({ 'Comment': comment_list})

    # save comments to separate csv 
    comments_file_path = os.path.join(desired_directory, 'youtube_comments.csv')
    comments_df.to_csv(comments_file_path, index=False)

    #execute callback function with file paths
    callback(video_details_file_path, comments_file_path)
    # return file paths
    return video_details_file_path, comments_file_path  

load_dotenv()

#Summarization Class
class SummarizationClass:
    # initiate class with api key and openai model
    def __init__(self, apikey, openai_model):
        self.apikey = apikey    
        self.openai_model = openai_model
    # Summarization function
    def summarize_text(self, input_text):
        client = OpenAI(api_key=self.apikey)
        completion = client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": "You are an assistant summarizing YouTube comments. Your goal is to provide a detailed yet concise summary of viewer opinions on a video. Additionally, organize the summary into distinct sections for positive feedback, negative feedback, and suggestions for improvement, each presented as bullet points. Ensure each section contains relevant feedback and suggestions."},
                {"role": "user", "content": "Here are the YouTube comments for summarization:\n{text}".format(text=input_text)}
            ]
        )
        summary_output = completion.choices[0].message.content
        client.close()
        return summary_output

    # Summarization function for overall summary
    def overall_summarize_text(self, input_text):
        client = OpenAI(api_key=self.apikey)
            model=self.openai_model,
            messages=[
                {"role": "system", "content": "You are an assistant summarizing YouTube comments. Your goal is to provide a detailed yet concise summary of viewer opinions on a video. Additionally, organize the summary into distinct sections for positive feedback, negative feedback, and suggestions for improvement, each presented as bullet points. Ensure each section contains relevant feedback and suggestions."},
                {"role": "user", "content": "You are provided with various summarized chunks, all belonging to one single video. Here are the summarized chunks :\n{text}".format(text=input_text)}
            ]
        )
        summary_output = completion.choices[0].message.content 
        client.close()
        return summary_output


# Initialize SummarizationClass with your API key and OpenAI model
openai_model = "gpt-3.5-turbo"
summarization_instance = SummarizationClass(apikey=os.getenv('api_key'), openai_model=openai_model)

def summarize_comments(csv_file_path):
    comments_df = pd.read_csv(csv_file_path)
    comments_df = comments_df.dropna(subset=['Comment'])

    num_comments = len(comments_df) 
    start_idx = 0
    chunk_summaries = []

    while start_idx < num_comments:
        end_idx = min(start_idx + 500, num_comments)
        chunk_comments = comments_df['Comment'].iloc[start_idx:end_idx].tolist()
        remaining_tokens = 4096
        remaining_tokens -= len('\n'.join(chunk_summaries))
        comment_length_limit = remaining_tokens // len(chunk_comments)
        truncated_comments = [comment[:comment_length_limit] for comment in chunk_comments]
        chunk_text = '\n'.join(truncated_comments)
        chunk_summary = summarization_instance.summarize_text(chunk_text)
        chunk_summaries.append(chunk_summary)
        start_idx += 500

        overall_summary = summarization_instance.overall_summarize_text('\n'.join(chunk_summaries))
        print (overall_summary)  #for debugging
        return overall_summary

def parse_summary(overall_summary):
    keywords = ["Positive Feedback:", "Negative Feedback:", "Suggestions for Improvement:"]
    sections = {keyword: [] for keyword in keywords}
    current_section = None

    for line in overall_summary.split('\n'):
        for keyword in keywords:
            if keyword in line:
                current_section = keyword
                break

        if current_section:
            section_content = line.replace(current_section, '').strip()
            if section_content and section_content != "****" and section_content!= "####":
                sections[current_section].append(section_content)
    print(sections) #for debugging
    return sections
        
#route for root URL of flask app
@app.route('/')
def index():
    return render_template('index.html')

#Scrapping route
@app.route('/scrape', methods=['POST'])
def scrape():
    if request.method == 'POST':
        if request.headers['Content-Type'] != 'application/json':  #for debugging
            return jsonify({'error': 'Unsupported Media Type'}), 415
        video_url = request.json.get('video_url')  
        def notify_completion(video_details_file, comments_file): 
            print("Scraping completed. Files generated:", video_details_file, comments_file)  #for debugging
        video_details_file, comments_file = scrape_youtube_details(video_url, notify_completion)
        return jsonify({'message': 'Scraping completed', 'video_details': video_details_file, 'comments': comments_file}) 
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'POST':
        print("Received POST request to /analyze")  # for debugging
        #get csv files using json request
        video_details_csv = request.json.get('video_details')
        comments_csv = request.json.get('comments')
        print(video_details_csv, comments_csv)  # for debugging prints paths
        if not (video_details_csv and comments_csv):
            return jsonify({'error': 'Invalid file paths provided'}), 400
        
        # read csv files
        video_details_df = pd.read_csv(video_details_csv)
        comments_df = pd.read_csv(comments_csv)

        # check for empty file
        if 'Comment' not in comments_df.columns:
            return jsonify({'error': 'Column "Comment" not found in CSV file'}), 400

        # drop rows with NaN values in 'Comment' column
        comments_df.dropna(subset=['Comment'], inplace=True)

        # create a df with 1 column
        comments = comments_df['Comment']
        df = pd.DataFrame(comments, columns=['Comment'])

        #create obj
        analyzer = SentimentIntensityAnalyzer()

        # for sentiment score
        def get_sentiment_score(comment):
            if isinstance(comment, str):  
                sentiment = analyzer.polarity_scores(comment)
                return sentiment['compound']
            return np.nan  
            
        # apply function to each comment
        df['Sentiment_Score'] = df['Comment'].apply(get_sentiment_score)
            
        # categorize comment and store label in new column
        df['Sentiment'] = df['Sentiment_Score'].apply(lambda score: 'positive' if score > 0 else 'negative' if score < 0 else 'neutral')

        # generate pie chart
        sentiment_counts = df['Sentiment'].value_counts()
        plt.figure(figsize=(8, 8))
        plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140, colors=['#66b3ff', '#99ff99', '#ffcc99'])
        plt.title('Sentiment Distribution')

        # encoding pie chart to base64 for display in HTML
        img = io.BytesIO() 
        plt.savefig(img, format='png') 
        img.seek(0)
        pie_chart = base64.b64encode(img.getvalue()).decode()
        
        # generating word clouds
        def generate_wordcloud(sentiment):
            sentiment_comments = ' '.join(df[df['Sentiment'] == sentiment]['Comment'].astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(sentiment_comments)
            img = io.BytesIO()
            wordcloud.to_image().save(img, format='PNG')
            img.seek(0)
            wordcloud_encoded = base64.b64encode(img.getvalue()).decode('utf-8') 
        
        #apply funtion for each sentiment
        positive_wordcloud = generate_wordcloud('positive')
        negative_wordcloud = generate_wordcloud('negative')
        neutral_wordcloud = generate_wordcloud('neutral')

        # extract video details
        video_title = video_details_df['Video_Title'].values[0]
        video_owner = video_details_df['Video_Owner'].values[0]
        comment_count = video_details_df['Comment_Count'].values[0]

        # prepare for passing to result.html
        video_info = {
            'video_title': str(video_title),
            'video_owner': str(video_owner),
            'comment_count': int(comment_count) if isinstance(comment_count, np.int64) else comment_count
            }
        
        #overall summary
        overall_summary = summarize_comments(comments_csv)
        parsed_sections = parse_summary(overall_summary)

        #render result.html with data
        return render_template('result.html', pie_chart=pie_chart, positive_wordcloud=positive_wordcloud,
                        negative_wordcloud=negative_wordcloud, neutral_wordcloud=neutral_wordcloud,
                        video_info=video_info, parsed_sections=parsed_sections)

    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)
