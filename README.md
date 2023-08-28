# alma-top-secret

Copy `aml` from `compiled_aml` here to run.

Requisites from `aml`, working setup with:
- Ubuntu 22.04.1 LTS and Ubuntu 22.04.2 LTS (possibly requires libgomp1)
- Python 3.10.6 (possibly requires cffi)
- OpenSSL
  - libssl1.1_1.1.1f-1ubuntu2.17_amd64.deb
  - libssl1.1_1.1.1f-1ubuntu2.19_amd64.deb

## Docker

Build:

```bash
docker build -t alma-openrave -f ./Dockerfile .
```

Run via Rocker:

- With NVIDIA:

```bash
rocker --home --user --nvidia --x11 --privileged alma-openrave /bin/bash
```

- With intel integrated graphics support:


```bash
rocker --home --user --devices /dev/dri/card0 --x11 --privileged alma-openrave /bin/bash
```
