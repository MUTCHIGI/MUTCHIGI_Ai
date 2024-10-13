import os
import shutil
import zipfile
from flask import Flask, request, send_file, jsonify
from pytubefix import YouTube  # pytubefix 사용
import ffmpeg
import subprocess

app = Flask(__name__)

DOWNLOAD_FOLDER = './downloads'
OUTPUT_FOLDER = './output'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# YouTube URL에서 WAV 파일 추출 함수 (pytubefix 사용)
def download_youtube_audio(url, output_path):
    yt = YouTube(url)  # pytubefix YouTube 객체 사용
    audio_stream = yt.streams.filter(only_audio=True).first()
    video_file = audio_stream.download(output_path=output_path)
    wav_file = os.path.splitext(video_file)[0] + '.wav'

    ffmpeg.input(video_file).output(wav_file).run(overwrite_output=True)

    os.remove(video_file)

    return wav_file

# Demucs로 오디오 파일 분리 함수 (자식 프로세스 방식)
def separate_audio_with_demucs(wav_file, output_dir):
    result = subprocess.run(
        ['demucs', '-n', 'mdx', '-o', output_dir, wav_file], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    if result.returncode != 0:
        raise Exception(f"Demucs error: {result.stderr.decode()}")

# Flask API: POST 요청으로 YouTube URL 수신
@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.get_json()
    
    if not data or 'youtube_url' not in data:
        return jsonify({"error": "youtube_url not provided"}), 400

    youtube_url = data['youtube_url']

    try:
        wav_file = download_youtube_audio(youtube_url, DOWNLOAD_FOLDER)
        
        output_dir = os.path.join(OUTPUT_FOLDER, os.path.splitext(os.path.basename(wav_file))[0])
        separate_audio_with_demucs(wav_file, output_dir)

        zip_filename = os.path.join(OUTPUT_FOLDER, 'pseparated_files.zip')
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            mdx_dir = os.path.join(output_dir, 'mdx')
            for root, _, files in os.walk(mdx_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.basename(file))
                    # zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

        return send_file(zip_filename, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 서버 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5843)