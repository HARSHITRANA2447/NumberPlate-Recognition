import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')

# Function to extract text from a URL
def extract_text(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract the title
            title = soup.find('title').get_text() if soup.find('title') else ''
            # Extract the body text
            paragraphs = soup.find_all('p')
            body = ' '.join([p.get_text() for p in paragraphs])
            return title + '\n' + body
        else:
            return ''
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return ''

# Function to clean and tokenize text
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    return tokens

# Function to calculate text analysis metrics
def analyze_text(text, positive_words_path, negative_words_path):
    sentences = sent_tokenize(text)
    words = preprocess_text(text)
    word_count = len(words)
    sentence_count = len(sentences)
    syllable_count = sum([sum(1 for char in word if char in 'aeiou') for word in words])

    # Positive and negative words
    positive_words = set(open(positive_words_path).read().split())
    negative_words = set(open(negative_words_path).read().split())
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words)

    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (word_count + 0.000001)

    avg_sentence_length = word_count / sentence_count if sentence_count != 0 else 0
    avg_word_length = sum(len(word) for word in words) / word_count if word_count != 0 else 0

    # Complex words
    complex_word_count = sum(1 for word in words if sum(1 for char in word if char in 'aeiou') >= 3)
    percentage_complex_words = (complex_word_count / word_count) * 100 if word_count != 0 else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

    # Personal pronouns
    personal_pronouns = sum(1 for word in words if word in ["i", "we", "my", "ours", "us"])

    return {
        "positive_score": positive_score,
        "negative_score": negative_score,
        "polarity_score": polarity_score,
        "subjectivity_score": subjectivity_score,
        "avg_sentence_length": avg_sentence_length,
        "percentage_complex_words": percentage_complex_words,
        "fog_index": fog_index,
        "complex_word_count": complex_word_count,
        "word_count": word_count,
        "syllable_per_word": syllable_count / word_count if word_count != 0 else 0,
        "personal_pronouns": personal_pronouns,
        "avg_word_length": avg_word_length
    }

# Main function
def main():
    # File paths
    input_file = r'C:\Users\harshit rana\OneDrive\Desktop\textextraction\drive-download-20241204T125943Z-001\Input.xlsx'
    output_dir = r'C:\Users\harshit rana\OneDrive\Desktop\textextraction\submitionouput'
    output_file = os.path.join(output_dir, 'Output.xlsx')

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save positive and negative words in the output directory
    positive_words_path = os.path.join(output_dir, 'positive-words.txt')
    negative_words_path = os.path.join(output_dir, 'negative-words.txt')

    with open(positive_words_path, 'w') as pw:
        pw.write("""happy
joyful
excited
""")

    with open(negative_words_path, 'w') as nw:
        nw.write("""sad
angry
upset
""")

    # Load input data
    df = pd.read_excel(input_file)

    # Create a directory to save extracted articles
    articles_dir = os.path.join(output_dir, 'articles')
    os.makedirs(articles_dir, exist_ok=True)

    results = []

    for index, row in df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']

        print(f"Processing URL_ID {url_id}: {url}")

        # Extract and save article text
        article_text = extract_text(url)
        article_path = os.path.join(articles_dir, f"{url_id}.txt")
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(article_text)

        # Analyze text
        metrics = analyze_text(article_text, positive_words_path, negative_words_path)
        results.append({**row, **metrics})

    # Save results to Excel
    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Analysis complete. Results saved to {output_file}")

if __name__ == '__main__':
    main()
