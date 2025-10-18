# main.py
import pygame
import sys
from game.game_engine import GameEngine

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong - Pygame Version")

# Colors
BLACK = (0, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Game engine
engine = GameEngine(WIDTH, HEIGHT, winning_score=5)

def main():
    running = True
    while running:
        SCREEN.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # let engine handle relevant events (like replay choices)
            engine.handle_event(event)

        # If engine signalled an 'exit' via winner (ESC during game over), quit
        if engine.winner == 'exit':
            running = False
            break

        # Only process input/movement when not game over
        if not engine.game_over:
            engine.handle_input()
        # update game state & render
        engine.update()
        engine.render(SCREEN)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    # ensure full exit from program
    try:
        sys.exit(0)
    except SystemExit:
        pass

if __name__ == "__main__":
    main()