from math import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from typing import overload
import inspect
import logging
import colorlog
from termcolor import colored
from matplotlib.animation import FuncAnimation

def funcname():
  return inspect.currentframe().f_back.f_code.co_name

# 创建日志处理器
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s: %(message)s",
    log_colors={
        'DEBUG'   : 'cyan',
        'INFO'    : 'green',
        'WARNING' : 'yellow',
        'ERROR'   : 'red',
        'CRITICAL': 'bold_red',
    }
))

# 创建日志记录器
logger = logging.getLogger("base")
logger.addHandler(handler)

L1  = 80.0 # 大腿轴>小腿轴
_L1 = 75.0
L1_ = 5.0
L2  = 65.0 # 小腿轴>足尖
L3  = 20.0 # 小腿轴>拉杆轴 
L4  = 32.0 # 舵机轴尖>大腿轴 垂直距离
L5  = sqrt(pow(_L1,2) + pow(L4,2)) # 舵机轴尖到小腿轴
L8  = 15.0 # 小腿扭杆
L9  = 73.0 # 小腿拉杆
R14 = pi/2
R15 = atan(L4/_L1)

class Coord:
  X = 0.0
  Z = 0.0

  def __init__(self, X=0.0, Z=0.0):
    self.X = X
    self.Z = Z

  def __str__(self):
    return '%f,%f' % (self.X, self.Z)

  def __iter__(self):
    return iter((self.X, self.Z))

