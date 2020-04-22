# Introduction

Python Flask media server I run on a raspberry pi inside a Docker container with web interface for viewing pictures and videos while also uploading and storing them to the file system.

## Running Locally

You must first create a .env file and add local environment variables. This is how you will login to the app through the web interface:

```
EMAIL=<email>
PASSWORD=<password>
SECRET=<app secret key>
```

Run locally:

```
pip install -r requirements.txt
flask run
```

To run locally on network:
`flask run -h <ip Address>`

To run locally with Docker (with Docker running):

```
docker build -t raspberry_pi_server .
docker run -d -p 5000:5000 raspberry_pi_server
```
