
import random
from random import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
from math import *

from Shaders import *
from Matrices import *

class maze:
    def __init__(self):
        self.Grid = []


    def Open_wall(self, index, wall):
        block = self.Grid[index-1]
        block.Open_wall(wall)
    
    def make_maze(self,size):
        f = open('maze.txt','r')
        wallArray = []
        jebb = f.readlines()
        #print(jebb)
        for line in jebb:
            if line.strip("\n") == "":
                break
            lina = []
            line = line.strip("\n").split(",")
            #print(line)
        
            wallArray.append(line)

        numBlock = -1
  
        for x in range(size):
            
            for z in range(size):
                

                northwall = wallArray[numBlock][0] == "True"
                southWall = wallArray[numBlock][1] == "True"
                westWall = wallArray[numBlock][2] == "True"
                eastWall = wallArray[numBlock][3] == "True"
                # print(numBlock)
                # print(eastWall)

                self.Grid.append(block(x,z,0,northwall,southWall,westWall,eastWall))
                numBlock += 1

    def check_player_location(self, camX,camZ):
        blockNum = 0
        for blck in self.Grid:
        # for i in range(100):
            blck = self.Grid[0]
            #print(blck.check_if_in_block(camX,camZ))
            blockNum += 1
            if blck.check_if_in_block(camX,camZ) == True:
                return blockNum 
       

                
 

class block:
    def __init__(self,x,z,y,northwall = False, southwall = False, westwall = False, eastwall = False):
        self.x = x
        self.z = z
        self.y = y
        self.northWall = northwall
        self.southWall = southwall
        self.westWall = westwall
        self.eastWall = eastwall
    
    def Open_wall(self, wall):
        if wall == 1:
            self.northWall = False
        if wall == 2:
            self.southWall = False
        if wall == 3:
            self.westWall = False
        if wall == 4:
            self.eastWall = False

    def check_if_in_block(self, camX,camZ):
        # print("camx: {}".format(camX))
        # print("blockx: {}".format(self.x))
        if camX <= self.x+0.5 and camX >= self.x-0.5:
            # print("x is true")
            if camX <= self.z+0.5 and camZ >= self.z-0.5:
                return True
            else:
                return False
        else:
            return False


