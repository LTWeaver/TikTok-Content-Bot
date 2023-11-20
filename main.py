import os
import re
import time
import pyautogui
import keyboard
from clicknium import clicknium as cc, ui, locator
from googleapiclient.discovery import build
from pytube import YouTube

# Set your API key
api_key = 'AIzaSyApz2wAkqFO9al-oR6hhWLAY_iixoCVamk'

# Create a YouTube Data API client
youtube = build('youtube', 'v3', developerKey=api_key)

directory_path = 'scraped_content'

def auto_scrape(topic, count):
    # Define the search query and other parameters
    search_query = topic
    max_results = count

    # Call the search.list method to retrieve matching videos
    search_response = youtube.search().list(
        q=search_query,
        part='id,snippet',
        type='video',  # Only search for videos
        maxResults=max_results
    ).execute()

    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_title = search_result['snippet']['title']

        # Check if the video title contains any special characters
        if any(not (char.isalnum() or char.isspace()) for char in video_title):
            print(f"[*] Skipping video with special characters in the title: {video_title}")
            continue

        # Retrieve video details, including duration
        video_details = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()

        # Get video duration in ISO 8601 format
        duration_iso = video_details['items'][0]['contentDetails']['duration']

        # Use regular expressions to extract minutes and seconds
        match = re.match(r'PT(\d+M)?(\d+S)?', duration_iso)

        if match:
            # Extract minutes and seconds if there is a match
            minutes = int(match.group(1)[:-1]) if match.group(1) else 0
            seconds = int(match.group(2)[:-1]) if match.group(2) else 0

            # Calculate total duration in seconds
            duration_seconds = minutes * 60 + seconds

            # Check if the video is a short based on duration
            if duration_seconds < 60 and duration_seconds != 0:
                try:
                    print("[*] Checking if video already exists...")
                    output_file_path = os.path.join("scraped_content", f"{video_title}.mp4")

                    # Check if the video file already exists
                    if os.path.isfile(output_file_path):
                        print(f"[*] Video already exists: {video_title}")
                    else:
                        print("[*] Downloading...")
                        link = f"https://www.youtube.com/shorts/{video_id}"
                        yt = YouTube(link)
                        video = yt.streams.get_highest_resolution()

                        # Format the video file name
                        video_file_name = f"{video_title}.mp4"

                        # Specify the output file path directly
                        output_file_path = os.path.join("scraped_content", video_file_name)

                        # Ensure the output directory exists, or create it if necessary
                        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                        # Download the video
                        video.download(output_path=os.path.dirname(output_file_path))

                        # Verify that the file is downloaded successfully
                        downloaded_file_path = os.path.join(os.path.dirname(output_file_path), video.title + ".mp4")
                        try:
                            # Rename the downloaded video file
                            os.rename(downloaded_file_path, output_file_path)
                            print(f"[+] Added video to database: {video_title} (ID: {video_id}, Duration: {duration_seconds} seconds)")
                            return video_file_name
                        
                        except Exception as e:
                            print(f"Error: {e}")

                except Exception as e:
                    print(f"[-] Failed to download: {e}")
            else:
                continue
        else:
            print("[-] Unable to extract duration information for the video.")


def upload(path):
    tab = cc.chrome.open("https://www.tiktok.com/upload?lang=en") #opens the web browser on tiktok
    time.sleep(5)
    pyautogui.press('F11')
    tab.find_element(locator.tiktok.one).click(by='mouse-emulation') #starts the mouse emulation and locates the upload button

    time.sleep(2)
    keyboard.write(f"C:\\Users\\josep\\OneDrive\\Desktop\\content_bot\\scraped_content\\{path}")
    pyautogui.press('enter')
    time.sleep(15)
    tab.find_element(locator.tiktok.five).click(by='mouse-emulation')

def main():
    print("""Welcome to LTWeaver's content bot\n\n1) Start generating""")
    select = input(">>>: ")

    if select == '1':
        os.system('cls')
        op1 = input("Topic: ")
        os.system('cls')
        op2 = int(input("Delay between posts (seconds): "))
        os.system('cls')
        print("Starting...: ")
        while True:
            auto_mode(op1, 5000)
            time.sleep(op2)

def list_videos(directory):
    videos = [f.path for f in os.scandir(directory) if f.is_file() and f.name.endswith(".mp4")]
    return videos

def auto_mode(topic, count, max_attempts=5):
    for _ in range(max_attempts):
        print("[*] Attempting to find and upload a video...")
        video = auto_scrape(topic, count)  # Utilize your existing scrape function

        # Check if there are videos in the scraped_content directory
        videos = list_videos(directory_path)
        if videos:
            try:
                # Select the first video for upload
                selected_video = video
                print(f"[*] Found a video: {os.path.basename(selected_video)}")
                
                # Upload the video
                upload(selected_video)
                print("[+] Uploaded video")
                return  # Exit the function once a successful upload is done
            
            except Exception as e:
                print(f"[-] Failed to upload video: {e}")
        else:
            print("[-] No videos found in scraped_content directory. Trying again...")

    print("[-] Auto-mode failed after multiple attempts.")

main()