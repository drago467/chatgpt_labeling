import os
import re

with open(os.path.join(os.path.dirname(__file__), 'vietnamese-stopwords.txt')) as file:
    STOPWORDS = [line.strip() for line in file.readlines()]
    
def remove_stopwords(text: str) -> str:
    for word in STOPWORDS:
        text = re.sub(r'\b' + re.escape(word) + r'\b\s*', '', text)

    text = re.sub(r'\s+', ' ', text)
    return text.strip()