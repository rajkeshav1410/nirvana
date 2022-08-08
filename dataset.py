from operator import index
from re import search
import pandas as pd
import numpy as np
import pickle
import socket
import threading
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from IPython.display import display, HTML
import video

# song_data, con_data = None, None
song_df, con_df, user_df, pop_df, song_features, all_songs = None, None, None, None, None, None


def load_dataset():
	global song_data, con_data, con_df, user_df, song_df, song_features, all_songs
	song_df = pd.read_csv('dataset/song_dataset.csv', dtype={"year": "string"})
	user_df = pd.read_csv('dataset/user_dataset.csv')
	song_df.drop_duplicates(subset='song_id', keep='first', inplace=True)
	print(song_df)

	con_df = pd.merge(user_df, song_df, on='song_id', how='left')
	con_df['song'] = con_df['title'] + ' - ' + con_df['artist_name']
	con_df = con_df.head(10000)
	print(con_df)

	song_features = song_df['title'] + " " + song_df['artist_name'] + " " + song_df['release']
	vectorizer = TfidfVectorizer()
	song_features = vectorizer.fit_transform(song_features.values.astype('U'))

	all_songs = list(con_df['song'].unique())
	# song_data = pickle.dumps(song_df)
	# con_data = pickle.dumps(con_df)


def get_users_by_song(song):
	return con_df[con_df['song'] == song]['user_id'].unique()


def get_songs_of_user(user):
	return con_df[con_df['user_id'] == user]['song'].unique()


def collaborative(user, n=25):
	if type(user) == type([]):
		user_songs = user
		user = ''
	else:
		user_songs = list(get_songs_of_user(user))
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
			df.loc[rank - 1] = [user, all_songs[song_similarity[i][1]], song_similarity[i][0], rank]
			rank += 1

	return df.reset_index(drop=True)

def search_song(song_name):
	if song_name == '':
		return pd.DataFrame()
	return pd.DataFrame(pop_df.loc[pop_df['song'].str.contains(song_name, case=False, na=False)]['song']).reset_index(drop=True)

def popular(n=10):
	global pop_df
	pop_df = con_df.groupby(['song']).agg(
		{'listen_count': 'count'}).reset_index()
	grouped_sum = pop_df['listen_count'].sum()
	pop_df['percentage'] = pop_df['listen_count'] / grouped_sum * 100
	pop_df = pop_df.sort_values(
		['listen_count', 'song'], ascending=[0, 1])
	pop_df['rank'] = pop_df['listen_count'].rank(ascending=0, method='first')
	pop_df = pop_df.reset_index(drop=True)


def content_similarity(songs, n=10):
	print(f'Searching: {songs}')
	title, artist_name = songs.split(' - ')
	# songs = [con_df[con_df['song'] == songs]['song_id'].iloc[0]]
	songs = [song_df[(song_df['title'] == title) & (song_df['artist_name'] == artist_name)]['song_id'].iloc[0]]
	similarity = []
	for song in songs:
		similarity.append(list(cosine_similarity(
			song_features[song_df[song_df['song_id'] == song].index[0]], song_features)[0]))
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

	for i, song in enumerate(recommend_song):
		recommend_song[i] = song_df.iloc[song]['title'] + ' - ' + song_df.iloc[song]['artist_name']

	return recommend_song

def get_popular_song(c, n):
	print('Popularity called')
	pop_data = pickle.dumps(pop_df['song'].head(n))
	c.send(pop_data)
	print('Popularity sent')
	c.close()

def get_collab_song(c, data):
	print(f'Collaborative called')
	df = collaborative(data)['song']
	c.send(pickle.dumps(df.head(50)))
	print('Collaborative sent')
	c.close()

def get_similar_song(c, data):
	print(f'Similarity called: {data}')
	df = pd.DataFrame(content_similarity(data), columns=['song'])
	c.send(pickle.dumps(df['song'].head(50)))
	print('Similarity sent')
	c.close()

def get_searched_song(c, data):
	print('Search called')
	if len(data) > 1:
		df = search_song(data)
		if not df.empty:
			df = df['song']
			c.send(pickle.dumps(df if df.shape[0] < 15 else df.head(15)))
		else:
			c.send(pickle.dumps(pd.DataFrame()))
	else:
		c.send(pickle.dumps(pd.DataFrame()))
	print('Search sent')
	c.close()

def start_server():
	s = socket.socket()
	host = socket.gethostname()
	port = 12345
	s.bind(('localhost', port))
	print("host name:", host, " socket name:", s)
	print("Waiting for client to connect...")
	s.listen()
	while True:
		c, addr = s.accept()
		print('Got connection from', addr, '...')
		data = c.recv(1024).decode().split()
		# if data == 'song_df':
		# 	bytes = c.send(song_data)
		# elif data == 'con_df':
		# 	bytes = c.send(con_data)
		if data[0] == 'popularity':
			threading.Thread(target=get_popular_song, args=(c, int(data[1]))).start()

		elif data[0] == 'similarity':
			threading.Thread(target=get_similar_song, args=(c, " ".join(data[1:]))).start()

		elif data[0] == 'collaborative':
			threading.Thread(target=get_collab_song, args=(c, [" ".join(data[1:])])).start()

		elif data[0] == 'search':
			threading.Thread(target=get_searched_song, args=(c, " ".join(data[1:]))).start()

		# elif data[0] == 'video':
		# 	c.send(pickle.dumps(pd.DataFrame([video.search(" ".join(data[1:]))], columns=['song'])))

load_dataset()
popular()  # invoked once before starting server (must be changed)
start_server()
# df = pd.DataFrame(content_similarity("Cuore nero - Punkreas"), columns=['song'])
# print(df['song'].head(50))
# df = song_df[(song_df['title'] == "Cuore nero") & (
# 	song_df['artist_name'] == "Punkreas")]['song_id'].iloc[0]
# print(df)
