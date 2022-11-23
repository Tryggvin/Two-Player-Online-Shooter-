
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

from Shaders import *
from Matrices import *
from maze import *
from network import Network
from bullet import bullet
from collision_object import collision_object

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
        self.player2_x = 15
        self.player2_z = 20
        self.door_z = 0.0
        #collision
        self.collision = collision_object(1,0,1,1,1,1)

        #random
        self.random = random

        # crosshair
        self.crosshair = Sphere()
        self.player1_crosshair_x = 0
        self.player1_crosshair_z = 0

        # shooting player1
        self.player1_bullet = bullet(0,-100, 0, 0)
        self.shot = 0
        
        # shooting player1
        self.player2_bullet = bullet(0,-100, 0, 0)
        self.player2_shot = 0

        # objects 
        self.col = collision_object(1,0,1,1,1,1)
        self.object_list = []
        self.object_list.append(self.col)
        self.bullets = [self.player1_bullet, self.player2_bullet]

        
        self.door = True
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.player1_id = 0
        self.speed = 1

        self.angle = 0
        self.player1_angle = 0
        self.player2_angle = 0
        self.player2_gun_rotation_x = 0
        self.player2_gun_rotation_z = 0
        
        self.in_button_area_1 = False
        self.in_button_area_2 = False

        ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
        self.UP_key_down = False
        self.DW_key_down = False
        self.W_key_down = False
        self.S_key_down = False
        self.A_key_down = False
        self.D_key_down = False
        self.LA_key_down = False
        self.RA_key_down = False
        self.G_key_down = False
        self.E_key_down = False

        self.button_y_1 = -0.05

        self.button_y_2 = -0.05
        self.L_shift_down = False
        
        self.white_background = False

        self.maze = maze()
        self.maze.make_maze(10)
        # print(self.maze.Grid[99].eastWall)

        # if self.net.id == 1:
        #     self.view_matrix.eye.x = 20
        #     self.view_matrix.eye.z = 10

        self.hnit = [(7.0,5.0),(9.0,15.0),(5.0,10.0),(13.0,4.0),(12.0,17.0),(18.0,5.0),(19.0,15.0),(18.0,10.0),(21.0,15.0),(25.0,3.0)]
        # self.hnit = [(5,10),(6,10),(7,10),(8,10),(9,10)]
        # self.hnit = [(10,x) for x in range(20)]
        #box array
        self.boxes = [collision_object(box[0]-14.5,box[1]-9.5,1,1)for box in self.hnit]

            

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

    def check_bullet_collision(self, item: collision_object, bul: bullet ):
        # collision box test
        if (item.z1+0.01 > bul.z > item.z2)  and (item.x1 > bul.x):
            if (item.x1-0.01 < bul.x):
                bul.x = item.x1-0.01
        if (item.z1+0.01 > bul.z > item.z2)  and (item.x2 < bul.x):
            if (item.x2+0.01 > bul.x):
                bul.x = item.x2+0.01

        if (item.z1 < bul.z)  and (item.x1-0.01 < bul.x < item.x2+0.01):
            if (item.z1+0.01 > bul.z):
                bul.z = item.z1+0.01
        if (item.z2 > bul.z)  and (item.x1-0.1 < bul.x < item.x2+0.01):
            if (item.z2-0.01 < bul.eye.z):
                bul.z = item.z2-0.01
            

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

        if self.G_key_down:
            self.door = True

        #in button area 1
        if (self.view_matrix.eye.z <= 0.5) and (self.view_matrix.eye.z >= -0.5) and (self.view_matrix.eye.x <= 5.5) and (self.view_matrix.eye.x >= 4.5):
            self.in_button_area_1 = True
        else:
            self.in_button_area_1 = False
            # print("bool: ",self.door)
            # print("z: ", self.door_z)

        if (self.view_matrix.eye.z <= 0.5) and (self.view_matrix.eye.z >= -0.5) and (self.view_matrix.eye.x >= -5.5) and (self.view_matrix.eye.x <= -4.5):
            self.in_button_area_2 = True
        else:
            self.in_button_area_2 = False

        # if self.E_key_down and (self.in_button_area_1 or self.in_button_area_2): 
        #     if self.in_button_area_1:
        #         self.button_y_1 = -0.06
        #     if self.in_button_area_2:
        #         self.button_y_2 = -0.06

        #     if self.door == False and self.door_z <= 1:
            
        #         self.door = True
        #         print("open")
        #     else:
        #         self.button_y_1 = -0.05
        #         self.button_y_2 = -0.05
            
        if self.E_key_down and (self.in_button_area_1 or self.in_button_area_2): 
            print(self.door_z)
            print(self.door)
            if self.in_button_area_1:
                self.button_y_1 = -0.06
                print("button 1")
                
            elif self.in_button_area_2:
                self.button_y_2 = -0.06
                print("button 2")

            if self.door == True and self.door_z >= 1.5:
                self.door = False
                print("close")
            elif self.door == False and self.door_z <= 1:
                self.door = True
             
        else:
            self.button_y_1 = -0.05
            self.button_y_2 = -0.05
        
        # if self.E_key_down and (self.in_button_area_1 or self.in_button_area_2) and self.door == True and self.door_z >= 1.5:
        #     if self.in_button_area_1:
        #         self.button_y_1 = -0.06
        #     if self.in_button_area_2:
        #         self.button_y_2 = -0.06
        #     self.door = False
        #     print("close")
        # else:
        #     self.button_y_1 = -0.05
        #     self.button_y_2 = -0.05
        


        if self.door == True and self.door_z <= 2.0:
            self.door_z += 0.01

        if self.door == False and self.door_z >= 0.0:
            self.door_z -= 0.01

        
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
            print("I'm shooting")
            self.player1_bullet.set(self.view_matrix.eye.x,0,self.view_matrix.eye.z,self.player1_angle+1.6)

        if self.player1_bullet.alive:
            self.player1_bullet.update(delta_time)
    
        if self.player2_shot == 1:
            print("the other player shot a bullet")
            self.player2_bullet.set(self.player2_x,0,self.player2_z,self.player2_angle+1.6)
        if self.player2_bullet.alive:
            self.player2_bullet.update(delta_time)

        
        for item in self.boxes:
            self.check_collision(item)
            self.check_bullet_collision(item, self.player1_bullet)
            self.check_bullet_collision(item, self.player2_bullet)
        self.check_collision(self.player2_bullet.collision)
        
        
        # crosshair
        self.player1_crosshair_x = 0.1*cos(self.player1_angle+1.6) + self.view_matrix.eye.x
        self.player1_crosshair_z = -0.1*sin(self.player1_angle+1.6) + self.view_matrix.eye.z

        
        
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
            self.model_matrix.add_scale(35,20,25)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0.5294,0.8078,0.9216)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            # collision box test

            for box in self.boxes:
                self.model_matrix.load_identity()
                self.model_matrix.push_matrix()
                # tmp = collision_object(1)
                self.model_matrix.add_translation(box.x,-.3,box.z)
                self.model_matrix.add_scale(1,1,2)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_solid_color(1,0,1)
                self.player.draw(self.shader)
                self.model_matrix.pop_matrix()

            #wall
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,-.3,5.5)
            self.model_matrix.add_scale(1,1.5,10)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,-.3,-5.5)
            self.model_matrix.add_scale(1,1.5,10)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()


            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,0.6,0)
            self.model_matrix.add_scale(1,0.3,20)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            #door
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,-0.3,self.door_z)
            self.model_matrix.add_scale(0.9,1.5,1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0,0,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()


            #buttons
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(5,-0.3,0)
            self.model_matrix.add_scale(0.1,0.5,0.1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0,0,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(5,self.button_y_1,0)
            self.model_matrix.add_scale(0.05,0.05,0.05)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()
            


            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(-5,-0.3,0)
            self.model_matrix.add_scale(0.1,0.5,0.1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(0,0,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(-5,self.button_y_2,0)
            self.model_matrix.add_scale(0.05,0.05,0.05)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()


            #border
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,-.3,-10)
            self.model_matrix.add_scale(30,1.5,0.1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,1,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,-.3,10)
            self.model_matrix.add_scale(30,1.5,0.1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,1,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(-15,-.3,0)
            self.model_matrix.add_scale(0.1,1.5,30)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,1,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(15,-.3,0)
            self.model_matrix.add_scale(0.1,1.5,30)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_solid_color(1,1,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()


            

            # floor 
            self.model_matrix.load_identity()
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(0,-.8,0)
            self.model_matrix.add_scale(30,0.1,20)
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

                self.model_matrix.load_identity()
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(self.player1_crosshair_x,self.view_matrix.eye.y-0.1,self.player1_crosshair_z)
                self.model_matrix.add_scale(0.03,0.01,0.03)
                self.model_matrix.add_rotate_y(self.player1_angle)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_solid_color(0,0,0)
                self.player.draw(self.shader)
                self.model_matrix.pop_matrix()
            
            # bullet
            for bul in self.bullets:
                self.model_matrix.load_identity()
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(bul.x,bul.y-0.15,bul.z)
                self.model_matrix.add_scale(0.02,0.02,0.02)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_solid_color(0,0,1)
                bul.shape.draw(self.shader)
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
            # print(data.split(":")[0])
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

                    if event.key == K_g:
                        self.G_key_down = True
                    
                    if event.key == K_e:
                        self.E_key_down = True

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
                    if event.key == K_g:
                        self.G_key_down = False
                    
                    if event.key == K_e:
                        self.E_key_down = False

                    # sprint
                    if event.key == K_LSHIFT:
                        self.L_shift_down = False
            
            # Send Network Stuff
            self.player2_x, self.player2_z, self.player2_angle, self.player2_shot= self.parse_data(self.send_data()) # --- uncomment this
            
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