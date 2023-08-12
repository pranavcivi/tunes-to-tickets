import os
import time
from dotenv import load_dotenv
from flask import Flask, render_template, session, request, redirect
from flask_session import Session
import requests
import spotipy
import ticketpy
import pickle
import random

# export SPOTIPY_CLIENT_ID=67e069ea49824790817bfa121c13eb2b
# "export SPOTIPY_CLIENT_SECRET=6bc07e5864c6479e8d90c016a927249c"
# "export SPOTIPY_REDIRECT_URI='http://tunestotickets.pythonanywhere.com/'" // must contain a port
# export SPOTIPY_REDIRECT_URI='127.0.0.1:9090/

# SPOTIPY_CLIENT_ID='67e069ea49824790817bfa121c13eb2b'
# SPOTIPY_CLIENT_SECRET='6bc07e5864c6479e8d90c016a927249c'
# SPOTIPY_REDIRECT_URI='http://tunestotickets.pythonanywhere.com/'

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

project_folder = os.path.expanduser('/home/tunestotickets/mysite')
load_dotenv(os.path.join(project_folder, '.env'))

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
tm_client = ticketpy.ApiClient('hSTysYlgGtubTzR3CVTSiI9x157dGacH')


@app.route('/')
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-top-read',
                                               cache_handler=cache_handler,
                                               show_dialog=True)
    # auth_manager = spotipy.oauth2.SpotifyOAuth(
    #     client_id = '67e069ea49824790817bfa121c13eb2b',
    #     client_secret = '6bc07e5864c6479e8d90c016a927249c',
    #     redirect_uri='http://tunestotickets.pythonanywhere.com/',
    #     scope="user-follow-read user-read-recently-played"
    # )

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return render_template("selector.html", name=spotify.me()["display_name"])
        # return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('login.html', auth_url=auth_url)
        # return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 3. Signed in, display data
   
    # return f'<h2>Hi {spotify.me()["display_name"]}, ' \
    #        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
    #        f'<a href="/playlists">my playlists</a> | ' \
    #        f'<a href="/currently_playing">currently playing</a> | ' \
    #        f'<a href="/current_user">me</a> | ' \
    #        f'<a href="/top_artists">top artists</a> | ' \
    #        f'<a href="/top_tracks_name">top tracks name</a> | ' \
    #        f'<a href="/genres">genres</a> | ' \
    #        f'<a href="/artistsExtended">artists extended</a> | ' \
    #        f'<a href="/topArtistsRelated">get top artists related</a> | ' \
    #        f'<a href="/ticketMasterCouponGenerator">Ticket Master Coupon Generator</a> | ' \
    #        f'<a href="/ticketMasterNamesAndID">Ticket Master Names and ID</a> | ' \
    #        f'<a href="/ticketMasterLinks">Ticket Master Links</a> | ' \
    #        f'<a href="/htmlPage">Html Page</a> | ' \
    return render_template("selector.html", name=spotify.me()["display_name"])


@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')


@app.route('/playlists')
def playlists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user_playlists()


@app.route('/currently_playing')
def currently_playing():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()

@app.route('/top_artists')
def top_artists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artists = spotify.current_user_top_artists(limit=50, offset=0, time_range='long_term')
    # artists = spotify.current_user_top_artists(limit=20, offset=0, time_range='medium_range')
    list = []
    for x in artists['items']:
        list.append(x['name'])

    return ', '.join(list)

@app.route('/top_tracks_name')
def top_tracks_name():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    tracks = spotify.current_user_top_tracks(limit=50, offset=0, time_range='long_term')

    list = []
    for x in tracks['items']:
        list.append(x['name'])

    return ', '.join(list)

@app.route('/genres')
def genres():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    mySet = set()
    artists = spotify.current_user_top_artists(limit=50, offset=0, time_range='long_term')
            
    for x in artists['items']:
        for genre in x['genres']:
            mySet.add(genre)

    return '\n'.join(mySet)

# this route should get the user's top artists and all artists related to those artists
@app.route('/artistsExtended')
def artistsExtended():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artists = spotify.current_user_top_artists(limit=50, offset=0, time_range='long_term')

    myList = []
    for x in artists['items']:
        myList.append(x['name'])
    
    answer = ""

    bruno_mars_id = spotify.search(q="Bruno Mars", type='artist', limit=1)['artists']['items'][0]['id']
    answer += "bruno mars id: " + bruno_mars_id + "\n"

    related = spotify.artist_related_artists(str(bruno_mars_id))

    for iter in related['artists']:
        answer += iter['name'] + '\n'
    
    return answer

    
    # for artistName in myList:
    #     print(spotify.search(q="Bruno Mars"))