class KinematicsData:

  AS1 = 0.0
  AS2 = 0.0
  RS1 = 0.0
  RS2 = 0.0
  L6 = 0.0
  L7 = 0.0
  R12 = 0.0
  R13 = 0.0
  R17 = 0.0
  R35 = 0.0
  R7X = 0.0
  X = 0.0
  Z = 0.0
  KX = 0.0
  KZ = 0.0

  def __init__(
    self,
    AS1=0.0, AS2=0.0, 
    RS1=0.0, RS2=0.0, 
    L6=0.0, L7=0.0, 
    R12=0.0, R13=0.0, R17=0.0, R35=0.0, R7X=0.0, 
    X=0.0, Z=0.0,KX=0.0, KZ=0.0):

    self.AS1 = AS1
    self.AS2 = AS2
    self.RS1 = RS1
    self.RS2 = RS2
    self.L6 = L6
    self.L7 = L7
    self.R12 = R12
    self.R13 = R13
    self.R17 = R17
    self.R35 = R35
    self.R7X = R7X
    self.X = X
    self.Z = Z
    self.KX = KX
    self.KZ = KZ

  def _str_0(self):
    return "\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % (
      '| %-5s : %20.10f° | %-5s : %20.10f° |' % ('AS1',self.AS1,'AS2',self.AS2),
      '| %-5s : %20.10f  | %-5s : %20.10f  |' % ('RS1',self.RS1,'RS2',self.RS2),
      '| %-5s : %20.10f  | %-5s : %20.10f  |' % ('L6',self.L6,'L7',self.L7),
      '| %-5s : %20.10f  | %-5s : %20.10f  |' % ('R12',self.R12,'R13',self.R13),
      '| %-5s : %20.10f  | %-5s : %20.10f  |' % ('R17',self.R17,'',0),
      '| %-5s : %20.10f  | %-5s : %20.10f  |' % ('R35',self.R35,'R7X',self.R7X),
      '| %-5s : %20.10f  | %-5s : %20.10f  |' % ('X',self.X,'Z',self.Z),
    )  
  
  def _str_1(self):
    return "\n%s\n%s\n%s\n%s\n%s\n%s\n%s\n" % (
      '| %-5s : %64.32f° | %-5s : %64.32f° |' % ('AS1',self.AS1,'AS2',self.AS2),
      '| %-5s : %64.32f  | %-5s : %64.32f  |' % ('RS1',self.RS1,'RS2',self.RS2),
      '| %-5s : %64.32f  | %-5s : %64.32f  |' % ('L6',self.L6,'L7',self.L7),
      '| %-5s : %64.32f  | %-5s : %64.32f  |' % ('R12',self.R12,'R13',self.R13),
      '| %-5s : %64.32f  | %-5s : %64.32f  |' % ('R17',self.R17,'',0),
      '| %-5s : %64.32f  | %-5s : %64.32f  |' % ('R35',self.R35,'R7X',self.R7X),
      '| %-5s : %64.32f  | %-5s : %64.32f  |' % ('X',self.X,'Z',self.Z),
    )
  
  def _str_2(self):
    '''
    C语言量化表str
    '''
    def __str__(self):
      return '%f,%f' % (self.X, self.Z)

  def __str__(self, mode=0):
    match(mode):
      case 0:
        return self._str_0()
      case 1:
        return self._str_1()
      case 2:
        return self._str_2()
      case _:
        logger.error('Invalid mode: %s' % mode)
        return None

  def __eq__(self, other):
    
    agnle_error = 0.001
    radian_error = radians(agnle_error)
    length_error = 0.001

    if not isinstance(other, KinematicsData):
      logger.error('Not same type: %s != %s' % (type(self), type(other)))
      return NotImplemented
    else:
      AS1_eq = abs(self.AS1 - other.AS1) < agnle_error
      AS2_eq = abs(self.AS2 - other.AS2) < agnle_error
      RS1_eq = abs(self.RS1 - other.RS1) < radian_error
      RS2_eq = abs(self.RS2 - other.RS2) < radian_error
      L6_eq  = abs(self.L6  - other.L6)  < length_error
      L7_eq  = abs(self.L7  - other.L7)  < length_error
      R12_eq = abs(self.R12 - other.R12) < radian_error
      R13_eq = abs(self.R13 - other.R13) < radian_error
      R17_eq = abs(self.R17 - other.R17) < radian_error
      R35_eq = abs(self.R35 - other.R35) < radian_error
      R7X_eq = abs(self.R7X - other.R7X) < radian_error
      X_eq   = abs(self.X   - other.X)   < length_error
      Z_eq   = abs(self.Z   - other.Z)   < length_error
      All    = AS1_eq and AS2_eq and RS1_eq and RS2_eq and L6_eq and L7_eq and R12_eq and R13_eq and R17_eq and R35_eq and R7X_eq and X_eq and Z_eq

      def _logger0(eq, tag , data0, data1):
        if eq:
          logger.debug('| %5s | %20.10f | %20.10f | %20.10f |' 
                       % (tag, data0, data1, abs(data0-data1)))
        else:
          logger.error('| %5s | %20.10f | %20.10f | %20.10f |' 
                       % (tag, data0, data1, abs(data0-data1)))   

      def _logger1(eq, tag , data0, data1):
        if eq:
          logger.debug('| %5s | %64.32f | %64.32f | %64.32f |' 
                       % (tag, data0, data1, abs(data0-data1)))
        else:
          logger.error('| %5s | %64.32f | %64.32f | %64.32f |' 
                       % (tag, data0, data1, abs(data0-data1)))

      def _logger(eq, tag , data0, data1, mode=0):
        match(mode):
          case 0:
            _logger0(eq, tag , data0, data1)
          case 1:
            _logger1(eq, tag , data0, data1)
          case _:
            logger.error('Invalid mode: %s' % mode)

      if not All == True:
        logger.error('KinematicsData not equal:\n')
        logger.error('| %5s | %20s | %20s | %20s |' % ('','self','other','diff'))
        _logger(AS1_eq, 'AS1', self.AS1, other.AS1)
        _logger(AS2_eq, 'AS2', self.AS2, other.AS2)
        _logger(RS1_eq, 'RS1', self.RS1, other.RS1)
        _logger(RS2_eq, 'RS2', self.RS2, other.RS2)
        _logger(L6_eq,  'L6',  self.L6,  other.L6)
        _logger(L7_eq,  'L7',  self.L7,  other.L7)
        _logger(R12_eq, 'R12', self.R12, other.R12)
        _logger(R13_eq, 'R13', self.R13, other.R13)
        _logger(R17_eq, 'R17', self.R17, other.R17)
        _logger(R35_eq, 'R35', self.R35, other.R35)
        _logger(R7X_eq, 'R7X', self.R7X, other.R7X)
        _logger(X_eq,   'X',   self.X,   other.X)
        _logger(Z_eq,   'Z',   self.Z,   other.Z)
      return All

