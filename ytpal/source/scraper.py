import os
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd


load_dotenv()

# Initializing googleapi client to scrap video details
def initiate_scraper_object():
    api_key = os.getenv('API_KEY')
    return build('youtube', 'v3', developerKey = api_key)
    
def extract_videos_ids(channel_id):

    youtube = initiate_scraper_object()

    request = youtube.channels().list(part = 'snippet, contentDetails, statistics', id = channel_id)

    channel_data_response = request.execute()

    #IF USER ENTERS INVALID CHANNEL ID:
    # Catch an empty items list instantly before getting error and crashing code
    if not channel_data_response.get("items"):
        raise ValueError("The provided YouTube Channel ID does not exist or has been deleted.")
    
    channel_overview = {'channel_name': channel_data_response["items"][0]["snippet"]["title"] ,
                            'total_views': channel_data_response["items"][0]["statistics"]["viewCount"],
                            'total_subscribers': channel_data_response["items"][0]["statistics"]["subscriberCount"],
                            'total_videos': channel_data_response["items"][0]["statistics"]["videoCount"],
                            'videos_list_id': channel_data_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"],
                            'description' : channel_data_response["items"][0]["snippet"]["description"]
                        }

    videos_ids_ls = []

    next_page_token = None
    new_page_available = True

    while new_page_available:
    
        video_data_request = youtube.playlistItems().list(part = 'contentDetails', 
                                                        playlistId = channel_overview['videos_list_id'], 
                                                        maxResults = 30, 
                                                        pageToken = next_page_token)
        video_data_response = video_data_request.execute()

        # Extracting the inpayload container items safely
        # response_items = video_data_response.get("items", [])
        
        # looping strictly over the ACTUAL returned rows...
        for vid_data in video_data_response["items"]:
            video_id = vid_data["contentDetails"]["videoId"]
            if video_id not in videos_ids_ls:
                videos_ids_ls.append(video_id)
            else:
                continue

        next_page_token = video_data_response.get("nextPageToken")

        # If the API response doesn't have token for next page, we reached the end of the videos list
        if not next_page_token:
            print('All videos detials fetched successfully!')
            new_page_available = False


    return channel_overview, videos_ids_ls

def extract_video_details_make_df(videos_ids_ls):

    youtube = initiate_scraper_object()

    all_videos_details = []

    for i in range(0, len(videos_ids_ls), 50):  # SLICE and use 50 videos ids in single API request to improve speed and
        # YT API Allows max 50 videos per page/api request
        bulk_ids = videos_ids_ls[i:i+50]
        
        # Convert the list array into a single comma-separated string to pass in request
        comma_separated_ids = ",".join(bulk_ids)

        video_details_request = youtube.videos().list(part='snippet, contentDetails, player, statistics, liveStreamingDetails',
                                                            id = comma_separated_ids)
        video_details_response = video_details_request.execute()

        # Crash Guard: If the video was deleted or made private mid-run, skip it
        if not video_details_response.get('items'):
            continue

        
        for in_video_data in video_details_response['items']:
            
          #  in_video_data >> ANCHOR: cuz we have to go inside this part for every details, so to avoid repetition!

            # THE LIVE BROADCAST GUARD:
            # YouTube API explicitly tags active streams as 'live' and scheduled streams as 'upcoming'
            broadcast_status = in_video_data["snippet"].get("liveBroadcastContent", "none")
            if broadcast_status in ["live", "upcoming"]:
                print(f"Skipping active live/scheduled stream: {in_video_data['snippet']['title']}")
                continue # Instantly skips the rest of this loop pass

            #for details in video_details_response:
            vid_title = in_video_data["snippet"]["title"]
            
            # Check if the video contains live stream processing metrics.
            # If yes, extract 'actualStartTime' to bypass the scheduling placeholder trap!
            if 'liveStreamingDetails' in in_video_data:
                vid_upload_time = in_video_data['liveStreamingDetails'].get('actualStartTime', in_video_data['snippet']['publishedAt'])
            else:
                vid_upload_time = in_video_data['snippet']['publishedAt']
            
            vid_duration = in_video_data["contentDetails"]["duration"]
            vid_views = in_video_data["statistics"].get("viewCount", 0) # in case creator hid these data
            vid_likes = in_video_data["statistics"].get("likeCount", 0)
            vid_comment_count = in_video_data["statistics"].get("commentCount", 0)
            vid_tags = in_video_data["snippet"].get("tags", []) # Fallback to empty list if no tags exist
            vid_description = in_video_data["snippet"]["description"]

            all_videos_details.append({'video_title': vid_title,
                                        'upload_time': vid_upload_time,
                                        'duration': vid_duration,
                                        'views': vid_views,
                                        'likes': vid_likes,
                                        'comment_count': vid_comment_count,
                                        'tags': vid_tags,
                                        'description': vid_description})

    
    return pd.DataFrame(all_videos_details)


# NOTE:
# These two functions connect perfectly in app.py
# Inside your app.py execution pipeline block:

# # 1. First function accepts the raw text ID and returns a simple list of codes
# harvested_ids_list = extract_videos_ids('UC4EbRppBvaHjVT3ys-9eGDg')

# # 2. Second function picks up that list array and outputs your raw master dataframe!
# vids_df = extract_video_details_make_df(harvested_ids_list)