@app.route('/topArtistsRelated')
def topArtistsRelated():

    # get top artists and store in a list
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artists = spotify.current_user_top_artists(limit=50, offset=0, time_range='long_term')
    top_artists_list = []
    for x in artists['items']:
        top_artists_list.append(x['name'])
    
    # get related artists from top_artists_list and put them into a new list

    related_set = set()
    for artist in top_artists_list:
        temp_id = spotify.search(q=artist, type='artist', limit=1)['artists']['items'][0]['id']
        related = spotify.artist_related_artists(str(temp_id))

        for iter in related['artists']:
            related_set.add(iter['name'])
    
    # add top artists into the set
    for name in top_artists_list:
        related_set.add(name)
    return list(related_set)

@app.route('/ticketMasterCouponGenerator')
def ticketMasterCouponGenerator():
    return redirect("https://youtu.be/dQw4w9WgXcQ")

@app.route('/ticketMasterNamesAndID')
def ticketMasterNamesAndID():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artists = spotify.current_user_top_artists(limit=50, offset=0, time_range='long_term')
    top_artists_list = []
    for x in artists['items']:
        top_artists_list.append(x['name'])
    
    # get related artists from top_artists_list and put them into a new list

    related_set = set()
    for artist in top_artists_list:
        temp_id = spotify.search(q=artist, type='artist', limit=50)['artists']['items'][0]['id']
        related = spotify.artist_related_artists(str(temp_id))

        for iter in related['artists']:
            related_set.add(iter['name'])
        
    
    # add top artists into the set
    artist_list = top_artists_list + list(related_set)
    
    answer_list = []
    for artist in artist_list:
        try:
            attractions = tm_client.attractions.find(keyword=artist).all()[0]
            answer_list.append(str(attractions.id) + " " + str(attractions.name))
        except:
            pass
    
    return answer_list

@app.route('/ticketMasterLinks')
def ticketMasterLinks():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artists = spotify.current_user_top_artists(limit=25, offset=0, time_range='long_term')
    top_artists_list = []
    for x in artists['items']:
        top_artists_list.append(x['name'])
    
    # get related artists from top_artists_list and put them into a new list
    related_set = set()
    for artist in top_artists_list:
        temp_id = spotify.search(q=artist, type='artist', limit=25)['artists']['items'][0]['id']
        related = spotify.artist_related_artists(str(temp_id))

        for iter in related['artists']:
            related_set.add(iter['name'])
        
    # we should have artist_list and related_set
    # grab 15 from artist_list and 15 from related_set


    # add top artists into the set
    num = min(30, len(top_artists_list))
    names_list = random.sample(top_artists_list, num) + random.sample(list(related_set), num)
    if(len(names_list) < 1):
        return "no concerts found"
    
    # artist_to_id_dict = {artist: None for artist in artist_list}
    pickle_in = open("artist_to_id.pickle", "rb")
    artist_to_id_dict = pickle.load(pickle_in)
    
    # does not require as many api calls
    artist_id_list = []
    for artist in names_list:
        if artist in artist_to_id_dict:
            artist_id_list.append(artist_to_id_dict[artist])
            continue
        else:
            try:
                attractions = tm_client.attractions.find(keyword=artist).all()[0]
                if attractions:
                    artist_id_list.append(str(attractions.id))
                    artist_to_id_dict[artist] = str(attractions.id)
                    # artist_id_list.append(artist_to_id_dict[artist])
            except:
                continue
            # finally:
            #     artist_to_id_dict[artist] = str(attractions.id)
            #     artist_id_list.append(artist_to_id_dict[artist])
    
    


    # traverse through artist_id_list and find links for each
    info_list = []

    # create a list with resorted ticketmaster IDs -- CHANGE TO: random_id_list holds 25 random valid IDs
    if(len(artist_id_list) < 1):
        return "no concerts found"
    random_id_list = random.sample(artist_id_list, len(artist_id_list))
    
    count = 50
    for artist_id in random_id_list:
        count -= 1
        if(len(info_list) >= 10 or count < 0):
            break
        try:
            res = requests.get(f"https://app.ticketmaster.com/discovery/v2/events.json?offset=0&attractionId={artist_id}&countryCode=US&apikey=hSTysYlgGtubTzR3CVTSiI9x157dGacH")
            info_list.append([str(res.json()["_embedded"]["events"][0]["url"]), 
                              str(res.json()["_embedded"]["events"][0]["images"][0]["url"]),
                              str(res.json()["_embedded"]["events"][0]["dates"]["start"]["localDate"]), 
                              str(res.json()["_embedded"]["events"][0]["priceRanges"][0]["min"]),
                              str(res.json()["_embedded"]["events"][0]["priceRanges"][0]["max"]), 
                              str(res.json()["_embedded"]["events"][0]["classifications"][0]["subGenre"]["name"])])
            time.sleep(1)
        except:
            continue
    
    pickle_out = open("artist_to_id.pickle", "wb")
    pickle.dump(artist_to_id_dict, pickle_out)
    pickle_out.close()
    

    if(len(info_list) < 1):
        return "No concerts found that fit your taste :("
    return info_list


