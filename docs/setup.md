# MUTCHIGI Ai 설정

실행환경: windows 10

## cuda
> cuda 설치 버전 >= 12.6 

- 설치 링크 : https://developer.nvidia.com/cuda-toolkit
- 설치 완료 확인은 cmd에서 아래를 통해 확인해주십시오.
```
  C:\> nvidia-smi
```

> 결과물 : 
```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI your_version           Driver Version: your_version   CUDA Version: 12.6     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
...이하 생략
```

## NVIDIA Container Toolkit

하단 url의 설명을 참고하여 설치하여 주세요 (wsl 2를 이용하는 것을 권장합니다)
 - https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html


## docker container 빌드 및 실행

다운 받은 폴더 최상단(docker-compose.yml)이 있는 폴더에서 cmd를 실행 시킨 후 다음 명령어를 입력해주세요
```
  your_directory:\> docker compose up
```

## 인증
gcp의 IAM에 등록한 서비스 계정으로 키 생성 및 다운로드 후 해당 파일의 경로를 환경 변수 GOOGLE_APPLICATION_CREDENTIALS 에 저장
수동으로 header에 Authorization token을 넣고 싶은 경우 다음 명령어로 토큰 생성 가능
```
  gcloud auth application-default print-access-token
```
gcloud 패키지를 사용하여 서비스 계정과 자동 연결하여 요청 권장



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
PROJECT_ID=$(your_project_id)
TOPIC_NAME=$(your_topic_name)
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
