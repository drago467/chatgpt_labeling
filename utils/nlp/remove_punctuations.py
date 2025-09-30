import re

def remove_punctuations(text: str) -> str:
    characters = [',', '.', '?', '!', ';']

    pattern = f'[^{"".join(map(re.escape, characters))}]'
    text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()