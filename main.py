
from PySide6.QtWidgets import (
    QWidget,
    QApplication,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QSlider
)

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, Qt, QTimer, QSignalBlocker

import subprocess, os, random

from mutagen import File

# Stores the paths of imported music files
music_library = []
shuffled_library = []

current_index = 0
shuffled_index = 0

next_scheduled = False
is_shuffled = False


def toggle_shuffle(media, track_label):
    global shuffled_index
    global is_shuffled

    is_shuffled = not is_shuffled

    if is_shuffled:
        media.pause()
        media.setSource(QUrl())
        shuffle_library()
        shuffled_index = 0
        random_songs(media, track_label)
#  Shuffling library
def shuffle_library():  
    global shuffled_library
    if is_shuffled == True:
        shuffled_library = music_library.copy()
        random.shuffle(shuffled_library)
    return shuffled_library
    

def random_songs(media, track_label):
    # 1. Stop the current song
    # 2. Shuffle the music library
    # 3. Play the first music from the library, Continue
    # 4. Finish the last song shuffle again.
    global shuffled_library


    if media.source().isEmpty():
        file_path = shuffled_library[shuffled_index]
        song_url = QUrl.fromLocalFile(file_path)
        track_label.setText(get_title(file_path))
        media.setSource(song_url)
        media.play()

    
# Get title func

def get_title(file_path):
    file = File(file_path)

    if file is not None and file.get("TIT2"):
        return str(file.get("TIT2"))
    else: 
        return os.path.splitext(os.path.basename(file_path))[0]


def next_music(media, track_label):
    global current_index 
    global is_shuffled
    global shuffled_index
    global next_scheduled
    global shuffled_library

    if is_shuffled:
        if not music_library:
            return
        else:
            if shuffled_index == len(shuffled_library) - 1:
                shuffled_library = shuffle_library() 
                shuffled_index = 0
            else:
                shuffled_index += 1
                shuffled_index %= len(shuffled_library)

        file_path = shuffled_library[shuffled_index]
        song_url = QUrl.fromLocalFile(file_path)
        track_label.setText(get_title(file_path))
        media.setSource(song_url)
        media.play()

    else:
        if not music_library:
            return
        else:
            current_index += 1
            current_index %= len(music_library)
        file_path = music_library[current_index]
        song_url = QUrl.fromLocalFile(file_path)
        track_label.setText(get_title(file_path))
        media.setSource(song_url)
        media.play()

def previous_music(media, track_label):
    global current_index
    global is_shuffled
    global shuffled_index

    if is_shuffled:
        if not music_library:
            return
        else:
            shuffled_index -= 1
            shuffled_index %= len(shuffled_library)
            file_path = shuffled_library[shuffled_index]
            song_url = QUrl.fromLocalFile(file_path)
            track_label.setText(get_title(file_path))
            media.setSource(song_url)
            media.play()

    else:
        if not music_library:
            return
        current_index -= 1
        current_index %= len(music_library)
        file_path = music_library[current_index]
        song_url = QUrl.fromLocalFile(file_path)
        track_label.setText(get_title(file_path))
        media.setSource(song_url)
        media.play()

# PLAY MUSIC
def play_music(media, track_label):

    # Check whether the library is empty
    if not music_library:
        return


    if media.source().isEmpty():
        # Get the first song from the library
        file_path = music_library[current_index]

        # Convert the file path into a Qt URL
        song_url = QUrl.fromLocalFile(file_path)
        track_label.setText(get_title(file_path))
        # Set the selected song as the player's source
        media.setSource(song_url)

    # Start playback
    media.play()

def update_progress(media, slider, track_label):
    global next_scheduled
    song_time_stamp = media.position()
    song_duration = media.duration()
    slider.setRange(0, song_duration)
    slider.setMaximum(song_duration)
    slider.setValue(song_time_stamp)
    if song_time_stamp == song_duration and song_duration > 0 and not next_scheduled:
        next_scheduled = True
        QTimer.singleShot(2000, lambda: next_music(media, track_label))

def seek_music(media, position):
    media.setPosition(position)

# PAUSE MUSIC
def pause_music(media):
    print("Pause button clicked!")
    media.pause()

def seek_volume(volume):
    subprocess.run([
        "wpctl",
        "set-volume",
        "@DEFAULT_AUDIO_SINK@",
        f"{volume}%"
    ])

def get_system_volume():
    result = subprocess.run(
        ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
        capture_output=True,
        text=True
    )

    volume = float(result.stdout.split()[1])
    return round(volume * 100)

def sync_system_volume(slider):
    volume = get_system_volume()

    if slider.value() != volume:
        blocker = QSignalBlocker(slider)
        slider.setValue(volume)
        del blocker

