FROM cielavenir/openrave:jammy

ARG SSL_DEBFILE="libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb"
ARG DEBIAN_FRONTEND="noninteractive"
ARG YCM="0.15.3"
ARG YARP="3.7.2"
ARG OYP="0.1.0"
ARG TOM="0.1.0"
ARG TCF="0.1.0"

RUN apt update \
    && apt install -y --no-install-recommends \
        wget swig \
    && wget -q http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/$SSL_DEBFILE \
    && dpkg -i $SSL_DEBFILE \
    && rm $SSL_DEBFILE \
    && wget -q https://github.com/robotology/ycm/archive/refs/tags/v$YCM.tar.gz \
    && tar -xzvf v$YCM.tar.gz \
    && mkdir -p ycm-$YCM/build && cd ycm-$YCM/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$YCM.tar.gz \
    && wget -q https://github.com/robotology/yarp/archive/refs/tags/v$YARP.tar.gz \
    && tar -xzvf v$YARP.tar.gz \
    && mkdir -p yarp-$YARP/build && cd yarp-$YARP/build \
    && cmake .. -DSKIP_ACE=ON \
        -DYARP_COMPILE_BINDINGS=ON -DCREATE_PYTHON=ON -DCMAKE_INSTALL_PYTHON3DIR=/usr/local/lib/python3.10/dist-packages \
    && make -j$(nproc) && make install && cd ../.. && rm v$YARP.tar.gz \
    && wget -q https://github.com/roboticslab-uc3m/openrave-yarp-plugins/archive/refs/tags/v$OYP.tar.gz \
    && tar -xzvf v$OYP.tar.gz \
    && mkdir -p openrave-yarp-plugins-$OYP/build && cd openrave-yarp-plugins-$OYP/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$OYP.tar.gz \
    && wget -q https://github.com/roboticslab-uc3m/teo-openrave-models/archive/refs/tags/v$TOM.tar.gz \
    && tar -xzvf v$TOM.tar.gz \
    && mkdir -p teo-openrave-models-$TOM/build && cd teo-openrave-models-$TOM/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$TOM.tar.gz \
    && wget -q https://github.com/roboticslab-uc3m/teo-configuration-files/archive/refs/tags/v$TCF.tar.gz \
    && tar -xzvf v$TCF.tar.gz \
    && mkdir -p teo-configuration-files-$TCF/build && cd teo-configuration-files-$TCF/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$TCF.tar.gz
