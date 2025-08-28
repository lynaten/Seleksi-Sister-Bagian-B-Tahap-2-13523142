FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gnucobol \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN cobc -x -o main main.cob

RUN touch input.txt output.txt temp.txt

# COPY app.py index.html main.cob accounts.txt ./

EXPOSE 8000

ENTRYPOINT []
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
