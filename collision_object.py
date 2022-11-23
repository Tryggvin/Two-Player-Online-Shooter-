class collision_object():
    def __init__(self, x,y,z, width, length, height):
        self.x = x
        self.y = y
        self.z = z
        self.y = y
        self.width = width
        self.height = height
        self.len = length
        self.x1 = x - (width / 2)
        self.x2 = x + (width / 2)
        self.z1 = z + (length / 2)
        self.z2 = z - (length / 2)
    
    def __str__(self):
        return str(self.x1) + ", " + str(self.x2) + ", " + str(self.z1) + ", " + str(self.z2)