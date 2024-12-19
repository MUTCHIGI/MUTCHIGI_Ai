# MUTCHIGI_Ai

MUTCHGI_Ai 는 demucs 모델을 사용하여 MUTCHGI 프로젝트의 음원 분리 요청 처리 및 결과 파일 제공 목적으로 작성된 프로젝트입니다

# 주의 사항

demucs를 자식 프로세스로 작동하기 때문에 song_id를 unique한 폴더 이름 생성에 사용합니다
만약 같은 song_id로 요청한다면 기존 파일은 새로운 song_id로 요청된 파일로 교체됩니다
서버 실행 전에 /downloads 와 /output 폴더 내부 파일을 모두 지우는 것을 권장합니다

## API

### 음악 분리 요청
- url : "https://pubsub.googleapis.com/v1/projects/$PROJECT_ID/topics/$TOPIC_NAME:publish"
- 필요 헤더 : youtube_url : $(your_url), songId : $(your_song_id)
- 주의 : 같은 songId 로 요청 할 경우 기존 파일은 삭제 되고 새로 만들어집니다

### 분리 결과 음원 요청

- pub/sub에서 pull한 메세지
```
"status": "completed",
"song_id": "your_songID",
"download_links": {
    "no_vocals": "/download/${path}/no_vocals.mp3",
    "vocals": "/download/${path}/vocals.mp3",
    "drums": "/download/${path}/drums.mp3",
    "bass": "/download/${path}/bass.mp3"
}
```
- download_links의 각 링크를 요청해서 파일 다운로드 가능 

> curl 예제 (최상위 디렉터리에 있는 test.sh 과 동일)
```
ACCESS_TOKEN=$(gcloud auth application-default print-access-token)
PROJECT_ID=$(your_project_id) # Replace with the actual PROJECT ID
TOPIC_NAME=$(your_topic_name) # Replace with the actual PUB/SUB TOPIC ID
YOUTUBE_URL=$(your_youtube_url)  # Replace with the actual YouTube URL
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
```
