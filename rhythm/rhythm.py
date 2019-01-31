import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# beat_tracker
def beat_tracker(filename):
    # y : audio time-series
    # sr : sampling rate of y

    # load audio file
    y, sr = librosa.load(filename)

    # pre-calculate onset envelope
    onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)

    # calculate beats
    beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)[1]

    # plot the beat events(first 15 seconds) against the onset strength envelope
    hop_length = 512
    plt.figure(figsize=(8, 4))
    times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr, hop_length=hop_length)
    plt.plot(times, librosa.util.normalize(onset_env), label='Onset strength')
    plt.vlines(times[beats], 0, 1, alpha=0.5, color='r', linestyle='--', label='Beats')
    plt.legend(frameon=True, framealpha=0.75)
    plt.xlim(0, 15)
    plt.gca().xaxis.set_major_formatter(librosa.display.TimeFormatter())
    plt.tight_layout()
    plt.show()

    #return beats array
    return beats

# tempo tracker
def tempo_tracker(filename):
    # y : audio time-series
    # sr : sampling rate of y

    # load audio file
    y, sr = librosa.load(filename)

    # pre-calculate onset envelope
    onset_env = librosa.onset.onset_strength(y, sr=sr)

    # calculate dynamic tempo
    dtempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)

    # plot dynamic tempo estimates over a tempogram
    plt.figure()
    tg = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr, hop_length=hop_length)
    librosa.display.specshow(tg, x_axis='time', y_axis='tempo')
    plt.plot(librosa.frames_to_time(np.arange(len(dtempo))), dtempo, color='w', linewidth=1.5, label='Tempo estimate')
    plt.title('Dynamic tempo estimation')
    plt.legend(frameon=True, framealpha=0.75)
    plt.show()

    # return tempo array
    return dtempo

if __name__ == '__main__':
    beat_tracker('temp3.wav')
    tempo_tracker('temp3.wav')