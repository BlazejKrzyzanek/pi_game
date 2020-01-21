import RPi.GPIO as GPIO 
import time

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

GPIO.setmode(GPIO.BCM)
# speaker
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 100)
GPIO.output(12, True)
# buttons
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

song_index = 0

def lcd_write(text):
    print(text)

def play_song(song):
    can_play = False
    pwm.stop()
    playing = -1
    last_start = time.time() - 20
    pwm.start(10) # 10% duty cycle sounds 'ok'
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
    can_play = True

def change_input(key, previous_key=-1):
    global song_index
    if key == 0:
        song_index += 1
        if song_index >= len(songs):
            song_index = 0
        text = "Song " + str(song_index + 1)
        lcd_write(text)
        pwm.start(10)
        pwm.ChangeFrequency(freqs[0])
        
    elif key == 1:
        pwm.start(10)
        pwm.ChangeFrequency(freqs[1])
    
    elif key == 2:
        pwm.stop()
        play_song(songs[song_index])
            
    elif key == -1:
        pwm.stop()

def menu_loop():
    pwm.stop()
    can_play = True
        
    last_key = -1
    last_change = time.time()
    while True:
        if time.time() - last_change < 0.08:
            continue
        
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