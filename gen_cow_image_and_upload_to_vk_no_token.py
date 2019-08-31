#!/usr/bin/env python3
import sys

import requests
import json

from PIL import Image, ImageDraw, ImageFont
import random

import subprocess

from os import listdir
from os.path import isfile, join

import vk

DEBUG = False

##########  COW GEN CONST:
URL = 'http://api.forismatic.com/api/1.0/'    
URL_DATA = {"method": "getQuote", "format": "json", "lang": "ru"}   

COWS_DIR = '/usr/local/Cellar/cowsay/3.03/share/cows'
COWSAY_PATH = '/usr/local/bin/cowsay'
COWTHINK_PATH = '/usr/local/bin/cowthink'

########## IMAGE GEN CONST
FONT_SIZE = 20
BACKGROUND_COLOR = 'black'


## we using it only for generate right size of the image
FONT_WIDTH_ABSTRACT = int(FONT_SIZE - ((FONT_SIZE / 2) -  FONT_SIZE / 10))
FONT_HEIGHT_ABSTRACT = int(FONT_SIZE + (FONT_SIZE / 6))

IMG_FILENAME = 'tmp.png'

########## VK CONST
TOKEN = ''
VK_OWNER_ID = ''

def get_quote(url, url_data):
    try:
        r = requests.post(url, url_data)
    except requests.exceptions.ConnectTimeout:
        print("Connection timeout error.")
        sys.exit()
    except requests.exceptions.ReadTimeout:
        print("Read timeout error.")
        sys.exit()
    except requests.exceptions.ConnectionError:
        print("Connection error.")
        sys.exit()
    except requests.exceptions.HTTPError as err:
        print("Http error.")
        sys.exit()
    except:
        print("Undefined error while connecting to aforist resources.")
        sys.exit()

    return r.json()['quoteText'] + ' (' + r.json()['quoteAuthor'] + ')'



# r - mean raw string, to disable escape sequenses
COW_SAY_TEST = r"""
 _________________________________________________________________________________
/ Тот день, когда вы полностью возьмете на себя ответственность за собственное    \
| будущее и прекратите искать оправдание сомнениям, станет днем начала движения к |
\ вершинам. (Джим Рон)                                                            /
 ---------------------------------------------------------------------------------
     \
      \
        ,__, |    |
        (oo)\|    |___
        (__)\|    |   )\_
             |    |_w |  \
             |    |  ||   *

             Cower....
"""




def get_max_line_len(text):
    max_len = 0
    for line in text.splitlines():
        if len(line) > max_len:
            max_len = len(line)
    return max_len

def get_random_cow_path(): 
    if random.randint(0, 1) == 0: 
        return COWSAY_PATH
    return COWTHINK_PATH

def make_a_cow(quote):
    cow_path = get_random_cow_path()

    cow_theme_filenames = [f for f in listdir(COWS_DIR) if isfile(join(COWS_DIR, f))]

    cow_theme = cow_theme_filenames[random.randint(0, len(cow_theme_filenames) - 1)]

    try:
        proc = subprocess.Popen([cow_path, '-W', '60', '-f', cow_theme, quote], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        print('Script trying to execute non existing binary')
        sys.exit()
    except ValueError: 
        print('Popen is called with invalid arguments')
        sys.exit()
    except:
        print('Unknown error occured while do Popen, exit..')
        sys.exit()

    out, err = proc.communicate()
    return out.decode('utf-8')



def gen_an_image_from_cow_text(cow):
    max_line_len = get_max_line_len(cow)
    num_of_lines = len(cow.splitlines())
    

    img = Image.new('RGBA', 
                    (max_line_len * FONT_WIDTH_ABSTRACT + FONT_SIZE * 2, 
                    4 * FONT_HEIGHT_ABSTRACT + num_of_lines * FONT_HEIGHT_ABSTRACT), 
                    BACKGROUND_COLOR)
    
    idraw = ImageDraw.Draw(img)
    
    fnt = ImageFont.truetype('./Cousine-Bold.ttf', FONT_SIZE)
    
    for idx, line in enumerate(cow.splitlines()):
        idraw.text((FONT_SIZE, idx * (FONT_SIZE + 4) + FONT_SIZE), line, font=fnt, 
                    fill=(  random.randint(130, 255),
                            random.randint(130, 255),
                            random.randint(130, 255),
                            255))
    
    
    try:
        img.save(IMG_FILENAME)

    except KeyError:
        print('Output format could not be determined from the file name')
        sys.exit()
    except IOError:
        print('file could not be written')
        sys.exit()
    except:
        print('Unknown error occured while do image save, exit..')
        sys.exit()

def upload_image_to_vk():
    # VK PART
    try:
        session = vk.Session(access_token=TOKEN)
        vk_api = vk.API(session, v='5.52')

        wall_upload_server = vk_api.photos.getWallUploadServer()
        upload_url = wall_upload_server['upload_url']

        request = requests.post(upload_url, files={'photo': open(IMG_FILENAME, "rb")})
        params = {  'server':   request.json()['server'],
                    'photo':    request.json()['photo'],
                    'hash':     request.json()['hash'] }

        photo_id = vk_api.photos.saveWallPhoto(**params)[0]['id']

        params = {  'owner_id':     VK_OWNER_ID,
                    'attachments':  'photo' + VK_OWNER_ID + '_' + str(photo_id),
                    'from_group':   1 }

        vk_api.wall.post(**params)
    except:
        #currently have no idea how to catch exception for the module so
        print('Some error occured while trying to upload image to VK, exit...')
        sys.exit()


def main():
    quote = get_quote(URL, URL_DATA)

    if DEBUG == True:
        print(quote)

    cow = make_a_cow(quote)

    if DEBUG == True:
        print(cow)

    #we do not expect errors from this function
    gen_an_image_from_cow_text(cow)

    upload_image_to_vk()


if __name__=="__main__":
    main()
