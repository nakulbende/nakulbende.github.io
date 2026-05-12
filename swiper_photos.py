import os
import glob, os
from os.path import exists
from os import listdir
from os.path import isfile, join
import numpy as np
import random

# current directory
dirname = os.path.dirname(__file__)
dirname = dirname + '/'
print("Current directory: ", dirname)

path = 'assets/img'
path = dirname + path
#path = '/content'

files = glob.glob(path + '/*.png') + glob.glob(path + '/*.jpg')
#files.sort()
random.shuffle(files)
print("Found ", str(len(files)), "image files in ", path)
html_file = glob.glob(dirname + '/*.html')
print("Manipulating html file at: ", html_file)

photo_string = ''
for file_name in files: 
    # Logic: 
    # 1. Added class="img-fluid" for responsiveness
    # 2. Added loading="lazy" for performance
    # 3. Cleaned up the pathing
    img_path = file_name[len(dirname):]
    
    temp_string = f"""
                  <div class="swiper-slide">
                    <img src="{img_path}" class="img-fluid" alt="Portfolio Image" loading="lazy">
                  </div>"""
    photo_string = "\n".join([photo_string, temp_string])

with open(html_file[0], 'r') as f: 
        html_string = f.read()

beginning_string = '<div class="swiper-wrapper align-items-center">'
end_string = '''
              </div>
              <div class="swiper-pagination"></div>'''

photo_start = html_string.find(beginning_string)
photo_end = html_string.find(end_string)

photo = html_string[photo_start+ len(beginning_string): photo_end]

final = html_string[:photo_start+ len(beginning_string)] + photo_string + html_string[photo_end:]

htmlwriter = open(html_file[0],"w")
htmlwriter.write(final)
htmlwriter.close()

print(final)