# ADD MUSIC
def add_music(playlist_container, media, track_label, playlist_container_label):
    # Open a file dialog and get selected file paths
    file_paths, selected_filter = QFileDialog.getOpenFileNames()

    # Exit if the user selected no files
    if not file_paths:
        return

    # Iterate through the selected files
    for file in file_paths:

        # Skip files already in the library
        if file in music_library:
            continue

        # Add new file paths to the library
        music_library.append(file)

    # Display the total number of songs
    print(f"Library contains {len(music_library)} songs")
    music_playlist(playlist_container, media, track_label, playlist_container_label)


def play_certain_music(file_path, media, track_label):
    global current_index
    current_index = music_library.index(file_path)
    song_url = QUrl.fromLocalFile(file_path)
    media.setSource(song_url)
    track_label.setText(get_title(file_path))
    media.play()


# Music tracks

def music_playlist(playlist_container, media, track_label, playlist_container_label):
    while playlist_container.layout().count() > 0:
        item = playlist_container.layout().takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    playlist_container_label = QLabel("Tracks")
    playlist_container.layout().addWidget(playlist_container_label)
    for music in music_library:
        music_button = QPushButton(f"{get_title(music)}")
        music_button.setProperty("file_path", music)
        file_path = music_button.property("file_path")
        music_button.clicked.connect(lambda checked=False, file_path=file_path: play_certain_music(file_path, media, track_label))
        playlist_container.layout().addWidget(music_button)

# MAIN APPLICATION
def main():

    # Create the Qt application
    app = QApplication([])

    # Create the playback engine and audio output
    media = QMediaPlayer()
    audio = QAudioOutput()

    # Connect the audio output to the player
    media.setAudioOutput(audio)


    # Create the main window and vertical layout
    window = QWidget()
    layout = QVBoxLayout()

    # LABELS
    title_label = QLabel("Penguin Music")
    subtitle_label = QLabel("Free. Open Source. Hyprland + Arch")

    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)

    # track label
    track_label = QLabel("")

    # Music Playlist

    playlist_container = QWidget()
    playlist_container.setLayout(QVBoxLayout())

    playlist_container_label = QLabel("Tracks")
    playlist_container.layout().addWidget(playlist_container_label)

    music_playlist(playlist_container, media, track_label, playlist_container_label)

    layout.addWidget(playlist_container)


    # VOLUME SLIDER

    volume_slider = QSlider(Qt.Orientation.Vertical)
    volume_slider.setRange(0, 100)

    volume_slider.setValue(get_system_volume())

    layout.addWidget(volume_slider)

    volume_slider.valueChanged.connect(seek_volume)

    volume_timer = QTimer()

    volume_timer.timeout.connect(
        lambda: sync_system_volume(volume_slider)
    )

    volume_timer.start(100)

    # TRACK LABEL

    layout.addWidget(track_label)

    # PROGRESS SLIDER

    slider = QSlider(Qt.Orientation.Horizontal)
    layout.addWidget(slider)

    slider.sliderMoved.connect(
        lambda position: seek_music(media, position)
    )

    # progress_bar = QProgressBar()
    # layout.addWidget(progress_bar)

    media.positionChanged.connect(
        lambda position: update_progress(media, slider, track_label)
    )

    # PLAYBACK CONTROLS

    play_previous_button = QPushButton("<")
    play_previous_button.clicked.connect(lambda: previous_music(media, track_label))


    play_button = QPushButton("▶")

    # Pass the media object to the playback function
    play_button.clicked.connect(lambda: play_music(media, track_label))


    play_next_button = QPushButton(">") 
    play_next_button.clicked.connect(lambda: next_music(media, track_label))

    
    pause_button = QPushButton("⏸")
    pause_button.clicked.connect(lambda: pause_music(media))

    shuffle_button = QPushButton("⇄")
    shuffle_button.clicked.connect(
        lambda checked=False: toggle_shuffle(media, track_label)
        )
    
    layout.addWidget(play_previous_button)
    layout.addWidget(play_button)
    layout.addWidget(play_next_button)

    layout.addWidget(pause_button)
    layout.addWidget(shuffle_button)

    # ADD MUSIC BUTTON
    add_music_button = QPushButton("+ Add music")
    add_music_button.clicked.connect(
        lambda: add_music(playlist_container, media, track_label,playlist_container_label)
    )

    layout.addWidget(add_music_button)

    # CONFIGURE THE WINDOW
    window.setWindowTitle("Penguin Music")
    window.setLayout(layout)

    # Display the window
    window.show()

    # Start the Qt event loop
    app.exec()

# Run main() only when this file is executed directly
if __name__ == "__main__":
    main()
