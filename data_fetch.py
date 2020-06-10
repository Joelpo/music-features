import config
import pandas as pd
import numpy as np

def data_fetch(sp):

    ### GET TOP TRACKS
    top_user_tracks_short_term = clean_top_user_tracks(sp.current_user_top_tracks(
    limit=50, offset=0, time_range='short_term')['items'])

    top_user_tracks_medium_term = clean_top_user_tracks(sp.current_user_top_tracks(
        limit=50, offset=0, time_range='medium_term')['items'])

    top_user_tracks_long_term = clean_top_user_tracks(sp.current_user_top_tracks(
        limit=50, offset=0, time_range='long_term')['items'])

    ### GET TRACK FEATURES
    features_short_term = pd.DataFrame.from_dict(sp.audio_features(tracks=top_user_tracks_short_term['track_id']))
    features_medium_term = pd.DataFrame.from_dict(sp.audio_features(tracks=top_user_tracks_medium_term['track_id']))
    features_long_term = pd.DataFrame.from_dict(sp.audio_features(tracks=top_user_tracks_long_term['track_id']))

    ### CONCATENATE TRACK FEATURES AND TOP TRACKS
    top_user_tracks_short_term = pd.concat([top_user_tracks_short_term.reset_index(drop=True),features_short_term.reset_index(drop=True)], axis= 1)
    top_user_tracks_medium_term = pd.concat([top_user_tracks_medium_term.reset_index(drop=True),features_medium_term.reset_index(drop=True)], axis= 1)
    top_user_tracks_long_term = pd.concat([top_user_tracks_long_term.reset_index(drop=True),features_long_term.reset_index(drop=True)], axis= 1)

    ### GET TOP ARTISTS
    top_user_artists_short_term = clean_top_user_artists(sp.current_user_top_artists(
    limit=50, offset=0, time_range='short_term')['items'])

    top_user_artists_medium_term = clean_top_user_artists(sp.current_user_top_artists(
    limit=50, offset=0, time_range='medium_term')['items'])

    top_user_artists_long_term = clean_top_user_artists(sp.current_user_top_artists(
    limit=50, offset=0, time_range='long_term')['items'])

    ### GET PLAYLISTS
    user_playlists = clean_top_user_playlists(sp,sp.user_playlists(sp.current_user()['id'])['items'])


    ## RETURN DICT WITH RESULTS
    return {
        'top_user_tracks_short_term':top_user_tracks_short_term,
        'top_user_tracks_medium_term':top_user_tracks_medium_term,
        'top_user_tracks_long_term':top_user_tracks_long_term,
        'top_user_artists_short_term':top_user_artists_short_term,
        'top_user_artists_medium_term':top_user_artists_medium_term,
        'top_user_artists_long_term':top_user_artists_long_term,
        'user_playlists': user_playlists
    }


    # [top_user_tracks_short_term,top_user_tracks_medium_term,top_user_tracks_long_term],[top_user_artists_short_term,top_user_artists_medium_term,top_user_artists_long_term],[user_playlists]]


# define clean_top_user_playlists : return dataframe of top user tracks with selected columns
# performs some aggregation : adding tracks id list
def clean_top_user_playlists(sp,user_playlists):
    # columns ['playlist_name', 'playlist_id', 'playlist_tracks_id']
    result_df = pd.DataFrame(columns=[
        'playlist_name', 'playlist_id', 'playlist_tracks_id'])

    for playlist in user_playlists:
        index = user_playlists.index(playlist)
        tracks_inside_playlist = sp.playlist_tracks(
            playlist_id=playlist['id'], limit=100)

        tracks_id_wrapped = ["" for x in range(
            len(tracks_inside_playlist['items']))]

        for track in tracks_inside_playlist['items']:
            current_track_id = track['track']['id']
            tracks_id_wrapped[tracks_inside_playlist['items'].index(
                track)] = current_track_id

        new_entry = pd.Series(data={
            'playlist_name': playlist['name'], 'playlist_id': playlist['id'], 'playlist_tracks_id': tracks_id_wrapped
        }, name=str(index + 1))
        # print("new entry :{}".format(new_entry))
        result_df = result_df.append(new_entry, ignore_index=False)

    return result_df

# define clean_top_user_tracks : return dataframe of top user tracks with selected columns
def clean_top_user_tracks(top_user_tracks):
    # columns ['track_name', 'artist_name', 'track_id', 'artist_id', 'popularity']
    result_df = pd.DataFrame(columns=['track_name', 'artist_name', 'track_id', 'artist_id', 'popularity'])
    popularity = None
    for track in top_user_tracks:
        index = top_user_tracks.index(track)
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        popularity = track['popularity']
        track_id = track['id']
        artist_id = track['artists'][0]['id']
        # define new entry Series element and name : index + 1
        new_entry = pd.Series(data={'track_name': track_name,
                                    'artist_name': artist_name,
                                    'track_id': track_id,
                                    'artist_id': artist_id,
                                    'popularity': popularity
                                    }, name=str(index + 1)
                              )
        # Append the new row to the review df
        result_df = result_df.append(new_entry, ignore_index=False)
    return result_df

# define clean_top_user_artists : return dataframe of top user artists with selected columns
def clean_top_user_artists(top_user_artists):
    # columns ['artist_name', 'artist_id', 'popularity', 'genre']
    result_df = pd.DataFrame(columns=['artist_name', 'artist_id', 'popularity', 'genre'])
    popularity = None
    for artist in top_user_artists:
        index = top_user_artists.index(artist)
        artist_name = artist['name']
        artist_id = artist['id']
        popularity = artist['popularity']
        genre = artist['genres']
        # define new entry Series element and name : index + 1
        new_entry = pd.Series(data={
        'artist_name': artist_name,'artist_id': artist_id,'popularity': popularity,'genre': genre
                                    }, name=str(index + 1)
                              )
        result_df = result_df.append(new_entry, ignore_index=False)
    return result_df
