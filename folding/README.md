# alma-aml/folding

Train with labeled data generated via <https://github.com/roboticslab-uc3m/alma-dataset>. You can also directly train with the publicly available dataset <https://doi.org/10.5281/zenodo.14864392>.

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
