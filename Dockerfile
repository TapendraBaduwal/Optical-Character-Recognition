FROM python:3.8   
WORKDIR /app  
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt requirements.txt 
RUN pip3 install -r requirements.txt 
COPY . .  

CMD ["uvicorn", "fast-api:app", "--proxy-headers","--host", "0.0.0.0", "--port", "80"]  

