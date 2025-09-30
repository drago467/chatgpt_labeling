
def remove_invalid_words(text: str) -> str:
    words = text.split(' ')
    valid_words = []

    for word in words:
        if not (1 <= len(word) <= 8):
            continue  # Loại từ quá dài hoặc quá ngắn

        # Kiểm tra nếu từ chứa cả chữ cái và số
        has_letter = any(c.isalpha() for c in word)
        has_digit = any(c.isdigit() for c in word)
        if has_letter and has_digit:
            continue  # Loại từ chứa cả chữ cái và số

        valid_words.append(word)

    return ' '.join(valid_words)