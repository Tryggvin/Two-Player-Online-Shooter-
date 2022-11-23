
# from OpenGL.GL import *
# from OpenGL.GLU import *
from math import *
#from tkinter import W

import pygame
from pygame.locals import *

import sys
import time
from _thread import *
import server
from collision_object import collision_object

from Shaders import *
from Matrices import *
from maze import *
from network import Network

class GraphicsProgram3D:
    def __init__(self, hoster):

        pygame.init() 
        pygame.display.set_mode((800,600), pygame.OPENGL|pygame.DOUBLEBUF)

        self.shader = Shader3D()
        self.shader.use()

        # networking 
        self.net = Network(hoster) #------ uncomment this ------ 

        self.model_matrix = ModelMatrix()

        # mini map
        self.map_matrix = ViewMatrix()
        self.map_matrix.look(Point(0,10,0), Point(1,0,0), Vector(1,0,0))
        self.shader.set_view_matrix(self.map_matrix.get_matrix())

        # view matrix
        self.view_matrix = ViewMatrix()
        self.view_matrix.look(Point(1,0,1), Point(1,0,0), Vector(0,1,0))
        self.shader.set_view_matrix(self.view_matrix.get_matrix())

        #projection matrix
        self.projection_matrix = ProjectionMatrix()
        # self.projection_matrix.set_orthographic(-2, 2, -2, 2, 0.5, 10)
        self.projection_matrix.set_perspective(pi / 2, 800 / 600, 0.009, 50)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.cube = Cube()
        self.player = Cube()
        self.player2 = Cube()
        self.player2_x = 0
        self.player2_z = 0

        # crosshair
        self.crosshair = Sphere()
        self.player1_crosshair_x = 0
        self.player1_crosshair_z = 0

        # shooting player1
        self.player1_bullet = Sphere()
        self.shot = 0
        self.player1_bullet_cord = Point(0,0,0)
        self.player1_bullet_alive = False
        # shooting player1
        self.player2_bullet = Sphere()
        self.player2_shot = 0
        self.player2_bullet_cord = Point(0,0,0)
        self.player2_bullet_alive = False

        # objects 
        self.col = collision_object(1, -1, 1, 1)
        self.object_list = []
        self.object_list.append(self.col)
        

        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.player1_id = 0
        self.speed = 1

        self.angle = 0
        self.player1_angle = 0
        self.player2_angle = 0
        self.player2_gun_rotation_x = 0
        self.player2_gun_rotation_z = 0
        

        ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
        self.UP_key_down = False
        self.DW_key_down = False
        self.W_key_down = False
        self.S_key_down = False
        self.A_key_down = False
        self.D_key_down = False
        self.LA_key_down = False
        self.RA_key_down = False
        self.L_shift_down = False
        
        self.white_background = False

        self.maze = maze()
        self.maze.make_maze(10)
        # print(self.maze.Grid[99].eastWall)


    def check_collision(self, item: collision_object):
        # collision box test
        if (item.z1+0.1 > self.view_matrix.eye.z > item.z2)  and (item.x1 > self.view_matrix.eye.x):
            if (item.x1-0.1 < self.view_matrix.eye.x):
                self.view_matrix.eye.x = item.x1-0.1
        if (item.z1+0.1 > self.view_matrix.eye.z > item.z2)  and (item.x2 < self.view_matrix.eye.x):
            if (item.x2+0.1 > self.view_matrix.eye.x):
                self.view_matrix.eye.x = item.x2+0.1

        if (item.z1 < self.view_matrix.eye.z)  and (item.x1-0.1 < self.view_matrix.eye.x < item.x2+0.1):
            if (item.z1+0.1 > self.view_matrix.eye.z):
                self.view_matrix.eye.z = item.z1+0.1
        if (item.z2 > self.view_matrix.eye.z)  and (item.x1-0.1 < self.view_matrix.eye.x < item.x2+0.1):
            if (item.z2-0.1 < self.view_matrix.eye.z):
                self.view_matrix.eye.z = item.z2-0.1
            

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        self.angle += pi * delta_time
        # if angle > 2 * pi:
        #     angle -= (2 * pi

        self.player2_x

        if self.UP_key_down:
            self.white_background = True
        else:
            self.white_background = False

        # slide
        if self.L_shift_down:
            self.speed *= 1.01
            print(self.speed)
        else:
            self.speed = 1
        if self.speed > 4:
            self.speed = 4

        if self.W_key_down:
            self.view_matrix.slide(0,0,-self.speed*delta_time)
            #self.map_matrix.slide(0,0,-1*delta_time)
        if self.S_key_down:
            self.view_matrix.slide(0,0,self.speed*delta_time)
            #self.map_matrix.slide(0,0,1*delta_time)
        if self.A_key_down:
            self.view_matrix.slide(-self.speed*delta_time,0,0)
            #self.map_matrix.slide(-1*delta_time,0,0)
        if self.D_key_down:
            self.view_matrix.slide(self.speed*delta_time,0,0)
            #self.map_matrix.slide(1*delta_time,0,0)
        # yaw
        if self.LA_key_down:
            self.player1_angle += pi *delta_time
            self.view_matrix.yaw(pi *delta_time)
        if self.RA_key_down:
            self.player1_angle -= pi *delta_time
            self.view_matrix.yaw(-pi *delta_time)
        # pitch 
        if self.UP_key_down:
            self.view_matrix.pitch(pi *delta_time)
        if self.DW_key_down:
            self.view_matrix.pitch(-pi *delta_time)
        
        # shooting 
        if self.shot == 1:
            self.shot = 0
            self.player1_bullet_cord = Vector(self.view_matrix.eye.x,-.4,self.view_matrix.eye.z)
            print("I'm shooting")
            print("x: " + str(self.view_matrix.eye.x) + ", z:" + str(self.view_matrix.eye.z))
            # load bullet here
        #if self.player1_bullet_alive:
            #print(self.angle)
            #self.player1_bullet_cord.x = 0.1*sin(self.angle)
            #self.player1_bullet_cord.z = 0.1*-cos(self.angle)
            #self.player1_bullet_cord.x += self.player1_bullet_cord.x
            #self.player1_bullet_cord.z += self.player1_bullet_cord.z
        
        for item in self.object_list:
            self.check_collision(item)
        
        # crosshair
        self.player1_crosshair_x = 0.1*cos(self.player1_angle+1.6) + self.view_matrix.eye.x
        self.player1_crosshair_z = -0.1*sin(self.player1_angle+1.6) + self.view_matrix.eye.z

        if self.player2_shot == 1:
            print("the other player shot a bullet")
            # load bullet here
        
        self.player2_gun_rotation_x = .16*cos(self.player2_angle+0.9) + self.player2_x
        self.player2_gun_rotation_z = -.1*sin(self.player2_angle+0.9) + self.player2_z
        
        # barrel
        self.player2_barrel_rotation_x = .16*cos(self.player2_angle+0.9) + self.player2_x
        self.player2_barrel_rotation_z = -.14*sin(self.player2_angle+0.9) + self.player2_z

        tmp_point = Point(self.view_matrix.eye.x,1,self.view_matrix.eye.z)
        self.map_matrix.eye = tmp_point

        # print("x : {}".format(self.view_matrix.eye.x))
        # print("z : {}".format(self.view_matrix.eye.z))
        #blockNum = self.maze.check_player_location(self.view_matrix.eye.x,self.view_matrix.eye.z)
        #print(blockNum)

    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        for count in range(0,2):
            if count == 0:
                glViewport(0, 0, 800, 600)
                self.shader.set_view_matrix(self.view_matrix.get_matrix())
            else:
                glViewport(320,480,160,120)
                self.shader.set_view_matrix(self.map_matrix.get_matrix())

            # skybox 
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(0,0,0)
            self.model_matrix.add_scale(10,20,10)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0.5294,0.8078,0.9216)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            # collision box test
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            
            self.model_matrix.add_translation(self.col.x,0,self.col.z)
            self.model_matrix.add_scale(self.col.width,1,self.col.length)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()
            

            # floor 
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(0,-.8,0)
            self.model_matrix.add_scale(10,0.1,10)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0.5,0.5,0.5)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()
            
            if(count != 0):
                # ================================= player 1 =============================================== #
                self.model_matrix.load_identity()
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z)
                self.model_matrix.add_scale(0.2,0.2,0.2)
                self.model_matrix.add_rotate_y(self.player1_angle)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_solid_color(0,0,1)
                self.player.draw(self.shader)
                self.model_matrix.pop_matrix()

                # crosshair 
            if count == 0:
                self.model_matrix.load_identity()
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(self.player1_crosshair_x,self.view_matrix.eye.y,self.player1_crosshair_z)
                self.model_matrix.add_scale(0.001,0.001,0.001)
                self.model_matrix.add_rotate_y(self.player1_angle)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_solid_color(0,0,0)
                self.crosshair.draw(self.shader)
                self.model_matrix.pop_matrix()
            
            # bullet
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player1_bullet_cord.x,self.player1_bullet_cord.y,self.player1_bullet_cord.z)
            self.model_matrix.add_scale(0.02,0.02,0.02)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0,0,1)
            self.player1_bullet.draw(self.shader)
            self.model_matrix.pop_matrix()
                
                

            # ================================= player 2 =============================================== #
            # head
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_x,0,self.player2_z)
            self.model_matrix.add_scale(0.2,0.2,0.2)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            # body
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_x,-.5,self.player2_z)
            self.model_matrix.add_scale(0.2,-0.5,0.2)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            # gun shaft
            #self.model_matrix.load_identity()
            #self.model_matrix.push_matrix()
            #self.model_matrix.add_translation(self.player2_gun_rotation_x,-.45,self.player2_gun_rotation_z)
            #self.model_matrix.add_scale(0.05,-0.1,0.05)
            #self.model_matrix.add_rotate_y(self.player2_angle)
            #self.shader.set_model_matrix(self.model_matrix.matrix)
            #self.shader.set_solid_color(0,0,0)
            #self.player.draw(self.shader)
            #self.model_matrix.pop_matrix()
            
            # gun barrel
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_barrel_rotation_x,-.4,self.player2_barrel_rotation_z)
            self.model_matrix.add_scale(0.05,-0.05,0.05)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

        pygame.display.flip()
    
    def send_data(self):
        """
        Send position to server
        :return: reply
        """
        data = str(self.net.id) + ":" + str(self.view_matrix.eye.x) + "," + str(self.view_matrix.eye.z) + "," + str(self.player1_angle) + "," + str(self.shot)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return float(d[0]), float(d[1]), float(d[2]), float(d[3])
        except:
            return 0,0,0,0



    def program_loop(self):
        exiting = False
        while not exiting:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                    # shooting
                    if event.key == K_UP:
                        self.player1_bullet_alive = True
                        self.shot = 1
                    if event.key == K_DOWN:
                        self.DW_key_down = False
                    # slide
                    if event.key == K_w:
                        self.W_key_down = True
                    if event.key == K_s:
                        self.S_key_down = True
                    if event.key == K_a:
                        self.A_key_down = True
                    if event.key == K_d:
                        self.D_key_down = True
                    # yaw
                    if event.key == K_LEFT:
                        self.LA_key_down = True
                    if event.key == K_RIGHT:
                        self.RA_key_down = True
                    # sprint
                    if event.key == K_LSHIFT:
                        self.L_shift_down = True

                elif event.type == pygame.KEYUP:
                    # pitch
                    if event.key == K_UP:
                        self.UP_key_down = False
                    if event.key == K_DOWN:
                        self.DW_key_down = False
                    # slide
                    if event.key == K_w:
                        self.W_key_down = False
                    if event.key == K_s:
                        self.S_key_down = False
                    if event.key == K_a:
                        self.A_key_down = False
                    if event.key == K_d:
                        self.D_key_down = False
                    # yaw
                    if event.key == K_LEFT:
                        self.LA_key_down = False
                    if event.key == K_RIGHT:
                        self.RA_key_down = False
                    # sprint
                    if event.key == K_LSHIFT:
                        self.L_shift_down = False
            
            # Send Network Stuff
            self.player2_x, self.player2_z, self.player2_angle, self.player2_shot = self.parse_data(self.send_data()) # --- uncomment this
            
            self.update()
            self.display()

        #OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

if __name__ == "__main__":
    inn = input("type 'y' for hosting or 'n'")
    hoster = False
    if inn == 'y':
        hoster = True
        start_new_thread(server.host_server,())
    GraphicsProgram3D(hoster).start()