def forward(AS1: np.float64, AS2: np.float64) -> KinematicsData:

  def F1_RS2_to_L6(RS2: np.float64) -> np.float64:
    _a = np.float64(1)
    _b = np.float64(-2 * L8 * cos(RS2))
    _c = np.float64(pow(L8, 2) - pow(L9, 2))
    D = np.float64(pow(_b, 2) - 4 * _a * _c)
    if D < 0:
      logger.error('%-20s: L9:%f, L8:%f, RS2:%f [ %f° ], _a:%f, _b:%f, _c:%f, D:%f' % (funcname(), L9, L8, RS2, degrees(RS2), _a, _b, _c, D))
      return np.float64(0)
    L6 = np.float64((-_b + sqrt(D)) / (2 * _a))
    logger.debug('%-20s: RS2=%f, L6=%f' % (funcname(), RS2, L6))
    return L6

  def F2_L6_to_R35(L6: np.float64) -> np.float64:
    T = np.float64((pow(L3, 2) + pow(L5, 2) - pow(L6, 2)) / (2 * L3 * L5))
    R35 = np.float64(acos(T))
    logger.debug('%-20s: L3=%f, L5=%f, L6=%f, T=%f, R35=%f [ %f° ]' % (funcname(), L3, L5, L6, T, R35, degrees(R35)))
    return R35

  def F3_R15R35_to_R13(R15: np.float64, R35: np.float64) -> np.float64:
    R13 = np.float64(R15 + R35)
    logger.debug('%-20s: R15=%f [ %f° ], R35=%f [ %f° ], R13=%f [ %f° ]' % (funcname(), R15, degrees(R15), R35, degrees(R35), R13, degrees(R13)))
    return R13

  def F4_R13_to_R12(R13: np.float64) -> np.float64:
    R12 = np.float64(pi - R13)
    logger.debug('%-20s: R13=%f [ %f° ], R12=%f [ %f° ]' % (funcname(), R13, degrees(R13), R12, degrees(R12)))
    return R12

  def F5_R12_to_L7(R12: np.float64) -> np.float64:
    L7 = np.float64(sqrt(pow(L1, 2) + pow(L2, 2) - 2 * L1 * L2 * cos(R12)))
    logger.debug('%-20s: L1=%f, L2=%f, R12=%f [ %f° ], L7=%f' % (funcname(), L1, L2, R12, degrees(R12), L7))
    return L7

  def F6_L7_to_R17(L7: np.float64) -> np.float64:
    T = np.float64((pow(L1, 2) + pow(L7, 2) - pow(L2, 2)) / (2 * L1 * L7))
    R17 = np.float64(acos(T))
    logger.debug('%-20s: L1=%f, L7=%f, T=%f, R17=%f [ %f° ]' % (funcname(), L1, L7, T, R17, degrees(R17)))
    return R17

  def F7_RS1R17_to_R7X(RS1: np.float64, R17: np.float64) -> np.float64:
    R7X = np.float64(RS1 + R17)
    logger.debug('%-20s: RS1=%f [ %f° ], R17=%f [ %f° ], R7X=%f [ %f° ]' % (funcname(), RS1, degrees(RS1), R17, degrees(R17), R7X, degrees(R7X)))
    return R7X

  def F8_L7R7X_to_xz(L7: np.float64, R7X: np.float64) -> tuple[np.float64, np.float64]:
    X = np.float64(L7 * cos(R7X))
    Z = np.float64(L7 * sin(R7X))
    
    if R7X > pi / 2:
      X = -X
    elif R7X > pi:
      X = -X
      Z = -Z

    logger.debug('%-20s: L7=%f, R7X=%f [ %f° ], X=%f, Z=%f' % (funcname(), L7, R7X, degrees(R7X), X, Z))
    return X, Z

  if AS2 > 120:
    logger.error('AS2 [ %f° ] > 120' % AS2)
    AS2 = 120

  RS1 = np.float64(radians(AS1))
  RS2 = np.float64(radians(AS2))

  L6  = F1_RS2_to_L6(RS2)
  R35 = F2_L6_to_R35(L6)
  R13 = F3_R15R35_to_R13(R15,R35)
  R12 = F4_R13_to_R12(R13)
  L7  = F5_R12_to_L7(R12)
  R17 = F6_L7_to_R17(L7)
  R7X = F7_RS1R17_to_R7X(RS1,R17)
  X,Z = F8_L7R7X_to_xz(L7,R7X)

  if RS1+R17>pi/2: 
    X=-X

  #计算膝盖坐标
  if RS1 < pi/2:
    KX = L1*cos(RS1)
    KZ = L1*sin(RS1)
  elif RS1 == pi/2:
    KX = 0
    KZ = L1
  else:
    KX = -L1*cos(RS1)
    KZ = L1*sin(RS1)

  data = KinematicsData(
    AS1=AS1, AS2=AS2, RS1=RS1, RS2=RS2,
    L6=L6, L7=L7, R12=R12, R13=R13, R17=R17,
    R35=R35, R7X=R7X, X=X, Z=Z, KX=KX, KZ=KZ
  )
  return data

