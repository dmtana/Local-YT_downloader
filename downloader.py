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
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # read tag from json info
        with open(f"{folder_name}/{id}.txt", "r") as file:
            ###   GET INFO FROM JSON   ###
            json_info = json.loads(file.read())
            title = json_info['title']
            # EDIT TAG
            audiofile = ID3(f"media_from_yt/{str_buf_fix(title)}.mp3")

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
                with open(f"photo/Thumbnails/{id}.jpeg", "rb") as album_art:
                    audiofile.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=album_art.read()))
            except Exception as e:
                print("[BAD ATTRIBUTES]", e)
                try:
                    audiofile.add(TIT2(encoding=3, text=str_buf_fix(title)))
                except Exception as e:
                    print("[BAD ATTRIBUTES: 2]", e)
            # SAVE TAG
            audiofile.save()

    except Exception as e:
        print('[NO MP3 TAG]', e)

def save_json(a, j): #this method save json info
    folder = 'JSON_INFO_MP3'
    if not os.path.exists(folder):
        os.makedirs(folder)
    try: # a: name of ID / j: json str
        with open(f"JSON_INFO_MP3/{a}.txt", "w") as json_file:
            # SAVE JSON FILE TO HAVE INFO ABOUT SOUND
            json_file.write(json.dumps(j))
            print('[+][JSON SAVE]')
    except Exception as e:
        print("[-][ERROR JSON SAVE]", e)

def download_media(URL):
    ### First we need folder for images
    # Folder for album covers, if not exist
    folder = 'photo/Thumbnails'
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_name = ""
    file_id = ""

    try: # GETING JSON FILE 
        with yt_dlp.YoutubeDL() as ydl:
            some_var = ydl.sanitize_info(ydl.extract_info(URL, download=False))
            # WE GET TITLE AND ID FROM LINK
            file_name += some_var['title']
            file_id += some_var['id']
            save_json(file_id, some_var)
    except Exception as e:
            print("[CAN'T GET JSON FROM LINK]", e)   
    img_ = some_var['thumbnails'][5]['url']
    print("link url:", img_)               # img_ is link to image of this sound
    try: # DOWNLOAD AND SAVE IMAGE
        with urlopen(img_) as resource:
            print("[+][DOWNLOADING IMAGE]")
            with open(f'photo/Thumbnails/{file_id}.jpeg', 'wb') as file:
                file.write(resource.read())    
        print("[+][DOWNLOAD IMAGE COMPLETE]")   
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

download_media(URL)

print("[DONE!]")