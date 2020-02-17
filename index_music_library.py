import csv
import logging
import os
from os.path import splitext, basename


def index_music_library():
    library_path = os.getenv('MUSIC_LIBRARY_PATHS', "")
    if library_path == "":
        exit(0)
    logging.basicConfig(filename='index_music_library.log', filemode='w', level="INFO",
                        format='%(message)s')

    logging.info("Start Indexing")
    log_file = os.path.abspath("index_music_library.log")
    os.system('gnome-terminal -- tail -F "{}"'.format(log_file))
    if not os.path.exists("file_paths.txt"):

        file_paths = []
        for root, dirs, files in os.walk(library_path):
            print(root)
            logging.info("Indexing->" + root)

            for file in files:
                try:
                    if file.find(".mp3") < 0:
                        continue
                    file_path = os.path.abspath(os.path.join(root, file))
                    file_paths.append(file_path)

                except Exception as e:
                    logging.error(e)
                    continue

        with open("file_paths.txt", "w") as f:
            f.writelines("%s\n" % f_p for f_p in file_paths)

    with open("file_paths.txt") as f:
        file_paths = [current_path.rstrip() for current_path in f.readlines()]

    count = 0
    songs = []

    while len(file_paths) != 0:
        file_path = file_paths.pop()
        p = file_path.split("/")
        tag = {'path': file_path,
               'artist': p[4],
               'album': p[5],
               'title': splitext(basename(file_path))[0]}
        songs.append(tag)

        count += 1

    keys = songs[0].keys()
    with open('songs.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(songs)
    os.remove("file_paths.txt")
    logging.info("\nThat's it! Done!\n Now restart the application and you are ready to go!")