def forwardN( AS1Range, AS2Range):
  fkdatas = []
  fkcoords = []
  for AS1 in AS1Range:
    for AS2 in AS2Range:
      fkdata=forward(AS1, AS2)
      fkdatas.append(fkdata)
      fkcoords.append(Coord(fkdata.X, fkdata.Z))
  return fkdatas, fkcoords

def inverse(X: np.float64, Z: np.float64) -> KinematicsData:

  def I1_XZ_to_L7(X: np.float64, Z: np.float64) -> np.float64:
    L7 = np.float64(sqrt(pow(X, 2) + pow(Z, 2)))
    logger.debug('%-20s: X=%f, Z=%f, L7=%f' % (funcname(), X, Z, L7))
    return L7

  def I2_L7_to_R17(L7: np.float64) -> np.float64:
    R17 = np.float64(acos((pow(L1, 2) + pow(L7, 2) - pow(L2, 2)) / (2 * L1 * L7)))
    logger.debug('%-20s: L1=%f, L7=%f, R17=%f [ %f° ]' % (funcname(), L1, L7, R17, degrees(R17)))
    return R17

  def I3_L7_to_R12(L7: np.float64) -> np.float64:
    T = np.float64((pow(L1, 2) + pow(L2, 2) - pow(L7, 2)) / (2 * L1 * L2))
    R12 = np.float64(acos(T))
    logger.debug('%-20s: L1=%f, L2=%f, L7=%f\n' \
    '                             T=%f, R12=%f [ %f° ]' 
    % (funcname(), L1, L2, L7, T, R12, degrees(R12)))
    return R12

  def I4_XZ_to_RX7(X: np.float64, Z: np.float64) -> np.float64:

    if X == 0:
      return pi/2

    K = Z/X
    if X >=0 and Z >=0:
      R7X = atan(K)
    elif X < 0 and Z >= 0:
      R7X = pi + atan(K)
    elif X < 0 and Z < 0:
      R7X = pi + atan(K)
    logger.debug('%-20s: X=%f, Z=%f, R7X=%f [ %f° ]' % (funcname(), X, Z, R7X, degrees(R7X)))
    return R7X

  def I5_R17R7X_to_RS1(R17: np.float64, R7X: np.float64) -> np.float64:
    RS1 = R7X - R17
    logger.debug('%-20s: R17=%f [ %f° ], R7X=%f [ %f° ]\n' \
    '                             RS1=%f [ %f° ]' 
    % (funcname(), R17, degrees(R17), R7X, degrees(R7X), RS1, degrees(RS1)))
    return RS1

  def I6_R12_to_R35(R12: np.float64) -> np.float64:
    R35 = pi - R12 - R15
    logger.debug('%-20s: R12=%f [ %f° ], R15=%f [ %f° ]\n' \
    '                             R35=%f [ %f° ]' 
    % (funcname(), R12, degrees(R12), R15, degrees(R15), R35, degrees(R35)))
    return R35

  def I7_R35_to_L6(R35: np.float64) -> np.float64:
    L6 = sqrt(pow(L3,2) + pow(L5,2) - 2*L3*L5*cos(R35))
    if L6 > L8 + L9:
      logger.error('%-20s: L6值异常 L6[%f] > L8 + L9[%f]' % (funcname(), L6, L8+L9))
      logger.error('%-20s: L3=%f, L5=%f, R35=%f [ %f° ], L6=%f' % (funcname(), L3, L5, R35, degrees(R35), L6))
    else:
      logger.debug('%-20s: L3=%f, L5=%f, R35=%f [ %f° ], L6=%f' % (funcname(), L3, L5, R35, degrees(R35), L6))
    return L6

  def I8_L6_to_RS2(L6: np.float64) -> np.float64:
    T = (pow(L6,2) + pow(L8,2) - pow(L9,2)) / (2*L6*L8)
    RS2 = acos(T)
    logger.debug('%-20s: L6=%f, L8=%f, T=%f, RS2=%f [ %f° ]' % (funcname(), L6, L8, T, RS2, degrees(RS2)))
    return RS2

  L7  = I1_XZ_to_L7(X, Z)
  R17 = I2_L7_to_R17(L7)
  R12 = I3_L7_to_R12(L7)
  R7X = I4_XZ_to_RX7(X, Z)
  RS1 = I5_R17R7X_to_RS1(R17, R7X)
  R35 = I6_R12_to_R35(R12)
  L6  = I7_R35_to_L6(R35)
  RS2 = I8_L6_to_RS2(L6)
  AS1 = degrees(RS1)
  AS2 = degrees(RS2)
  
  #计算膝盖坐标
  if RS1 < pi/2:
    KX = L1*cos(RS1)
    KZ = L1*sin(RS1)
  elif RS1 == pi/2:
    KX = 0
    KZ = L1
  else:
    KX = -L1*cos(RS1)
    KZ = L1*sin(RS1)

  data = KinematicsData(
    AS1=AS1, AS2=AS2,
    RS1=RS1, RS2=RS2,
    L6=L6, L7=L7,
    R12=R12, R13=pi-R12, R17=R17, R35=R35, R7X=R7X,
    X=X, Z=Z, KX=KX, KZ=KZ
  )
  return data

