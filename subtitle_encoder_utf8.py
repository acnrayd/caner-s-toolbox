# I occasionally download movies and get Turkish subtitles from Opensubtitles.org
# Opensubtitles.org provides subtitles in Windows-1254 encoding, which means Turkish characters are not displayed correctly.
# To fix this, I had to manually open subtitles in Windows-1254 encoding and save them in UTF-8.
# I have created following Py script that scans the folder for .srt files, opens them in Windows-1254 and saves in UTF-8 automatically.
# Instructions: run the script in the same folder as your subtitles.

import os
import codecs

folder_path = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(folder_path):
    for filename in files:
        if filename.endswith('.srt'):
            file_path = os.path.join(root, filename)
            with codecs.open(file_path, 'r', encoding='cp1254') as f:
                content = f.read()
            with codecs.open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
