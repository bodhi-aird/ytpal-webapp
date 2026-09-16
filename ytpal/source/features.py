# VIDEO FORMAT TAGGING FEATURE AND COLUMN ON THE BASIS OF VIDEO LENGTH/DURATION
import pandas as pd


def assign_video_type(duration):
    
    if duration <= 120:  # 2 mins in seconds
        return 'short'
    elif 120 < duration <= 1200:  # 20 mins in seconds
        return 'normal'
    elif 1200 < duration <= 3600:
        return 'long'    
    else:
        return 'very long'
        

# ---

# function to identify and mark genre for each video in case of multiple video genres on a channel

def mark_genre(title_description_col):
    # Comprehensive Genre Identifier Tokens tailored specifically for Indian Creators (English + Romanized Hinglish)
    genre_keywords_collection = {
    "film_animation": {
        "trailer", "teaser", "vfx", "cgi", "shortfilm", "movie", "cinema",  "scene", "climax", "blockbuster",
        "filmy", "acting", "film", "film", "documentary", "webseries", "bts", "bloopers", "outtakes",
        "cinematography", "director", "actor", "actress", "audition", "monologue", "dubbed", "remake", "amv",
        "kahani", "storyline", "blooper", "skit", "naatak", "natak", "nautanki", "filmistan", 'blender', 'maya'
        },
    "auto_vehicles": { 
        # Vehicle Elements & Mechanicals
        "suv", "exhaust", "ev", "scooty", "splendor", "sedan", "mileage", "testdrive", "topspeed",
        "hatchback", "supercar", "superbike", "engine", "cc", "torque", "bhp", "modification", "ownership", "drag",
        "turbo", "rpm", "clutch", "brake", "alloys", "tyre", "headlight", "led", "abs",
        "maintenance", "restoration", "facelift"
        },
    "music": { 
        # Audio formats & Releases
        "lyrics", "remix", "lofi", "cover", "singing", "visualizer", "karaoke",
        "dj", "rap", "hiphop", "instrumental", "beat", "singer", "concert", "sufi", "lofi", 
        "album", "unplugged", "acoustic", "mashup", "mixtape", "reverb", "slowed", 
        "guitar", "piano", "flute", "tabla", "harmonium", "synthesizer", "drums", "vocal", 
        "vocals", "pitch", "melody", "rhythm", "composer", "lyricist", "musician", "audios",
        "gana", "geet", "gayan", "gaye", "sangeet", "dhun", "sur", "taal", "raaga", "ragini", 
        "bhajan", "kirtan", "qawwali", "bhangra", "dhol", "baje", "nacho", "thumka"
    },
    "pets_animals": { 
        # Common Domestic & Street
        "dog", "cat", "puppy", "kitten", "pet", "animal", "birds", "parrot", "cow", "vet", 
        "aquarium", "fish", "hamster", "rabbit", "street dog", "stray", "indie dog", 
        "labrador", "pitbull", "german shepherd", "husky", "stray cat", "pigeon",
        # Wildlife & Farm Elements
        "animals", "wildlife", "jungle", "forest", "lion", "tiger", "leopard", 
        "elephant", "snake", "reptile", "monkey", "horse", "buffalo", "goat", "hen", "poultry",
        # Care & Rescue Actions
        "rescue", "funny cat", "funny dog", "adoption",
        "shelter", "training", "dog food", "meow", "bark", "puppies",
        # Hinglish/Local Animal Slang
        "kutta", "kuttiya", "billi", "billa", "gaay", "bhains", "bakri", "tota", "kabootar", 
        "pashu", "pakshi", "janwar", "janwaro", "bachda", "bachra", "pillo", "billi ke bache"
    },
    "sports": { 
        # Main Regional & International Games
        "cricket", "ipl", "football", 
        "dhoni", "kohli", "kabaddi", "basketball", "volleyball", "tennis", "badminton", 
        "chess", "t20", "odi", "wcl", "wpl", "fifa", "athlete", "wicket", "sixer", "sports",
        "pkl", "olympics", "athletics", "mma", "ufc", "boxing", "wrestling", "wwe",
        "bodybuilding", "powerlifting", "calisthenics", "abs", "moto", "akhada", "daud", 
        "khel", "khiladi", "maidan", "gilli", "chakka", "chauka", "bhago", "pahalwan", "kushti"
    },
    "travel_events": { 
        # In-Transit & Lodging Metrics
        "travel", "trip", "tour", "explore", "vlog", "guide", "hotel", "resort", "flight", "trek", "camping",
        "itinerary", "airport", "train", "railway", "trekking", "safari", "mountains", "beach", "hills", 
        "backpacking", "roadtrip", "luggage", "homestay", "tent", "bonfire", "waterfall", "monastery", "zoo",
        "airbnb", "wanderlust", "motovlog", "scenic", "yatra", "ghoomne", "ghoomna", "safar", "outing", "nightout",
        "musafir", "darshan", "kedarnath", "manali", "pahad", "pahado", "samundar", "videsh", "bhatakna"
    },
    "gaming": { 
        # Game Titles & Ecosystems
        "gaming", "gameplay", "freefire", "pubg", "bgmi", "gta", "minecraft", "ps5", "xbox", "nintendo", 
        "gamer", "cod", "fortnite", "playstation", "rtx", "graphics", "emulator", "1v1", "1v4", "solosquad" 
        "montage", "clutch", "playing", "walkthrough", "palythrough", "trolling", "squads", "play", "ranked",
        "noob", "pro", "aimbot", "headshot", "ping", "frag", "killmontage", "activision",
        "bande", "enemy", "maro", "hotdrop", "goli", "revive", "bachao", "easports",
        "booyah", "pubg", "killed", "apex", "horror", "dota", "lol", "codm", "krafton", "supercell",  
    },
    "people_vlogs_howto": {
        'anniversary', 'awareness', 'baje', 'bazaar', 'behen', 'bhai', 'bhangra', 'birthday',
        'celebration', 'charity', 'clean up', 'clubbing', 'cooking', 'craft', 'diet', 'diy', 'donation', 'dost', 'dosto', 'dukaan',
        'environment', 'fashion', 'fitness', 'fundraiser', 'gifting', 'grooming', 'hairstyle', 'house', 'humanity', 'kaise banaye',
        'khana', 'kitchen', 'lifestyle', 'madad', 'makeup', 'marriage', 'minivlog', 'mumbai', 'mummy', 'nacho', 'ngo', 'outfit',
        'papa', 'parents', 'parivar', 'podcastghar', 'rasoi', 'recipe', 'rescue', 'rishtedar', 'saree', 'shaam', 'shadi',
        'social', 'style', 'village', 'vlogger', 'vlogging', 'vlogs', 'wedding', 'welfare', 'fest', 'festival', 'magic'
    },
    "comedy": {
        'bakchod', 'bakchodi', 'chutkula', 'comedy', 'entertainment', 'gags', 'gajab', 'gazab', 'haso',
        'hilarious', 'humor', 'joke', 'joker', 'kamal', 'lmao', 'lol', 'lolwa', 'majak', 'mame', 'mazaak', 'meme', 'memes',
        'mimicry', 'parody', 'prank', 'pranking', 'reacting', 'roast', 'roasted', 'roasting', 'sarcasm', 'satire', 'smilehasna',
        'spoof', 'stand-up', 'standup', 'vine', 'vines'    
    },
    "news_politics": { 
        # Geopolitics & Governance Pillars
        'bill', 'bjp', 'cm', 'congress', 'constitution', 'country', 'court', 'crud', 'debate', 'economy', 'election',
        'gandhi', 'gdp', 'geopolitics', 'government', 'investigation', 'law', 'leader', 'modi', 'navy', 'neta', 'parliament', 'pm',
        'policy', 'politics', 'power', 'prime minister', 'protest', 'relations', 'rights', 'scandal', 'stock'
    },
    "science_tech": {
        'algorithms', 'angular', 'ansible', 'api', 'app', 'assembly', 'aws', 'azure', 'backend', 'bash', 'bitbucket',
        'bootstrap', 'c#', 'c++', 'ci/cd', 'deploy', 'cicd', 'claude', 'cloud', 'code', 'coding', 'command', 'computing', 'cpp',
        'crud', 'css', 'database', 'debugging', 'dev', 'developer', 'development', 'devops', 'django', 'docker', 'dsa', 'engineer', 
        'engineering', 'exception', 'expressjs', 'fastapi', 'firebase', 'flask', 'flutter', 'frontend', 'fullstack', 'gcp', 'git', 
        'github', 'gitlab', 'golang', 'graphql', 'hackathon', 'hosting', 'html', 'java', 'javascript', 'jenkins', 'json', 'jwt', 
        'k8s', 'keras', 'kotlin', 'kubernetes', 'langchain', 'language model', 'laravel', 'leetcode', 'linux', 'llm', 'machine', 
        'matplotlib', 'microservices', 'ml', 'mongodb', 'mvc', 'mysql', 'netlify', 'network', 'neural', 'nextjs', 'nlp', 'nodejs',
        'numpy', 'ollama', 'openai', 'pandas', 'pcreact', 'php', 'postgresql', 'programming', 'prompt', 'python', 'pytorch', 'rag', 'react', 
        'reactjs', 'redis', 'refactoring', 'ruby', 'rust', 'science', 'scikit', 'shell', 'scripting', 'software', 'sql', 'sqlite',
        'structures', 'supabase', 'sysadmin', 'tailwind', 'terminal', 'terraform', 'transformers', 'typescript', 'ubuntu', 'vercel',
        'vscode', 'vue', 'web', 'whatsapp', 'nvidia', 'built', 'robot', 'machine','technology', 'cyber', 'electronics', 'Firmware',
        'raspberry', 'gadgets'
        },
    "educational_study": {
        'academic', 'accounts', 'recall', 'admissions', 'algebra', 'arts', 'assignment', 'banking', 'bca', 'biology', 'upsc', 
        'board', 'boards', 'btech', 'calculus', 'campus','cat exam', 'cbse','cgl', 'chapter','chemistry', 'civics',
        'class', 'classmate','clat', 'coaching','coding', 'college','commerce', 'concentration','cse', 'cto','curriculum', 'degree',
        'diploma', 'documentation','economics', 'exam', 'fail','focus', 'gate','geography', 'geometry','gmat', 'graduation',
        'grammar', 'gre','guidance', 'homework','ias', 'icse', 'ielts', 'internship', 'ips', 'jee','junior dev', 'kaksha',
        'kitab', 'lecture', 'lesson','library', 'likho', 'literature', 'mann', 'math', 'mathematics', 'maths', 'mca', 'vidyarthi',
        'memorize', 'mock','module', 'naukri', 'ncert', 'nda', 'neet', 'notes', 'notetaking', 'owl', 'padhai', 'padho',
        'pariksha','pass', 'passing marks', 'physics', 'placement', 'political', 'pomodoro', 'portfolio', 'prep', 'vocabulary',
        'productivity', 'professor', 'pustak', 'pyq', 'rattamar', 'repetition', 'report card', 'revision','roadmap', 'samjho','sample', 'sarkari',
        'sat', 'scholarship', 'school', 'schooling', 'science', 'seekho', 'semester', 'shiksha','shikshak', 'source', 'spaced', 'ssc', 'student',
        'study', 'subject', 'syllabus', 'taiyari', 'teacher', 'tech ', 'tech lead', 'textbook', 'timetable', 'toefl', 'topper', 'tuition', 'university',
            
    }
    
    }

    genric_words_set = {'Blogging', 'diy', 'make', 'abs', 'accident', 'action', 'active', 'ai', 'animation', 'attack', 'audio', 'back', 'band',
        'behind', 'bhago', 'big', 'bike', 'booking', 'boss', 'boundary', 'boy', 'breakdown', 'breaking', 'budget', 'bug', 'build', 'bullet',
        'camera', 'car', 'cardio', 'case', 'celebrity', 'century', 'chalaan', 'chalana', 'challenge', 'chase', 'chatgpt', 'chill',
        'clean', 'clutch', 'commentary', 'comparison', 'compilation', 'computer', 'condition', 'crash', 'crime', 'cup', 'custom',
        'cycle', 'daily', 'dangal', 'dark', 'data', 'day', 'deep', 'design', 'desk', 'digital', 'drop', 'duo', 'easter', 'eggs', 'emi',
        'emotional', 'end', 'ending', 'enemy', 'ep', 'episode', 'error', 'event', 'explained', 'family', 'features', 'fire', 'first',
        'fix', 'force', 'free', 'front', 'full', 'fun', 'funny', 'gaadi', 'gadget', 'gadi', 'game', 'get', 'gift', 'girl', 'glitch', 'goal', 
        'grwm', 'guide', 'gym', 'haar', 'hack', 'hacker', 'hacking', 'hacks', 'hand', 'handling', 'help','war', 'work', 'workout', 'world',
        'hero', 'high', 'highlights', 'historical', 'history', 'home', 'hostel', 'how', 'international','viral', 'visa', 'vlog', 'vs'
        'interview', 'ipad', 'jeet', 'job', 'kaise', 'laptop', 'large', 'laws', 'league', 'learning', 'life', 'live', 'graphics',
        'local', 'loot', 'market', 'match', 'material', 'meetup', 'mic', 'microphone', 'minister', 'mobile', 'modded',
        'modify', 'moment', 'monument', 'morning', 'motivation', 'motorcycle', 'muscle', 'music', 'nature', 'new', 'news', 'night',
        'open', 'order', 'out', 'packing', 'party', 'passport', 'pc', 'penalty', 'performance', 'personal', 'phone', 'place', 'plan', 
        'podcast', 'police', 'poor', 'price', 'project', 'protein', 'push', 'race', 'racing', 'rank', 'rasta', 'reaction',
        'ready', 'reality', 'recall', 'red', 'rest', 'review', 'road', 'room', 'routine', 'run', 'rush', 'sasta', 'scam', 'scene',
        'score', 'season', 'second', 'series', 'server', 'service', 'settings', 'setup', 'shopping', 'short', 'show', 'showcase',
        'showroom', 'single', 'skill', 'smartwatch', 'solo', 'song', 'speedrun', 'spoiler', 'sport', 'station', 'story', 'stream',
        'studio', 'stunt', 'supplements', 'support', 'supreme', 'surpirse', 'system', 'talk', 'tech', 'temple', 'test',
        'theater', 'theory', 'ticket', 'tips', 'tools', 'tour', 'tournament', 'track', 'training', 'trend', 'trick', 'troll',
        'truck', 'unboxing', 'used', 'video', 'villain', 'playlist', 'model'}

    title_words_set = set(title_description_col["video_title"].split())
    description_words_set = set(title_description_col["description"].split())
    combined_words_set = title_words_set | description_words_set

    match_words_in_genres = {}

    for genre, keywords in genre_keywords_collection.items():
        matching_words = keywords & combined_words_set
        matching_words_count = len(matching_words)

        unmatched_words = combined_words_set - matching_words
        
        # match_words_in_genres[genre] = matching_words_count
        main_genre_words_score = matching_words_count * 3

        # match_words_in_genres['main_score'] = main_genre_words_score

        minor_genre_words_score = len(unmatched_words & genric_words_set)
        # match_words_in_genres['generic_score'] = minor_genre_words_score

        total_score = main_genre_words_score + minor_genre_words_score
        # match_words_in_genres['score'] = total_score
        match_words_in_genres[genre] = total_score


    genre = 'entertainment'
    # words_threshold = 3     #setting minimum threshold to qualify as specific genre else 'entertainment'
    score_threshold = 3
    
    for genre_name, score in match_words_in_genres.items():
        if score >= score_threshold:
            score_threshold = score
            genre = genre_name

    return genre

