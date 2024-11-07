import os
import requests
import threading
import json
from flask import Flask, jsonify
from google.cloud import pubsub_v1

app = Flask(__name__)

# Configuration
DOWNLOAD_FOLDER = './received_files'
PROJECT_ID = 'capston-test-436509'
NOTIFICATION_SUBSCRIPTION_ID = 'demucs-download-sub'

# Ensure the download folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Download function
def download_file(url, file_name):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded file: {file_name}")
        else:
            print(f"Failed to download file from {url}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading file {file_name} from {url}: {e}")

# Handle notification and download files
def handle_notification(data):
    download_links = data.get("download_links")
    if download_links:
        for part, url in download_links.items():
            file_name = f"{part}.mp3"
            download_file("http://localhost:5843" + url, file_name)

# Pull messages from Pub/Sub for notifications
def pull_notifications():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(PROJECT_ID, NOTIFICATION_SUBSCRIPTION_ID)

    def callback(message):
        print(f"Received message: {message.data}")
        data = json.loads(message.data.decode('utf-8'))
        
        # Handle the notification message
        handle_notification(data)
        message.ack()

    # Start the subscription listener
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for notifications on {NOTIFICATION_SUBSCRIPTION_ID}...")

    try:
        streaming_pull_future.result()
    except Exception as e:
        print(f"Listening failed: {e}")
        streaming_pull_future.cancel()
        subscriber.close()

# Endpoint to check server status
@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Notification receiver server is running and listening for notifications."})

if __name__ == "__main__":
    threading.Thread(target=pull_notifications, daemon=True).start()
    app.run(host='0.0.0.0', port=5850)

