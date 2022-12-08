import tkinter
from tkinter import *
import time
import matplotlib.pyplot as plt
import numpy as np
import pygame
from tkinter import filedialog
from mutagen.mp3 import MP3
import tkinter.ttk as ttk
import librosa
from serial import Serial

root = Tk()
root.title('Otto Media Player')
root.geometry('500x630')

# Initialize Pygame Mixer
pygame.mixer.init()

# PySerial Configuration
my_serial = Serial("COM8", baudrate=9600, timeout=0.01)

# Global Variables
stopped = False
paused = False
position: int = 0
new_song: int = 1000
beats_sec = []
rms_voice = []
rms_other = []
pace_voice: float = 0.0
pace_other: float = 0.0
song_duration: float = 0.0
converted_duration: ''


def get_beats(song):
    drums = f'output/{song}/drums.wav'

    # Librosa Process - Beat Detection
    y, sr = librosa.load(drums, offset=0)
    _, beats = librosa.beat.beat_track(y=y, sr=sr)

    return librosa.frames_to_time(beats, sr=sr)


def get_song_duration(song):
    song = f'output/{song}/vocals.wav'
    y, sr = librosa.load(song)
    duration = librosa.get_duration(y=y, sr=sr)
    conv_duration = time.strftime('%M:%S', time.gmtime(duration))

    return duration, conv_duration


def get_voice_energy(song, index):

    if index == 0:
        asset = f'output/{song}/vocals.wav'
    else:
        asset = f'output/{song}/other.wav'

    # Librosa Process - Voice Energy
    y, sr = librosa.load(asset)
    rms_array = librosa.feature.rms(y=y)[0]
    asset_length = int(librosa.get_duration(y=y, sr=sr))

    array_length = len(rms_array)
    rms_normalized = rms_array/max(rms_array)

    pace = asset_length/array_length
    # print(pace)

    # Plot Configuration
    # x_range = np.arange(0, voice_length, pace)
    # plt.plot(x_range, rms_normalized)
    # plt.title(song)
    # plt.xlabel('Song Duration [sec]')
    # plt.ylabel('Voice Energy')
    # plt.show()

    return rms_normalized, pace


def load_analyses():
    # Disable player buttons
    playPause_button.config(state='disabled')

    # Reset Satus and Slider
    status_bar.config(text='')
    my_slider.config(value=0)

    song = song_box.get(ACTIVE)

    global beats_sec
    beats_sec = get_beats(song).tolist()

    global rms_voice, pace_voice
    rms_voice, pace_voice = get_voice_energy(song, 0)

    global rms_other, pace_other
    rms_other, pace_other = get_voice_energy(song, 1)

    global song_duration, converted_duration
    song_duration, converted_duration = get_song_duration(song)

    # Disable player buttons
    playPause_button.config(state='normal')


def hit_beat(current_time):
    # print(current_time)
    for beat in beats_sec:
        index = str(beats_sec.index(beat) + 1)  # avoiding to send zero
        if (beat - 0.100) < current_time < (beat + 0.100):
            get_beat.config(image=yes_beat)
            str_beat = 'beat' + index
            #  print(str_beat)
            my_serial.write(str_beat.encode("UTF-8"))
            return

    get_beat.config(image=no_beat)


def meter_vocal(current_time, pace):
    index = round(current_time/pace)
    str_voice = 'voice'

    if rms_voice[index] < 0.1:
        vocal_meter.config(image=vol0)
        get_voice.config(image=no_beat)

        str_no_voice = 'no-voice'
        my_serial.write(str_no_voice.encode("UTF-8"))

    elif 0.2 <= rms_voice[index] <= 0.2:
        vocal_meter.config(image=vol1)
        get_voice.config(image=yes_beat)

        str_voice += '1'
        my_serial.write(str_voice.encode("UTF-8"))

    elif 0.2 <= rms_voice[index] <= 0.4:
        vocal_meter.config(image=vol2)
        vocal_meter.config(image=vol2)

        str_voice += '2'
        my_serial.write(str_voice.encode("UTF-8"))

    elif 0.4 <= rms_voice[index] <= 0.6:
        vocal_meter.config(image=vol3)
        get_voice.config(image=yes_beat)

        str_voice += '3'
        my_serial.write(str_voice.encode("UTF-8"))

    elif 0.6 <= rms_voice[index] <= 0.8:
        vocal_meter.config(image=vol4)
        get_voice.config(image=yes_beat)

        str_voice += '4'
        my_serial.write(str_voice.encode("UTF-8"))

    elif 0.8 <= rms_voice[index] <= 1:
        vocal_meter.config(image=vol5)
        get_voice.config(image=yes_beat)

        str_voice += '5'
        my_serial.write(str_voice.encode("UTF-8"))


def meter_other(current_time, pace):
    index = round(current_time/pace)

    if rms_other[index] < 0.1:
        other_meter.config(image=vol0)
    elif 0.2 <= rms_other[index] <= 0.2:
        other_meter.config(image=vol1)
    elif 0.2 <= rms_other[index] <= 0.4:
        other_meter.config(image=vol2)
    elif 0.4 <= rms_other[index] <= 0.6:
        other_meter.config(image=vol3)
    elif 0.6 <= rms_other[index] <= 0.8:
        other_meter.config(image=vol4)
    elif 0.8 <= rms_other[index] <= 1:
        other_meter.config(image=vol5)


# Slider Functions
def slide(x):
    # slider_label.config(text=f'{int(my_slider.get())} of {int(song_length)}')
    song = song_box.get(ACTIVE)
    song = f'songs/{song}.mp3'
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0, start=int(my_slider.get()))


