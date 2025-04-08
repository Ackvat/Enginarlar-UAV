#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import math

########################################
#              SINIFLAR                #
########################################

class Vector3:
    def __init__(self, x, y, z):
        self.x: float = x
        self.y: float = y
        self.z: float = z

        self.n = 3
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other):
        return Vector3(self.x * other, self.y * other, self.z * other)
    
    def __div__(self, other):
        return Vector3(self.x / other, self.y / other, self.z / other)
    
    def __truediv__(self, other):
        return Vector3(self.x / other, self.y / other, self.z / other)
    
    def __str__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def Magnitude(self):
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def Median(self):
        return (self.x + self.y + self.z) / self.n
    
    def AbsoluteMedian(self):
        return abs(self.Median())
    
    def Normalized(self):
        if self.Magnitude() == 0:
            return Vector3(0, 0, 0)
        
        normalizedVector = Vector3(self.x, self.y, self.z)
        normalizedVector.x /= self.Magnitude()
        normalizedVector.y /= self.Magnitude()
        normalizedVector.z /= self.Magnitude()
        return normalizedVector
    
    def Unit(self):
        normalizedVector = self.Normalized()

        if normalizedVector.x > 0: normalizedVector.x = 1 
        elif normalizedVector.x < 0: normalizedVector.x = -1 
        else: normalizedVector.x = 0

        if normalizedVector.y > 0: normalizedVector.y = 1 
        elif normalizedVector.y < 0: normalizedVector.y = -1 
        else: normalizedVector.y = 0

        if normalizedVector.z > 0: normalizedVector.z = 1 
        elif normalizedVector.z < 0: normalizedVector.z = -1 
        else: normalizedVector.z = 0

        return normalizedVector

    def RotateZ(self, angle):
        degreeToRadians = math.radians(angle)
        return Vector3(self.x*math.cos(degreeToRadians) - self.y*math.sin(degreeToRadians), self.x*math.sin(degreeToRadians) + self.y*math.cos(degreeToRadians), self.z)

    def Clone(self):
        return Vector3(self.x, self.y, self.z)


class Quaternion:
    def __init__(self, w, x, y, z):
        self.w: float = w
        self.x: float = x
        self.y: float = y
        self.z: float = z
    
        self.n = 4
    
    def __add__(self, other):
        return Quaternion(self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Quaternion(self.w - other.w, self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other):
        return Quaternion(self.w * other, self.x * other, self.y * other, self.z * other)
    
    def __div__(self, other):
        return Quaternion(self.w / other, self.x / other, self.y / other, self.z / other)
    
    def __truediv__(self, other):
        return Quaternion(self.w / other, self.x / other, self.y / other, self.z / other)
    
    def __str__(self):
        return f"({self.w:.3f}, {self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def Magnitude(self):
        return (self.w ** 2 + self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def Median(self):
        return (self.w + self.x + self.y + self.z) / self.n
    
    def AbsoluteMedian(self):
        return abs(self.Median())
    
    def Normalized(self):
        if self.Magnitude() == 0:
            return Quaternion(0, 0, 0, 0)
        
        normalizedQuaternion = Quaternion(self.w, self.x, self.y, self.z)
        normalizedQuaternion.w /= self.Magnitude()
        normalizedQuaternion.x /= self.Magnitude()
        normalizedQuaternion.y /= self.Magnitude()
        normalizedQuaternion.z /= self.Magnitude()
        return normalizedQuaternion
    
    def Unit(self):
        normalizedQuaternion = self.Normalized()

        if normalizedQuaternion.w > 0: normalizedQuaternion.w = 1 
        elif normalizedQuaternion.w < 0: normalizedQuaternion.w = -1 
        else: normalizedQuaternion.w = 0

        if normalizedQuaternion.x > 0: normalizedQuaternion.x = 1 
        elif normalizedQuaternion.x < 0: normalizedQuaternion.x = -1 
        else: normalizedQuaternion.x = 0

        if normalizedQuaternion.y > 0: normalizedQuaternion.y = 1 
        elif normalizedQuaternion.y < 0: normalizedQuaternion.y = -1 
        else: normalizedQuaternion.y = 0

        if normalizedQuaternion.z > 0: normalizedQuaternion.z = 1 
        elif normalizedQuaternion.z < 0: normalizedQuaternion.z = -1 
        else: normalizedQuaternion.z = 0

        return normalizedQuaternion
    
    def GetEulerAngles(self):
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x ** 2 + self.y ** 2)
        roll_x = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (self.w * self.y - self.z * self.x)
        if abs(sinp) >= 1:
            pitch_y = math.copysign(math.pi / 2, sinp) 
        else:
            pitch_y = math.asin(sinp)
        
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y ** 2 + self.z ** 2)
        yaw_z = math.atan2(siny_cosp, cosy_cosp)

        return Vector3(math.degrees(roll_x), math.degrees(pitch_y), math.degrees(yaw_z))

    def Clone(self):
        return Quaternion(self.w, self.x, self.y, self.z)



def Clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 