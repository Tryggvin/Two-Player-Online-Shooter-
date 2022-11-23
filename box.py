class collision_object():
    def __init__(self, x,z, width, length):
        self.x1 = x - (width / 2)
        self.x2 = x + (length / 2)
        self.z1 = z - (width / 2)
        self.z2 = z + (length / 2)
    
    def __str__(self):
        return str(self.x1) + ", " + str(self.x2) + ", " + str(self.z1) + ", " + str(self.z2)