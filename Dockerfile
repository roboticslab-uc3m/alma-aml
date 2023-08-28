FROM cielavenir/openrave:jammy

ARG SSL_DEBFILE="libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb"
ARG DEBIAN_FRONTEND="noninteractive"
ARG YCM="0.15.3"
ARG YARP="3.7.2"
ARG OPENRAVE_YARP_PLUGINS_COMMIT="72a5a0cedd644d11b535e7a406f7f2ba4990171a"
ARG TEO_OPENRAVE_MODELS="0.1.0"
ARG TEO_CONFIGURATION_FILES="0.1.0"
ARG OROCOS_KINEMATICS_DYNAMICS="1.5.1"
ARG KINEMATICS_DYNAMICS="0.1.0"

RUN apt update \
    && apt install -y --no-install-recommends \
        wget unzip swig \
    && wget -q http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/$SSL_DEBFILE \
    && dpkg -i $SSL_DEBFILE \
    && rm $SSL_DEBFILE \
    && wget -q https://github.com/robotology/ycm/archive/refs/tags/v$YCM.tar.gz \
    && tar -xzf v$YCM.tar.gz \
    && mkdir -p ycm-$YCM/build && cd ycm-$YCM/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$YCM.tar.gz \
    && wget -q https://github.com/robotology/yarp/archive/refs/tags/v$YARP.tar.gz \
    && tar -xzf v$YARP.tar.gz \
    && mkdir -p yarp-$YARP/build && cd yarp-$YARP/build \
    && cmake .. -DSKIP_ACE=ON \
        -DYARP_COMPILE_BINDINGS=ON -DCREATE_PYTHON=ON -DCMAKE_INSTALL_PYTHON3DIR=/usr/local/lib/python3.10/dist-packages \
    && make -j$(nproc) && make install && cd ../.. && rm v$YARP.tar.gz \
    && wget -q https://github.com/roboticslab-uc3m/openrave-yarp-plugins/archive/$OPENRAVE_YARP_PLUGINS_COMMIT.zip \
    && unzip $OPENRAVE_YARP_PLUGINS_COMMIT.zip \
    && mkdir -p openrave-yarp-plugins-$OPENRAVE_YARP_PLUGINS_COMMIT/build && cd openrave-yarp-plugins-$OPENRAVE_YARP_PLUGINS_COMMIT/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm $OPENRAVE_YARP_PLUGINS_COMMIT.zip \
    && wget -q https://github.com/roboticslab-uc3m/teo-openrave-models/archive/refs/tags/v$TEO_OPENRAVE_MODELS.tar.gz \
    && tar -xzf v$TEO_OPENRAVE_MODELS.tar.gz \
    && mkdir -p teo-openrave-models-$TEO_OPENRAVE_MODELS/build && cd teo-openrave-models-$TEO_OPENRAVE_MODELS/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$TEO_OPENRAVE_MODELS.tar.gz \
    && wget -q https://github.com/roboticslab-uc3m/teo-configuration-files/archive/refs/tags/v$TEO_CONFIGURATION_FILES.tar.gz \
    && tar -xzf v$TEO_CONFIGURATION_FILES.tar.gz \
    && mkdir -p teo-configuration-files-$TEO_CONFIGURATION_FILES/build && cd teo-configuration-files-$TEO_CONFIGURATION_FILES/build && cmake .. \
    && make -j$(nproc) && make install && cd ../.. && rm v$TEO_CONFIGURATION_FILES.tar.gz \
    && wget -q https://github.com/orocos/orocos_kinematics_dynamics/archive/refs/tags/v$OROCOS_KINEMATICS_DYNAMICS.tar.gz \
    && tar -xzf v$OROCOS_KINEMATICS_DYNAMICS.tar.gz \
    && mkdir -p orocos_kinematics_dynamics-$OROCOS_KINEMATICS_DYNAMICS/orocos_kdl/build && cd orocos_kinematics_dynamics-$OROCOS_KINEMATICS_DYNAMICS/orocos_kdl/build && cmake .. \
    && make -j$(nproc) && make install && cd ../../.. && rm v$OROCOS_KINEMATICS_DYNAMICS.tar.gz \
    && wget -q https://github.com/roboticslab-uc3m/kinematics-dynamics/archive/refs/tags/v$KINEMATICS_DYNAMICS.tar.gz \
    && tar -xzf v$KINEMATICS_DYNAMICS.tar.gz \
    && mkdir -p kinematics-dynamics-$KINEMATICS_DYNAMICS/build && cd kinematics-dynamics-$KINEMATICS_DYNAMICS/build \
    && cmake .. -DCREATE_PYTHON=ON -DCREATE_BINDINGS_PYTHON=ON -DCMAKE_INSTALL_PYTHONDIR=/usr/local/lib/python3.10/dist-packages \
    && make -j$(nproc) && make install && cd ../.. && rm v$KINEMATICS_DYNAMICS.tar.gz
