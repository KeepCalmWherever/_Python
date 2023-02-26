FROM python:3.9-slim as BUILD
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
COPY ./CLI-List-GitHub-Issues.py /src/CLI-List-GitHub-Issues.py
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /src/requirements.txt
ENTRYPOINT [ "python", "/src/CLI-List-GitHub-Issues.py", "https://api.github.com" ]
CMD [""]