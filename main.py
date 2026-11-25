
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

import subprocess

# Stores the paths of imported music files
music_library = []
current_index = 0
def next_music(media):
    global current_index 
    if not music_library:
        return
    current_index += 1
    current_index %= len(music_library)
    file_path = music_library[current_index]
    song_url = QUrl.fromLocalFile(file_path)
    media.setSource(song_url)
    media.play()

def previous_music(media):
    global current_index
    if not music_library:
        return
    current_index -= 1
    current_index %= len(music_library)
    file_path = music_library[current_index]
    song_url = QUrl.fromLocalFile(file_path)
    media.setSource(song_url)
    media.play()



# PLAY MUSIC
def play_music(media):

    # Check whether the library is empty
    if not music_library:
        return


    if media.source().isEmpty():
        # Get the first song from the library
        file_path = music_library[current_index]

        # Convert the file path into a Qt URL
        song_url = QUrl.fromLocalFile(file_path)
        # Set the selected song as the player's source
        media.setSource(song_url)

    # Start playback
    media.play()






def update_progress(media, slider):
    song_time_stamp = media.position()
    song_duration = media.duration()
    slider.setRange(0, song_duration)
    slider.setMaximum(song_duration)
    slider.setValue(song_time_stamp)

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
def add_music():

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

    volume_timer.start(10)

    # PROGRESS SLIDER



    slider = QSlider(Qt.Orientation.Horizontal)
    layout.addWidget(slider)

    slider.sliderMoved.connect(
        lambda position: seek_music(media, position)
    )

    # progress_bar = QProgressBar()
    # layout.addWidget(progress_bar)

    media.positionChanged.connect(
        lambda position: update_progress(media, slider)
    )






    # PLAYBACK CONTROLS

    play_previous_button = QPushButton("<")
    play_previous_button.clicked.connect(lambda: previous_music(media))


    play_button = QPushButton("▶")

    # Pass the media object to the playback function
    play_button.clicked.connect(lambda: play_music(media))


    play_next_button = QPushButton(">") 
    play_next_button.clicked.connect(lambda: next_music(media))

    
    pause_button = QPushButton("⏸")
    pause_button.clicked.connect(lambda: pause_music(media))

    shuffle_button = QPushButton("⇄")

    layout.addWidget(play_previous_button)
    layout.addWidget(play_button)
    layout.addWidget(play_next_button)

    layout.addWidget(pause_button)
    layout.addWidget(shuffle_button)


    






    # ADD MUSIC BUTTON
    add_music_button = QPushButton("+ Add music")
    add_music_button.clicked.connect(add_music)

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
