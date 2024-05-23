import pygame
import json
import sys

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((800, 600))

try:
	with open("map.txt", "r") as file:
		Map=json.loads(file.read())
except Exception as e:
	Map=[[0, 0, 100, 100]]

sas=False
scroll=False
conMenu=False
black=(0, 0, 0)
white=(255, 255, 255)
pos_x, pos_y=0, 0
x_cam, y_cam=0, 0
conPos=[0, 0]
s=''

def colision(pos, sizeX, sizeY, m):
	x, y=m
	return x>pos[0] and x<pos[0]+sizeX and y>pos[1] and y<pos[1]+sizeY

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	pygame.display.set_caption(f'WorldBuilder{s}')
	key=pygame.key.get_pressed()
	mouseC=pygame.mouse.get_pressed()

	if key[pygame.K_s]:
		s=''
		with open("map.txt", "w") as file:
			file.write(str(Map))
	if key[pygame.K_l]:
		s=''
		try:
			with open("map.txt", "r") as file:
				Map=json.loads(file.read())
		except Exception as e:
			print('Error')

	if sas and not mouseC[0]:
		x2, y2=pygame.mouse.get_pos()
		x2+=x_cam
		y2+=y_cam
		if x<x2 and y<y2:
			Map.append([x, y, x2-x, y2-y, 0])
			s='*'
		elif x<x2 and y>y2:
			Map.append([x, y2, x2-x, y-y2, 0])
			s='*'
		elif x>x2 and y>y2:
			Map.append([x2, y2, x-x2, y-y2, 0])
			s='*'
		elif x>x2 and y<y2:
			Map.append([x2, y, x-x2, y2-y, 0])
			s='*'
		sas=False

	if mouseC[0] and not colision(conPos, 60, 45, pygame.mouse.get_pos()) and not sas:
		x, y=pygame.mouse.get_pos()
		x+=x_cam
		y+=y_cam
		conMenu=False
		sas=True

	if mouseC[1] and scroll:
		if pos_x!=pygame.mouse.get_pos()[0] or pos_y!=pygame.mouse.get_pos()[1]:
			x_cam+=pos_x-pygame.mouse.get_pos()[0]
			y_cam+=pos_y-pygame.mouse.get_pos()[1]
		pos_x, pos_y=0, 0
		scroll=False

	if not mouseC[1]:
		pos_x, pos_y=0, 0
		scroll=False

	if mouseC[1] and not scroll:
		pos_x, pos_y=pygame.mouse.get_pos()
		conMenu=False
		scroll=True

	if mouseC[2] and not colision(conPos, 60, 45, pygame.mouse.get_pos()):
		conMenu=False
	if mouseC[0] and colision(conPos, 60, 45, pygame.mouse.get_pos()):
		if not colision(conPos, 60, 45/2, pygame.mouse.get_pos()):
			for obj in Map:
				if colision((obj[0]-x_cam, obj[1]-y_cam), obj[2], obj[3], conPos):
					Map.remove(obj)
					s='*'
					conMenu=False
					break
		else:
			for i in range(len(Map)):
				if not conMenu:
					break
				if Map[i]==oo:
					if Map[i][4]:
						Map[i][4]=0
					else:
						Map[i][4]=1
					s='*'
					conMenu=False
					break

	screen.fill(white)
	for obj in Map:
		if colision((obj[0]-x_cam, obj[1]-y_cam), obj[2], obj[3], pygame.mouse.get_pos()):
			if mouseC[2] and not sas and not conMenu:
				conMenu=True
				oo=obj
				conPos=pygame.mouse.get_pos()
			pygame.draw.rect(screen, (20, 20 ,20), (obj[0]-x_cam, obj[1]-y_cam, obj[2], obj[3]))
		else:
			pygame.draw.rect(screen, black, (obj[0]-x_cam, obj[1]-y_cam, obj[2], obj[3]))

	if conMenu:
		pygame.draw.rect(screen, (50, 50, 50), (conPos[0], conPos[1], 60, 45))

		color=(230, 230, 230)
		if not oo[4]:
			color=(120, 120, 120)

		font=pygame.font.Font(None, 25)
		text=font.render('mirror', True, color)
		screen.blit(text, (conPos[0]+3, conPos[1]))
		text=font.render('delete', True, (120, 120, 120))
		screen.blit(text, (conPos[0]+3, conPos[1]+23))

	pygame.display.flip()
	clock.tick(60)
