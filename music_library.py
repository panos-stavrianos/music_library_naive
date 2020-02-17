import os
import webbrowser
from os.path import dirname
from tkinter import *
from tkinter import messagebox
from tkinter.font import Font

import pandas as pd
from fuzzywuzzy import fuzz

from index_music_library import index_music_library

if os.path.exists("file_paths.txt"):
    start_refresh = True
    index_music_library()

if os.path.exists("songs.csv"):
    start_refresh = False
else:
    start_refresh = True
    index_music_library()
    exit(0)


class MusicLibrary(object):
    def __init__(self, master):
        self.songs = pd.read_csv("songs.csv", index_col=False)
        self.songs = self.songs.fillna('')

        self.current_artists = []
        self.current_songs = []

        self.menu_init(master)
        self.entry_artist_init(master)
        self.entry_title_init(master)
        self.popup_init(master)
        self.list_artist_init(master)
        self.list_title_init(master)
        self.binds_init(master)

        self.grid_init(master)
        self.callbackArtist(StringVar())

    def binds_init(self, master):
        self.list_artist.bind("<Double-Button-1>", self.open_artist_folder)
        self.list_artist.bind('<<ListboxSelect>>', self.show_songs_of_artist)

        self.list_title.bind("<Double-Button-1>", self.open_song_folder)
        self.list_title.bind("<Button-3>", self.popup)  # Button-2 on Aqua
        self.list_title.bind('<<ListboxSelect>>', self.popupFocusOut)
        # self.list_title.bind('<<Button-1>>', self.popupFocusOut)

    def grid_init(self, master):
        self.entry_artist.grid(column=0, row=0, ipadx=10, ipady=10, sticky="w")
        self.list_artist.grid(column=0, row=1, ipadx=10, ipady=10, sticky="w")
        self.entry_title.grid(column=1, row=0, ipadx=10, ipady=10, sticky="e")
        self.list_title.grid(column=1, row=1, ipadx=10, ipady=10, sticky="e")

    def entry_artist_init(self, master):
        my_font = Font(size=15)
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.callbackArtist(sv))
        self.entry_artist = Entry(master, textvariable=sv, width=30, bg='gray30', highlightcolor="gray30",
                                  highlightbackground="gray20",
                                  font=my_font,
                                  fg='gray93', highlightthickness=1,
                                  relief="groove", bd=0)

        self.entry_artist.focus()

    def entry_title_init(self, master):
        my_font = Font(size=15)
        sv = StringVar()
        sv.trace("w", lambda name, index, mode, sv=sv: self.callbackSong(sv))
        self.entry_title = Entry(master, textvariable=sv, width=30, bg='gray30', highlightcolor="gray30",
                                 highlightbackground="gray20",
                                 font=my_font, fg='gray93',
                                 highlightthickness=1, bd=0)
        self.entry_title.focus()

    def list_artist_init(self, master):
        my_font = Font(size=15)
        self.list_artist = Listbox(master, selectmode=SINGLE, bg='gray10', fg='gray93', highlightcolor="blue",
                                   highlightbackground="gray20",
                                   highlightthickness=0, bd=0,
                                   height=30, width=30, font=my_font)
        self.list_artist.configure(exportselection=False)

    def list_title_init(self, master):
        my_font = Font(size=15)
        self.list_title = Listbox(master, selectmode=SINGLE, bg='gray10', fg='gray93', highlightcolor="blue",
                                  highlightbackground="gray20", highlightthickness=0, bd=0,
                                  height=30, width=30, font=my_font)
        self.list_title.configure(exportselection=False)

    def popup_init(self, master):
        self.popup_menu = Menu(master, tearoff=0, bg='gray25', fg='gray93', )
        self.popup_menu.add_command(label="Show in files",
                                    command=self.open_song_folder)
        self.popup_menu.add_command(label="Add to vlc",
                                    command=self.add_to_vlc)
        self.popup_menu.add_command(label="Add to audacious",
                                    command=self.add_to_audacious)

    def menu_init(self, master):
        self.menubar = Menu(master, bg='gray10', fg='gray93', bd=0)

        # create a pulldown menu, and add it to the menu bar
        self.filemenu = Menu(self.menubar, tearoff=0, bg='gray13', fg='gray93')
        self.filemenu.add_command(label="Refresh Library", command=self.refresh_library)
        self.filemenu.add_command(label="Help", command=self.open_help)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=master.quit)
        self.menubar.add_cascade(label="Settings", menu=self.filemenu)
        master.config(menu=self.menubar)

    def open_help(self):
        webbrowser.open('https://github.com/panos-stavrianos/music_library')

    def refresh_library(self):
        MsgBox = messagebox.askquestion('Refresh Library', 'This may take a while\nAre you sure you want to continue',
                                        icon='warning')
        if MsgBox == 'yes':
            global start_refresh
            start_refresh = True
            root.destroy()
        else:
            messagebox.showinfo('Return', 'You will now return to the application screen')

    def popupFocusOut(self, event=None):
        print('popupFocusOut')
        self.popup_menu.unpost()

    def popup(self, event):
        try:
            self.current_songs[self.list_title.curselection()[0]]
            self.list_title.select_clear(0, 'end')
            self.list_title.select_set(self.list_title.index("@%s,%s" % (event.x, event.y)))
            self.list_title.event_generate("<<ListboxSelect>>")

            self.popup_menu.tk_popup(event.x_root, event.y_root + 25, 0)
        except:
            pass
        finally:
            self.popup_menu.grab_release()

    def callbackArtist(self, sv):
        text = sv.get()
        # text = (self.entry_artist.get() + event.char).replace("\n", "").replace("\r", "")
        # text = ''.join([x for x in text if x in string.printable])

        artists = self.songs[['artist', 'path']]

        artists.drop_duplicates(subset="artist", keep='first', inplace=True)

        def get_artist_path(x):
            return dirname(dirname(x))

        artists['path'] = artists['path'].apply(get_artist_path)
        if text != "":
            artists['score'] = artists.apply(lambda x: fuzz.token_set_ratio(x['artist'], text), axis=1)
            artists = artists.sort_values(by=['score'], ascending=False).head(100)
        else:
            artists = artists.sort_values(by=['artist'], ascending=True)

        self.list_artist.delete(0, 'end')
        self.current_artists = []

        for i, artist in enumerate(artists.itertuples()):
            self.current_artists.insert(i, [artist.path, artist.artist])
            self.list_artist.insert(i, artist.artist)

        self.list_artist.select_clear(0, 'end')
        self.list_artist.select_set(0)
        return True

    def show_songs_of_artist(self, event=None):
        self.popupFocusOut()

        path, artist = self.current_artists[self.list_artist.curselection()[0]]
        print(self.list_artist.curselection()[0], path, artist)

        songs = self.songs.loc[self.songs['artist'] == artist].sort_index(ascending=False)
        self.list_title.delete(0, 'end')
        self.current_songs = []

        for i, song in enumerate(songs.itertuples()):
            self.current_songs.insert(i, [song.path, song.title])
            self.list_title.insert(i, song.title)

        self.list_title.select_clear(0, 'end')
        self.list_title.select_set(0)
        return True

    def callbackSong(self, sv):
        text = sv.get()

        path, artist = self.current_artists[self.list_artist.curselection()[0]]
        print(path, artist)

        songs = self.songs.loc[self.songs['artist'] == artist]
        songs['score'] = songs.apply(lambda x: fuzz.token_set_ratio(x['title'], text), axis=1)
        songs = songs.sort_values(by=['score'], ascending=False).head(200)
        self.list_title.delete(0, 'end')
        self.current_songs = []

        for i, song in enumerate(songs.itertuples()):
            self.current_songs.insert(i, [song.path, song.title])
            self.list_title.insert(i, song.title)

        self.list_title.select_clear(0, 'end')
        # self.list_title.select_set(0)
        return True

    def open_artist_folder(self, event=None):
        try:
            artist_path = self.current_artists[self.list_artist.curselection()[0]][0]
            os.system('xdg-open "{}"'.format(artist_path))
        except:
            pass

    def open_song_folder(self, event=None):
        print('open_song_folder')
        try:
            song_path = self.current_songs[self.list_title.curselection()[0]][0]
            song_folder_path = os.path.abspath(os.path.join(song_path, os.pardir))
            os.system('xdg-open "{}"'.format(song_folder_path))
        except:
            pass

    def add_to_vlc(self, event=None):
        print('add_to_vlc')

        try:
            song_path = self.current_songs[self.list_title.curselection()[0]][0]
            os.system('vlc --one-instance --playlist-enqueue --no-playlist-autostart "{}" &'.format(song_path))
        except:
            pass

    def add_to_audacious(self, event=None):
        print('add_to_audacious')
        try:
            song_path = self.current_songs[self.list_title.curselection()[0]][0]
            os.system('audacious --enqueue "{}" &'.format(song_path))
        except:
            pass


root = Tk()

root.title("Music Library")
root.configure(background='gray19')

root.geometry('815x800')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=2)
app = MusicLibrary(root)
root.resizable(0, 0)

root.mainloop()

if start_refresh:
    index_music_library()