def inverseN(kdatas:list[KinematicsData]=None, kcoords:list[Coord]=None):
  if kdatas is None and kcoords is None:
    logger.error('No data to inverse')
    return None
  elif kdatas is not None and kcoords is not None:
    logger.error('Both data and coords to inverse')
    return None
  elif kdatas is not None:
    ikdatas = []
    for fkdata in kdatas:
      ikdata = inverse(fkdata.X, fkdata.Z)
      ikdatas.append(ikdata)
    logger.info('从kdatas逆解了 %d 个数据' % len(kdatas))
    return ikdatas
  elif kcoords is not None:
    ikdatas = []
    for fkcoord in kcoords:
      ikdata = inverse(fkcoord.X, fkcoord.Z)
      ikdatas.append(ikdata)
    logger.info('从kcoords逆解了 %d 个数据' % len(kcoords))
    return ikdatas
  else:
    logger.error('Invalid data to inverse')
    return None

class Kinematics:

  fkdatas = []
  fkcoords = []
  ikdatas = []
  ikcoords = []

  x_max : KinematicsData
  x_min : KinematicsData
  z_max : KinematicsData
  z_min : KinematicsData
  start : KinematicsData
  end   : KinematicsData

  def __init__(self, AS1Range, AS2Range):

    self.fkdatas, self.fkcoords = forwardN(AS1Range, AS2Range)
    self.ikdatas = inverseN(kdatas=self.fkdatas)
    self.ikcoords = inverseN(kcoords=self.fkcoords)
    logger.info('fk数据量: %d' % len(self.fkdatas))
    logger.info('ik数据量: %d' % len(self.ikdatas))

    self.x_max = max(self.fkdatas, key=lambda x: x.X)
    self.x_min = min(self.fkdatas, key=lambda x: x.X)
    self.z_max = max(self.fkdatas, key=lambda x: x.Z)
    self.z_min = min(self.fkdatas, key=lambda x: x.Z)
    self.start = self.fkdatas[0]
    self.end   = self.fkdatas[-1]

  def plot(self):
    plt.plot([coord.X for coord in self.fkcoords], [coord.Z for coord in self.fkcoords], 'b.', markersize=1)
    plt.plot(self.x_max.X, self.x_max.Z, 'ro', markersize=3)
    plt.text(self.x_max.X, self.x_max.Z, 'x_max', fontsize=12, color='black', ha='center', va='center')
    plt.plot(self.x_min.X, self.x_min.Z, 'ro', markersize=3)
    plt.text(self.x_min.X, self.x_min.Z, 'x_min', fontsize=12, color='black', ha='center', va='center')
    plt.plot(self.z_max.X, self.z_max.Z, 'ro', markersize=3)
    plt.text(self.z_max.X, self.z_max.Z, 'z_max', fontsize=12, color='black', ha='center', va='center')
    plt.plot(self.z_min.X, self.z_min.Z, 'ro', markersize=3)
    plt.text(self.z_min.X, self.z_min.Z, 'z_min', fontsize=12, color='black', ha='center', va='center')
    plt.plot(self.start.X, self.start.Z, 'ro', markersize=3)
    plt.text(self.start.X, self.start.Z, 'start', fontsize=12, color='black', ha='center', va='center')
    plt.plot(self.end.X, self.end.Z, 'ro', markersize=3)
    plt.text(self.end.X, self.end.Z, 'end', fontsize=12, color='black', ha='center', va='center')

