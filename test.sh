ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
PROJECT_ID="capston-test-436509"
TOPIC_NAME="demucs"
YOUTUBE_URL="https://www.youtube.com/watch?v=phuiiNCxRMg&list=PL4fGSI1pDJn6jXS_Tv_N9B8Z0HTRVJE0m&index=8"  # Replace with the actual YouTube URL
SONG_ID="1"  # Replace with the actual Song ID

curl -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "messages": [
          {
            "data": "'"$(echo -n "{\"youtube_url\": \"$YOUTUBE_URL\", \"songId\": \"$SONG_ID\"}" | base64 -w 0)"'"
          }
        ]
      }' \
  "https://pubsub.googleapis.com/v1/projects/$PROJECT_ID/topics/$TOPIC_NAME:publish"