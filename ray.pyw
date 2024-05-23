import pygame
import json
import math
import socket
import threading
import sys

pygame.init()
clock=pygame.time.Clock()
screen=pygame.display.set_mode((800, 600))

# Завантаження карти
try:
	with open("map.txt", "r") as file:
		Map=json.loads(file.read())
except Exception as e:
	Map=[]

# Змінні
x, y=50, 50
x_pl2, y_pl2=-50, -50
angle=0
quality=40
max_depth=500
x_q=272
x_s=125
smoothL=0.05
server=False
client=False
menu=False
clicked=False, False
smooth=False
click=False

stop_event=threading.Event()

def colision(x, y): # Обробка колізії
	for obj in Map:
		if x>obj[0] and x<obj[0]+obj[2] and y>obj[1] and y<obj[1]+obj[3] or x>x_pl2 and x<x_pl2+20 and y>y_pl2 and y<y_pl2+20:
			if obj[4]: # Якщо це зеркало то сповістити
				return True, True
			else:
				return True, False
	return False, False

def move(speed, angle): # Рух вперед на speed кроків на angle градусів
	angle_rad=angle*(math.pi/180.0)
	end_x=x+speed*math.cos(angle_rad)
	end_y=y+speed*math.sin(angle_rad)
	return end_x, end_y

def cast_ray(x, y, angle, max_depth, step_size=1):# Рух променів та їх колізія
	angle_rad=math.radians(angle)
	for depth in range(0, max_depth, step_size):
		target_x=x+depth*math.cos(angle_rad)
		target_y=y+depth*math.sin(angle_rad)
		colD=colision(target_x, target_y)
		if colD[1]:# Обробка дзеркал
			angle_rad=math.radians(math.pi-angle)
			target_x=x+depth*math.cos(angle_rad)
			target_y=y+depth*math.sin(angle_rad)
			colD=colision(target_x, target_y)
		if colD[0]:# Доторкнувся
			color=(0, 0, 0)
			i=0
			if smooth and not depth>200:# Згладжування
				color=(255, 0, 0)
				while not i>50 and colision(target_x, target_y)[0]:
					angle_rad=math.radians(angle)
					target_x=x+(depth-i)*math.cos(angle_rad)
					target_y=y+(depth-i)*math.sin(angle_rad)
					i+=smoothL
			if key[pygame.K_m]:# Показати промені
				pygame.draw.line(screen, color, (x, y), (target_x, target_y), 3)
			return depth-i, target_x, target_y
	return max_depth, target_x, target_y

