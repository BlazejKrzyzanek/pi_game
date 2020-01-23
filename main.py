import RPi.GPIO as GPIO 
import time
import lcddriver

freqs = [261, 392]
tutorial0 = [1,1,0,1,0]
tutorial1 = [0.66,1,0,1,1,0]
tutorial2 = [0.5,0,1,-1,1,0,1]
neighbours = [0.33,0,0,-1,1,-1,-1,0,0,-1,0]
my1 = [0.33,0,-1,0,1,-1,0,0,-1,0,1]
my2 = [0.25,0,1,0,1,1,-1,1,-1,0,1,0,1,0]
mozart_40 = [0.2,1,0,0,-1,1,0,0,-1,1,0,0,-1,1]
turkish_march = [0.16,1,0,1,0,1,-1,-1,-1,1,0,1,0,1,-1,-1,-1,1,0,1,0,1,0,1,0,1,0,1,0,1]

songs = [tutorial0,tutorial1,tutorial2,neighbours,my1,my2,mozart_40,turkish_march]

sound_start = [523, 554, 587, 622, 659, 698, 740, 784, 830, 880]
sound_repeat = [880, 740, 880]
sound_end = [880, 830, 784, 740, 698, 659, 622, 587, 554, 523]

GPIO.setmode(GPIO.BCM)
# speaker
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50)
GPIO.output(12, True)
# buttons
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# lcd
display = lcddriver.lcd()

song_index = 0
repeating = False
repeat = []
last_repeat = time.time()

def lcd_write(text):
    display.lcd_clear()
    display.lcd_display_string(str(text), 1) # Write line of text to first line of display
    
def show_song():
    global song_index
    if song_index >= len(songs):
        song_index = 0
    elif song_index < 0:
        song_index = len(songs)-1
    text = "Song " + str(song_index + 1)
    lcd_write(text)

def play_sound(sound, delay=0.5):
    pwm.stop()
    time.sleep(delay)
    pwm.start(10)
    for s_index in range(len(sound)):
        pwm.ChangeFrequency(sound[s_index])
        time.sleep(0.1)
    pwm.stop()

def play_song(song):
    global repeating
    global last_repeat
    play_sound(sound_start, 1)
    time.sleep(1)
    
    playing = -1
    last_start = time.time() - 20
    pwm.start(10)
    song_index = 1
    interval = song[0]
    while True:
        if time.time() - last_start > interval*0.85 and playing >= 0:
            pwm.stop()
            playing = 0
            
        if time.time() - last_start > interval:
            if song_index == len(song):
                break
                    
            if song[song_index] >= 0:
                pwm.start(10)
                playing = song[song_index]
                pwm.ChangeFrequency(freqs[song[song_index]])
                
            last_start =  time.time()
            song_index+=1
    pwm.stop()
    
    play_sound(sound_repeat, 1)
    time.sleep(1)
    
    repeat.clear()
    repeating = True
    last_repeat = time.time() + 10

def on_repeat(key):
    global repeating
    global last_repeat
    if repeating == False:
        return
    repeat.append([time.time(),key])
    last_repeat = time.time()

def show_score():
    global repeating
    global sound_end
    global repeat
    play_sound(sound_end)
    repeating = False
    if repeat[0][1] == -1:
        repeat = repeat[1:]
        
    s = repeat[0][0]
    for i in range(len(repeat)):
        repeat[i][0] -= s
    l = repeat[len(repeat)-1][0]
    if l==0:
        l=1
    for i in range(len(repeat)):
        repeat[i][0] /= l
        
    sg = songs[song_index][1:]
    srepeat = []
    for i in range(len(sg)):
        if sg[i] != -1:
            srepeat.append([i,sg[i]])
            srepeat.append([i+0.85,-1])
    for i in range(len(srepeat)):
        srepeat[i][0]/=srepeat[len(srepeat)-1][0]
        
    print(srepeat)
    print(repeat)
    srepeat.append([100,-2])
    repeat.append([100,-2])
    score = 0
    i_s = 0
    i_r = 0
    p_lim = 0
    while not(i_r == len(repeat)-2 and i_s == len(srepeat)-2):
        if srepeat[i_s+1][0] < repeat[i_r+1][0]:
            lim = srepeat[i_s+1][0]            
            dif = lim - p_lim
            p_lim = lim
            if srepeat[i_s][1] == repeat[i_r][1]:
                score += dif
            i_s += 1
        else:
            lim = repeat[i_r+1][0]            
            dif = lim - p_lim
            p_lim = lim
            if srepeat[i_s][1] == repeat[i_r][1]:
                score += dif
            i_r += 1
    
    lcd_write(str(int(score*100))+"%")

def change_input(key, previous_key=-1):
    global repeating
    global song_index
    if key == 0:
        if not repeating:
            song_index -= 1
            show_song()
        pwm.start(10)
        pwm.ChangeFrequency(freqs[0])
        on_repeat(0)
        
    elif key == 1:
        if not repeating:
            song_index += 1
            show_song()
        pwm.start(10)
        pwm.ChangeFrequency(freqs[1])
        on_repeat(1)
    
    elif key == 2:
        pwm.stop()
        if not repeating:
            play_song(songs[song_index])
            
    elif key == -1:
        pwm.stop()
        on_repeat(-1)

def menu_loop():
    global last_repeat
    show_song()
    pwm.stop()
        
    last_key = -1
    last_change = time.time()
    while True:
        if time.time() - last_change < 0.08:
            continue
        
        if repeating and time.time() - last_repeat > 3:
            show_score()
        
        if GPIO.input(14) == GPIO.HIGH and GPIO.input(15) == GPIO.HIGH:
            if last_key == 2:
                continue
            change_input(2, last_key)
            last_key = 2
            last_change = time.time()
        
        if GPIO.input(14) == GPIO.HIGH:
            if last_key == 0:
                continue
            change_input(0, last_key)
            last_key = 0
            last_change = time.time()
            
        elif GPIO.input(15) == GPIO.HIGH:
            if last_key == 1:
                continue
            change_input(1, last_key)
            last_key = 1
            last_change = time.time()
            
        elif last_key != -1:
            change_input(-1, last_key)
            last_key = -1
            last_change = time.time()

menu_loop()
    
GPIO.cleanup()