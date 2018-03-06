
def freq_table(peak):

    if (peak < 339):
        note = 'E    '
        value = 1
    elif(peak < 359):
        note = 'F    '
        value = 2
    elif(peak < 381):
        note = 'F#/Gb'
        value = 3
    elif(peak < 397):
        note = 'G    '
        value = 4
    elif(peak < 427.5):
        note = 'G#/Ab'
        value = 5
    elif(peak < 453):
        note = 'A    '
        value = 6
    elif(peak < 479.75):
        note = 'A#/Bb'
        value = 7
    elif(peak < 508):
        note = 'B    '
        value = 8
    elif(peak < 538):
        note = 'C    '
        value = 9
    elif(peak < 569.75):
        note = 'C#/Db'
        value = 10
    elif(peak < 605):
        note = 'D    '
        value = 11
    elif(peak < 640.5):
        note = 'D#/Eb'
        value = 12
    else:
        note = 'ERROR'
        value = 1

    return (note,value)