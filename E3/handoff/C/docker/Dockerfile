FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      git \
      make \
      bash \
      ca-certificates \
      python3 \
      strace \
      jq \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /lab

COPY E3/handoff/A/ /lab/A/
COPY E3/handoff/B/ /lab/B/
COPY E2/ /lab/E2/
COPY scripts/ /lab/scripts/
COPY E3/handoff/C/docker/run-all.sh /lab/run-all.sh

RUN sed -i 's/\r$//' /lab/A/run-experiments.sh \
 && chmod +x /lab/A/run-experiments.sh

RUN sed -i 's/\r$//' /lab/A/run-experiments.sh /lab/run-all.sh \
 && chmod +x /lab/A/run-experiments.sh /lab/run-all.sh

CMD ["/lab/run-all.sh"]
