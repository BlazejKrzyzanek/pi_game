#! /usr/bin/env python

import pygame, time
pygame.init()
beep = pygame.mixer.Sound("a.wav")
beep.play()
time.sleep(10)
pygame.quit()