

def calculate_video_groups_baselines(vids_df):
    # FINDING baseline values(bare minimum) of: views(median) , seo(median), engagement(median)

    video_type_groups = vids_df.groupby("video_type", observed=False)

    video_groups_details_df = video_type_groups.agg(
                                views_baseline = ('views','median'),
                                views_per_day_baseline = ('views_per_day','median'),
                                seo_baseline = ('title_description_similarity','median'),
                                engagement_baseline = ('engagement_ratio','median')
                                ).reset_index()

    modified_df = vids_df.merge(video_groups_details_df, how = 'left', on = 'video_type')

    modified_df["breakout_index"] = modified_df["views"] / modified_df['views_baseline']
    modified_df["algo_momentum"] = modified_df["views_per_day"] / modified_df['views_per_day_baseline']

    return modified_df

#---

def genre_analysis(master_df, subs = 1):

    modified_df = master_df.copy()

    genres_insight_summary_ls= []
    total_videos = len(modified_df)
    
    groups = modified_df.groupby("genre", observed=False)   # groupby object
    created_group_names_valuecount = groups.size() # pd Series is created holding THE INFORMATION: name of each group & no. of data/content in each
    
    total_groups = len(created_group_names_valuecount) 

    # lets Find aggregate values for each genre and convert it to dataframe for easy access n all
    genre_metrices_overview = groups.agg(
                                        videos_count = ('video_title', 'count'),
                                        breakout_median = ('breakout_index','median'),
                                        algo_median = ('algo_momentum', 'median')
                                    ).reset_index()

    genre_metrices_overview["content_share"] = (genre_metrices_overview["videos_count"] / total_videos) * 100


    genre_analysis_conclusion = """**Channel Strategy:** Your content metrics match balanced structural 
    thresholds without any active identity conflicts across niches. \n However, picking a clear niche helps channel in longrun."""

    if total_groups == 1:
        genres_insight_summary_ls.append('The channel is working on only one genre/niche, lovely!')
        return genres_insight_summary_ls, genre_metrices_overview, genre_analysis_conclusion
    
    elif total_groups > 1:
        baseline_content_share = 100/total_groups   # this gives distribution of each genre in %
        
        high_traction = 1.5
        lower_traction = .5
    
        minimum_content_share = genre_metrices_overview["content_share"].min()
        maximum_content_share = genre_metrices_overview["content_share"].max()

        great_genre_status = False
        great_genre_name_ls = []

        core_genre_name_status = False
        core_genre_name = ''

        worst_genre_name_ls = []

        hidden_good_genre_count = 0
        hidden_bad_genre_count = 0

        for index, data_row in genre_metrices_overview.iterrows():
            content_share = data_row["content_share"]
            breakout_median = data_row["breakout_median"]
            algo_median = data_row["algo_median"]
            genre = data_row["genre"]

            if content_share == maximum_content_share and breakout_median >= high_traction and algo_median >= high_traction:
                            genres_insight_summary_ls.append(f"Core Genre(Primary), Keep grinding : '{genre.capitalize()}'")
                            core_genre_name = genre
                            core_genre_name_status = True
            
            elif content_share == minimum_content_share and breakout_median >= high_traction and algo_median >= high_traction:
                genres_insight_summary_ls.append(f"Seconday Performing Genre : '{genre.capitalize()}'")
                great_genre_name_ls.append(genre)
                great_genre_status = True
                hidden_good_genre_count += 1
        
            elif content_share == maximum_content_share and breakout_median <= lower_traction and algo_median <= lower_traction:
                genres_insight_summary_ls.append(f"Genre Hampering Channel : '{genre.capitalize()}'")
                hidden_bad_genre_count += 1
                worst_genre_name_ls.append(genre)
        
            elif content_share == minimum_content_share and breakout_median <= lower_traction and algo_median <= lower_traction:
                genres_insight_summary_ls.append(f"DROP THIS GENRE : '{genre.capitalize()}'")
                hidden_bad_genre_count += 1
                worst_genre_name_ls.append(genre)
        
            elif maximum_content_share > content_share > baseline_content_share and breakout_median >= high_traction and algo_median >= high_traction:
                genres_insight_summary_ls.append(f"Rising Solid Genre!: Must test this genre and upload more around it : '{genre.capitalize()}'")
                great_genre_name_ls.append(genre)
                great_genre_status = True
                hidden_good_genre_count += 1

            elif hidden_good_genre_count < 2 and (minimum_content_share < content_share < baseline_content_share and breakout_median >= high_traction and algo_median >= high_traction):
                genres_insight_summary_ls.append(f"Another Hidden Good Genre! that's working well... : '{genre.capitalize()}'")
                hidden_good_genre_count += 1
        
            elif hidden_bad_genre_count < 3 and (maximum_content_share > content_share > baseline_content_share and breakout_median <= lower_traction and algo_median <= lower_traction):
                genres_insight_summary_ls.append(f"Stop putting effort in this Genre : '{genre.capitalize()}'")
                hidden_bad_genre_count += 1
                worst_genre_name_ls.append(genre)
        
            elif hidden_bad_genre_count < 4 and (minimum_content_share < content_share < baseline_content_share and breakout_median <= lower_traction and algo_median <= lower_traction):
                genres_insight_summary_ls.append(f"This Genre Is Waste of Time : '{genre.capitalize()}'")
                hidden_bad_genre_count += 1
                worst_genre_name_ls.append(genre)

            

        if core_genre_name_status and hidden_bad_genre_count >= 2:
            genre_analysis_conclusion = f"""STRONG CORE GENRE IDENTIFIED: > >\n
            "{core_genre_name}" genre is showing strong and consistent performance!
            And appears to be the strongest content direction for your channel.\n
            Consider creating more quality content around it.
            At the same time, multiple other genres are showing weak performance and 
            may be diluting your channel's content strategy.\n
            GENRES TO AVOID: {worst_genre_name_ls}"""

        elif great_genre_status and not core_genre_name_status and hidden_bad_genre_count >= 2:
            genre_analysis_conclusion = f"""SOLID CONTENT OPPORTUNITIES IDENTIFIED: > >\n
            Your channel does not yet have one clearly established core genre, but...
            these genres are showing strong performance potential: {great_genre_name_ls}\n
            These categories deserve more attention and further testing. 
            Consider creating more high-quality content around them to determine which one can eventually become your channel's strongest content direction.
            At the same time, several genres are underperforming and may be consuming content effort without producing comparable results.\n
            GENRES TO AVOID: {worst_genre_name_ls}"""

        elif not core_genre_name_status and not great_genre_status and hidden_bad_genre_count >=2:
            genre_analysis_conclusion = f"""YOUR CHANNEL NEEDS A CONTENT STRATEGY RESET: > >\n
            No clear core or high-potential genre was identified, while multiple genres are underperforming.
            You should reconsider where you are investing your content effort.\n
            UNDERPERFORMING GENRES: {worst_genre_name_ls}
            Focus on testing fewer, more promising content categories and monitor their performance before committing heavily to them."""

        elif not core_genre_name_status and not great_genre_status and hidden_bad_genre_count <= 1:
            genre_analysis_conclusion = """NO CORE GENRE IDENTIFIED YET: > [KEEP EXPERIMENTING WITH YOUR EXISTING GENREs]\n
            
            Currently your channel does not show one clearly dominant or exceptionally high-performing genre.
            However, there are NO underperforming genres to indicate a serious content strategy problem.\n
            And, monitor which categories consistently perform better.\n
            Over time, focus more of your content around the genres that demonstrate stronger performance."""

    return genres_insight_summary_ls, genre_metrices_overview, genre_analysis_conclusion

