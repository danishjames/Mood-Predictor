import spotipy
from spotipy import util
import time
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 250)

auth = open('auth.txt', 'r')

# Authentication information below
client_id = ''
client_secret = ''
username = ''
scope = ''
redirect_uri = ''

auth.close()

# Initialize arrays
track_ids = []
track_names = []
artist_names = []
moods = []


def track_add(tracks, mood):
    for i in range(0, len(tracks)):
        track_ids.append(tracks[i]['track']['id'])
        track_names.append(tracks[i]['track']['name'])
        artist_names.append(tracks[i]['track']['artists'][0]['name'])
        moods.append(mood)


if __name__ == '__main__':
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

    if token:
        sp = spotipy.Spotify(auth=token)
        print('Token acquired')
    else:
        print("Can't get token for", username)

    playlist_ids = {'happy': ['https://open.spotify.com/playlist/37i9dQZF1DWSqmBTGDYngZ?si=8CiZ5DHJT0KxVj_xUX1Tag',
                              'https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0?si=gm5C4QfWS6a-RirJ3A04Zw',
                              'https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC?si=n_zLF7RWQHGwFnFA0S7uyQ'],
                    'sad': ['https://open.spotify.com/playlist/37i9dQZF1DWZUAeYvs88zc?si=DGJP4FAPRvODmp9VXCG-cg',
                            'https://open.spotify.com/playlist/37i9dQZF1DX3YSRoSdA634?si=BGY63d5rS5OyVqvYgoH6Sw',
                            'https://open.spotify.com/playlist/37i9dQZF1DWVrtsSlLKzro?si=CxUC12C6Rd-EYfCVCQ_JKg']}

    for mood, playlist_link in playlist_ids.items():
        for i in range(0, len(playlist_link)):
            playlist = sp.user_playlist(username, playlist_link[i])
            tracks = playlist["tracks"]['items']
            track_add(tracks, mood)

    data = {'Track IDs': track_ids, 'Names': track_names, 'Artists': artist_names, 'Moods': moods}
    track_df = pd.DataFrame(data=data)

    print(track_df.describe())

    track_df.insert(4, 'Loudness', 0, allow_duplicates=True)
    track_df.insert(5, 'Instrumentalness', 0, allow_duplicates=True)
    track_df.insert(6, 'Modality', 0, allow_duplicates=True)
    track_df.insert(7, 'Speechiness', 0, allow_duplicates=True)
    track_df.insert(8, 'Energy', 0, allow_duplicates=True)
    track_df.insert(9, 'Tempo', 0, allow_duplicates=True)
    track_df.insert(10, 'Valence', 0, allow_duplicates=True)

    counter = 0

    for i in range(0, len(track_df)):
        if token:
            track_df.loc[i, 'Loudness'] = sp.audio_features(track_df['Track IDs'][i])[0]['loudness']
            track_df.loc[i, 'Instrumentalness'] = sp.audio_features(track_df['Track IDs'][i])[0]['instrumentalness']
            track_df.loc[i, 'Modality'] = sp.audio_features(track_df['Track IDs'][i])[0]['mode']
            track_df.loc[i, 'Speechiness'] = sp.audio_features(track_df['Track IDs'][i])[0]['speechiness']
            track_df.loc[i, 'Energy'] = sp.audio_features(track_df['Track IDs'][i])[0]['energy']
            track_df.loc[i, 'Tempo'] = sp.audio_features(track_df['Track IDs'][i])[0]['tempo']
            track_df.loc[i, 'Valence'] = sp.audio_features(track_df['Track IDs'][i])[0]['valence']

            counter += 1

            print('{} done and {} left.'.format(i, len(track_df) - i))

            if counter > 5:
                time.sleep(2)
                print('Cooling down...')
                counter = 0
        else:
            # Re-authentication when token expires
            token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
            sp = spotipy.Spotify(auth=token)

    track_df.to_csv(path_or_buf='./track_data.csv', index=True)
