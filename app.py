import requests
import json
from flask import Flask , render_template ,request
import html

def check_audio(url):
  r = requests.get(url)
  return r.status_code

def fix_title(title):
    title = title.replace('&quot;', '')
    return html.unescape(title)


def fix_media_url(url):
    ur = url.replace("preview","h")
    ur= ur.replace("_96_p.mp4","_320.mp4")
    return ur

app = Flask(__name__,static_url_path='/static')
album_name = []
year = []
images = []
album_ids = []


@app.route('/home',methods = ['GET'])
def get_top_40():
    language= request.args.get('lang')
    album_name.clear()
    year.clear()
    images.clear()
    album_ids.clear()

    cookies = {"L":language}
    url = f'https://www.jiosaavn.com/api.php?__call=content.getHomepageData'

    result = requests.get(url,cookies=cookies).text

    convert_to_json = "{"+result.split("{", 1)[1]

    convert_to_json = json.loads(convert_to_json)['new_albums']

    for i in range(len(convert_to_json)):

     album_name.append(convert_to_json[i]['text'])
     year.append(convert_to_json[i]['year'])
     images.append(convert_to_json[i]['image'].replace("150x150","250x250"))
     album_ids.append(convert_to_json[i]['albumid'])

    return render_template('home.html',album_name=album_name,year=year,images=images,album_ids=album_ids,zip=zip,language=language)

@app.route('/get_album',methods = ['GET'])
def get_album_details():
    songIDs = []
    songImages = []
    songNames = []
    albumID = request.args.get('albumID')
    url = f'https://www.jiosaavn.com/api.php?__call=content.getAlbumDetails&albumid={albumID}'
    result = requests.get(url).text
    convert_to_json = "{" + result.split("{", 1)[1]
    convert_to_json = json.loads(convert_to_json)
    title = html.unescape(convert_to_json['title'])
    release_date = convert_to_json['release_date']
    primary_artist = convert_to_json['primary_artists']
    songs = convert_to_json['songs']
    album_image = convert_to_json['image'].replace("150x150","500x500")

    for i in range(len(songs)):
        songIDs.append(songs[i]['id'])
        songImages.append(songs[i]['image'].replace("150x150","250x250"))
        songNames.append(html.unescape(songs[i]['song']))


    return render_template('Album_Details.html',title=title,songNames=songNames,release_date=release_date,primary_artist=primary_artist,zip=zip,
                           album_image=album_image,song_IDs=songIDs,song_covers=songImages)


@app.route('/play_song',methods = ['GET'])
def play():
    songID = request.args.get('songID')
    url = f'https://www.jiosaavn.com/api.php?cc=in&_marker=0%3F_marker%3D0&_format=json&model=Redmi_5A&__call=song.getDetails&pids={songID}'
    result = requests.get(url).text
    convert_to_json = "{" + result.split("{", 1)[1]
    convert_to_json = json.loads(convert_to_json)
    song_name = fix_title(convert_to_json[songID]['song'])
    singers = convert_to_json[songID]['singers']
    year = convert_to_json[songID]['year']
    image = convert_to_json[songID]['image'].replace("150x150","250x250")

    mp3_urls = fix_media_url(convert_to_json[songID]['media_preview_url'])

    return render_template("Play.html",song_name=song_name,singers=singers,year=year,image=image,mp3_url=mp3_urls)

@app.route('/search',methods = ['GET'])
def search_song():
    songIDs = []
    images = []
    songs_titles = []
    songs_subtitles = []
    songName = request.args.get('songName')
    url = f"https://www.jiosaavn.com/api.php?p=1&q={songName}&_format=json&_marker=0&api_version=4&ctx=web6dot0&n=20&__call=search.getResults"
    r = requests.get(url).json()['results']
    for i in range(len(r)):

        songIDs.append(r[i]['id'])
        images.append(r[i]['image'].replace("150x150","250x250"))
        songs_titles.append(r[i]['title'])
        songs_subtitles.append(r[i]['subtitle'])

    return render_template("search_results.html",songIDs=songIDs,images=images,zip=zip,songName=songName,songs_titles=songs_titles,songs_subtitles=songs_subtitles)

@app.route("/Album_Search",methods = ['GET'])
def Album_Search():
    AlbumIDs = []
    titles = []
    images = []


    albumName = request.args.get('AlbumName')
    url = f"https://www.jiosaavn.com/api.php?_format=json&query={albumName}&__call=autocomplete.get&ctx=android&_format=json&_marker=0"

    r= requests.get(url).json()['albums']['data']

    for i in range(len(r)):
        AlbumIDs.append(r[i]['id'])
        titles.append(html.unescape(r[i]['title']))
        images.append(r[i]['image'].replace("50x50","250x250"))



    return render_template("Album_Search.html",albumName=albumName,AlbumIDs=AlbumIDs,titles=titles,images=images,zip=zip)

if __name__ == '__main__':
   app.run()