# ---

def values_normalizer(vids_df):
    modified_df = vids_df.copy()
    # Define the normalizer with explicit index coordinates
    scale_normalizer = pd.Series(((modified_df.index + 1) / len(modified_df)) * 0.000001, index=modified_df.index)

    target_cols = ['views', 'likes', 'comment_count', 'views_per_day']

    for col in target_cols:
        is_value_zero = (modified_df[col] == 0) | (modified_df[col] == 0.0)
        # >>>>> HIDDEN Pandas rule: A Series of True/False values can act as a dynamic label filter inside .loc
        
        if is_value_zero.sum() == 0:
            continue
            
        modified_df.loc[is_value_zero, col] += scale_normalizer[is_value_zero]

    return modified_df

# ---

def run_feature_engineering_functions(vids_df):
    """Executing all loose features processing functions inside this function"""
    modified_df = vids_df.copy()

    # Tagging video type on the basis of duration by applying function ON Column.
    modified_df["video_type"] = modified_df["duration"].apply(assign_video_type).astype('category')

    # Tagging Genre to each video, going row-by-row
    modified_df["genre"] = modified_df[["video_title", "description"]].apply(mark_genre, axis=1).astype("category")

    # Normalizer function to omit zero with almost negligible dynamic no. to safely clear zero values causing issues
    modified_df = values_normalizer(modified_df)

    return modified_df