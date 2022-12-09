FROM python:3.10

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /code/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

RUN git -C /hsmusic-data pull || git clone https://github.com/hsmusic/hsmusic-data.git /hsmusic-data

COPY . /code/

COPY entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]