f = open('./gait.txt', 'w')

class Gait:

  tag = None
  period = 0
  swingDuty = 0
  swingLength = 0
  swingHeight = 0
  frameCount = 0
  base = Coord()

  swingTime = 0
  t_values = []

  leftFrontCoords  = []
  leftBackCoords   = []
  rightFrontCoords = []
  rightBackCoords  = []

  leftFrontKinematicsDatas = []
  leftBackKinematicsDatas  = []
  rightFrontKinematicsDatas = []
  rightBackKinematicsDatas  = []

  pltObjToe       = None
  pltObjKnee      = None
  pltObjThigh     = None
  pltObjshanke    = None
  pltObjAnimation = None

  pltAnimationFranmeSkip = 20
  pltAnimationFranmeCount = 0

  def __init__(self, tag=None, period=1000, frameCount=1000, swingDuty=0.5, swingLength=35, swingHeight=35, base:Coord=Coord(0,110)):

    self.tag         = tag
    self.period      = period
    self.frameCount  = frameCount
    self.swingDuty   = swingDuty
    self.swingLength = swingLength
    self.swingHeight = swingHeight
    self.base        = base

    self.swingTime   = self.period * self.swingDuty
    self.t_values    = np.linspace(0, self.period, self.frameCount+1)
    print('t_values:', self.t_values)

  def coordMap(self, x:float, z:float) -> tuple[float, float]:
    x = -x
    z = -z
    x += self.base.X
    z += self.base.Z
    return Coord(x, z)

  def getGaitCoord(self, t:float) -> tuple[Coord, Coord]:
    
    if t <= self.swingTime:
      T = 2*pi* t / (self.swingTime)
      Kx = (T - sin(T)) / (2*pi)
      Kz = (1 - cos(T)) / 2
      x_swing   = self.swingLength * Kx
      x_support = (-self.swingLength) * Kx + self.swingLength
      z         = self.swingHeight * Kz
      #写入到日志文件
      f.write('SWING t:%f, st:%f, T=%f, Kx:%f, Kz:%f, x_swing:%f, x_support:%f, z:%f\n' % (t, self.swingTime, T, Kx, Kz, x_swing, x_support, z))
    elif t > self.swingTime and t <= self.period:
      T = 2*pi* (t - self.swingTime) / (self.swingTime)
      Kx = (T - sin(T)) / (2*pi)
      Kz = (1 - cos(T)) / 2
      x_swing   = (-self.swingLength) * Kx + self.swingLength
      x_support = self.swingLength * Kx
      z         = 0
      f.write('SUPPORT t:%f, st:%f, T=%f, Kx:%f, Kz:%f, x_swing:%f, x_support:%f, z:%f\n' % (t, self.swingTime, T, Kx, Kz, x_swing, x_support, z))
    
   
    swing:Coord = self.coordMap(x_swing, z)
    support:Coord = self.coordMap(x_support, z)

    # print('SWING >> t:%f, st:%f, x:%f, z:%f' % (t, self.swingTime, swing.X, swing.Z))
    # print('SUPPORT >> t:%f, st:%f, x:%f, z:%f' % (t, self.swingTime, support.X, support.Z))
    return swing, support
  
  def getLeftFrontCoord(self, t:float) -> tuple[Coord, Coord]:
    swing = self.getGaitCoord(t)[0]
    return swing
  
  def getLeftBackCoord(self, t:float) -> tuple[Coord, Coord]:
    support = self.getGaitCoord(t)[1]
    return support
  
  def getRightFrontCoord(self, t:float) -> tuple[Coord, Coord]:
    support = self.getGaitCoord(t)[1]
    return support
  
  def getRightBackCoord(self, t:float) -> tuple[Coord, Coord]:
    swing = self.getGaitCoord(t)[0]
    return swing
  
  def getOnePeriodCoords(self) -> tuple[list[Coord], list[Coord]]:
    for t in self.t_values:
      lfc = self.getLeftFrontCoord(t)
      lbc = self.getLeftBackCoord(t)
      rfc = self.getRightFrontCoord(t)
      rbc = self.getRightBackCoord(t)
      self.leftFrontCoords.append(lfc)
      self.leftBackCoords.append(lbc)
      self.rightFrontCoords.append(rfc)
      self.rightBackCoords.append(rbc)
    self.leftFrontKinematicsDatas  = inverseN(kcoords=self.leftFrontCoords)
    self.leftBackKinematicsDatas   = inverseN(kcoords=self.leftBackCoords)
    self.rightFrontKinematicsDatas = inverseN(kcoords=self.rightFrontCoords)
    self.rightBackKinematicsDatas  = inverseN(kcoords=self.rightBackCoords)
    logger.info('获取了一周期的坐标数据')

  def plotOnePeriod(self,leg='lf'):

    if self.leftFrontCoords == [] or self.leftBackCoords == [] \
      or self.rightFrontCoords == [] or self.rightBackCoords == []:
      self.getOnePeriodCoords()

    if leg == 'rf':
      coords = self.leftFrontCoords
      color = 'r.'
    elif leg == 'rb':
      coords = self.leftBackCoords
      color = 'g.'
    elif leg == 'lf':
      coords = self.rightFrontCoords
      color = 'r.'
    elif leg == 'lb':
      coords = self.rightBackCoords
      color = 'g.'
    else:
      logger.error('Invalid leg: %s' % leg)
      return None
    plt.plot([coord.X for coord in coords], [coord.Z for coord in coords], color, markersize=1)
    plt.text(coords[0].X, coords[0].Z, leg, fontsize=12, color='black', ha='center', va='center')

  def plotAnimationOnePeriod(self, leg='rf'):

    if self.leftFrontCoords == [] or self.leftBackCoords == [] \
      or self.rightFrontCoords == [] or self.rightBackCoords == []:
      self.getOnePeriodCoords()   

    self.pltAnimationFranmeCount = int(len(self.t_values) / self.pltAnimationFranmeSkip) + 1

    def init():
      pass

    def update(frame):

      index = frame * self.pltAnimationFranmeSkip

      #清除上次绘制的图形
      if self.pltObjToe is not None:
        self.pltObjToe[0].remove()
      if self.pltObjKnee is not None:
        self.pltObjKnee[0].remove()
      if self.pltObjThigh is not None:
        self.pltObjThigh[0].remove()
      if self.pltObjshanke is not None:
        self.pltObjshanke[0].remove()
      
      if leg == 'rf':
        kdatas = self.leftFrontKinematicsDatas
      elif leg == 'rb':
        kdatas = self.leftBackKinematicsDatas
      elif leg == 'lf':
        kdatas = self.rightFrontKinematicsDatas
      elif leg == 'lb':
        kdatas = self.rightBackKinematicsDatas
      else:
        logger.error('Invalid leg: %s' % leg)
        return None
      
      #绘制大腿
      self.pltObjThigh = plt.plot([0, kdatas[index].KX], [0, kdatas[index].KZ], 'black', linewidth=5)
      #绘制小腿
      self.pltObjshanke = plt.plot([kdatas[index].X, kdatas[index].KX], [kdatas[index].Z, kdatas[index].KZ], 'black', linewidth=5)
      #绘制脚尖
      self.pltObjToe = plt.plot(kdatas[index].X, kdatas[index].Z, 'go', markersize=10)
      #绘制膝盖
      self.pltObjKnee = plt.plot(kdatas[index].KX, kdatas[index].KZ, 'go', markersize=10)
      
    self.pltObjAnimation = FuncAnimation(
      plt.gcf(), func=update, frames=self.pltAnimationFranmeCount, init_func=init, interval=0, blit=False, repeat=True, cache_frame_data=False
    )

