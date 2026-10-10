FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    ca-certificates \
    bash \
    make \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY source/ /work/source/
COPY run-experiments.sh /work/run-experiments.sh
RUN chmod +x /work/run-experiments.sh
CMD ["bash", "-lc", "./run-experiments.sh"]
