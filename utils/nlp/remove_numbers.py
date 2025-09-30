import re


def remove_numbers(text: str) -> str:
    pattern = r'''
        ((?:\d{1,3}(?:[.,]\d{3})*[.,]\d+)  # Số thực có phần thập phân
        |                                        # hoặc
        (?:\d+[.,]\d+))                     # Số thực dạng 123,45 hoặc 123.45
        |                                        # hoặc
        ((?:                                # Số nguyên:
            \d{1,3}(?:[.,]\d{3})+               # Có dấu phân cách phần nghìn (ít nhất 1 dấu)
            |                                    # hoặc
            \d+                                  # Không có dấu phân cách
        ))
    '''
    pattern = re.compile(pattern, re.X)
    
    text = re.sub(pattern, ' ', text)
    text = re.sub(r'\bM{0,3}(CM|CD|D?C{0,3})?(XC|XL|L?X{0,3})?(IX|IV|V?I{0,3})\b', ' ', text)
    return re.sub(r'\s+', ' ', text) 
    
def convert_numbers(text: str) -> str:
    import re

    pattern = r'''
        ((?:\d{1,3}(?:[.,]\d{3})*[.,]\d+)  # Số thực có phần thập phân
        |                                        # hoặc
        (?:\d+[.,]\d+))                     # Số thực dạng 123,45 hoặc 123.45
        |                                        # hoặc
        ((?:                                # Số nguyên:
            \d{1,3}(?:[.,]\d{3})+               # Có dấu phân cách phần nghìn (ít nhất 1 dấu)
            |                                    # hoặc
            \d+                                  # Không có dấu phân cách
        ))
    '''
    pattern = re.compile(pattern, re.X)
    
    text = re.sub(pattern, ' number ', text)
    text = re.sub(r'^M{0,3}(cm|cd|d?c{0,3})?(xc|xl|l?x{0,3})?(ix|iv|v?i{0,3})?$', ' number ', text)
    return re.sub(r'\s+', ' ', text)
    
    