import re
from unicodedata import normalize
from .remove_stopwords import *
from .remove_special_characters import *
from .remove_numbers import *
from .remove_invalid_words import *
from .remove_punctuations import *
from .text_augmentation import *
import random

def normalize_text(text: str):
    text = normalize('NFC', text)
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    invisible_chars = [
        '\xa0', '\u200b', '\u200c', '\u200d',
        '\u2060', '\ufeff', '\u202f', '\u00ad',
        '\x0b', '\x0c', '\x1f', '\x7f', '\x00'
    ]
    
    for char in invisible_chars:
        text = text.replace(char, '')
        
    for punc in [',', '.', '?', '!', ';']:
        text = text.replace(punc, f' {punc} ')
        
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def shuffle_sentences(text: str) -> str:
    sentences = text.split('.')
    sentences = [sentence.strip() for sentence in sentences]
    random.shuffle(sentences)
    
    return ' . '.join(sentences)

def normalize_word_case(text: str) -> str:
    words = text.split()
    normalized_words = []

    for word in words:
        if word[0].isupper():
            normalized_words.append(word.capitalize())
        else:
            normalized_words.append(word.lower())

    return ' '.join(normalized_words)
