import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from source.analysers import best_worst_df, run_analysers
from source.dataprocessor import check_similarity, data_formating_processing, omit_stop_words
from source.features import run_feature_engineering_functions

from source.scraper import extract_video_details_make_df, extract_videos_ids

load_dotenv()

# 1. Initialize full wide-screen layout
st.set_page_config(page_title="YouTube Channel Auditor", layout="wide")  # Options: "centered" (default) or "wide"

# 2. Inject CSS to remove the default top margin gap completely
st.markdown(
     """
    <style>
    /* Pushes your app content closer to the very top edge safely */
    section.stMain .block-container { 
        padding-top: 1.2rem; 
    }
    /* Forcefully compress the title bottom margin and divider gap spacing */
    .stHeading h1 {
        text-align: center !important;
        margin-bottom: -15px !important;  /* Pushes the divider closer to the title text */
        padding-bottom: 0px !important;
    }
    /* Shrinks the default space above the divider line itself */
    hr {
        margin-top: 5px !important;
        margin-bottom: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("YTPal")

st.markdown(
    """
    <div style="text-align: center; margin-top: 3px; margin-bottom: 12px;">
        <!-- ROW 1: The Main Capitalised Title Header Line -->
        <div style="color: #F8F9FA; font-weight: bold; font-size: 1.2rem; letter-spacing: 1px; margin-bottom: 5px;">
            YouTube Channel Auditor
        </div>
        <span style="color: #FF4B4B; font-weight: bold; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px;">
            Note: 
        </span>
        <span style="color: #A3A3A3; font-size: 0.95rem; font-style: italic;">
            <u>This is a prototype in Phase 1 of live testing...</u>
        </span>
    </div>
    """,
    unsafe_allow_html=True
)

# left_col, mid_col, right_col = st.columns([4,2,4]) # Pass a list of relative integer weights: [2, 5, 3] 
# Look at your code here:
tab1, tab2, tab3, tab4 = st.tabs(["Initiate and Track Audit", "Content Niche Distribution", "BEST & WORST Videos", 'Latest 10 Videos: Insights & Summary'])

left_col, right_col = st.columns([4,6], border=True)

with tab1:
    with left_col:
        st.markdown(
            """
            <style>
            /* Force the parent container padding to shrink to zero */
            [data-testid="stBlock"] {
                padding-top: 0rem !important;
                margin-top: -15px !important; /* Pulls the content up to the top border line */
            }
            /* Controls heading sub-spacing alignments */
            h2.custom-heading {
                text-align: center !important;
                margin-top: -15px !important;
                margin-bottom: -10px !important;
            }
            </style>
            <h2 class="custom-heading">Provide Details Here</h2>
            """, 
            unsafe_allow_html=True
        )

        channel_id_input = st.text_input("Enter YouTube Channel ID:")

        with st.expander("Where to find channel ID?", expanded = False):
            st.write("Go to channel's page  "
            "       >  In description section Click 'more'   "
            "       >  Scroll down till you find 'Share channel' "
            "       > Click 'Share Channel'  >  Click 'Copy channel ID'")
      
    with right_col:

        top_cont = st.container() 
        mid_cont = st.container()
        bot_cont = st.container()    

        if channel_id_input:
            try:
                with top_cont:
                    with st.spinner('Fetching Video details... [Time may vary depending upon channel size]'):
                        channel_overview, videos_id_ls = extract_videos_ids(channel_id_input)

                        channel_name = channel_overview['channel_name']
                        total_subscribers = channel_overview['total_subscribers']
                        total_videos = channel_overview['total_videos']

                        vids_df = extract_video_details_make_df(videos_id_ls)
                        st.success("Videos Data extracted Flawlessly!")

                with mid_cont:
                    
                    col1, col2 = st.columns([5,5])
                    with col1:
                        with st.spinner('Processing videos Data...'):
                            processed_df = data_formating_processing(vids_df)

                            original_clean_df = processed_df.copy()

                            #Computes stop-words on the fly and calculates similarity instantly!
                            processed_df['title_description_similarity'] = processed_df.apply(
                                lambda row: check_similarity({
                                    'video_title': omit_stop_words(row['video_title']), 
                                    'description': omit_stop_words(row['description'])
                                }), 
                                axis=1
                            )
                            # processed_df['video_title'] = processed_df['video_title'].apply(omit_stop_words)
                            # processed_df['description'] = processed_df['description'].apply(omit_stop_words)
                            # processed_df['title_description_similarity'] = processed_df.apply(check_similarity, axis=1)

                            # original_clean_df ['title_description_similarity'] = processed_df['title_description_similarity']

                            st.success("Data processed!")

                    with col2:
                        with st.spinner('Feature Engineering for channel audit...'):
                            modified_df = run_feature_engineering_functions(processed_df) 

                            st.success("Time to analyes your channel's performance!")

                            master_df, genres_summary, genre_distribution, genres_conclusion = run_analysers(modified_df)
                            
                            #modified_df is vids_df
                            top_5_df, worst_5_df, final_df = best_worst_df(master_df)

                with bot_cont:
                    with st.spinner("Tracking Progress"):
                        st.success("Channel Audit Complete")

                st.markdown('---')
                st.info(f"""OVERVIEW:\n
                    Channel name : {channel_overview['channel_name']}\n
                    Current Subscribers : {channel_overview['total_subscribers']}\n
                    This channel has a total of '{channel_overview['total_videos']}' Videos.\n
                    Note: Switch Tabs on top to see details!" \n""")

                st.toast("🏆 Channel Audit Matrix Computed Successfully!", icon="🚀")
                
                # ---------------------------------------------------------------------

                with tab2:
                    st.markdown("### 📡 Niche Topic & Category Strategy Analysis")
                    st.write("This interactive donut visualization charts(Hover to see respective readings)")
                    
                    # Filter out dead niches with 0 content rows to ensure pristine legend spacing
                    clean_chart_df = genre_distribution[genre_distribution["content_share"] > 0]
                    
                    if not clean_chart_df.empty:
                        # Generate a premium modern interactive donut layout pie chart
                        fig = px.pie(
                            clean_chart_df, 
                            values = 'content_share', 
                            names = 'genre', 
                            title = 'Content Share Per Genre (%)',
                            hole = 0.4,  
                            color_discrete_sequence = px.colors.qualitative.Pastel
                        )
                        
                        fig.update_layout(
                            margin = dict(t=50, b=20, l=20, r=20),
                            legend = dict(orientation="h", y=-0.1, x=0.5, xanchor="center")
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

                    st.markdown("##### Quick Summary:")
                    # if not genres_summary:
                    for summary in genres_summary:
                        st.write(summary)

                    st.markdown("#### Genre Assessment Conclusion")
                    st.info(genres_conclusion)

                    st.markdown("<br>", unsafe_allow_html=True)

                # ---------------------------------------------------------------------
                with tab3:
                    st.markdown("### 🏆 Channel's BEST & WORST 5")
                    st.write("Review your absolute highest and lowest performing videos based on multi-factor data evaluation models.")
                    
                    left_table_col, right_table_col = st.columns(2)
                    
                    with left_table_col:
                        st.markdown("#### 🔥 Top 5 High-Velocity Performing Videos")
                        st.dataframe(    
                            top_5_df[['video_title', 'views', 'views_per_day', 'engagement_ratio']], 
                            use_container_width=True,
                            hide_index=True
                        ) 

                    with right_table_col:
                        st.markdown("#### 📉 Bottom 5 Flatlined Videos")
                        # display_info_df = processed_display_df.merge(worst_5_df, how = 'right', on = ['duration', 'views', 'likes', 'comment_count'])
                        st.dataframe(
                            worst_5_df[['video_title', 'views', 'views_per_day', 'engagement_ratio']], 
                            use_container_width=True,
                            hide_index=True
                        )

                # ---------------------------------------------------------------------
                with tab4:
                    st.markdown("### 🎬 Tactical Video Lifecycle Audit Scans")
                    st.markdown("""##### Below is Your channel's Latest 10 Videos SUMMARY - CONCLUSION - FEEDBACK.
                         [Click on Video's Below To See Individual's Details]""")

                    #latest 10 VIDEOS audit - summary - feedback
                    filtered_vids = final_df.sort_values('days_elapsed').head(10)
                    
                    for index, row in filtered_vids.iterrows():
                        advice_text = row['insights_advices']
                        with st.expander(f"Video: {row['video_title'].title()} ({int(row['days_elapsed'])} Days Old)"):
                            col1, col2, col3 = st.columns(3)
                            col1.write(f"📊 **Views:** {int(row['views']):,}")
                            col2.write(f"⚡ **Velocity:** {row['views_per_day']:.1f} VPD")
                            col3.write(f"🪝 **SEO Score:** {row['title_description_similarity']:.1f}%")
                            
                            st.markdown(" ")
                            if "FIRE" in advice_text or "CONGRATS" in advice_text or "GREAT CONTENT" in advice_text:
                                st.success(advice_text)
                            elif "FAIL" in advice_text or "WORK" in advice_text or "EXPIRED" in advice_text or "CLICKBAIT" in advice_text:
                                st.error(advice_text)
                            else:
                                st.info(advice_text)
                    # -------------------------------------------------------------------------            
                        
                    # Error Guard: To check and handle wrong input fields instantly!
            except ValueError as custom_input_error:
                st.error(f"**Invalid Input Entry:** {str(custom_input_error)}")
                st.info("**Pro-Tip:** Make sure you are entering the raw alphanumeric Channel ID string rather than a handle name, video link, or custom URL shortcut text.")
                
            except Exception as global_api_error:
                st.error(f"**API Error Connection Failure:** {str(global_api_error)}")
