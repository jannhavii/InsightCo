# InsightCo

## Overview
InsightCo is a sentiment analysis tool designed for YouTube content. It leverages advanced Natural Language Processing (NLP) techniques, including the VADER Sentiment Analysis Model, to analyze viewer sentiment from video comments. Additionally, it integrates the ChatGPT API to provide detailed summarizations of the analyzed content. The tool provides comprehensive insights into user feedback, helping content creators, marketers, and researchers understand audience reactions and refine their content strategies and engagement approaches. The user-friendly interface, built with HTML, CSS, and JavaScript, ensures seamless input and visualization of analysis results.

## Features

- **Video Information**: Displays details such as video title, owner, and comment count.
- **Pie Chart**: Displays the percentage of positive, negative, and neutral comments.
- **Overall Summary**: Divides content into sections of positive feedback, negative feedback, and suggestions for improvement.
- **Word Clouds**: Shows positive, negative, and neutral word clouds in a carousel for comparison.

## Technologies

- **Web Scraping and Data Collection**: Utilizes Flask and Selenium for automated extraction of video details and comments from YouTube, storing data in CSV files for analysis.
- **Sentiment Analysis (Vader Sentiment Analyzer)**: Employs VADER and NLTK for tokenization, scoring, and categorizing comments as positive, negative, or neutral.
- **Comment Summarization (ChatGPT API)**: Integrates ChatGPT API using GPT-3.5 Turbo for summarizing YouTube comments and highlighting key points and sentiments.
- **Frontend Development (HTML, CSS, JavaScript)**: Creates an interactive and dynamic user interface to trigger sentiment analysis, visualize results, and access comment summaries.
- **JSON Content Type for Data Transmission**: Utilizes JSON for structured data transmission to ensure compatibility and ease of processing for web scraping and sentiment analysis functionalities.

## Demo Video

[![InsightCo Demo](https://img.youtube.com/vi/MIz8oxSyiSA/0.jpg)](https://www.youtube.com/watch?v=MIz8oxSyiSA)
