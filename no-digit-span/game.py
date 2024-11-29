import pygame
import random
import string
import csv

# pygame setup
pygame.init()
WIDTH = 1280
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

# colors
WHITE = (255,255,255)
BLACK = (0,0,0)

font = pygame.font.Font(None, 74)

pygame.display.set_caption('Digit Span Test')

def generate_sequence(length):
    return ''.join(random.choices(string.digits, k=length))

def update_sequence(sequence):
    new_digit = random.choice(string.digits)
    return sequence + new_digit

def flip_sequence(sequence):
    return sequence[::-1]


def display_sequence(sequence):
    screen.fill(BLACK)
    text_surface = font.render(sequence, True, WHITE)
    # text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()

def display_end_screen(sequence, name):
    csv_row = [name, len(sequence)]
    with open("data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(csv_row)
    screen.fill(BLACK)
    feedback_text = font.render(f"Wrong answer, score: {len(sequence)}", True, WHITE)
    screen.blit(feedback_text, (WIDTH // 2 - feedback_text.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()


def display_start_screen():
    """Display the start screen where the player enters their name."""
    name = ""
    while True:
        screen.fill(BLACK)
        prompt_text = font.render("Enter your name:", True, WHITE)
        name_text = font.render(name, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()  # Return the name once Enter is pressed
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode         

    


# Game loop variables
running = True
sequence_length = 3  # Start with a 3-letter sequence
sequence = generate_sequence(sequence_length)
showing_sequence = True
response = ""

player_name = display_start_screen()

if not player_name:
    exit()  # Exit if no name is provided

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not showing_sequence:
                if event.key == pygame.K_RETURN:  # Enter key to submit response
                    if response == flip_sequence(sequence):
                        sequence_length += 1
                    else:
                        display_end_screen(sequence, player_name)
                        pygame.time.delay(3000)
                        running = False
                    response = ""
                    if running:  # Update de sequence alleen als het spel doorgaat
                        sequence = update_sequence(sequence)
                        showing_sequence = True
                elif event.key == pygame.K_BACKSPACE:  # Backspace to edit response
                    response = response[:-1]
                else:
                    response += event.unicode.upper()

    if showing_sequence:
        display_sequence(sequence)
        pygame.time.delay(1000 + 200 * sequence_length)  # Show sequence longer as it gets longer
        showing_sequence = False
        screen.fill(BLACK)
        pygame.display.flip()
    else:
        # Display response and feedback
        screen.fill(BLACK)
        response_text = font.render(f"Your Response: {response}", True, WHITE)
        screen.blit(response_text, (WIDTH // 2 - response_text.get_width() // 2, HEIGHT // 2 - 50))
        pygame.display.flip()

        

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
