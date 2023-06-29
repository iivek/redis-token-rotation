<!-- Add your project logo or banner -->

[//]: # (<p align="center">)
[//]: # (  <img src="https://your-image-url.com/your-logo.png" alt="Project Logo" width="400">)
[//]: # (</p>)

<!-- Add your project name and tagline -->
<h1 align="center">TokenCycle</h1>
<p align="center">Custom token lifecyle and rotation in Redis

<!-- Add badges, such as build status or version badges -->
<p align="center">

[//]: # (  <img src="https://img.shields.io/travis/username/repo.svg" alt="Build Status">)
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/version-0.1-green.svg" alt="Version">

[//]: # (  <img src="https://img.shields.io/npm/dm/package.svg" alt="Downloads">)
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">

[//]: # (  <img src="https://img.shields.io/github/contributors/username/repo.svg" alt="Contributors">)
</p>

<!-- Describe your key features -->
## About

- Made for customized app authorization that uses refresh tokens
- Implements token generation, validation, rotation and token reuse detection
- Uses an async Redis client. 

<!-- Provide instructions on how to install and run your project -->
## Installation

1. Clone the repository: `git clone https://github.com/your-username/your-repo.git`
2. Install the dependencies: `poetry install`

<!-- Provide examples or instructions on how to use your project -->
## Usage
First, let's provision a local redis instance, using terraform. From project root:

```bash
$ export PROJECT_ROOT=$(pwd)
$ cd $PROJECT_ROOT/examples/terraform && \
  terraform init && \
  terraform plan && \
  terraform apply -auto-approve   # provision a local redis instance
```

Next, we can run the example python script:
```bash
$ cd $PROJECT_ROOT/examples && \
  PYTHONPATH=$PROJECT_ROOT python main.py           # run the example
```