# Song Functions
def duration_data(current_time, song_length, converted_song_length):

    current_time += 1
    slider_position = int(song_length)

    if int(my_slider.get()) == int(song_length):
        status_bar.config(text=f'{converted_song_length} of {converted_song_length}  ')
    elif paused:
        pass
    elif int(my_slider.get()) == int(current_time):
        # Updating Slider To Position
        my_slider.config(to=slider_position, value=int(current_time))
    else:
        # Updating Slider To Position
        my_slider.config(to=slider_position, value=int(my_slider.get()))

        converted_current_time = time.strftime('%M:%S', time.gmtime(int(my_slider.get())))
        status_bar.config(text=f'{converted_current_time} of {converted_song_length}  ')

        next_time = int(my_slider.get()) + 1
        my_slider.config(value=next_time)


def play_time():
    if stopped:
        return

    current_time = pygame.mixer.music.get_pos() / 1000  # returns a float
    # slider_label.config(text=f'Slider: {int(my_slider.get())} and Song Pos: {int(current_time)}')

    duration_data(current_time, song_duration, converted_duration)
    hit_beat(current_time)
    meter_vocal(current_time, pace_voice)
    meter_other(current_time, pace_other)

    # update time
    status_bar.after(50, play_time)


def play_song(song):
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)
    play_time()


# Menu Functions
def add_song():
    song = filedialog.askopenfilename(initialdir='songs/',
                                      title="Choose A Song",
                                      filetypes=(('mp3 Files', '*.mp3'),))
    song = song.replace('C:/Users/otto.rodrigues/PycharmProjects/tcc/songs/', '')
    song = song.replace('.mp3', '')
    song_box.insert(END, song)


# Control Functions
def play():
    global paused
    global stopped
    global new_song

    stopped = False

    song = song_box.get(ACTIVE)
    song = f'songs/{song}.mp3'
    current_song = song_box.get(song_box.curselection()[0])

    if current_song == new_song:
        pause(paused)
    else:
        new_song = current_song
        play_song(song)


def stop():
    # Reset Satus and Slider
    status_bar.config(text='')
    my_slider.config(value=0)

    # Stop Song
    pygame.mixer.music.stop()
    song_box.select_clear(ACTIVE)

    global stopped
    stopped = True


def pause(is_paused):
    global paused
    paused = is_paused

    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True


# 1 - Header Buttons Frame
header_frame = Frame(root)
header_frame.pack()

# Add Song Button
upload_image = PhotoImage(file='images/add_song.png')
get_song_button = Button(header_frame, text="  Choose Song  ", image=upload_image,
                         compound=tkinter.LEFT, command=add_song, font=('Calibri', 11))

# Process Song Button
process_image = PhotoImage(file='images/process.png')
process_button = Button(header_frame, text="  Process Song  ", image=process_image,
                        compound=tkinter.LEFT, command=load_analyses, font=('Calibri', 11))

# Master Frame Grids
get_song_button.grid(row=0, column=1, padx=40, pady=20)
process_button.grid(row=0, column=2, padx=60, pady=20)

# 2 - Player Frame
player_frame = Frame(root)
player_frame.pack()

# Display Song
song_box = Listbox(player_frame, width=20, height=1, bg='black', fg='green', selectbackground='gray',
                   selectforeground='black', font=('Calibri', 14, 'bold'))

# Play Button
playPause_image = PhotoImage(file='images/playPause_icon.png')
playPause_button = Button(player_frame, image=playPause_image, borderwidth=0, command=play)

# Player Frame Grids
song_box.grid(row=1, column=1, pady=20)
playPause_button.grid(row=2, column=1, padx=10)

# 3 - Create a Music Position Slider
my_slider = ttk.Scale(root, from_=0, to=100, orient=HORIZONTAL, command=slide, length=360, value=0)
my_slider.pack(pady=20)

# Create Status Bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

# 4 - Analyzes Visualization
meter_frame = Frame(root)
meter_frame.pack()

# VU Meter
vol0 = PhotoImage(file='images/vol0.png')
vol1 = PhotoImage(file='images/vol1.png')
vol2 = PhotoImage(file='images/vol2.png')
vol3 = PhotoImage(file='images/vol3.png')
vol4 = PhotoImage(file='images/vol4.png')
vol5 = PhotoImage(file='images/vol5.png')

vocal_meter = Label(meter_frame, image=vol0)
other_meter = Label(meter_frame, image=vol0)

# VU Meter - Label
vocal_meter_label = Label(meter_frame, text='Vocals', font=('', 12))
other_meter_label = Label(meter_frame, text='Others', font=('', 12))

# Analyzes Visualization Grids
vocal_meter_label.grid(row=5, column=1)
vocal_meter.grid(row=5, column=2)
other_meter_label.grid(row=4, column=1)
other_meter.grid(row=4, column=2)

# Beat Detector
yes_beat = PhotoImage(file='images/green_ball.png')
no_beat = PhotoImage(file='images/black_ball.png')
get_beat = Label(meter_frame, image=no_beat)
get_voice = Label(root, image=no_beat)

# VU Meter - Label
beat_label = Label(meter_frame, text='Beat', font=('', 12))
voice_label = Label(root, text='Voice', font=('', 12))

# Analyzes Visualization Grids
beat_label.grid(row=3, column=1)
get_beat.grid(row=3, column=2, sticky=tkinter.W)
voice_label.place(x=325, y=282)
get_voice.place(x=380, y=252)

root.mainloop()
