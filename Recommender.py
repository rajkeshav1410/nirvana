import pandas as pd
import numpy as np

# song_df, user_df, con_df = None, None, None

# def load_dataset():
song_df = pd.read_csv('dataset/song_dataset.csv', dtype={"year": "string"})
user_df = pd.read_csv('dataset/user_dataset.csv')
song_df.drop_duplicates(subset='song_id', keep='first', inplace=True)

con_df = pd.merge(user_df, song_df, on='song_id', how='left')
con_df['song'] = con_df['title'] + ' - ' + con_df['artist_name']
con_df = con_df.head(10000)


def popular(n=10):
    con_df = pd.merge(user_df, song_df, on='song_id', how='left')
    con_df['song'] = con_df['title'] + ' - ' + con_df['artist_name']
    song_grouped = con_df.groupby(['song']).agg(
        {'listen_count': 'count'}).reset_index()
    grouped_sum = song_grouped['listen_count'].sum()
    song_grouped['percentage'] = song_grouped['listen_count'] / \
        grouped_sum * 100
    song_grouped = song_grouped.sort_values(
        ['listen_count', 'song'], ascending=[0, 1])
    song_grouped['rank'] = song_grouped['listen_count'].rank(
        ascending=0, method='first')
    return song_grouped.head(n)


def get_users_by_song(song):
    return con_df[con_df['song'] == song]['user_id'].unique()


def get_songs_of_user(user):
    return con_df[con_df['user_id'] == user]['song'].unique()


def collaborative(user, n=10):
    if type(user) == 'list':
        user_songs = user
    else:
        user_songs = list(get_songs_of_user(user))
    all_songs = list(con_df['song'].unique())
    com_user = []
    for song in user_songs:
        com_user.append(list(get_users_by_song(song)))
    co_matrix = np.matrix(
        np.zeros(shape=(len(user_songs), len(all_songs))), float)
    for i in range(len(all_songs)):
        user_i = set(get_users_by_song(all_songs[i]))
        for j in range(len(user_songs)):
            com_user_ij = user_i.intersection(com_user[j])
            if com_user_ij != 0:
                co_matrix[j, i] = len(com_user_ij) / \
                    len(user_i.union(com_user[j]))
            else:
                co_matrix[j, i] = 0
    song_similarity = np.array(co_matrix.sum(
        axis=0) / co_matrix.shape[0])[0].tolist()
    song_similarity = sorted(
        [(e, i) for i, e in enumerate(song_similarity)], reverse=True)
    df = pd.DataFrame(columns=['user_id', 'song', 'score', 'rank'])
    rank = 1
    for i in range(len(song_similarity)):
        if not np.isnan(song_similarity[i][0]) and all_songs[song_similarity[i][1]] not in song_similarity and rank <= n:
            df.loc[rank - 1] = [user, all_songs[song_similarity[i][1]],
                                song_similarity[i][0], rank]
            rank += 1

    return df if df.shape[0] != 0 else 0


if __name__ == '__main__':
    # load_dataset()
    print(collaborative(user_df['user_id'][100]))
