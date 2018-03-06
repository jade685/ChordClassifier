from tkinter import *
from chord_record import chord_record
from chord_play import chord_play
from chord_denoise import chord_denoise

if sys.version_info[0] < 3:
	# for Python 2
	import Tkinter as Tk
else:
	# for Python 3
	import tkinter as Tk

def chord_classify(event, denoised):
    import numpy as np
    import soundfile as sf
    from freq_table import freq_table

    # read the recorded chord file
    if denoised == False:
        wavefile = 'output.wav'
    elif denoised == True:
        wavefile = 'output_denoised.wav'

    x, fs = sf.read(wavefile)
    l_ori = len(x)
    N_fft = 2**np.ceil(np.log2(l_ori))
    X = np.abs(np.fft.fft(x,int(N_fft)))
    XdB = 20 * np.log10(X)
    l_dB = len(XdB)

    # get the max dB value and its frequency
    maxdb = np.amax(XdB[int(np.floor(100*l_dB/fs)):int(np.floor(l_dB/2))])
    index1 = np.argmax(XdB[int(np.floor(100*l_dB/fs)):int(np.floor(l_dB/2))])
    index1 = index1 + 100*l_dB/fs - 1
    index1 = index1 * fs/l_dB

    # get the other dB value +or- 20 dB of max
    peaks = np.zeros(300)
    indices = np.zeros(300)
    j=0
    for i in range(int(np.floor(100*l_dB/fs)),int(np.floor(l_dB/2))):
        if(XdB[i]>(maxdb-20)):
            if XdB[i]>XdB[i-1] and XdB[i]>=XdB[i+1]:
                peaks[j]=XdB[i]
                tmp = np.where(XdB==XdB[i])
                indices[j]=(int(tmp[0][0]-1))*fs/l_dB
                j=j+1
    peaks2 = []
    for index, value in enumerate(peaks):
        if (not value == 0):
            peaks2.append(peaks[index])
    indices2 = []
    for index, value in enumerate(indices):
        if (not value == 0):
            indices2.append(indices[index])

    # clear the repeat note with in 5 Hz
    pks = np.zeros(300)
    inds = np.zeros(300)
    j=0
    i=0
    while(i<len(peaks2)):
        k = i + 1
        while( k<len(peaks2) and ((indices2[k]-indices2[i])<5) ):
            k = k + 1
        if peaks2[i:k] == []:
            continue
        s = np.max(peaks2[i:k])
        pks[j]=s
        tmp = np.where(XdB==s)
        inds[j]=(int(tmp[0][0]-1))*fs/l_dB
        j=j+1
        i=k
    pks2 = []
    for index, value in enumerate(pks):
        if (not value == 0):
            pks2.append(pks[index])
    inds2 = []
    for index, value in enumerate(inds):
        if (not value == 0):
            inds2.append(inds[index])

    # clear the repeat note more precisely
    max_freq = [index1]
    sort_peak = sorted(pks2)
    pks_indx = np.argsort(pks2)
    pks_indx_back = np.zeros(len(pks_indx))
    j = 0
    for i in range(len(pks_indx)-1,-1,-1):
        pks_indx_back[j] = int(pks_indx[i])
        j = j+1
    pks_indx_back = pks_indx_back.astype(int)
    for i in range(0,len(sort_peak)-1):
        if (np.all(np.abs(inds2[pks_indx_back[i]] - max_freq) > 5)):
            max_freq.append(inds2[pks_indx_back[i]])

    # find notes with patten and get correspond notes
    sorted_max=sorted(max_freq)
    check = np.zeros(len(sorted_max))
    hi = np.zeros(len(sorted_max))
    lo = np.zeros(len(sorted_max))
    for i in range(len(sorted_max)):
        if (np.any(abs(sorted_max - sorted_max[i] * 2) < 5)):
            hi[i] = 1
    for i in range(len(sorted_max)):
        if (np.any(abs(sorted_max - sorted_max[i] / 2) < 5)):
            lo[i] = 1
    for i in range(len(sorted_max)):
        if (hi[i] == 1 and lo[i] == 1):
            check[i] = 1
    a = []
    for index,value in enumerate(check):
        if(not value==0):
            a.append(index)
    b = []
    for i in range(len(a)):
        b.append(sorted_max[a[i]])
    sorted_max = b

    # search within one octave
    for i in range(len(sorted_max)):
        if(sorted_max[i]<320):
            sorted_max[i]=sorted_max[i]*2
        if(sorted_max[i]>630):
            sorted_max[i]=sorted_max[i]/2

    # eliminating repeats
    sorted_max=sorted(sorted_max)
    for i in range(len(sorted_max)-1):
        if(sorted_max[i+1]-sorted_max[i]>0 and sorted_max[i+1]-sorted_max[i]<7):
            sorted_max[i]=0

    # find correspond notes from table
    notes = []
    valuer = np.zeros(len(sorted_max))
    for i in range(len(sorted_max)):
        [note,value]=freq_table(sorted_max[i])
        notes.append(note)
        valuer[i]=int(value)
    valuer = valuer.astype(int)

    # create frequency table within two octave
    frequencys = ['E    ','F    ','F#/Gb','G    ','G#/Ab','A    ','A#/Bb',
                  'B    ','C    ','C#/Db','D    ','D#/Eb','E    ','F    ',
                  'F#/Gb','G    ','G#/Ab','A    ','A#/Bb','B    ','C    ',
                  'C#/Db','D    ']

    # compare notes patten and find final chord
    for i in range(len(notes)):
        if (len(notes) == 3):
            # major pattern: R 3 5
            major = [frequencys[valuer[i] - 1], frequencys[valuer[i] + 4 - 1], frequencys[valuer[i] + 7 - 1]]
            if (sorted(major) == sorted(notes)):
                L3.configure(text=str(frequencys[valuer[i]]))
                print('Your chord is major', frequencys[valuer[i]])
                break
            # minor pattern: R 3b 5
            minor = [frequencys[valuer[i] - 1], frequencys[valuer[i] + 3 - 1], frequencys[valuer[i] + 7 - 1]]
            if (sorted(minor) == sorted(notes)):
                L3.configure(text=str(frequencys[valuer[i]]))
                print('Your chord is minor', frequencys[valuer[i]])
                break
        if (len(notes) == 4):
            # major-7 pattern: R 3 5 7b
            major7 = [frequencys[valuer[i] - 1], frequencys[valuer[i] + 4 - 1], frequencys[valuer[i] + 7 - 1],
                      frequencys[valuer[i] + 10 - 1]]
            if (sorted(major7) == sorted(notes)):
                # s.set('Your chord is major7')
                L3.configure(text=str(frequencys[valuer[i]]))
                print('Your chord is major7', frequencys[valuer[i]])
                break
            # minor-7 pattern: R 3b 5 7b
            minor7 = [frequencys[valuer[i] - 1], frequencys[valuer[i] + 4 - 1], frequencys[valuer[i] + 7 - 1],
                      frequencys[valuer[i] + 10 - 1]]
            if (sorted(minor7) == sorted(notes)):
                L3.configure(text=str(frequencys[valuer[i]]))
                print('Your chord is minor7', frequencys[valuer[i]])
                break
        else:
            L3.configure(text=str(notes))
            print('No patten has found')
            print(notes)


