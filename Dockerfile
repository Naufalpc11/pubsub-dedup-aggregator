FROM python:3.11-slim

# set working directory
WORKDIR /app

# create non-root user
RUN useradd --create-home --shell /usr/sbin/nologin appuser

# copy dependency dulu (biar cache efisien)
COPY requirements.txt .

# install dependency
RUN pip install --no-cache-dir -r requirements.txt

# copy semua source code
COPY . .

# app files ownership for non-root runtime
RUN chown -R appuser:appuser /app
USER appuser

# expose port
EXPOSE 8080

# run app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]