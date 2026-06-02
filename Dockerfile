FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
COPY streamlit_ui/requirements.txt streamlit_ui/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r streamlit_ui/requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_ui/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
