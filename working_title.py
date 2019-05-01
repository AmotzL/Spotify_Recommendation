
import json
import os
import spotipy
import spotipy.util as spot_util
import csv
from scipy import spatial
from globs import *

try:
    token = spot_util.prompt_for_user_token(USER_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
                                        , redirect_uri='http://google.com/', scope='playlist-modify-public')
except:
    os.remove(f".cache-{USER_ID}")
    token = spot_util.prompt_for_user_token(USER_ID, client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET, redirect_uri='http://google.com/', scope='playlist-modify-public')

sp = spotipy.Spotify(auth=token)


def get_key(item):
    """
    A method to get the key we sort according to it.
    """
    return item[3]


def cos_sim(first, second):
    """
    A method to calculate the cosine distance between two vectors.
    """
    return 1 - spatial.distance.cosine(first, second)


def manhattan_sim(x, y):
    """
    A method to calculate the manhattan distance between two vectors.
    """
    return sum(abs(a - b) for a, b in zip(x, y))


def feature_vector_mean(vec):
    mean = []
    for feature in vec:
        mean.append(feature[round(len(feature) / 2)])
    return mean


def feature_vector_average(vec):
    """
    A method to calculate the aevrage of the features we collected.
    """
    average = []
    for feature in vec:
        average.append(sum(feature) / len(feature))
    return average


def create_all_features_vector(data):
    """

    :param data:
    :return:
    """
    danceability, acousticness, energy, instrumentalness = [], [], [], []
    liveness, speechiness, valence, tempo = [], [], [], []
    # loudness = []
    for song in data['songs']:
        vec = song['song_features']
        danceability.append(vec['danceability'])
        acousticness.append(vec['acousticness'])
        energy.append(vec['energy'])
        # instrumentalness.append(vec['instrumentalness'])
        liveness.append(vec['liveness'])
        speechiness.append(vec['speechiness'])
        valence.append(vec['valence'])
        tempo.append(vec['tempo'] / 250)
        # loudness.append(vec['loudness'])

    danceability.sort()
    acousticness.sort()
    energy.sort()
    instrumentalness.sort()
    liveness.sort()
    speechiness.sort()
    valence.sort()
    tempo.sort()
    return [danceability, acousticness, energy, liveness, speechiness, valence, tempo]


def create_summarized_features_vector(data):
    """
    A method to create summarized feature vector for creating the playlist. (the distance might change)
    """
    danceability, energy, valence = [], [], []
    # loudness = []
    for song in data['songs']:
        vec = song['song_features']
        danceability.append(vec['danceability'])
        energy.append(vec['energy'])
        valence.append(vec['valence'])

    danceability.sort()
    energy.sort()
    valence.sort()
    return [danceability, energy, valence]


def build_average_all_feature_vector(data):
    """
    A method to build the average feature vector.
    :param data: The data we crawl from playlist mood of spotify.
    :return: The average feature of vectors.
    """
    features = create_all_features_vector(data)
    return feature_vector_average(features)


def build_average_summarized_feature_vector(data):
    """
    A method to build the average feature vector.
    :param data: The data we crawl from playlist mood of spotify.
    :return: The average feature of vectors.
    """
    features = create_summarized_features_vector(data)
    return feature_vector_average(features)


def build_vec_all_feature(track):
    """
    A method to analyze the record of a given dataset.
    :param track: the record.
    :return:
    """
    vec = list()
    vec.append(float(track['danceability']))
    vec.append(float(track['acousticness']))
    vec.append(float(track['energy']))
    vec.append(float(track['liveness']))
    vec.append(float(track['speechiness']))
    vec.append(float(track['valence']))
    vec.append(float(track['tempo'])/250)
    return vec


def build_vec_summarized_feature(track):
    """
    A method to analyze the record of a given dataset.
    :param track: the record.
    :return:
    """
    vec = list()
    vec.append(float(track['danceability']))
    vec.append(float(track['energy']))
    vec.append(float(track['valence']))
    return vec


