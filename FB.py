import cfg
import sys
import random
import pygame
from modules.obj.Pipe import *
from modules.obj.Bird import *
from modules.interfaces.endGame import *
from modules.interfaces.startGame import *


def initGame():
	pygame.init()
	pygame.mixer.init()
	screen = pygame.display.set_mode((cfg.SCREENWIDTH, cfg.SCREENHEIGHT))
	pygame.display.set_caption('Flappy Bird')
	return screen



def showScore(screen, score, number_images):
	digits = list(str(int(score)))
	width = 0
	for d in digits:
		width += number_images.get(d).get_width()
	offset = (cfg.SCREENWIDTH - width) / 2
	for d in digits:
		screen.blit(number_images.get(d), (offset, cfg.SCREENHEIGHT*0.1))
		offset += number_images.get(d).get_width()



def main():
	screen = initGame()
	sounds = dict()
	for key, value in cfg.AUDIO_PATHS.items():
		sounds[key] = pygame.mixer.Sound(value)
	
	number_images = dict()
	for key, value in cfg.NUMBER_IMAGE_PATHS.items():
		number_images[key] = pygame.image.load(value).convert_alpha()
	
	pipe_images = dict()
	pipe_images['bottom'] = pygame.image.load(random.choice(list(cfg.PIPE_IMAGE_PATHS.values()))).convert_alpha()
	pipe_images['top'] = pygame.transform.rotate(pipe_images['bottom'], 180)
	
	bird_images = dict()
	for key, value in cfg.BIRD_IMAGE_PATHS[random.choice(list(cfg.BIRD_IMAGE_PATHS.keys()))].items():
		bird_images[key] = pygame.image.load(value).convert_alpha()
	
	backgroud_image = pygame.image.load(random.choice(list(cfg.BACKGROUND_IMAGE_PATHS.values()))).convert_alpha()

	other_images = dict()
	for key, value in cfg.OTHER_IMAGE_PATHS.items():
		other_images[key] = pygame.image.load(value).convert_alpha()
	
	game_start_info = startGame(screen, sounds, bird_images, other_images, backgroud_image, cfg)

	score = 0
	bird_pos, base_pos, bird_idx = list(game_start_info.values())
	base_diff_bg = other_images['base'].get_width() - backgroud_image.get_width()
	clock = pygame.time.Clock()
	
	pipe_obj = pygame.sprite.Group()
	for i in range(2):
		pipe_pos = Pipe.randomPipe(cfg, pipe_images.get('top'))
		pipe_obj.add(Pipe(image=pipe_images.get('top'), position=(cfg.SCREENWIDTH+200+i*cfg.SCREENWIDTH/2, pipe_pos.get('top')[-1])))
		pipe_obj.add(Pipe(image=pipe_images.get('bottom'), position=(cfg.SCREENWIDTH+200+i*cfg.SCREENWIDTH/2, pipe_pos.get('bottom')[-1])))
	
	bird = Bird(images=bird_images, idx=bird_idx, position=bird_pos)
	
	is_add_pipe = True
	is_game_running = True
	while is_game_running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
					bird.setFlapped()
					sounds['wing'].play()
		
		for pipe in pipe_obj:
			if pygame.sprite.collide_mask(bird, pipe):
				sounds['hit'].play()
				is_game_running = False
		
		boundary_values = [0, base_pos[-1]]
		is_dead = bird.update(boundary_values, float(clock.tick(cfg.FPS))/1000.)
		if is_dead:
			sounds['hit'].play()
			is_game_running = False

		base_pos[0] = -((-base_pos[0] + 4) % base_diff_bg)
	
		flag = False
		for pipe in pipe_obj:
			pipe.rect.left -= 4
			if pipe.rect.centerx < bird.rect.centerx and not pipe.used_for_score:
				pipe.used_for_score = True
				score += 0.5
				if '.5' in str(score):
					sounds['point'].play()
			if pipe.rect.left < 5 and pipe.rect.left > 0 and is_add_pipe:
				pipe_pos = Pipe.randomPipe(cfg, pipe_images.get('top'))
				pipe_obj.add(Pipe(image=pipe_images.get('top'), position=pipe_pos.get('top')))
				pipe_obj.add(Pipe(image=pipe_images.get('bottom'), position=pipe_pos.get('bottom')))
				is_add_pipe = False
			elif pipe.rect.right < 0:
				pipe_obj.remove(pipe)
				flag = True
		if flag: is_add_pipe = True

		screen.blit(backgroud_image, (0, 0))
		pipe_obj.draw(screen)
		screen.blit(other_images['base'], base_pos)
		showScore(screen, score, number_images)
		bird.draw(screen)
		pygame.display.update()
		clock.tick(cfg.FPS)
	endGame(screen, sounds, showScore, score, number_images, b'''


if __name__ == '__main__':
	while True:
		main()
