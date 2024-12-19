import os
import shutil
import threading
import time
import requests
import shutil
from flask import Flask, send_file, jsonify, request, abort
from pytubefix import YouTube
import ffmpeg
import subprocess
from google.cloud import pubsub_v1
import json

app = Flask(__name__)

# Configuration
DOWNLOAD_FOLDER = './downloads'
OUTPUT_FOLDER = './output'
PROJECT_ID = os.environ['PROJECT_ID']
subscription_path = os.environ['SUBSCRIPTION_PATH']
NOTIFICATION_TOPIC = os.environ['NOTIFICATION_TOPIC']
FILE_DOWNLOAD_ENDPOINT = '/download'

# Ensure directories exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# YouTube audio download function
def download_youtube_audio(url, output_path):
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    video_file = audio_stream.download(output_path=output_path)
    wav_file = os.path.splitext(video_file)[0] + '.wav'
    ffmpeg.input(video_file).output(wav_file).run(overwrite_output=True)
    os.remove(video_file)
    return wav_file

# Demucs separation function
def separate_audio_with_demucs(wav_file, output_dir):
    result = subprocess.run(
        ['demucs', '-n', 'mdx', '-o', output_dir, wav_file], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(output_dir)
        error_message = result.stderr.decode()
        raise Exception("Demucs error: ", error_message)
    result = subprocess.run(
        ['demucs', '-n', 'mdx', '--two-stems=vocals', '-o', output_dir, wav_file], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(output_dir)
        error_message = result.stderr.decode()
        raise Exception("Demucs error: ", error_message)

# Convert WAV files to MP3
def convert_wav_to_mp3(output_dir):
    mp3_files = {}
    for part in ["no_vocals", "vocals", "drums", "bass"]:
        wav_path = os.path.join(output_dir, f"{part}.wav")
        mp3_path = os.path.join(output_dir, f"{part}.mp3")
        ffmpeg.input(wav_path).output(mp3_path, format='mp3').run(overwrite_output=True)
        mp3_files[part] = mp3_path
        os.remove(wav_path)  # Remove the original WAV file after conversion
    return mp3_files

# Send completion notification with combined download links via Pub/Sub
def send_combined_completion_notification(song_id, mp3_files):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, NOTIFICATION_TOPIC)
    
    # Create download links for each part
    download_links = {
        part: f"{FILE_DOWNLOAD_ENDPOINT}/{file_path}"
        for part, file_path in mp3_files.items()
    }
    
    # Create message data with combined download links
    message_data = json.dumps({
        "status": "completed",
        "song_id" : song_id,
        "download_links": download_links
    }).encode("utf-8")
    
    future = publisher.publish(topic_path, data=message_data)
    future.result()
    print(f"Combined notification sent with links {download_links}")

def process_message(youtube_url, song_id):
    try:
        # Set up output directory based on songId
        output_dir = os.path.join(OUTPUT_FOLDER, song_id)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        # Download audio
        wav_file = download_youtube_audio(youtube_url, DOWNLOAD_FOLDER)
        base_file = os.path.splitext(os.path.basename(wav_file))[0]
        separate_audio_with_demucs(wav_file, output_dir)
        output_dir = os.path.join(OUTPUT_FOLDER, song_id, "mdx", base_file)
        print("ouput dir: ", output_dir)
        mp3_files = convert_wav_to_mp3(output_dir)
        send_combined_completion_notification(song_id, mp3_files)
        
        print(f"Processing complete for URL: {youtube_url} with song ID: {song_id}")

    except Exception as e:
        print(f"Error processing URL {youtube_url} with song ID {song_id}: {e}")

def pull_messages():
    subscriber = pubsub_v1.SubscriberClient()

    def callback(message):
        print(f"Received message: {message.data}")
        data = json.loads(message.data.decode('utf-8'))
        
        # Extract youtube_url and songId from the message data
        youtube_url = data.get('youtube_url')
        song_id = data.get('songId')
        
        if youtube_url and song_id:
            process_message(youtube_url, song_id)
            message.ack()
        else:
            print("Invalid message format: Missing youtube_url or songId")
            message.nack()

    # Start the subscription listener
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}...")

    try:
        streaming_pull_future.result()
    except Exception as e:
        print(f"Listening failed: {e}")
        streaming_pull_future.cancel()
        subscriber.close()

# Endpoint to serve the MP3 files
@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join('./', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        abort(404, description="File not found")

# Run Flask server
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server is running and listening to Pub/Sub messages."})

if __name__ == "__main__":
    threading.Thread(target=pull_messages, daemon=True).start()
    app.run(host='0.0.0.0', port=5843)

