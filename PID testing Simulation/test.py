import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Crosshair Example")

# Define colors
black = (0, 0, 0)

# Run the game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Clear the screen
    screen.fill(black)

    # Draw the crosshair
    crosshair_size = 10
    pygame.draw.line(screen, (255, 255, 255), (width // 2, height // 2 - crosshair_size), (width // 2, height // 2 + crosshair_size), 2)
    pygame.draw.line(screen, (255, 255, 255), (width // 2 - crosshair_size, height // 2), (width // 2 + crosshair_size, height // 2), 2)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
