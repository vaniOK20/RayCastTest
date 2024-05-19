import pygame
import json

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
black=(0, 0, 0)
white=(255, 255, 255)
pos_x, pos_y=0, 0
x_cam, y_cam=0, 0
s=''

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()

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
			Map.append([x, y, x2-x, y2-y])
			s='*'
		elif x<x2 and y>y2:
			Map.append([x, y2, x2-x, y-y2])
			s='*'
		elif x>x2 and y>y2:
			Map.append([x2, y2, x-x2, y-y2])
			s='*'
		elif x>x2 and y<y2:
			Map.append([x2, y, x-x2, y2-y])
			s='*'
		sas=False

	if mouseC[0] and not sas:
		x, y=pygame.mouse.get_pos()
		x+=x_cam
		y+=y_cam
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
		scroll=True

	screen.fill(white)
	for obj in Map:
		x1, y1=pygame.mouse.get_pos()
		x1+=x_cam
		y1+=y_cam
		if x1>obj[0] and x1<obj[0]+obj[2] and y1>obj[1] and y1<obj[1]+obj[3]:
			if mouseC[2]:
				Map.remove(obj)
				s='*'
			pygame.draw.rect(screen, (20, 20 ,20), (obj[0]-x_cam, obj[1]-y_cam, obj[2], obj[3]))
		else:
			pygame.draw.rect(screen, black, (obj[0]-x_cam, obj[1]-y_cam, obj[2], obj[3]))

	pygame.display.flip()
	clock.tick(60)