import pygame
import json
import math
import socket
import threading
import sys

pygame.init()
clock=pygame.time.Clock()
screen=pygame.display.set_mode((800, 600))

try:
	with open("map.txt", "r") as file:
		Map=json.loads(file.read())
except Exception as e:
	Map=[]

x, y=50, 50
x_pl2, y_pl2=-50, -50
angle=0
quality=40
max_depth=500
server=False
client=False

stop_event=threading.Event()

def colision(x, y):
	for obj in Map:
		if x>obj[0] and x<obj[0]+obj[2] and y>obj[1] and y<obj[1]+obj[3] or x>x_pl2 and x<x_pl2+20 and y>y_pl2 and y<y_pl2+20:
			if obj[4]:
				return True, True
			else:
				return True, False
	return False, False

def move(speed, angle):
	angle_rad=angle*(math.pi/180.0)
	end_x=x+speed*math.cos(angle_rad)
	end_y=y+speed*math.sin(angle_rad)
	return end_x, end_y

def cast_ray(x, y, angle, max_depth, step_size=1):
	angle_rad=math.radians(angle)
	for depth in range(0, max_depth, step_size):
		target_x=x+depth*math.cos(angle_rad)
		target_y=y+depth*math.sin(angle_rad)
		colD=colision(target_x, target_y)
		if colD[1]:
			angle_rad=math.radians(math.pi-angle)
			target_x=x+depth*math.cos(angle_rad)
			target_y=y+depth*math.sin(angle_rad)
			colD=colision(target_x, target_y)
		if colD[0]:
			if key[pygame.K_m]:
				pygame.draw.line(screen, (0, 0, 0), (x, y), (target_x, target_y), 3)
			return depth, target_x, target_y
	return max_depth, target_x, target_y

def draw():
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

def server_thread():
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
				x_pl2, y_pl2=player_data
				conn.sendall(json.dumps([x, y]).encode())

def client_thread():
	global x_pl2, y_pl2
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(("127.0.0.1", 443))
		while True:
			text=json.dumps([x, y])
			s.sendall(text.encode())
			data=s.recv(1024)
			if data:
				server_data=json.loads(data.decode())
				x_pl2, y_pl2=server_data

server_thread_instance=None
client_thread_instance=None

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			stop_event.set()
			if server_thread_instance is not None:
				server_thread_instance.join()
			if client_thread_instance is not None:
				client_thread_instance.join()
			pygame.quit()
			sys.exit()

	key=pygame.key.get_pressed()

	if key[pygame.K_1] and not server:
		server=True
		server_thread_instance=threading.Thread(target=server_thread)
		server_thread_instance.start()
	if key[pygame.K_2] and not client:
		client=True
		client_thread_instance=threading.Thread(target=client_thread)
		client_thread_instance.start()

	if key[pygame.K_l]:
		try:
			with open("map.txt", "r") as file:
				Map=json.loads(file.read())
		except Exception as e:
			print('Error')

	if key[pygame.K_UP]:
		quality+=10
	if key[pygame.K_DOWN] and quality>10:
		quality-=10
	if key[pygame.K_RIGHT]:
		max_depth+=10
	if key[pygame.K_LEFT] and not max_depth<=10:
		max_depth-=10

	if key[pygame.K_w]:
		new_x, new_y=move(3, angle)
		if not colision(new_x, new_y)[0]:
			x, y=new_x, new_y
	if key[pygame.K_s]:
		new_x, new_y=move(-3, angle)
		if not colision(new_x, new_y)[0]:
			x, y=new_x, new_y
	if key[pygame.K_a]:
		angle -= 3
	if key[pygame.K_d]:
		angle += 3

	screen.fill((255, 255, 255))
	draw()

	pygame.display.flip()
	clock.tick(60)