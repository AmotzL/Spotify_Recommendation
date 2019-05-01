
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from working_title import *


def plot_histograms_first(data):
    fig, axs = plt.subplots(4, 1, figsize=(9, 9), sharex=True)
    axs[0].hist(data[0])
    axs[0].set_title('Danceability')
    axs[1].hist(data[2])
    axs[1].set_title('Energy')
    axs[2].hist(data[3])
    axs[2].set_title('Liveness')
    axs[3].hist(data[1])
    axs[3].set_title('acousticness')
    plt.show()

def plot_histograms_second(data):
    fig, axs = plt.subplots(3, 1, figsize=(9, 9), sharex=True)
    axs[0].hist(data[4])
    axs[0].set_title('Speechiness')
    axs[1].hist(data[5])
    axs[1].set_title('Valence')
    axs[2].hist(data[6])
    axs[2].set_title('Tempo')
    plt.show()


# danceability, acousticness, energy, liveness, speechiness, valence, tempo


def plot_features_correlation(data, start, stop, sentiment):
    random50 = data.iloc[start:stop]
    random50 = random50[['danceability', 'energy', 'liveness',
                   'acousticness', 'loudness', 'speechiness',
                   'valence', 'tempo', 'duration_ms']]
    corr = random50.corr()
    ax = plt.figure(figsize=(10, 10))
    sns.heatmap(corr, annot=True, xticklabels=corr.columns.values, yticklabels=corr.columns.values)
    plt.title("Correlation of Song Attributes - " + sentiment, size=15)
    plt.show()
    return


def main():
    sentiment = ["Happy", "Sad", "Angry"]
    file_name = ["Data_Files/full_data_happy_songs", "Data_Files/full_data_sad_songs", "Data_Files/full_data_angry_songs"]
    for i in range(3):
        dt = pd.read_csv(file_name[i] + ".csv")
        plot_features_correlation(dt, 0, 50, sentiment[i])

        data = dict()
        with open(file_name[i] + ".txt") as json_file:
            data = json.load(json_file)

        feature_vector = create_all_features_vector(data)
        plot_histograms_first(feature_vector)
        plot_histograms_second(feature_vector)


if __name__ == '__main__':
    main()