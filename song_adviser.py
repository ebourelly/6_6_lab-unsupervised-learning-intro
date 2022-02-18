import requests
import pandas as pd
from random import randint
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import getpass
import pickle

# c_id = getpass.getpass()
# c_secret = getpass.getpass()
# sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=c_id,client_secret=c_secret))

secrets_file = open("C:/Users/ebour/Documents/()_Ironhack DA Bootcamp/()_Labs/secrets_file.txt","r")
string = secrets_file.read()
secrets_dict={}
for line in string.split('\n'):
    if len(line) > 0:
        secrets_dict[line.split(':')[0]]=line.split(':')[1]
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=secrets_dict['cid'],
                                                           client_secret=secrets_dict['cs']))

popvortex_100 = pd.read_csv('C:/Users/ebour/Documents/()_Ironhack DA Bootcamp/()_Labs/6_1_lab-web-scraping-single-page/popvortex_100.csv')
suggestion_database = pd.read_csv('C:/Users/ebour/Documents/()_Ironhack DA Bootcamp/()_Labs/6_6_lab-unsupervised-learning-intro/clusterized_data.csv')

cluster_model = pickle.load(open('spotify_cluster_model.sav', 'rb'))
scaler = pickle.load(open('spotify_scaler.sav', 'rb'))

def song_advice():
    song_input = input('Please fill in the name of a song you like : ')
    song_input = song_input.lower()
    top_100_check = popvortex_100[popvortex_100['title'] == song_input]
    artist_input = ''

    if len(top_100_check['title']) > 0 :
        i = randint(1,100)
        while popvortex_100['title'][i] == song_input:   # used to avoid advising the same song as the input
            i = randint(1,100)
        proposed_title = popvortex_100['title'][i]
        proposed_artist = popvortex_100['artist'][i]
        output = 'Great choice ! This song is in the PopVortex Top 100. You should listen to "' + proposed_title + '" by ' + proposed_artist + '. You might like it !'
    
    else :
        res = sp.search(q='track:' + song_input, type='track')
        track_id = None

        # Check if we have more than 50 songs matching the given name and if  yes, asks for the artist to reduce the size of the dataset
        if res['tracks']['total'] > 50:
            artist_input = input('Please fill in the name of a the artist : ')
            artist_input = artist_input.lower()
            res = sp.search(q='track:' + song_input + ' artist:' + artist_input, type='track',limit = 50)

        data = pd.DataFrame(res['tracks']['items'])
        if len(data) == 0:
            output = 'We are sorry, but we cannot find any song with this name. Please try again.'
        else:
            data['name'] = data['name'].apply(lambda x: x.lower())
            data = data[data['name'] == song_input].reset_index(drop = True)
            track_id = None
            if len(data['artists'])>1:
                if artist_input == '':
                    artist_input = input('Please fill in the name of the artist : ')
                    artist_input = artist_input.lower()
                artist_match = False
                for i in range(len(data['artists'])):
                    art = data['artists'][i][0]['name'].lower()
                    if art == artist_input:
                        track_id = data['id'][i]
                        artist_match = True
                        break
                if artist_match == False:
                    return 'We are sorry, but we cannot find any song with this name and artist. Please check your spelling or try another song.'
            else:
                track_id =  data['id'][0]
            track_uri = 'spotify:track:' + track_id
            audio_features = pd.DataFrame(sp.audio_features(track_uri)[0], index=[0])[['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'time_signature']]
            audio_feat_prep = scaler.transform(audio_features)
            song_input_cluster = cluster_model.predict(audio_feat_prep)[0]
            suggestion_list = suggestion_database[suggestion_database['cluster'] == song_input_cluster].reset_index(drop=True)
            j = randint(1,len(suggestion_list['track_name']))
            while suggestion_list['track_name'][j] == song_input:  #used to avoid advising the same song as the input (if ever in the suggestion list)
                j = randint(1,len(suggestion_list['track_name']))
            proposed_title = suggestion_list['track_name'][j]
            proposed_artist = suggestion_list['artist_name'][j]
            output = 'Your song is not in the PopVortex Top 100 but we still have a great advice for you : "' + proposed_title + '" by ' + proposed_artist + '. You might like it !'
        
    return output

advice = song_advice()
print(advice)