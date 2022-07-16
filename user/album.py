import requests
import settings
import time

artist_genres = {}
playlists = {}

def get_user_id():
    url = 'https://api.spotify.com/v1/me'
    response = perform_get_request(url)
    user_id = response['id']
    return user_id

headers = {
        "authorization": "Bearer " + settings.AUTH_TOKEN 
}
def perform_get_request(url):
    response = requests.get(url, headers=headers).json()
    return response

def perform_post_request(url, body):
    response = requests.post(url , data=body, headers=headers).json()
    return response

def get_tracks(playlist_id):
    off_set = 0
    tracks = {}
    while(True):
        url = 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks?fields=items(track(album(artists%2Cid)%2C%20uri))&limit=100&offset=' + str(off_set)
        response = perform_get_request(url)
        for i in response['items']:
            album = i['track']['album']
            track_id = i['track']['uri']
            artist_id = album['artists'][0]['id']
            tracks[track_id] = artist_id
        off_set += 100
        if len(response['items']) == 0:
            return tracks


def get_artist_genre(artists_ids):
    for x in range(0, len(artists_ids), 50):
        y = x+50
        artists = artists_ids[x:y]
        formatted_artists = str(artists).replace('[', '').replace(']', '').replace('\'', '').replace(' ', '')
        url = 'https://api.spotify.com/v1/artists?ids=' + formatted_artists
        response = perform_get_request(url)
        artists_genre = response['artists']
        for i in range(0, len(artists), 1):
            id = artists_genre[i]['id']
            if id in artist_genres:
                continue
            artist = artists_genre[i]
            genres = set()
            if len(artist['genres']) == 0:
                artist_genres[id] = {settings.DEFAULT_PLAYLIST_NAME}
            else:
                for i in artist['genres']:
                    genre = i.split()
                    genres.add(genre[-1])
                    artist_genres[id] = genres

def insert_tracks_to_playlist():
    tracks = playlists[settings.PLAYLIST_NAME]['tracks']
    get_artist_genre(list(tracks.values()))
    for key, value in tracks.items():
        added_to_playlist = []
        genres = artist_genres[value]
        for i in genres:
            if i in settings.genres:
                tracks = playlists[i]['tracks']
            else:
                tracks = playlists[settings.DEFAULT_PLAYLIST_NAME]['tracks']
                i = settings.DEFAULT_PLAYLIST_NAME
            if key not in tracks and i not in added_to_playlist:
                added_to_playlist.append(i)
                key = key.replace(':', '%3A')
                playlist_id = playlists[i]['id']
                url = 'https://api.spotify.com/v1/playlists/'+ playlist_id +'/tracks?uris=' + key
                response = perform_post_request(url, None)
                print(key)
        time.sleep(0.5)


def create_playlists():
    off_set = 0
    while(True):
        url = 'https://api.spotify.com/v1/users/' + get_user_id() + '/playlists?limit=50&offset=' + str(off_set)
        response = perform_get_request(url)
        items = response['items']
        if len(items) == 0:
            break
        for i in items:
            name = i['name']
            id = i['id']
            tracks = get_tracks(id)
            playlists[name] = {
                'id': id,
                'tracks': tracks
            }
        off_set += 50
    for i in settings.genres:
        if i not in playlists:
            url = 'https://api.spotify.com/v1/users/' + settings.USER_ID + '/playlists'
            request_body = {
                "name": str(i)
            }
            request_body = str(request_body).replace('\'', '\"')
            response = perform_post_request(url, request_body)
            playlists[i] = response['id']
            time.sleep(1)
    insert_tracks_to_playlist()


if __name__ == "__main__":
    create_playlists()