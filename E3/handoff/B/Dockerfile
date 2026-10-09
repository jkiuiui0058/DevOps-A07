FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    make

WORKDIR /work
COPY . .

CMD ["bash"]