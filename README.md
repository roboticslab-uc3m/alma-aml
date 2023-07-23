# alma-top-secret

Copy `aml` from `compiled_aml` here to run.

Working setup on Ubuntu 22.04.1 LTS with Python 3.10.6.

## Docker

Build:

```bash
docker build -t alma-openrave -f ./Dockerfile .
```

Run via Rocker:

- Con NVIDIA:

```bash
rocker --home --user --nvidia --x11 --privileged alma-openrave /bin/bash
```

- Con intel integrated graphics support:


```bash
rocker --home --user --devices /dev/dri/card0 --x11 --privileged alma-openrave /bin/bash
```