# ---

def video_analysis(master_df_row):
    vid_title = master_df_row['video_title']
    vid_age = master_df_row['days_elapsed']
    
    #baseline > indicates respective median values
    own_algo_momentum, algo_baseline = master_df_row['algo_momentum'], 1.0
    own_breakout_index, breakout_baseline = master_df_row['breakout_index'], 1.0
    own_seo, seo_baseline = master_df_row['title_description_similarity'], master_df_row['seo_baseline']
    own_engagement_ratio, engagement_baseline = master_df_row['engagement_ratio'], master_df_row['engagement_baseline']

    features_high_traction = 1.5
    features_low_traction = 0.5

    seo_baseline_lowest_margin = seo_baseline * .70   # means lower the baseline to 70% bar from seo_baseline's dynamic 100% bar
    engagement_baseline_lowest_margin = engagement_baseline * .50

    if vid_age <= 7:   # YT ALGORITHM REACTION

        if vid_age < 2:
            return f"""FRESH RELEASE RUNNING:\n"{vid_title}" 
                    This video was uploaded just a few hours ago! YouTube's recommendation engine is actively building its initial impression grid. 
                    Check back in 24 hours for your first deep-dive strategic diagnostic scan."""

        else:
            if own_algo_momentum >= features_high_traction and own_engagement_ratio >= engagement_baseline and own_breakout_index >= breakout_baseline:
                return f"""THE VIDEO IS ON FIRE RIGHT NOW:\n"{vid_title}" \n CONGRATS"""
    
            elif own_algo_momentum >= features_high_traction and own_engagement_ratio <= engagement_baseline_lowest_margin:
                return f"""CLICKBAIT / HOOK DISMATCH DETECTED:\n"{vid_title}"\n
                        Your packaging (Thumbnail/Title) is generating massive clicks, but viewers are dropping off instantly!
                        CRITICAL FIX: Review the first (30/60) seconds of your video layout. Ensure your content delivers on the exact
                        promise made in your title hook right away!"""
    
            elif own_algo_momentum <= features_low_traction:
                if own_seo <= seo_baseline_lowest_margin:
                    return f"""SEO NEEDS WORK:\n"{vid_title}"\n Video Title and Video Description are not in sync!
                            Add high-signal keywords in title AND to your top 3 description lines, 
                            NOTE: Keywords must be related to video content!"""
                    
                elif own_engagement_ratio <= engagement_baseline_lowest_margin:
                    return f"""STARTING/HOOK OF VIDEO FAILING:\n"{vid_title}"\n Viewers are clicking but swiping away instantly.
                            Cut out long intros or slow animations in your next upload.
                            TIP: When the channel is new or small, Intro and animations annoys viewers!"""
    
                else:
                    return f"""TRYING TO FIND ITS AUDIENCE:\n"{vid_title}" is trying to clear initial algorithmic hurdles.
                            YT algo is figuring audience for this content..."""
                
            else:
                return f"""STABLE UPLOAD:\n"{vid_title}" is matching baseline expectations."""
    
    elif 7 < vid_age <= 15:   # CONTENT QUALITY AND PACKAGING SIGNAL
        if own_breakout_index >= features_high_traction and own_engagement_ratio >= engagement_baseline and own_algo_momentum >= algo_baseline:
            return f"""GREAT CONTENT:\n"{vid_title}" has cleanly converted its launch momentum into real views count and connection."""

        elif own_breakout_index <= features_low_traction and own_engagement_ratio >= engagement_baseline:
            return f"""CONTENT IS GOOD, BUT THUMBNAIL AND SEO NEEDS WORK:\n"{vid_title}"
                         Change your thumbnail graphic and Rewrite the title hook asap!
                         ALSO Add some keywords, related to content in FIRST 3 lines of Description."""
        else:
            return f"""STABLE VIDEO:\n"{vid_title}"\n
                    Performing as per the algorithm's categorized frame of your content"""

    else:
        if own_breakout_index >= features_high_traction and own_algo_momentum <= features_low_traction and own_engagement_ratio >= engagement_baseline_lowest_margin:
            return f"""EVERGREEN CONTENT:\n"{vid_title}"\n
                        Video is getting recommended search value but its speed has cooled.
                        NOTE: Update its description box with links of your newest/successful videos!"""

        elif own_breakout_index <= features_low_traction and own_algo_momentum <= features_low_traction and own_engagement_ratio <= engagement_baseline:
            return f"""EXPIRED ASSET:\n"{vid_title}"\n
                        Video failed to secure traffic retention. Learn from mistakes and focus on high-performing topics/content."""

        else:
            return f"""BUILDING BLOCK:\n"{vid_title}"\n
                        Helping YT algorithm in need, to figure channel's vision, content, target audience!"""

# ---

def run_analysers(vids_df):

    master_df = calculate_video_groups_baselines(vids_df)

    genres_summary, genre_distribution, genres_conclusion = genre_analysis(master_df)

    #calling function using apply function on master dataframe and storing the suggestions/insights in new col, passing data row wise, use axis = 1.
    master_df["insights_advices"] = master_df.apply(video_analysis, axis = 1)

    return master_df, genres_summary, genre_distribution, genres_conclusion

def best_worst_df(master_df):

    # vids_df_title_dict_map = vids_df['video_title'].to_dict()

    # master_df['original_title'] = master_df.index.map(vids_df_title_dict_map)

    top_5 = master_df.sort_values(['algo_momentum','breakout_index','engagement_ratio','title_description_similarity'], ascending = False).head().reset_index(drop=True)
    worst_5 = master_df.sort_values(['algo_momentum','breakout_index','engagement_ratio','title_description_similarity']).head().reset_index(drop=True)

    return top_5, worst_5, master_df
