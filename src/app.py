import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os

client_id = os.environ['CLIENT_ID']
client_secret = os.environ["CLIENT_SECRET"]

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class ArtistsNetwork():
    def __init__(self, spotipy_client):
        self.network = Network(width="100%")
        self.next_nodes_artists = []
        self.appended_artists_ids = []
        self.spotipy_client = spotipy_client
        self.max_artists_per_artist = 5

    def _add_artists_nodes(self, artist, is_last_depth=False):
        nodes = sp.artist_related_artists(artist["id"])["artists"]
        nodes = nodes[:self.max_artists_per_artist]

        self.next_nodes_artists = [
            a for a in self.next_nodes_artists if "id" in a and a["id"] != artist["id"]]

        for node in nodes:
            if not is_last_depth and node["id"] not in self.appended_artists_ids:
                next_artist = self.spotipy_client.artist(node["id"])
                self.next_nodes_artists.append(next_artist)
            image = node["images"][-1]["url"] if len(
                node["images"]) > 0 else ""
            href = node['external_urls']['spotify'] if len(
                node["external_urls"]) > 0 else ""
            self.network.add_node(node["name"], image=image, shape="circularImage",
                                  title=f"<a href=\"{href}\" target='_parent'>詳細</a>")
            self.network.add_edge(artist["name"], node["name"])

            self.appended_artists_ids.append(node["id"])

    def create_network(self, origin_artist, max_depth=4):
        self.network.add_node(
            origin_artist["name"], image=origin_artist["images"][-1]["url"], shape="circularImage")
        self.next_nodes_artists.append(origin_artist)

        for depth in range(max_depth):
            for artist in self.next_nodes_artists:
                self._add_artists_nodes(
                    artist, is_last_depth=depth == max_depth)


st.title("Spotify Artists Network")
q = st.text_input("", placeholder="Beatles")

if st.button("検索&作成"):
    artists = sp.search(q, type=["artist"])
    original_artist = artists["artists"]["items"][0] if len(
        artists["artists"]["items"]) > 0 else None
    if original_artist is None:
        st.error("検索結果がありません")
        st.stop()
    st.image(original_artist["images"][-1]["url"])
    st.markdown(
        f"[{original_artist['name']}](https://open.spotify.com/artist/{original_artist['id']})")
    with st.spinner("作成中"):
        an = ArtistsNetwork(sp)
        related_artists = sp.artist_related_artists(
            original_artist["id"])["artists"]
        an.create_network(original_artist)
        an.network.show(f"output_{original_artist['id']}.html")

        html_file = open(
            f"output_{original_artist['id']}.html", 'r', encoding='utf-8')
        source_code = html_file.read()
        components.html(source_code, height=2000, width=1000)
        st.code("各点最大5本のエッジ、最大の深さは4")
