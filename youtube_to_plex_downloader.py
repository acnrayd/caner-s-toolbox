### Youtube Downloader to Plex Folder (Poor Man's Youtube Premium)
# My wife loves watching Turkish soap operas from Youtube, but Youtube is full of ads.
# I have built this script to make her life easier.
# (Thanks ChatGPT for beautifying my horrible HTML)

# I have a QNAP NAS that can run Docker containers.
# This script and Plex runs in that Qnap which is turned on 7&24
# IP of this container has a friendly DNS domain in my local DNS server (indir.co)

### How it works?
# 1) She will enter the video URL that she wants to watch
# 2) In background Pytube will start downloading that video to my Plex folder in my local NAS
# 3) Plex will discover and add that video to the library immediately
# 4) She can enjoy the video on Plex app on our TV

## To do list: Login feature as age-restricted videos requires login.

from flask import Flask, render_template, request, render_template_string
from pytube import YouTube
import threading

app = Flask(__name__)

index_html = """
<!DOCTYPE html>
<html>
  <head>
    <title>Video Downloader</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
        text-align: center;
      }
      h1 {
        color: #333;
        margin-top: 20px;
      }
      form {
        margin-top: 50px;
      }
      label {
        display: block;
        margin-bottom: 10px;
        color: #555;
      }
      input[type="text"], input[type="submit"] {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        width: 100%;
        max-width: 400px;
        margin-bottom: 20px;
      }
      input[type="submit"] {
        background-color: #0077cc;
        color: #fff;
        font-weight: bold;
        cursor: pointer;
      }
      input[type="submit"]:hover {
        background-color: #005ea6;
      }
      @media only screen and (max-width: 600px) {
        input[type="text"], input[type="submit"] {
          width: 100%;
          max-width: 100%;
        }
      }
    </style>
 <body>
    <h1>Video Downloader</h1>
    <form method="post" action="/download">
<label for="yt-link">YT Link:</label>
<input type="text" id="yt-link" name="yt-link"><br><br>
<label for="destination">Destination:</label>
<input type="text" id="destination" name="destination" value="/Download/Youtube/"><br><br>
<input type="submit" value="Download">
</form>

  </body>
</html>
"""

global completion_html

completion_html = """
<!DOCTYPE html>
<html>
  <head>
    <title>Download Started</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f5f5f5;
        text-align: center;
      }
      h1 {
        color: #333;
        margin-top: 20px;
      }
      form {
        margin-top: 50px;
      }
      label {
        display: block;
        margin-bottom: 10px;
        color: #555;
      }
      input[type="text"], input[type="submit"] {
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        width: 100%;
        max-width: 400px;
        margin-bottom: 20px;
      }
      input[type="submit"] {
        background-color: #0077cc;
        color: #fff;
        font-weight: bold;
        cursor: pointer;
      }
      input[type="submit"]:hover {
        background-color: #005ea6;
      }
      @media only screen and (max-width: 600px) {
        input[type="text"], input[type="submit"] {
          width: 100%;
          max-width: 100%;
        }
      }
    </style>
  </head>
  <body>
    <h1>Download Started</h1>
    <p>Download has been started and will be available soon in destination folder.</p>
    <form method="get" action="/">
      <button type="submit">Back</button>
    </form>
  </body>
</html>
"""

def download_video(yt_link, destination):
    yt = YouTube(yt_link)
    ys = yt.streams.get_highest_resolution()
    ys.download(destination)

@app.route('/')
def index():
    return index_html

@app.route('/completion.html')
def completed():
    return completion_html

@app.route('/download', methods=['POST'])
def download():
    yt_link = request.form['yt-link']
    destination = request.form['destination']
    download_thread = threading.Thread(target=download_video, args=(yt_link, destination))
    download_thread.start()

    return render_template_string(completion_html)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80, debug=True)