@app.route('/htmlPage')
def htmlPage():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    artists = spotify.current_user_top_artists(limit=25, offset=0, time_range='long_term')
    top_artists_list = []
    for x in artists['items']:
        top_artists_list.append(x['name'])
    
    # get related artists from top_artists_list and put them into a new list
    related_set = set()
    for artist in top_artists_list:
        temp_id = spotify.search(q=artist, type='artist', limit=25)['artists']['items'][0]['id']
        related = spotify.artist_related_artists(str(temp_id))

        for iter in related['artists']:
            related_set.add(iter['name'])
        
    # we should have artist_list and related_set
    # grab 15 from artist_list and 15 from related_set


    # add top artists into the set
    num = min(30, len(top_artists_list))
    names_list = random.sample(top_artists_list, num) + random.sample(list(related_set), num)
    if(len(names_list) < 1):
        return "no concerts found"
    
    # artist_to_id_dict = {artist: None for artist in artist_list}
    pickle_in = open("artist_to_id.pickle", "rb")
    artist_to_id_dict = pickle.load(pickle_in)
    
    # does not require as many api calls
    artist_id_list = []
    for artist in names_list:
        if artist in artist_to_id_dict:
            artist_id_list.append(artist_to_id_dict[artist])
            continue
        else:
            try:
                attractions = tm_client.attractions.find(keyword=artist).all()[0]
                if attractions:
                    artist_id_list.append(str(attractions.id))
                    artist_to_id_dict[artist] = str(attractions.id)
                    # artist_id_list.append(artist_to_id_dict[artist])
            except:
                continue
            # finally:
            #     artist_to_id_dict[artist] = str(attractions.id)
            #     artist_id_list.append(artist_to_id_dict[artist])
    
    # traverse through artist_id_list and find links for each
    info_list = set()

    # create a list with resorted ticketmaster IDs -- CHANGE TO: random_id_list holds 25 random valid IDs
    if(len(artist_id_list) < 1):
        return "no concerts found"
    random_id_list = random.sample(artist_id_list, len(artist_id_list))
    
    count = 50
    for artist_id in random_id_list:
        count -= 1
        if(len(info_list) >= 10 or count < 0):
            break
        try:
            res = requests.get(f"https://app.ticketmaster.com/discovery/v2/events.json?offset=0&attractionId={artist_id}&countryCode=US&apikey=hSTysYlgGtubTzR3CVTSiI9x157dGacH")
            info_list.add((str(res.json()["_embedded"]["events"][0]["url"]), 
                           str(res.json()["_embedded"]["events"][0]["images"][0]["url"]),
                           str(res.json()["_embedded"]["events"][0]["dates"]["start"]["localDate"]), 
                           str(res.json()["_embedded"]["events"][0]["priceRanges"][0]["min"]),
                           str(res.json()["_embedded"]["events"][0]["priceRanges"][0]["max"]), 
                           str(res.json()["_embedded"]["events"][0]["classifications"][0]["subGenre"]["name"]),
                           str(res.json()["_embedded"]["events"][0]["name"])))
            time.sleep(1)
        except:
            continue
    
    pickle_out = open("artist_to_id.pickle", "wb")
    pickle.dump(artist_to_id_dict, pickle_out)
    pickle_out.close()
    

    if(len(info_list) < 1):
       return "No concerts found that fit your taste :("
    
    # info_list = [["https://www.ticketmaster.com/taylor-swift-the-eras-tour-inglewood-california-08-07-2023/event/0A005ECF84101066",
    #               "https://s1.ticketm.net/dam/a/a67/86eb84c0-ad6a-43c6-a55f-ff5d109c9a67_TABLET_LANDSCAPE_16_9.jpg",
    #               "2023-08-07",
    #               54.0,
    #               576.0,
    #               "Pop",
    #               "Taylor Swift Concert IDK"],
    #              ["https://www.ticketmaster.com/taylor-swift-the-eras-tour-inglewood-california-08-07-2023/event/0A005ECF84101066",
    #               "https://s1.ticketm.net/dam/a/a67/86eb84c0-ad6a-43c6-a55f-ff5d109c9a67_TABLET_LANDSCAPE_16_9.jpg",
    #               "2023-08-07",
    #               54.0,
    #               576.0,
    #               "Pop",
    #               "Taylor Swift Concert IDK"]]
    return render_template("main.html", infoList=list(info_list))

@app.route('/authors')
def authors():
    return render_template("authors.html")
