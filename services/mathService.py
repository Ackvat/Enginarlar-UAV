#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import math

########################################
#              SINIFLAR                #
########################################

class Vector3:
    def __init__(self, x:float=0.0, y:float=0.0, z:float=0.0):
        self.x: float = x
        self.y: float = y
        self.z: float = z

        self.n = 3
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, other):
        return Vector3(self.x*other, self.y*other, self.z*other)
    
    def __div__(self, other):
        return Vector3(self.x/other, self.y/other, self.z/other)
    
    def __truediv__(self, other):
        return Vector3(self.x/other, self.y/other, self.z/other)
    
    def __str__(self):
        return f"({self.x:.3f},{self.y:.3f},{self.z:.3f})"
    
    def Magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5
    
    def Median(self):
        return (self.x + self.y + self.z)/self.n
    
    def AbsoluteMedian(self):
        return abs(self.Median())

    def Add(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.y)
    
    def Sub(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def Dot(self, other):
        return (self.x*other.x + self.y*other.y + self.z*other.z)

    def Cross(self, other):
        return Vector3(
            self.y*other.z - self.z*other.y,
            self.z*other.x - self.x*other.z,
            self.x*other.y - self.y*other.x
        )

    def Normalized(self):
        if self.Magnitude() == 0:
            return Vector3(0, 0, 0)
        
        return Vector3(self.x/self.Magnitude(), self.y/self.Magnitude(), self.z/self.Magnitude())
    
    def Unit(self):
        unitVector = self.Normalized()

        if unitVector.x > 0: unitVector.x = 1 
        elif unitVector.x < 0: unitVector.x = -1 
        else: unitVector.x = 0

        if unitVector.y > 0: unitVector.y = 1 
        elif unitVector.y < 0: unitVector.y = -1 
        else: unitVector.y = 0

        if unitVector.z > 0: unitVector.z = 1 
        elif unitVector.z < 0: unitVector.z = -1 
        else: unitVector.z = 0

        return unitVector

    def Clone(self):
        return Vector3(self.x, self.y, self.z)



class Basis:
    def __init__(self, x=Vector3(1, 0, 0), y=Vector3(0, 1, 0), z=Vector3(0, 0, 1)):
        self.x: Vector3 = x
        self.y: Vector3 = y
        self.z: Vector3 = z



class Quaternion:
    def FromAxisAngle(angle, axis):
        axis = axis.Normalized()
        return Quaternion(axis.x*math.sin(angle/2), axis.y*math.sin(angle/2), axis.z*math.sin(angle/2), math.cos(angle/2))

    def __init__(self, x:float=0.0, y:float=0.0, z:float=0.0, w:float=1.0):
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.w: float = w
    
        self.n = 4
    
    def __add__(self, other):
        return Quaternion(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
    
    def __sub__(self, other):
        return Quaternion(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)
    
    def __mul__(self, other):
        return Quaternion(self.x*other, self.y*other, self.z*other, self.w*other)
    
    def __div__(self, other):
        return Quaternion(self.x/other, self.y/other, self.z/other, self.w/other)
    
    def __truediv__(self, other):
        return Quaternion(self.x/other, self.y/other, self.z/other, self.w/other)
    
    def __str__(self):
        return f"({self.x:.3f},{self.y:.3f},{self.z:.3f},{self.w:.3f})"
    
    def Magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2 + self.w**2)**0.5
    
    def Median(self):
        return (self.x + self.y + self.z + self.w)/self.n
    
    def AbsoluteMedian(self):
        return abs(self.Median())

    def Add(self, other):
        return Quaternion(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)
    
    def Sub(self, other):
        return Quaternion(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def Normalized(self):
        if self.Magnitude() == 0:
            return Quaternion(0, 0, 0, 1)
        
        return Quaternion(self.x/self.Magnitude(), self.y/self.Magnitude(), self.z/self.Magnitude(), self.w/self.Magnitude())
    
    def Conjugated(self):
        return Quaternion(-self.x, -self.y, -self.z, self.w)
    
    # !!DİKKAT!! Nedense yanlış burası. Neden olduğunu öğrenmek için burada bırakıyorum.
    def MultWRONG(self, other):
        vectorSelf = Vector3(self.x, self.y, self.z)
        vectorOther = Vector3(other.x, other.y, other.z)
        wSelf_VOther = vectorOther*self.w
        wOther_VSelf = vectorSelf*other.w
        VSelf_cross_VOther = vectorSelf.Cross(vectorOther)
        VSelf_dot_VOther = vectorSelf.Dot(vectorOther)
        ComplexPart = wSelf_VOther.Add(wOther_VSelf).Add(VSelf_cross_VOther)
        return Quaternion(ComplexPart.x, ComplexPart.y, ComplexPart.z, self.w*other.w - VSelf_dot_VOther)
    
    def Mult(self, other):
        w = self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
        x = self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y
        y = self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x
        z = self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
        return Quaternion(x, y, z, w)
    
    def Rotate(self, angle, axis):
        return Quaternion(self.x, self.y, self.z, self.w).Mult(Quaternion.FromAxisAngle(angle, axis))
    
    def GetEulerAngles(self):
        sinr_cosp = 2*(self.w*self.x + self.y*self.z)
        cosr_cosp = 1 - 2*(self.x**2 + self.y**2)
        roll_x = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (self.w*self.y - self.z*self.x)
        if abs(sinp) >= 1:
            pitch_y = math.copysign(math.pi/2, sinp) 
        else:
            pitch_y = math.asin(Clamp(sinp, -1.0, 1.0))
        
        siny_cosp = 2*(self.w*self.z + self.x*self.y)
        cosy_cosp = 1 - 2*(self.y**2 + self.z**2)
        yaw_z = math.atan2(siny_cosp, cosy_cosp)

        return Vector3(math.degrees(roll_x), math.degrees(pitch_y), math.degrees(yaw_z))

    def GetBasis(self):
        return Basis(
            Vector3(1 - 2*(self.y**2 + self.z**2), 2*(self.x*self.y - self.w*self.z), 2*(self.x*self.z + self.w*self.y)),
            Vector3(2*(self.x*self.y + self.w*self.z), 1 - 2*(self.x**2 + self.z**2), 2*(self.y*self.z - self.w*self.x)),
            Vector3(2*(self.x*self.z - self.w*self.y), 2*(self.y*self.z + self.w*self.x), 1 - 2*(self.x**2 + self.y**2))
        )

    def GetRotationMatrix(self):
        # Wolfram, R = [X, Y, Z], X = (1, 0, 0), Y = (0, 1, 0), Z = (0, 0, 1)
        return [[1 - 2*(self.y**2 + self.z**2), 2*(self.x*self.y - self.w*self.z), 2*(self.x*self.z + self.w*self.y)], # Sağ, X
                [2*(self.x*self.y + self.w*self.z), 1 - 2*(self.x**2 + self.z**2), 2*(self.y*self.z - self.w*self.x)], # Yukarı, Y
                [2*(self.x*self.z - self.w*self.y), 2*(self.y*self.z + self.w*self.x), 1 - 2*(self.x**2 + self.y**2)]] # Ön, Z

    def Clone(self):
        return Quaternion(self.x, self.y, self.z, self.w)



def Clamp(n, min, max): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 

def Map(n, fromMin, fromMax, toMin, toMax):
    return (n-fromMin) * (toMax - toMin) / (fromMax - fromMin) + toMin

def sin(n):
    return math.sin(n)

def cos(n):
    return math.cos(n)

def acos(n):
    return math.acos(n)



def LowPassFilterUpdate(alpha, value, newValue):
    return newValue*alpha + value*(1 - alpha)

def AmplitudeImpedanceUpdate(factor, value, newValue):
    if newValue.Magnitude() > (value*factor).Magnitude():
        return value
    else:
        return newValue