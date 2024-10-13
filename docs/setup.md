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

## API

- url : /process_audio
- 필요 헤더 : youtube_url : $(your_url)

> curl 예제
```
curl -X POST http://localhost:5843/process_audio \
    -H "Content-Type: application/json" \
    -d '{"youtube_url": "Your_url"}' \
    --output out.zip
```
