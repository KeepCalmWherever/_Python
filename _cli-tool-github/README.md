## CLI-Tool-Github

![image](https://img.freepik.com/free-vector/artificial-intelligence-robots-and-cyborg-with-infinity-symbol_107791-4668.jpg?w=1800&t=st=1677152568~exp=1677153168~hmac=eba8503d7b2d394d8633bf312f73b51e862e5e8f52c2418e2beead443864c388)

## Getting started

  - This project creates CLI tool to see a list of issues from GitHub repos called devopshq, the tool can be amended easily to extract issue list from any opened repo in GitHub
  - To run CLI you need to have docker installed and run this commands docker pull gorlovivan/devopshqissues:latest && docker run gorlovivan/devopshqissues:latest --get-all-issues
  - To create your own image you need to amend CLI-List-GitHub-Issues.py namely adding your github token and also provide in var section in CI/CD settings bot token and chat id, a run command will need to update with your docker login 'yourlogin'/devopshqissues:latest && docker run 'yourlogin'/devopshqissues:latest --get-all-issues

## Supported cli commands:
  - docker run gorlovivan/devopshqissues:latest --help            - shows possible list of commands
  - docker run gorlovivan/devopshqissues:latest --get-all-issues  - collect issues
  - docker run gorlovivan/devopshqissues:latest                   - if run cli without key it advises to use --help key

## Structure pipeline

Pipeline itself has 4 stages and 8 inner jobs, for executing jobs I've used docker outside of docker approach with linking docker.sock in config.toml

Stages and inner jobs:

  - test
    - pep8-check-style        - is used for pip8 check style code in project
    - semgrep-sast            - sast tool from gitlab
    - unit-pytest-locally     - unit test which is implemented by using python module pytest_httpserver, api structure of local http server is the same as github has whats lets testing api requests locally

  - build-cli-tool-image:
    - build-cli-tool-image    - build image locally
    - warming-up-run-cli-tool - warming-up a run cli-tool

  - publish-cli-tool:
    - publish-cli-tool        - publish image to dockerhub

  - create-mr-to-main:
    - create-mr-to-main       - create mr into main
    - notify-mr-to-telegram   - send notify to telegram chat about a new created mr

## Docker images used in CI/CD

  - eeacms/pep8:1.7.0.3
  - python:3.6
  - docker:cli
  - tmaier/gitlab-auto-merge-request:1
  - curlimages/curl:7.88.1
  - alpine:3.17.2

## Required python modules

  - requests
  - datetime
  - pytest_httpserver

## Variables

Variables are determined in CI/CD section in project settings

  - DOCKER_PASS               - password from dockerhub account
  - DOCKER_USER               - uname from dockerhub account
  - GITLAB_PRIVATE_TOKEN      - your pat
  - IMAGE_NAME                - image name, format like yourlogin/devopshqissues:latest
  - TELEGRAM_BOT_LINK         - https://api.telegram.org/bot'yourtokenbot'/sendMessage
  - TELEGRAM_CHAT_ID          - telegram chat id

