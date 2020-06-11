import Game
import pygame

GAME = None
events = None
running = True


def start_app():
    global GAME, events
    GAME = Game.Game()

    events = pygame.event.get()
