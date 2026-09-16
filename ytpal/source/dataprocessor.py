import pandas as pd
from deep_translator import GoogleTranslator
import re
import string
import spacy

def time_formatting(duration):  # called at bottom function to sync
    # Edge Case: If it's a live stream is ON or invalid string, return 0 immediately
    if not duration or "P0D" in duration or duration == "PT0S":
        return 0
        
    pattern = re.compile(r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = pattern.match(duration)
    
    if not match:
        return 0

    hours = int(match.group('hours') or 0)
    minutes = int(match.group('minutes') or 0)
    seconds = int(match.group('seconds') or 0)

    duration_in_seconds = (hours * 3600) + (minutes * 60) + seconds
    return duration_in_seconds

# ---

exclude = string.punctuation

def clean_text(text):   # called at bottom function to sync

    if not text or pd.isna(text):
        return ""

    text_str = str(text)

    rmvd_emoji_text = re.sub( r'[\U0001F600-\U0001F64F]|[\U0001F300-\U0001F5FF]|[\U0001F680-\U0001F6FF]|[\U0001F900-\U0001F9FF]|[\u2600-\u27BF]',
                              '', text_str, flags=re.UNICODE, )

    rmvd_url_text = re.sub(r'https?://\S+|www\.\S+', '', rmvd_emoji_text)

    # Remove any residual double/triple whitespace gaps down to a single clean space
    text_rmvd_spacers = re.sub(r'\s+', ' ', rmvd_url_text)

    #text_rmvd_spacers = re.sub(r'[\n\t\r]', '', rmvd_url_text)
    
    cleaner_text = text_rmvd_spacers.translate(str.maketrans('','',exclude))

    return cleaner_text.strip()

# ---

def clean_tags(tags_ls):
    tags_string = ' '.join(tags_ls)
    tags_string = tags_string.lower()
    cleaner_tags = clean_text(tags_string)
    cleaned_tags = cleaner_tags.split()
    return cleaned_tags

#---

def translation(cleaned_text):
    try:
        translator_engine = GoogleTranslator(source = 'auto', target = 'en')
        english_output_text = translator_engine.translate(cleaned_text)
        return english_output_text
    except Exception as network_error:
        return f"Translation Alert! : Couldn't translate data due to : {network_error}"

# ---

stop_words_set = {
    # 1. Standard English Structural Fillers (Articles, Prepositions, Conjunctions)
    " ", "ï", "â€“", "", '️', "-", "–", "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", 
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", 
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", 
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", 
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", 
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", 
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", 
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", 
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", 
    "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", 
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", 
    "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", 
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", 
    "you're", "you've", "your", "yours", "yourself", "yourselves"}

def omit_stop_words(cleaned_and_transltd_text):
    cleaned_text_words_set =  set(cleaned_and_transltd_text.split(' '))
    original_words = cleaned_text_words_set - stop_words_set
    return ' '.join(original_words).strip()

# ---

nlp = spacy.load('en_core_web_md')

def check_similarity(textual_cols_data):

    doc_title = nlp(textual_cols_data["video_title"])
    doc_description = nlp(textual_cols_data["description"])
    # doc_tags = nlp(' '.join(textual_cols_data["tags"]))

    is_title_desc_similar = doc_title.similarity(doc_description) * 100
    # is_title_tags_similar = doc_title.similarity(doc_tags) * 100
    # is_tags_desc_similar = doc_tags.similarity(doc_description) * 100

    return float(is_title_desc_similar) #, is_tags_desc_similar

# ---

def data_formating_processing(vids_df):
    clean_df = vids_df.copy()
    todays_date = pd.Timestamp.now().normalize()

    clean_df["upload_time"] = pd.to_datetime(clean_df["upload_time"])

    clean_df["upload_date"] = pd.to_datetime(clean_df["upload_time"]).dt.date  
    # I Ran .info() after this, and observed this create object column of date
    # Hence, just below line of code...
    clean_df["upload_date"] = pd.to_datetime(clean_df["upload_date"])

    clean_df["days_elapsed"] = (todays_date - clean_df["upload_date"]).dt.days

    clean_df["views"] = clean_df["views"].astype("float").round(2)
    clean_df['likes'] = clean_df['likes'].astype('float').round(2)
    clean_df["comment_count"] = clean_df["comment_count"].astype("float").round(2)

    clean_df["views_per_day"] = (clean_df["views"] / clean_df["days_elapsed"]).astype('float').round(2)
    clean_df["engagement_ratio"] = round(((clean_df['likes'] + clean_df["comment_count"]) / clean_df["views"]) * 100, 2)

    clean_df["duration"] = clean_df["duration"].apply(time_formatting) #calling time formating function
    clean_df["duration"] = clean_df["duration"].astype("float").round(2)

    #calling text cleaning function:
    clean_df['video_title'] = clean_df['video_title'].str.strip().str.lower().apply(clean_text)
    clean_df['description'] = clean_df['description'].str.strip().str.lower().apply(clean_text)

    #calling tag cleaning function:
    clean_df['tags'] = clean_df['tags'].apply(clean_tags)

    # calling translation function:
    # clean_df['video_title'] = clean_df['video_title'].apply(translation)
    # clean_df['description'] = clean_df['description'].apply(translation)

    #calling stop words removing function:
    clean_df['video_title'] = clean_df['video_title'].apply(omit_stop_words)
    clean_df['description'] = clean_df['description'].apply(omit_stop_words)


    return clean_df