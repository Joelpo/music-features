from flask import Flask, redirect, request, session  # FLASK
from flask.json import jsonify
import dash  # DASH
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd  # PANDAS
import spotipy  # SPOTIPY
from spotipy.oauth2 import SpotifyClientCredentials
import json
from datetime import timedelta
# LOCAL
import config
import secret
import helper
from data_fetch import data_fetch


# initialise the app
flask_app = Flask(__name__)
flask_app.secret_key = secret.FLASK_SECRET_KEY

app = dash.Dash(name=__name__, assets_folder=config.ASSETS_PATH, server=flask_app, external_stylesheets=[
                dbc.themes.LUX, config.fontawesome], url_base_pathname='/dashboard/')

server = app.server

# INITIALISE CACHE
cache = {}


@flask_app.route('/')
def index():
    return redirect(helper.AUTH_URL)


@flask_app.route("/callback/")
def callback():
    auth_token = request.args['code']
    auth_header = helper.authorize(auth_token)
    session['auth_header'] = auth_header

    # BACK END CALLS
    sp = spotipy.Spotify(session['auth_header'])
    # recover user ID
    session['user_id'] = sp.me()['id']
    # Fetch Data
    user_data = data_fetch(sp)

    # CACHING
    cache['{}/top_user_tracks_short_term'.format(
        session['user_id'])] = user_data['top_user_tracks_short_term'].to_json()
    cache['{}/top_user_tracks_medium_term'.format(
        session['user_id'])] = user_data['top_user_tracks_medium_term'].to_json()
    cache['{}/top_user_tracks_long_term'.format(
        session['user_id'])] = user_data['top_user_tracks_long_term'].to_json()
    cache['{}/top_user_artists_short_term'.format(
        session['user_id'])] = user_data['top_user_artists_short_term'].to_json()
    cache['{}/top_user_artists_medium_term'.format(
        session['user_id'])] = user_data['top_user_artists_medium_term'].to_json()
    cache['{}/top_user_artists_long_term'.format(
        session['user_id'])] = user_data['top_user_artists_long_term'].to_json()
    cache['{}/user_playlists'.format(session['user_id'])
          ] = user_data['user_playlists'].to_json()
    # print(session['top_user_tracks_short_term'])

    return redirect("/dashboard/")


def valid_token(resp):
    return resp is not None and not 'error' in resp

# APP LAYOUT


colors = {
    'background': '#FFFFFF',
    'text': '#111111'
}

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button("Search", color="secondary", className="ml-2"),
            width="auto",
        ),
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url(
                        'fav-music.png'), height="30px")),
                    # dbc.Col(dbc.NavbarBrand(", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/dashboard",
        ),
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Short term", href="/top_user_tracks_short_term", id="tracks-short-link"), dbc.DropdownMenuItem("Medium term",
                                                                                                                                  href="/top_user_tracks_medium_term", id="tracks-medium-link"), dbc.DropdownMenuItem("Long term", href="/top_user_tracks_long_term", id="tracks-long-link")],
            label="Top tracks",
            nav=True,
            color="primary"
        ),
        dbc.DropdownMenu(
            [dbc.DropdownMenuItem("Short term", href="/top_user_artists_short_term", id="artists-short-link"), dbc.DropdownMenuItem("Medium term",
                                                                                                                                    href="/top_user_artists_medium_term", id="artists-medium-link"), dbc.DropdownMenuItem("Long term", href="/top_user_artists_long_term", id="artists-long-link")],
            label="Top artists",
            nav=True,
        ),

        dbc.NavItem(
            dbc.NavLink("Insights", active=True, href="/insights")
        ),


        dbc.DropdownMenu(label="About", nav=True, children=[
            dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"),
                                  "  Contacts"], href=config.contacts, target="_blank"),
            dbc.DropdownMenuItem(
                [html.I(className="fa fa-github"), "  Code"], href=config.code, target="_blank")
        ]),

        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(search_bar, id="navbar-collapse", navbar=True),
    ],
    color="secondary",
    dark=False,
)

# add callback for toggling the collapse on small screens


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


content = html.Div(
    children=[
        # dcc.Location(id='url', refresh=False), # URL BAR does not render anything
    ],
    id="page-content",
    style=CONTENT_STYLE
)

app.layout = html.Div([dcc.Location(id="url", refresh=False), navbar, content])


@app.callback(
    dash.dependencies.Output(component_id='page-content',
                             component_property='children'),
    [dash.dependencies.Input(component_id='url', component_property='pathname')])
def display_page(pathname):
    # backend call - GET USER DATA

    # page variables
    data_path_names = ['dashboard', 'top_user_tracks_short_term', 'top_user_tracks_medium_term', 'top_user_tracks_long_term',
                       'top_user_artists_short_term', 'top_user_artists_medium_term', 'top_user_artists_long_term', 'insights']
    page_description = ''
    data_table = None
    page_content = ''
    page_text = ''

    data_requested = str(pathname).replace('/', '')
    print(data_requested)

    if (data_requested == 'top_user_tracks_short_term'):
        page_description = 'Your most listened tracks in the past 4 weeks'
    elif(data_requested == 'top_user_tracks_medium_term'):
        page_description = 'Your most listened tracks in the past 6 months'
    elif(data_requested == 'top_user_tracks_long_term'):
        page_description = 'Your most listened tracks of all time'
    elif(data_requested == 'top_user_artists_short_term'):
        page_description = 'Your most listened artists in the past 4 weeks'
    elif(data_requested == 'top_user_artists_medium_term'):
        page_description = 'Your most listened artists in the past 6 months'
    elif(data_requested == 'top_user_artists_long_term'):
        page_description = 'Your most listened artists of all time'
    elif(data_requested == 'about'):
        page_description = 'An experiment on Spotifys API DATA.'
    elif(data_requested == 'dashboard'):
        page_description = 'Welcome!'
        page_text = 'This simple app lets you consult your favourite songs and artists on Spotify. Take a look at your favourite tracks from all time :'
    elif(data_requested == 'insights'):
        page_description = 'Here are some insights on the music you enjoy.'
    else:
        page_description = 'Welcome!'

    if (data_requested in data_path_names):
        if(data_requested == 'dashboard'):
            data_table = generate_table(pd.read_json(
                cache['{}/top_user_tracks_long_term'.format(session['user_id'])]))

        elif (data_requested == 'insights'):
            data_table = "TODO"

        else:
            data_table = generate_table(pd.read_json(
                cache['{}/{}'.format(session['user_id'], data_requested)]))

    # return page content
    return html.Div([
        html.H3(page_description),
        page_text,
        html.Br(), html.Br(),
        data_table
    ])


# DASH functions
# Requires DASH -  Generates an html table
def generate_table(dataframe, max_rows=50):
    return dbc.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
