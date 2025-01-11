# alma-top-secret

## Setup

### Setup (post-2024-07)

Copy `aml_engine` from `compiled_aml` here to run.

Requisites from `aml`, working setup with:
- Ubuntu 22.04.1 LTS and Ubuntu 22.04.2 LTS (possibly requires libgomp1)
- ~~Python 3.10.6 (possibly requires cffi)~~ Python 3.11.9 (possibly requires cffi), see <https://github.com/roboticslab-uc3m/gymnasium-alma/commit/3a36654ba1c0e706a34cace383f1d35efe1c8632>
- OpenSSL
  - libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb
  - libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb
  - libssl1.1_1.1.1f-1ubuntu2.22_amd64.deb

### Setup (pre-2024-07)

Copy `aml` from `compiled_aml` here to run.

Requisites from `aml`, working setup with:
- Ubuntu 22.04.1 LTS and Ubuntu 22.04.2 LTS (possibly requires libgomp1)
- Python 3.10.6 (possibly requires cffi)
- OpenSSL
  - libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb
  - libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb
  - libssl1.1_1.1.1f-1ubuntu2.23_amd64.deb

## Docker

### OpenRAVE environment, built from this repository (python version for post-2024-07 aml engine)

Build:

```bash
docker build -t alma-openrave -f ./Dockerfile .
```

Tag:

```bash
docker tag alma-openrave ghcr.io/jgvictores/alma-openrave
```

Run via Rocker:

- With NVIDIA:

```bash
rocker --home --user --nvidia --x11 --privileged ghcr.io/jgvictores/alma-openrave /bin/bash
```

- With intel integrated graphics support:


```bash
rocker --home --user --devices /dev/dri/card0 --x11 --privileged ghcr.io/jgvictores/alma-openrave /bin/bash
```

Launch `yarpmanager`:

```bash
cd repos/jgvictores/alma-top-secret/applications/
yarpserver &
yarpmanager
```

In `Applications` you will find the OpenRAVE-based `ironingSim_App`.

### Gym environments which connect to OpenRAVE/real, from external repository (python version for post-2024-07 aml engine)

Run:

```bash
docker run -it --rm -v ${PWD}:/playground ghcr.io/roboticslab-uc3m/alma-playground
```