top = Tk.Tk()

# Define Tk variables
s = Tk.StringVar()
s.set('Chord is')


# Define widgets
F1 = Tk.Frame(top, width = 200, height = 30)
L1 = Tk.Label(top, text = 'Chord Classifier')
L4 = Tk.Label(top, text = ' ')
Butt1 = Tk.Button(top, text = 'Record  Chord')
Butt2 = Tk.Button(top, text = 'Play the Chord')
Butt3 = Tk.Button(top, text = 'Classify Chord', command= lambda: chord_classify('<Button-1>',False))
L2 = Tk.Label(top, textvariable = s)
L3 = Tk.Label(top, text = ' ')
Butt5 = Tk.Button(top, text = 'Play denoised Chord')
Butt6 = Tk.Button(top, text = 'classify denoised Chord', command= lambda: chord_classify('<Button-1>',True))
L5 = Tk.Label(top, textvariable = s)
L6 = Tk.Label(top, text = ' ')
Butt4 = Tk.Button(top, text = 'Quit', command = top.quit)
L7 = Tk.Label(top, text = ' ')

# Place buttons
F1.pack()
L1.pack()
L4.pack()
Butt1.pack()
Butt2.pack()
Butt3.pack()
L6.pack()
Butt5.pack()
Butt6.pack()
L7.pack()
L2.pack()
L3.pack()
Butt4.pack()


Butt1.bind('<Button-1>', chord_record)
Butt2.bind('<Button-1>', chord_play)
Butt5.bind('<Button-1>', chord_denoise)

top.mainloop()