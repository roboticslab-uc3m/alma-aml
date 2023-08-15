FROM cielavenir/openrave:jammy

ARG SSL_DEBFILE="libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb"
ARG DEBIAN_FRONTEND="noninteractive"
ARG YCM="0.15.3"

RUN apt update \
    && apt install -y --no-install-recommends \
        wget \
    && wget -q http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/$SSL_DEBFILE \
    && dpkg -i $SSL_DEBFILE \
    && rm $SSL_DEBFILE \
    && wget -q https://github.com/robotology/ycm/archive/refs/tags/v$YCM.tar.gz \
    && tar -xzvf v$YCM.tar.gz \
    && mkdir -p ycm-$YCM/build && cd ycm-$YCM/build && cmake .. \
    && make -j$(nproc) && make install
