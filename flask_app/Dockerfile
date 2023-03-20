FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
EXPOSE 8080

CMD ["bash", "-c", "python app.py & python model.py"]
