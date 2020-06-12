import Game
import pygame
import Menu

MENU = None
events = None
running = True


def start_app():
    global MENU, events
    MENU = Menu.Menu()

    events = pygame.event.get()
