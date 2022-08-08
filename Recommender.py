import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

song_df, user_df, con_df = None, None, None

def load_dataset():
	global song_df, user_df, con_df
	song_df = pd.read_csv('dataset/song_dataset.csv', dtype={"year": "string"})
	user_df = pd.read_csv('dataset/user_dataset.csv')
	song_df.drop_duplicates(subset='song_id', keep='first', inplace=True)

	con_df = pd.merge(user_df, song_df, on='song_id', how='left')
	con_df['song'] = con_df['title'] + ' - ' + con_df['artist_name']
	con_df = con_df.head(10000)

def popular(n=10):
	# con_df = pd.merge(user_df, song_df, on='song_id', how='left')
	# con_df['song'] = con_df['title'] + ' - ' + con_df['artist_name']
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
	if type(user) == type([]):
		user_songs = user
		user = ''
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

def content_similarity(songs, n=10):
	song_features = song_df['title'] + " " + song_df['artist_name'] + " " + song_df['release']
	vectorizer = TfidfVectorizer()
	song_features = vectorizer.fit_transform(song_features.values.astype('U'))
	similarity = []
	print('Song features extracted')
	for song in songs:
		 
		similarity.append(list(cosine_similarity(
			song_features[song_df[song_df['song_id'] == song].index[0]], song_features)[0]))
	# print(len(similarity), 'x', len(similarity[0]))
	print('Song found')
	similarity_score = []

	for i in range(len(songs)):
		for index, score in enumerate(similarity[i]):
			similarity_score.append((index, score))

	similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)
	recommend_song, i, j = [similarity_score[0][0]], 0, 1
	while i < n + len(songs) - 1:
		if similarity_score[j][0] != recommend_song[i]:
			recommend_song.append(similarity_score[j][0])
			i += 1
		j += 1
	# return recommend_song[len(songs):]
	for i, song in enumerate(recommend_song):
		recommend_song[i] = song_df.iloc[song]['title']

	# return song_df[song_df['song_id'] in recommend_song]
	return recommend_song
		
def user_content_similarity(user_id, n=10):
	user_data = user_df[user_df['user_id'] == user_id]
	user_data = user_data.sort_values('listen_count', ascending=False)
	return content_similarity(list(user_data['song_id'].head(10)), n)

if __name__ == '__main__':
	load_dataset()
	print('Dataset loaded')
	# print(collaborative(user_df['user_id'][100]))
	# df = collaborative(["Ain't Misbehavin - Sam Cooke"])
	# print(df)
	# df.to_json('fav.json')
	# print(content_similarity(['SOBXHDL12A81C204C0']))
	# print(user_content_similarity(user_df['user_id'][100]))
	# print(content_similarity([con_df[con_df['song'] == 'Hello - Evanescence']['song_id'].iloc[0]]))
