# Throwaway lab image: the sandboxes measured, pinned. Every download is checked
# against a fixed hash; the adapters record the sha256 of what actually ran.
FROM ubuntu:24.04@sha256:ac3a3d13e90c660a1cb3e89ec695533399f7378dc1ae5fbdc28eb5781d561594
RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
      bubblewrap python3 curl ca-certificates socat ripgrep git procps iproute2 netcat-openbsd xz-utils attr \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1500 agent
RUN cd /tmp && curl -fsSLO https://nodejs.org/dist/v22.20.0/node-v22.20.0-linux-x64.tar.xz \
    && echo "00bbd05e306ea68b6e13e17360d0e2f680b493ef95f2fea1c4296ff7437530bc  node-v22.20.0-linux-x64.tar.xz" | sha256sum -c \
    && tar -xJf node-v22.20.0-linux-x64.tar.xz -C /usr/local --strip-components=1 && rm -rf /tmp/*
RUN npm install -g --silent @anthropic-ai/sandbox-runtime@0.0.81 @openai/codex@0.163.0
RUN curl -fsSL https://github.com/Zouuup/landrun/releases/download/v0.1.17/landrun-linux-amd64 -o /usr/local/bin/landrun \
    && echo "6ada66a06669e8994e174a7271af2db636308e55a0d6ec896cc7d326b46727f6  /usr/local/bin/landrun" | sha256sum -c \
    && chmod 755 /usr/local/bin/landrun
RUN cd /tmp && curl -fsSLO https://github.com/nolabs-ai/nono/releases/download/v0.80.0/nono-v0.80.0-x86_64-unknown-linux-gnu.tar.gz \
    && curl -fsSLO https://github.com/nolabs-ai/nono/releases/download/v0.80.0/SHA256SUMS.txt \
    && grep x86_64-unknown-linux-gnu.tar.gz SHA256SUMS.txt | sha256sum -c \
    && tar -xzf nono-v0.80.0-x86_64-unknown-linux-gnu.tar.gz \
    && find /tmp -name nono -type f -exec install -m755 {} /usr/local/bin/nono \; && rm -rf /tmp/*
