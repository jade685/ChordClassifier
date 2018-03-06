def chord_play(event):

    import wave
    import pyaudio
    import time

    wf = wave.open('output.wav', 'rb')
    CHANNELS = wf.getnchannels()
    RATE = wf.getframerate() 
    WIDTH = wf.getsampwidth() 

    def my_callback(input_string, block_size, time_info, status):
        output_string = wf.readframes(block_size)
        return (output_string, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(WIDTH),
                    channels = CHANNELS,
                    rate = RATE,
                    input = False,
                    output = True,
                    stream_callback = my_callback)

    print('Playing...')
    stream.start_stream()

    while stream.is_active():
        time.sleep(0.1)

    stream.stop_stream()
    print('End play')
    stream.close()

    p.terminate()