def filter_for_happy(row, row_vector, average_vec):
    """
    A method to filter the songs for happy.
    :param average_vec: Our average vec.
    :param row: The record from the csv file.
    :param row_vector: The vector feature of the record.
    :return: The {Blank} distance
    """
    if float(row['valence']) > 0.7 and float(row['popularity']) > 85:
        return cos_sim(average_vec, row_vector)


def filter_for_sad(row, row_vector, average_vec):
    """
    A method to filter the songs for sad.
    :param average_vec: Our average vec.
    :param row: The record from the csv file.
    :param row_vector: The vector feature of the record.
    :return: The {Blank} distance
    """
    if float(row['valence']) < 0.2 and float(row['popularity']) > 80:
        return manhattan_sim(average_vec, row_vector)


def filter_for_angry(row, row_vector, average_vec):
    """
    A method to filter the songs for sad.
    :param average_vec: Our average vec.
    :param row: The record from the csv file.
    :param row_vector: The vector feature of the record.
    :return: The {Blank} distance
    """
    if float(row['energy']) > 0.8 and float(row['loudness']) > -7:
        return cos_sim(average_vec, row_vector)


def build_score_list(average_vec, build_vec_feature, filter_add_func):
    """
    A method to build the best songs sorted by the filter_add_func.
    """
    score_similarity = list()
    with open('Data_Files/data_set_song.csv', 'rt') as data_set:
        reader = csv.DictReader(data_set)

        # we go over the data set and compute the manhattan distance between the track and the average vector.
        for row in reader:
            song_name = row['track_name']
            song_artist = row['artist_name']
            song_id = row['track_id']
            vector = build_vec_feature(row)
            distance_score = filter_add_func(row, vector, average_vec)
            if distance_score:
                score_similarity.append((song_name, song_artist, song_id, distance_score))

    # now we need to sort.
    score_similarity.sort(key=get_key, reverse=True)
    return score_similarity

# danceability, acousticness, energy, liveness, speechiness, valence, tempo


def build_playlist_mode(input_filename, filter_add_func, build_average_feature_vector, build_vec_row, playlist_name):
    """
    A method to build a playlist of 10 songs from dataset from studying the dataset of the input_filename.
    :param input_filename: The file of the input songs we learn.
    :param filter_add_func: The method we filter by.
    :param build_average_feature_vector: The method for building the average feature vectors list.
    :param build_vec_row: The method we build the row vec by.
    :param playlist_name: The name of the playlist we create in Spotify
    """
    with open(input_filename) as json_file:
        data = json.load(json_file)

        # after reading the file we build the average feature vector.
        average_vec = build_average_feature_vector(data)

        # now we build the list of tracks after some filtering.
        score_list = build_score_list(average_vec, build_vec_row, filter_add_func)
        top_10_tracks = [score_list[i][2] for i in range(10)]

        new_playlist = sp.user_playlist_create(USER_ID, playlist_name)
        sp.user_playlist_add_tracks(USER_ID, new_playlist['id'], top_10_tracks)
        print(new_playlist['external_urls']['spotify'])


def main():
    build_playlist_mode(HAPPY_SONGS_FILE_SET, filter_for_happy, build_average_all_feature_vector, build_vec_all_feature, 'playlist_1')
    build_playlist_mode(ANGRY_SONGS_FILE_SET, filter_for_angry, build_average_all_feature_vector, build_vec_all_feature, 'playlist_2')
    build_playlist_mode(SAD_SONGS_FILE_SET, filter_for_sad, build_average_all_feature_vector, build_vec_all_feature, 'playlist_3')
    build_playlist_mode(HAPPY_SONGS_FILE_SET, filter_for_happy, build_average_summarized_feature_vector, build_vec_summarized_feature, 'playlist_4')
    build_playlist_mode(SAD_SONGS_FILE_SET,filter_for_sad, build_average_summarized_feature_vector, build_vec_summarized_feature, 'playlist_5')
    build_playlist_mode(ANGRY_SONGS_FILE_SET, filter_for_angry, build_average_summarized_feature_vector, build_vec_summarized_feature, 'playlist_6')


if __name__ == '__main__':
    main()
