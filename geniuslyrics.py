import lyricsgenius
genius = lyricsgenius.Genius("F-6z9zjNCL_wF_mFpLCGd9y3aF1katSAs_oDEP-NKrCjvrBvjFt2GJE8nFqynMl6")
artist = genius.search_artist("BROCKHAMPTON", max_songs=1, sort="title")
print(artist.songs)

song = genius.search_song("JUNKY", artist.name)
print(song.lyrics)

artist.add_song(song)

print(artist.save_lyrics())
