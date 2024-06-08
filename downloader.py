from PIL import Image
import yt_dlp
import os
import json
import os
import json
from urllib.request import urlopen
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TCON, TDRC, APIC
import ssl

# crutch for MacOS BADYLLLLL =D
ssl._create_default_https_context = ssl._create_unverified_context

'''
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install pillow
pip install yt-dlp
'''

curren_path = os.path.dirname(__file__)+'/'

print("*** Hello I'm simple program for downloading music from YT ***")
URL = input("Input you're link: \n")

def str_buf_fix(s):
    trans_table = str.maketrans('$', 'S', '"<>:/\\|?*')
    s = s.translate(trans_table)
    # some bugfix
    # s.translate(str.maketrans("$", "S"))
    return s

def tag_edit(id):
    folder_name = 'JSON_INFO_MP3'
    try:
        if not os.path.exists(curren_path+folder_name):
            os.makedirs(curren_path+folder_name)
        # read tag from json info
        with open(f"{curren_path+folder_name}/{id}.json", "r") as file:
            ###   GET INFO FROM JSON   ###
            json_info = json.loads(file.read())
            title = json_info['title']
            # EDIT TAG
            audiofile = ID3(f"{curren_path}media_from_yt/{str_buf_fix(title)}.mp3")

            try:
                artist = json_info['artist']
                album = json_info['album']
                track = json_info['track']
                release_year = json_info['release_year']

                audiofile.add(TIT2(encoding=3, text=track))
                audiofile.add(TALB(encoding=3, text=album))
                audiofile.add(TPE1(encoding=3, text=artist))
                audiofile.add(TCON(encoding=3, text=""))  # genre
                audiofile.add(TDRC(encoding=3, text=str(release_year)))
                # EDIT IMAGE
                with open(f"{curren_path}photo/Thumbnails/{id}.jpeg", "rb") as album_art:
                    audiofile.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=album_art.read()))
            except Exception as e:
                print("[tag_editor][BAD ATTRIBUTES]", e)
                try:
                    audiofile.add(TIT2(encoding=3, text=str_buf_fix(title)))
                except Exception as e:
                    print("[tag_editor][BAD ATTRIBUTES: 2]", e)
            # SAVE TAG
            audiofile.save()
    except Exception as e:
        print('[tag_editor][NO MP3 TAG]', e)

def save_json(a, j): #this method save json info
    folder = curren_path+'JSON_INFO_MP3'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try: # a: name of ID / j: json str
        with open(f"{curren_path}JSON_INFO_MP3/{a}.json", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
            print('[bot][+][JSON SAVE]')
            return True
    except Exception as e:
        print("[bot][-][ERROR JSON SAVE]", e)

def download_media(URL):
    ### First we need folder for images
    # Folder for album covers, if not exist
    folder = f'{curren_path}photo/Thumbnails'
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_name = ""
    file_id = ""
    done = 0
    while done < 15: # kostyl for facebook reels etc
        try:
            with yt_dlp.YoutubeDL() as ydl:
                print('yt-dlp 1')
                some_var = ydl.sanitize_info(ydl.extract_info(URL, download=False))
                # WE GET TITLE AND ID FROM LINK
                file_name = some_var['title']
                file_id = some_var['id']
                if save_json(file_id, some_var):
                    done = 15
                print('yt-dlp 2')    
        except Exception as e:
                print("[bot][X][CAN'T GET JSON FROM LINK]", e)
        done += 1 
    link_thumbnail = some_var['thumbnail']
    print("link url:", link_thumbnail)               # link_thumbnail is link to image of this sound
    try: # DOWNLOAD AND SAVE IMAGE
        with urlopen(link_thumbnail) as resource:
            print("[+][DOWNLOADING IMAGE]")
            with open(f'{curren_path}photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                file.write(resource.read())    
        print("[+][DOWNLOAD IMAGE COMPLETE]")
        try:
            crop_to_square(f'{curren_path}photo/Thumbnails/{file_id}.jpeg',
                                 f'{curren_path}photo/Thumbnails/{file_id}.jpeg')
        except Exception as e:
            print(e)    
    except Exception as e:
        print("[-][ERROR IMAGE]", e)
    try:
        os.system(f'yt-dlp -f ba -o "{str_buf_fix(file_name)}" -x --audio-quality 0 -x --audio-format mp3 ' # using ffmpeg.exe # 
                  f'-P media_from_yt '  # path
                  f'"{URL}"')  # link
        print("[+][DOWNLOAD AUDIOFILE COMPLETE]")
    except Exception as e:
        print("[-][ERROR DOWNLOAD AUDIOFILE]")
    tag_edit(file_id)
    return file_id  

def crop_to_square(image_path, output_path):
    with Image.open(image_path) as img:
        width, height = img.size
        new_side = min(width, height)
        left = (width - new_side) / 2
        top = (height - new_side) / 2
        right = (width + new_side) / 2
        bottom = (height + new_side) / 2
        img_cropped = img.crop((left, top, right, bottom))
        img_cropped.save(output_path)

download_media(URL)

print("[DONE!]")