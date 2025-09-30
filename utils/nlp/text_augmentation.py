import random
import json
import os
from copy import deepcopy

WORDNET: dict = json.load(open(os.path.join(os.path.dirname(__file__), 'wordnet.json'), 'r'))

def get_synonyms(word: str):
    return WORDNET.get(word, [])

def synonym_replacement(text: str, num_augment: int = 100):
    if not text:
        return [text] * num_augment
    
    augmented_texts = []
    alpha = 0.1
    
    words = text.split(' ')
    max_replacement = max(1, int(alpha * len(words)))
    words = list(set(words))

    for _ in range(num_augment):
        text_copy = deepcopy(text)
        random.shuffle(words)
        
        num_replaced = 0
        
        for word in words:
            synonyms = WORDNET.get(word, [])
            
            if len(synonyms) >= 1:
                synonym = random.choice(list(synonyms))
                text_copy = text_copy.replace(word, synonym)
                num_replaced += 1
                
            if num_replaced >= max_replacement: 
                break

        augmented_texts.append(text_copy)

    return augmented_texts[:num_augment]

def random_deletion(text: str, min_words: int = 10, num_augment: int = 100):
    words = text.split(' ')
    if len(words) <= min_words:
        return [text] * num_augment
    
    max_words_to_delete = len(words) - min_words
    num_words_to_delete = list(range(1, min(num_augment, max_words_to_delete) + 1))
    samples_per_num_words = int(num_augment / len(num_words_to_delete)) + 1
    
    augmented_texts = []
    
    for num_words in num_words_to_delete:
        for _ in range(samples_per_num_words):
            indexes_to_delete = random.sample(range(len(words)), k=num_words)
            augmented_texts.append(' '.join([word for index, word in enumerate(words) if index not in indexes_to_delete]))
            
    return augmented_texts[:num_augment]

def word_deletion(text: str, words_to_delete: list[str], min_words: int = 10, num_augment: int = 100):
    words = text.split(' ')
    if len(words) <= min_words:
        return [text] * num_augment
    
    max_words_to_delete = len(words) - min_words
    num_words_to_delete = list(range(1, min(num_augment, max_words_to_delete) + 1))
    samples_per_num_words = int(num_augment / len(num_words_to_delete)) + 1
    
    augmented_texts = []
    
    for num_words in num_words_to_delete:
        for _ in range(samples_per_num_words):
            augmented_texts.append(' '.join([word for word in words if word not in random.sample(words_to_delete, k=min(len(words_to_delete), num_words))]))
            
    return augmented_texts[:num_augment]