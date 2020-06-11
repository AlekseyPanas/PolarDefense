import pygame
import Constants
import Globe

screen = pygame.display.set_mode(Constants.SCREEN_SIZE, pygame.DOUBLEBUF)
clock = pygame.time.Clock()
fps = 0
last_fps_show = 0

# Converts images
Constants.convert()

Globe.start_app()

while Globe.running:
    Globe.GAME.run_game(screen)

    Globe.events = pygame.event.get()

    for event in Globe.events:
        if event.type == pygame.QUIT:
            Globe.running = False

    pygame.display.update()

    # sets fps to a variable. can be set to caption any time for testing.
    last_fps_show += 1
    if last_fps_show == 30:  # every 30th frame:
        fps = clock.get_fps()
        pygame.display.set_caption("Polar Defense" + "   FPS: " + str(fps))
        last_fps_show = 0

    # fps max 60
    clock.tick(60)