if __name__ == '__main__':
  #! 日志级别
  # logger.setLevel(logging.NOTSET)
  # logger.setLevel(logging.DEBUG)
  logger.setLevel(logging.INFO)
  # logger.setLevel(logging.WARNING)
  # logger.setLevel(logging.ERROR)
  # logger.setLevel(logging.CRITICAL)

  K = Kinematics( range(0, 181, 1), range(0, 121, 1))
  K.plot()
  walk = Gait(tag='walk',period=200,frameCount=1000,swingDuty=0.5,swingLength=40,swingHeight=45,base=Coord(20, 115))
  # walk.plotOnePeriod(leg='rf')
  # walk.plotOnePeriod(leg='rb')
  # walk.plotOnePeriod(leg='lf')
  # walk.plotOnePeriod(leg='lb')
  # walk.plotOnePeriod(leg='rf')
  walk.plotAnimationOnePeriod(leg='rf')

  plt.title('Quadruped Kinematics')
  plt.xlabel('X')
  plt.ylabel('Z')
  #设置刻度
  plt.xticks(np.arange( -150,150, 10))
  plt.yticks(np.arange( -70,140, 10))
  #设置网格
  plt.grid(True)
  #设置坐标轴范围
  plt.xlim(150, -150)
  plt.ylim(140, -70)
  #设置坐标轴比例
  plt.gca().set_aspect('equal', adjustable='box')
  #设置窗口最大化
  plt.get_current_fig_manager().window.showMaximized()
  #绘制XZ坐标系
  plt.axhline(0, color='black', lw=1)
  plt.axvline(0, color='black', lw=1)
  #绘制原点在最顶层
  plt.plot(0, 0, 'ro', markersize=10,zorder=5)
  
  plt.show()

f.close()

