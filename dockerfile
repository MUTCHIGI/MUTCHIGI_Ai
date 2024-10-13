FROM nvidia/cuda:12.3.1-base-ubuntu20.04
# Set environment variables for Python
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PATH=/root/.local/bin:$PATH

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    curl \
    ffmpeg \
    && apt-get clean

RUN pip install --upgrade pip

RUN pip install --ignore-installed Flask
RUN pip install --ignore-installed pytubefix
RUN pip install --ignore-installed ffmpeg-python

RUN pip install demucs


WORKDIR /app
COPY . /app

EXPOSE 5843

CMD ["python3", "main.py"]