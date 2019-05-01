
import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
from globs import *

TRACKS_LIMIT = 500

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def playlists_by_word(search_word):
    """
    A method to search playlists in Spotify by word.
    :param search_word: The given word.
    :return: List of playlists with total TRACKS_LIMIT number if tracks. (maybe more)
    """
    list_playlist = list()
    result_search = sp.search(search_word, type='playlist', limit=50)
    num_songs = 0
    while result_search:
        for playlist in result_search['playlists']['items']:
            num_songs += playlist['tracks']['total']
            list_playlist.append(playlist['id'])
            # tracks_playlist = sp.user_playlist('spotify', playlist['id'], fields="tracks,next")
            # analyze_playlist(tracks_playlist['tracks'])
            if num_songs > TRACKS_LIMIT:
                return list_playlist
        if result_search['playlists']['next']:
            result_search = sp.next(result_search['playlists'])
        else:
            result_search = None


def analyze_playlists(playlists):
    """
    A method that goes over a given list of playlists ids. (to do something with it).
    :param playlists: A list of ids of playlist in spotify.
    :return: List of tracks ids.
    """
    list_tracks_id = list()
    for playlist_id in playlists:

        # get the playlist by id from spotify.
        result = sp.user_playlist('spotify', playlist_id, fields="tracks,next")

        # from result we take the tracks.
        playlist = result['tracks']

        # now we go over the tracks(songs).
        while playlist:
            for track in playlist['items']:

                # track is some dictionary, we need the track id.
                list_tracks_id.append(track['track']['id'])
            if playlist['next']:
                playlist = sp.next(playlist)
            else:
                playlist = None

    return list_tracks_id


def filter_happy_songs(tracks):
    """
    A method to filter the songs to get the most "happy" ones.
    :param tracks: The tracks we want to analyze.
    :return: List of songs, with their features.
    """
    data = dict()
    data['songs'] = list()
    for track_id in tracks:

        # next line get the feature.
        result = sp.audio_features(track_id)
        data['songs'].append({'song_name': track_id, 'song_features': result[0]})

    return data


def filter_sad_songs(tracks):
    """
    A method to filter the songs to get the most "sad" ones.
    :param tracks: The tracks we want to analyze.
    :return: List of songs, with their features.
    """
    data = dict()
    data['songs'] = list()
    for track_id in tracks:

        # next line get the feature.
        result = sp.audio_features(track_id)
        if result[0]['valence'] < 0.21:
            data['songs'].append({'song_name': track_id, 'song_features': result[0]})
    return data


def filter_angry_songs(tracks):
    """
    A method to filter the songs to get the most "angry" ones.
    :param tracks: The tracks we want to analyze.
    :return: List of songs, with their features.
    """
    data = dict()
    data['songs'] = list()
    for track_id in tracks:

        # next line get the feature.
        result = sp.audio_features(track_id)
        if result[0]['energy'] > 0.7 and result[0]['loudness'] > -10:
            data['songs'].append({'song_name': track_id, 'song_features': result[0]})
    return data


def no_filter_songs(tracks):
    """
    A method to put the tracks in a list of features.
    :param tracks: The tracks we want to analyze.
    :return: List of songs, with their features.
    """
    data = dict()
    data['songs'] = list()
    for track_id in tracks:

        # next line get the feature.
        result = sp.audio_features(track_id)
        data['songs'].append({'song_name': track_id, 'song_features': result[0]})
    return data


def get_playlist_by_keys(key_words):
    """
    A method to search for playlists in mood category of spotify.
    :param key_words: A list of key words we search in the name of playlists.
    :return: A list of playlists with the key words in their names.
    """
    list_playlist = list()
    categories = sp.categories()['categories']['items']
    for category in categories:
        if category['name'] == 'Mood':
            result = sp.category_playlists(category_id=category['id'], country='US', limit=50)['playlists']
            for i in range(2):
                mood_playlists = result['items']
                for playlist in mood_playlists:
                    playlist_name = playlist['name']
                    for happy_key in key_words:
                        if happy_key in playlist_name:
                            list_playlist.append(playlist['id'])
                            break
                if result['next']:
                    result = sp.next(result)['playlists']
    return list_playlist


def build_data_songs_from_spotify(key_words, filename, filter_feature_func):
    """
    A method to build the "data.txt" files for each mode.
    :param key_words: The words we search in playlist name.
    :param filename: The name of the file we save.
    :param filter_feature_func: A method to filter the songs we have.
    :return:
    """
    playlists_ids = get_playlist_by_keys(key_words)
    tracks_ids = analyze_playlists(playlists_ids)
    data = filter_feature_func(tracks_ids)
    # now you have list of "vectors"
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    outfile.close()


def main():
    build_data_songs_from_spotify(KEY_HAPPY_WORDS, HAPPY_SONGS_FILE_SET, filter_happy_songs)
    build_data_songs_from_spotify(KEY_SAD_WORDS, SAD_SONGS_FILE_SET, filter_sad_songs)
    build_data_songs_from_spotify(KEY_ANGRY_WORDS, ANGRY_SONGS_FILE_SET, filter_angry_songs)

if __name__ == '__main__':
    main()
