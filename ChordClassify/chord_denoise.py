def chord_denoise(event):
    import pyaudio
    import struct
    import wave
    import math
    import numpy as np

    wavfile = 'output.wav'

    x = wave.open(wavfile)
    num_channels = x.getnchannels()       	# Number of channels
    RATE = x.getframerate()                # Sampling rate (frames/second)
    LEN = x.getnframes()          	    # Signal length
    width = x.getsampwidth()       		# Number of bytes per sample

    print("The file has %d channel(s)."            % num_channels)
    print("The frame rate is %d frames/second."    % RATE)
    print("The file has %d frames."                % LEN)
    print("There are %d bytes per sample."         % width)

    output_wavfile = wavfile[:-4] + '_denoised.wav'
    output_wf = wave.open(output_wavfile, 'w')      # wave file
    output_wf.setframerate(RATE)
    output_wf.setsampwidth(width)
    output_wf.setnchannels(num_channels)

    p = pyaudio.PyAudio()
    stream = p.open(format      = pyaudio.paInt16,
                    channels    = num_channels,
                    rate        = RATE,
                    input       = False,
                    output      = True )

    R = 64
    Nfft = 128
    T = 10000
    MAXVALUE = 2**15-1

    window = np.cos(np.pi * (np.arange(0,R) + 0.5)/R - np.pi/2)
    num_blocks = int(math.floor(LEN/R))
    input_array_pre = np.zeros(R)

    print('* Playing...')

    for n in range(0, num_blocks):

        input_string = x.readframes(R)
        input_block = struct.unpack('h' * R, input_string)
        input_array = np.array(list(input_block)).astype(float)

        x_pre = np.fft.fft(input_array_pre * window, Nfft)
        x_add = np.fft.fft(np.hstack((input_array_pre[R//2:R], input_array[0:R//2])) * window, Nfft)
        x_now = np.fft.fft(input_array * window, Nfft)

        x_pre[np.abs(x_pre)<T] = 0
        x_add[np.abs(x_add)<T] = 0
        x_now[np.abs(x_now)<T] = 0

        input_array_pre = input_array

        y = np.fft.ifft(x_add)[:R]
        y[0:R//2] += (np.fft.ifft(x_pre)[:R] * window)[R//2:R]
        y[R//2:R] += (np.fft.ifft(x_now)[:R] * window)[0:R//2]

        y = np.clip(y, -MAXVALUE, MAXVALUE)

        y = np.real(y)
        output_string = struct.pack('h' * R, *y.astype(int))
        stream.write(output_string)
        output_wf.writeframes(output_string)

    print('* Finished')

    stream.stop_stream()
    stream.close()
    p.terminate()

    x.close()
    output_wf.close()