def draw():# Відмальовування
	fov=70
	half_fov=fov/2
	color=(0, 255, 0)
	screen_width=screen.get_width()
	wall_width=screen_width/quality

	for ray in range(quality):
		ray_angle=angle - half_fov+(ray*fov/quality)
		depth, end_x, end_y=cast_ray(x, y, ray_angle, max_depth, step_size=5)

		wall_height=600/(depth+0.0001)*50
		wall_x=ray*wall_width
		if depth<max_depth:
			intensity=255/(1+depth/100)
			wall_color=(color[0]*intensity/255, color[1]*intensity/255, color[2]*intensity/255)
			pygame.draw.rect(screen, wall_color, (wall_x, 300 - wall_height//2, wall_width+1, wall_height))

def server_thread():# Обробка серверу
	global x_pl2, y_pl2
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind(("127.0.0.1", 443))
		s.listen()
		conn, addr=s.accept()
		with conn:
			while True:
				data=conn.recv(1024)
				if not data:
					break
				player_data=json.loads(data.decode())
				x_pl2, y_pl2=player_data # Приймання даних
				conn.sendall(json.dumps([x, y]).encode())

def client_thread():# Обробка клієнту
	global x_pl2, y_pl2
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(("127.0.0.1", 443))
		while True:
			text=json.dumps([x, y])
			s.sendall(text.encode())
			data=s.recv(1024)
			if data:
				server_data=json.loads(data.decode())
				x_pl2, y_pl2=server_data # Приймання даних

server_thread_instance=None
client_thread_instance=None

while True:# Основний цикл
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			stop_event.set()
			if server_thread_instance is not None:
				server_thread_instance.join()
			if client_thread_instance is not None:
				client_thread_instance.join()
			pygame.quit()
			sys.exit()
		elif event.type==pygame.KEYDOWN and event.unicode=='\x1b' and not menu:
			menu=True
		elif event.type==pygame.KEYDOWN and event.unicode=='\x1b' and menu:
			menu=False

	# Керування
	key=pygame.key.get_pressed()

	if key[pygame.K_1] and not server: # Підсключення серверу
		server=True
		server_thread_instance=threading.Thread(target=server_thread)
		server_thread_instance.start()
	if key[pygame.K_2] and not client: # Підсключення кліїнту
		client=True
		client_thread_instance=threading.Thread(target=client_thread)
		client_thread_instance.start()

	if key[pygame.K_l]: # Завантаження карти
		try:
			with open("map.txt", "r") as file:
				Map=json.loads(file.read())
		except Exception as e:
			print('Error')

	if key[pygame.K_RIGHT]: # Збільшення дальності промальовування
		max_depth+=10
	if key[pygame.K_LEFT] and not max_depth<=10: # Зменшення дальності промальовування
		max_depth-=10

	# Керування гравцем
	if key[pygame.K_w]:
		new_x, new_y=move(3, angle)
		if not colision(new_x, new_y)[0]:# Обробка колізії
			x, y=new_x, new_y
	if key[pygame.K_s]:
		new_x, new_y=move(-3, angle)
		if not colision(new_x, new_y)[0]:
			x, y=new_x, new_y
	if key[pygame.K_a]:# Повертання гравця
		angle -= 3
	if key[pygame.K_d]:
		angle += 3

	# Відмальовування
	if not menu:
		screen.fill((255, 255, 255))
		draw()
		if key[pygame.K_m]:# Показати карту
			for obj in Map:
				pygame.draw.rect(screen, (0, 0, 0), (obj[0], obj[1], obj[2], obj[3]), 3)
	else:
		pygame.draw.rect(screen, (50, 50, 50), (30, 30, 740, 540))
		font=pygame.font.Font(None, 25)
		text=font.render('Settings', True, (0, 0, 0))
		screen.blit(text, (740/2, 60))
		# Повзунок якості
		pygame.draw.rect(screen, (70, 70, 70), (60, 80, 680, 60))
		text=font.render('Quality', True, (0, 0, 0))
		screen.blit(text, (60, 80))
		text=font.render(str(((x_q-60)//7)+10), True, (0, 0, 0))
		screen.blit(text, (60, 80+43))
		pygame.draw.rect(screen, (150, 150, 150), (70, (80/2)+65, 660, 10))
		pygame.draw.rect(screen, (40, 40, 40), (x_q, ((80/2)+65)-5, 10, 20))
		# Обробка натискань
		pos_x, pos_y=pygame.mouse.get_pos()
		if pos_x>x_q and pos_x<x_q+70 and pos_y>((80/2)+65)-5 and pos_y<((80/2)+65)-5+20 and pygame.mouse.get_pressed()[0] and not clicked[0] and not clicked[1]:
			clicked=True, False
		if clicked[0] and pygame.mouse.get_pos()[0]>65 and pygame.mouse.get_pos()[0]<70+660:
			x_q=pygame.mouse.get_pos()[0]-5
			quality=((x_q-60)//7)+10
		if clicked[0] and not pygame.mouse.get_pressed()[0]:
			clicked=False, False
		# Згладжування
		if smooth:
			color=(220, 220, 220)
		else:
			color=(220, 100, 100)
		pygame.draw.rect(screen, (70, 70, 70), (60, 160, 680, 60))
		pygame.draw.rect(screen, color, (75, 175, 35, 35))
		pygame.draw.rect(screen, (150, 150, 150), (125, (60/2)+155, 605, 10))
		pygame.draw.rect(screen, (40, 40, 40), (x_s, ((60/2)+155)-5, 10, 20))
		text=font.render('Smoothing', True, (0, 0, 0))
		screen.blit(text, (60, 160))
		# Обробка натискання
		if not pygame.mouse.get_pressed()[0]:
			click=False
		pos_x, pos_y=pygame.mouse.get_pos()
		if pos_x>75 and pos_x<75+35 and pos_y>175 and pos_y<175+35 and pygame.mouse.get_pressed()[0] and not click and not clicked[1]:
			smooth=not smooth
			click=True
		if smooth and pos_x>x_s and pos_x<x_s+70 and pos_y>((60/2)+155)-5 and pos_y<((60/2)+155)-5+20 and pygame.mouse.get_pressed()[0] and not clicked[1] and not clicked[0]:
			clicked=False, True
		if clicked[1] and pygame.mouse.get_pos()[0]>120 and pygame.mouse.get_pos()[0]<125+605:
			x_s=pygame.mouse.get_pos()[0]-5
			smoothL=((x_s-115)/100)+0.05
		if clicked[1] and not pygame.mouse.get_pressed()[0]:
			clicked=False, False
			
	pygame.display.flip()
	clock.tick(60)