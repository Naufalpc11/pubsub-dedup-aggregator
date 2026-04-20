FROM python:3.11-slim

# set working directory
WORKDIR /app

# copy dependency dulu (biar cache efisien)
COPY requirements.txt .

# install dependency
RUN pip install --no-cache-dir -r requirements.txt

# copy semua source code
COPY . .

# expose port
EXPOSE 8000

# run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]