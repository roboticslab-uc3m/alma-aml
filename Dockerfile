FROM cielavenir/openrave:jammy

ARG SSL_DEBFILE="libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb"
ARG DEBIAN_FRONTEND="noninteractive"

RUN apt update \
    && apt install -y --no-install-recommends \
        wget \
    && wget -q http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/$SSL_DEBFILE \
    && dpkg -i $SSL_DEBFILE \
    && rm $SSL_DEBFILE