import os
import pprint
import pandas as pd
import numpy as np
import re
from collections import namedtuple

# CHANGE THIS FILE PATH TO YOUR FOLDER WITH THE GRAMMAR SPREADSHEETS
loc = (r"C:\Users\rever\OneDrive\Desktop\grammar_project\Spreadsheets")

col_labels = ['phenomenon id', 'description', 'category', 'page number', 'chapter',
    'comment', 'keyword', 'cross-ref/chapter', 'page cross-ref']
    
ColumnLabels = namedtuple('ColumnLabels', (
    'phenomenon_id', 'description', 'category', 'page_number', 'chapter',
    'comment', 'keyword', 'cross_ref_chapter', 'page_cross_ref'))

categories = ['phonetic', 'syllabic', 'grammatical word form', 'lexical word form',
    'word set alternation', 'inflectional affixes', 'derivational affixes', 'gender',
    'syntactic', 'historical', 'orthographic']

def check_column_headers(df):
    # Check column headers for consistency
    cols = df.columns
    for count, col in enumerate(cols):
        if col.lower().rstrip() != col_labels[count]:
            col_label = col_labels[count]
            print(f".....Found inconsistent header for \'{col_label}\' column: {col}")
    
def check_categories(values, cat_dict, desc_values):
    file_cat_dict = {}
    for index, cat in enumerate(values):
        row_num = index + 2
        try:
            lower_cat = cat.lower().rstrip()
        except AttributeError:
            # Case where the category value is not a string
            # and not 0 (the General variation marker)
            if cat != 0:
                # Make sure the rest of the row isn't just empty
                if desc_values[index] is not np.nan:
                    print(f"....Unrecognized category \'{cat}\' found at row {row_num}")
                    cat_dict['totals']['uncategorized'] += 1
                    if 'uncategorized' in file_cat_dict:
                        file_cat_dict['uncategorized'] += 1
                    else:
                        file_cat_dict['uncategorized'] = 1
            else:
                cat_dict['totals']["general"] += 1
                if 'general' in file_cat_dict:
                    file_cat_dict['general'] += 1
                else:
                    file_cat_dict['general'] = 1
        else:
            if lower_cat in categories:
                cat_dict['totals'][lower_cat] += 1
                if lower_cat in file_cat_dict:
                    file_cat_dict[lower_cat] += 1
                else:
                    file_cat_dict[lower_cat] = 1
            else:
                print(f"....Unrecognized category \'{cat}\' found at row {row_num}")
                cat_dict['totals']['uncategorized'] += 1
                if 'uncategorized' in file_cat_dict:
                    file_cat_dict['uncategorized'] += 1
                else:
                    file_cat_dict['uncategorized'] = 1
    return dict(sorted(file_cat_dict.items(), key=lambda item: item[1], reverse=True))

def get_keywords(values, keyword_dict):
    file_keyword_dict = {}
    totals_dict = keyword_dict['totals']
    for index, keywords in enumerate(values):
        if keywords is not np.nan:
            words = re.split(',\s*', keywords)
            for word in words:
                word = word.lower()
                if word in file_keyword_dict:
                    file_keyword_dict[word] += 1
                else:
                    file_keyword_dict[word] = 1
                if word in totals_dict:
                    totals_dict[word] += 1
                else:
                    totals_dict[word] = 1
    return dict(sorted(file_keyword_dict.items(), key=lambda item: item[1], reverse=True))
            

if __name__ == "__main__":
    # Setting up dictionary to print
    cat_dict = {
        'totals': dict.fromkeys(categories, 0),
        'spreadsheets': {}
    }
    cat_dict['totals']['general'] = 0
    cat_dict['totals']['uncategorized'] = 0
    
    keyword_dict = {
        'totals': {},
        'spreadsheets': {}
    }
    
    for filename in os.listdir(loc):
        # DataFrame object
        df = pd.read_excel(os.path.join(loc, filename))
        df.columns = [x.lower() for x in df.columns]

        print(f"\n..Checking for Category names in {filename}")
        cat_values = df.get('category')
        desc_values = df.get('description')
        if cat_values.any() and desc_values.any():
            cat_dict['spreadsheets'][filename] = check_categories(cat_values, cat_dict, desc_values)
        else:
            print("CATEGORY COLUMN DOES NOT EXIST")
        
        print(f"\n..Checking for keywords in {filename}")
        keyword_values = df.get('keyword')
        if keyword_values.any():
            keyword_dict['spreadsheets'][filename] = get_keywords(keyword_values, keyword_dict)
        else:
            print("KEYWORD COLUMN DOES NOT EXIST")
    
        print("\n---\n")
    keyword_dict['totals'] = dict(sorted(keyword_dict['totals'].items(), key=lambda item: item[1], reverse=True))
    cat_dict['totals'] = dict(sorted(cat_dict['totals'].items(), key=lambda item: item[1], reverse=True))
    final_dict = {
        'categories': cat_dict,
        'keywords': keyword_dict
    }
    print(final_dict)