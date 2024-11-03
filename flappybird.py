# Import required libraries
import pygame
from pygame.locals import*
import random

# Initialize the Pygame and its mixer for sound
pygame.init()
pygame.mixer.init()

# Set up the game clock and frame rate
clock = pygame.time.Clock()
fps = 60 # Frames per second

# Define the screen dimensions
screen_width = 864
screen_height = 768

# Create the game window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird Remastered | Julien Okumu') # Set window title

# Set up fonts
font = pygame.font.SysFont('Bahaus 93', 60)

# Define colors
white = (255, 255, 255)

# Initialize the game variables
ground_scroll = 0 # For scrolling ground effect
scroll_speed = 4 # Speed of scrolling
flying = False # Initial state of bird flying
game_over = False # Initial state of game
pipe_gap = 150 # Gap between the top and bottom pipes
pipe_frequency = 1500 # How often new pipes spawn(milliseconds)
last_pipe = pygame.time.get_ticks() - pipe_frequency # Time since last pipe spawned
score = 0 # Player's initial score
pass_pipe = False # Initial state of bird passing pipe
game_over_sound_played = False

# Load images
bg = pygame.image.load('bg.png') # Background image
ground_img = pygame.image.load('ground.png') # Ground image
button_img = pygame.image.load('restart.png') # Restart button

# Load audio files
jump_sound = pygame.mixer.Sound('wing-flap-1-6434.ogg') # Sound when bird jumps
game_over_sound = pygame.mixer.Sound('game-over-arcade-6435.ogg') # Sound when game is over
pygame.mixer.music.load('game-music-loop-7-145285.ogg') # Background music

# Function to draw text on screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

# Function to reset the game
def reset_game():
	global game_over_sound_played
	pipe_group.empty() # Remove all pipes
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	flappy.vel = 0 # Reset bird velocity
	game_over_sound_played = False
	game_over_sound.stop() # Stop game over sound
	pygame.mixer.music.play(-1) # Restart background music

	return score

# Bird class
class Bird(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = [] # List to hold bird images for animation
		self.index = 0 # Current image index
		self.counter = 0 # Counter for animation timing
		for num in range(1, 4):
			img = pygame.image.load(f'bird{num}.png')
			self.images.append(img)
		self.image = self.images[self.index] # Current image
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0 # Vertical velocity
		self.clicked = False # Initial mouse click state

	def update(self):
		if flying:
			# Apply gravity
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if not game_over:
			# Jump when mouse is clicked
			if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
				self.clicked = True
				self.vel = -10
				jump_sound.play() # Play jump sound
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			# Handle animation
			self.counter += 1
			flap_cooldown = 5

			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
			self.image = self.images[self.index]

			# Rotate the bird
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			# Point the bird at the ground
			self.image = pygame.transform.rotate(self.images[self.index], -90)


# Pipe class
class Pipe(pygame.sprite.Sprite):
	def __init__(self, x, y, position):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('pipe.png')
		self.rect = self.image.get_rect()
		# Position 1 is from the top, -1 is from the bottom
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		if position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]

	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill() # Remove pipe when its off the screen


# Button class
class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False
		pos = pygame.mouse.get_pos()

		# Check if mouse is over the button
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		# Draw the button
		screen.blit(self.image, (self.rect.x, self.rect.y))
		
		return action

# Create sprite groups
(bird_group, pipe_group) = (pygame.sprite.Group(), pygame.sprite.Group())

# Create the bird
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create restart button
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

# Start playing background music
pygame.mixer.music.play(-1) # -1 means loop indefinitely

# Main game loop
run = True
while run:
	clock.tick(fps)

	# Draw background
	screen.blit(bg, (0, 0))

	# Draw and update the bird
	bird_group.draw(screen)
	bird_group.update()

	# Draw pipes
	pipe_group.draw(screen)

	# Draw ground
	screen.blit(ground_img, (ground_scroll, 768))

	# Check for game to start
	if not flying and not game_over:
		# Start game on first click
		if pygame.mouse.get_pressed()[0] == 1:
			flying = True

	# Check score
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and not pass_pipe:
			pass_pipe = True
		if pass_pipe:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				pass_pipe = False

	# Display score
	draw_text(str(score), font, white, int(screen_width / 2), 20)

	# Check for collisions
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		if not game_over: # Only trigger game over once
			game_over = True
			pygame.mixer.music.stop()
			if not game_over_sound_played:
				game_over_sound.play()
				game_over_sound_played = True

	# Check if bird has hit the ground
	if flappy.rect.bottom >= 768:
		if not game_over: # Only trigger game over once
			game_over = True
			pygame.mixer.music.stop()
			if not game_over_sound_played:
				game_over_sound.play()
				game_over_sound_played = True
			flying = False

	if not game_over and flying: # Only generate pipes if game is not over
		# Generate new pipes
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1) # Bottom pipe
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe, top_pipe)
			last_pipe = time_now

		# Update pipes
		pipe_group.update()

	if game_over:
		if not game_over_sound_played: # Check if music is still playing
			pygame.mixer.music.stop()
			game_over_sound.play() # Play game over sound
			game_over_sound_played = True
		
		draw_text('Game Over!', font, white, int(screen_width / 2) - 120, int(screen_height / 2) - 150)
		if button.draw():
			game_over = False
			score = reset_game()
			flying = True

	# Update display
	pygame.display.update()

	# Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
			flying = True

	# Scroll the ground
	if not game_over:
		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0

pygame.quit()


