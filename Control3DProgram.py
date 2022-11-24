
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
        pygame.display.set_mode((1280,720), pygame.OPENGL|pygame.DOUBLEBUF)
        self.shader = Shader3D()
        self.shader.use()

        # networking 
        self.net = Network(hoster)

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
        self.projection_matrix.set_perspective(pi / 2, 1280 / 720, 0.009, 50)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.cube = Cube()
        self.player = Cube()
        self.player2 = Cube()
        self.player2_x = 15
        self.player2_z = 20
        self.door_z = 0.0

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
        self.col = collision_object(1, -1, 1, 1,1,1)
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
        self.L_ctrl_down = False
        self.space_down = False
        self.score = 0
        self.p2_score = 0

        
        

        

        self.button_y_1 = -0.05

        self.button_y_2 = -0.05
        self.L_shift_down = False

        self.id = 0
        
        self.white_background = False

        self.maze = maze()
        self.maze.make_maze(10)

        self.collision_obj =[
             collision_object(0,-0.3,5.5,1,10,1.5), collision_object(0,-0.3,-5.5,1,10,1.5),
        # collision_object(0,0.6,0,1,20,0.3),
            collision_object(-7.5,-0.3,-4.5,1,2,1),collision_object(-5.5,-0.3,5.5,1,2,1),
        collision_object(-9.5,-0.3,0.5,1,2,1),collision_object(-1.5,-0.3,-5.5,1,2,1),
        collision_object(-2.5,-0.3,7.5,1,2,1),collision_object(3.5,-0.3,-4.5,1,2,1),
        collision_object(4.5,-0.3,5.5,1,2,1),collision_object(3.5,-0.3,0.5,1,2,1),
        collision_object(6.5,-0.3,5.5,1,2,1),collision_object(10.5,-0.3,-6.5,1,2,1),
        collision_object(0,-0.3,-10,30,0.1,1.5),collision_object(0,-0.3,10,30,0.1,1.5),
        collision_object(-15,-0.3,0,0.1,30,1.5),collision_object(15,-0.3,0,0.1,30,1.5),
       collision_object(5,-0.3,0,0.1,0.1,0.5), collision_object(-5,-0.3,0,0.1,0.1,0.5)
        
        ]
        self.respawn()
        self.texture_id01 = self.load_texture(sys.path[0] + "/textures/test.png")
        self.texture_id02 = self.load_texture(sys.path[0] + "/textures/wall.jpg")

    def load_texture(self, path_string):
        surface = pygame.image.load(path_string)
        tex_string = pygame.image.tostring(surface, "RGBA",1)
        width = surface.get_width()
        height = surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        #glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
        return tex_id

    def respawn(self):
        self.player1_alive = True
        if self.net.id == "0":
            self.view_matrix.eye.x = 14
            self.view_matrix.eye.z = -9
        else:
            self.view_matrix.eye.x = -14
            self.view_matrix.eye.z = 9
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
    def check_p1_bullet_collision(self, item: collision_object, bul: bullet):
        # collision box test
        if (item.z1+0.1 > bul.z > item.z2)  and (item.x1 > bul.x):
            if (item.x1-0.1 < bul.x):
                bul.x = item.x1
                bul.alive = False
        if (item.z1+0.1 > bul.z > item.z2)  and (item.x2 < bul.x):
            if (item.x2+0.1 > bul.x):
                bul.x = item.x2
                bul.alive = False

        if (item.z1 < bul.z)  and (item.x1-0.1 < bul.x < item.x2+0.1):
            if (item.z1+0.1 > bul.z):
                bul.alive = False
                bul.z = item.z1
        if (item.z2 > bul.z)  and (item.x1-0.1 < bul.x < item.x2+0.1):
            if (item.z2-0.1 < bul.z):
                bul.z = item.z2
                bul.alive = False
    def check_player_bullet_collision(self, item: collision_object, bul: bullet):
        # collision box test
        if (item.z1+0.1 > bul.z > item.z2)  and (item.x1 > bul.x):
            if (item.x1-0.1 < bul.x):
                self.player1_alive = False
        if (item.z1+0.1 > bul.z > item.z2)  and (item.x2 < bul.x):
            if (item.x2+0.1 > bul.x):
                self.player1_alive = False

        if (item.z1 < bul.z)  and (item.x1-0.1 < bul.x < item.x2+0.1):
            if (item.z1+0.1 > bul.z):
                self.player1_alive = False
        if (item.z2 > bul.z)  and (item.x1-0.1 < bul.x < item.x2+0.1):
            if (item.z2-0.1 < bul.z):
                self.player1_alive = False
            

    def update(self, hit):
        delta_time = self.clock.tick() / 1000.0
        self.angle += pi * delta_time
        # if angle > 2 * pi:
        #     angle -= (2 * pi
        if hit == 1:
            print("our score: "+self.score+", their score: "+self.p2_score)

        if not self.player1_alive:
            self.respawn()
            # #respawn
            # self.player1_alive = True
            # if self.net.id == 0:
            #     self.view_matrix.eye.x = 14
            #     self.view_matrix.eye.z = -9
            # else:
            #     self.view_matrix.eye.x = -14
                # self.view_matrix.eye.z = 9

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
            self.respawn()

        #in button area 1
        if (self.view_matrix.eye.z <= 0.5) and (self.view_matrix.eye.z >= -0.5) and (self.view_matrix.eye.x <= 5.5) and (self.view_matrix.eye.x >= 4.5):
            self.in_button_area_1 = True
        else:
            self.in_button_area_1 = False


        if (self.view_matrix.eye.z <= 0.5) and (self.view_matrix.eye.z >= -0.5) and (self.view_matrix.eye.x >= -5.5) and (self.view_matrix.eye.x <= -4.5):
            self.in_button_area_2 = True
        else:
            self.in_button_area_2 = False

            
        if self.E_key_down and (self.in_button_area_1 or self.in_button_area_2): 

            if self.in_button_area_1:
                self.button_y_1 = -0.06

                
            elif self.in_button_area_2:
                self.button_y_2 = -0.06


            if self.door == True and self.door_z >= 1.5:
                self.door = False

            elif self.door == False and self.door_z <= 1:
                self.door = True
             
        else:
            self.button_y_1 = -0.05
            self.button_y_2 = -0.05
        


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
            self.player1_bullet.alive = True
            print("I'm shooting")
            self.player1_bullet.set(self.view_matrix.eye.x,0,self.view_matrix.eye.z,self.player1_angle+1.6)

        if self.player1_bullet.alive:
            self.player1_bullet.update(delta_time)
    
        if self.player2_shot == 1:
            print("the other player shot a bullet")
            self.player2_bullet.alive = True
            self.player2_bullet.set(self.player2_x,0,self.player2_z,self.player2_angle+1.6)
        if self.player2_bullet.alive:
            self.player2_bullet.update(delta_time)

        
        for item in self.collision_obj:
            self.check_collision(item)
            self.check_p1_bullet_collision(item, self.player1_bullet)
            self.check_p1_bullet_collision(item, self.player2_bullet)
        self.check_player_bullet_collision(collision_object(self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z,0.2,0.2,0.2), self.player2_bullet)
        self.check_collision(collision_object(self.player2_x,0,self.player2_z,0.2,0.2,0.2))
        self.check_collision(collision_object(0,-3,self.door_z,0.9,1,1.5))
        #self.check_collision(self.player2_bullet.collision)
        
        
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


    def display(self):
        glEnable(GL_DEPTH_TEST)  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        for count in range(0,2):
            if count == 0:
                glViewport(0, 0, 1280, 720)
                self.shader.set_view_matrix(self.view_matrix.get_matrix())
            else:
                glViewport(100,550,160,120)
                self.shader.set_view_matrix(self.map_matrix.get_matrix())

            self.shader.set_eye_position(self.view_matrix.eye)
            #self.shader.set_eye_position(Point(0,10,0))
            # light pos
            self.shader.set_light_position(Point(self.view_matrix.eye.x,2,self.view_matrix.eye.z))
            #self.shader.set_light_position(Point(4.0*cos(self.angle),5,4.0*sin(self.angle)))
            self.shader.set_light_diffuse(1.0,1.0,1.0)
            self.shader.set_light_specular(1.0,1.0,1.0)

            self.shader.set_material_specular(1.0,1.0,1.0)
            self.shader.set_material_shine(1)

            self.model_matrix.load_identity()

            #self.shader.set_material_diffuse(1.0,1.0,1.0)
            
            
            #self.shader.set_light_diffuse(1,1,1)
            

            # skybox 
            glBindTexture(GL_TEXTURE_2D, self.texture_id01)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(0,0,0)
            self.model_matrix.add_scale(35,20,25)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(0.5294,0.8078,0.9216)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            glBindTexture(GL_TEXTURE_2D, self.texture_id01)
            self.shader.set_material_diffuse(1,1,1)
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(14,0,-5)
            self.model_matrix.add_scale(2,2,2)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            
            self.cube.draw(self.shader)
            self.model_matrix.pop_matrix()

            # collision box test

            for obj in self.collision_obj:
                #glBindTexture(GL_TEXTURE_2D, self.texture_id01)
                
                self.shader.set_material_diffuse(1.0,0.0,0.0)
                self.model_matrix.push_matrix()
                # tmp = collision_object(1)
                self.model_matrix.add_translation(obj.x,obj.y,obj.z)
                self.model_matrix.add_scale(obj.width,obj.height,obj.len) 
                self.shader.set_model_matrix(self.model_matrix.matrix)
                
                
                #self.shader.set_material_diffuse(1,0,1)
                self.player.draw(self.shader)
                #self.shader.set_diffuse_texture(self.texture_id01)
                self.model_matrix.pop_matrix()



            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,0.6,0)
            self.model_matrix.add_scale(1,0.3,20)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            #door
            
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(0,-0.3,self.door_z)
            self.model_matrix.add_scale(0.9,1.5,1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(0,0,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(5,self.button_y_1,0)
            self.model_matrix.add_scale(0.05,0.05,0.05)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()
            
            self.model_matrix.push_matrix()
                # tmp = collision_object(1)
            self.model_matrix.add_translation(-5,self.button_y_2,0)
            self.model_matrix.add_scale(0.05,0.05,0.05)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()        

            # floor 
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(0,-.8,0)
            self.model_matrix.add_scale(30,0.1,20)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(0.5,0.5,0.5)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()
            
            if(count != 0):
                # ================================= player 1 =============================================== #
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(self.view_matrix.eye.x,self.view_matrix.eye.y,self.view_matrix.eye.z)
                self.model_matrix.add_scale(0.2,0.2,0.2)
                self.model_matrix.add_rotate_y(self.player1_angle)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_material_diffuse(0,0,1)
                self.player.draw(self.shader)
                self.model_matrix.pop_matrix()

                # crosshair 
            if count == 0:
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(self.player1_crosshair_x,self.view_matrix.eye.y,self.player1_crosshair_z)
                self.model_matrix.add_scale(0.001,0.001,0.001)
                self.model_matrix.add_rotate_y(self.player1_angle)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_material_diffuse(0,0,0)
                self.crosshair.draw(self.shader)
                self.model_matrix.pop_matrix()

                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(self.player1_crosshair_x,self.view_matrix.eye.y-0.1,self.player1_crosshair_z)
                self.model_matrix.add_scale(0.03,0.01,0.03)
                self.model_matrix.add_rotate_y(self.player1_angle)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_material_diffuse(0,0,0)
                self.player.draw(self.shader)
                self.model_matrix.pop_matrix()
            
            # bullet
            for bul in self.bullets:
                self.model_matrix.push_matrix()
                self.model_matrix.add_translation(bul.x,bul.y-0.15,bul.z)
                self.model_matrix.add_scale(0.02,0.02,0.02)
                self.shader.set_model_matrix(self.model_matrix.matrix)
                self.shader.set_material_diffuse(0,0,1)
                bul.shape.draw(self.shader)
                self.model_matrix.pop_matrix()
                
                

            # ================================= player 2 =============================================== #
            # head
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_x,0,self.player2_z)
            self.model_matrix.add_scale(0.2,0.2,0.2)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            #neck
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_x,-0.2,self.player2_z)
            self.model_matrix.add_scale(0.15,0.4,0.15)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(1,0,1)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

            # body
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_x,-.5,self.player2_z)
            self.model_matrix.add_scale(0.2,-0.5,0.2)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(1,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()
            
            # gun barrel
            self.model_matrix.push_matrix()
            self.model_matrix.add_translation(self.player2_barrel_rotation_x,-.4,self.player2_barrel_rotation_z)
            self.model_matrix.add_scale(0.05,-0.05,0.05)
            self.model_matrix.add_rotate_y(self.player2_angle)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(0,0,0)
            self.player.draw(self.shader)
            self.model_matrix.pop_matrix()

        pygame.display.flip()
    
    def send_data(self):
        """
        Send position to server
        :return: reply
        """
        tmp = 0
        if self.door:
            tmp = 1
        if not self.player1_alive:
            tmp_score = 1
        data = str(self.net.id) + ":" + str(self.view_matrix.eye.x) + "," + str(self.view_matrix.eye.z) + "," + str(self.player1_angle) + "," + str(self.shot)+ "," + str(tmp)+ "," + str(tmp_score)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return float(d[0]), float(d[1]), float(d[2]), float(d[3]), float(d[4]), float(d[5])
        except:
            return 0,0,0,0,0,0

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

                    if event.key == K_LCTRL:
                        self.L_ctrl_down = True

                    if event.key == K_SPACE:
                        self.space_down = True

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
                    if event.key == K_LCTRL:
                        self.L_ctrl_down = False
                    if event.key == K_SPACE:
                        self.space_down = False
            
            # Send Network Stuff
            self.player2_x, self.player2_z, self.player2_angle, self.player2_shot, self.door, tmp = self.parse_data(self.send_data()) # --- uncomment this
            self.p2_score += tmp
            self.update(tmp)
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