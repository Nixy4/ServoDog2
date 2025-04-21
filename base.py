from math import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from typing import overload
import inspect
import logging
import colorlog
from termcolor import colored

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

if __name__ == '__main__':

  logger.setLevel(logging.DEBUG)

  logger.info('已知常量')
  logger.info('%5s | %20.10f'%('L1', L1))
  logger.info('%5s | %20.10f'%('_L1', _L1))
  logger.info('%5s | %20.10f'%('L1_', L1_))
  logger.info('%5s | %20.10f'%('L2', L2))
  logger.info('%5s | %20.10f'%('L3', L3))
  logger.info('%5s | %20.10f'%('L4', L4))
  logger.info('%5s | %20.10f'%('L5', L5))
  logger.info('%5s | %20.10f'%('L8', L8))
  logger.info('%5s | %20.10f'%('L9', L9))
  logger.info('%5s | %20.10f | %20.10f°'%('R14', R14, degrees(R14)))
  logger.info('%5s | %20.10f | %20.10f°'%('R15', R15, degrees(R15)))

  # KinematicsData.__eq__测试
  data0 = KinematicsData(
    AS1=1.0, AS2=2.0, 
    RS1=3.0, RS2=4.0, 
    L6=5.0, L7=6.0, 
    R12=7.0, R13=8.0, R17=9.0, R35=10.0, R7X=11.0, 
    X=12.0, Z=13.0)
  
  data1 = KinematicsData(
    AS1=1.0, AS2=2.0, 
    RS1=3.0, RS2=4.0, 
    L6=5.0, L7=6.0, 
    R12=7.0, R13=8.0, R17=9.0, R35=10.0, R7X=11.0, 
    X=12.0, Z=13.0)
  
  deta2 = KinematicsData(
    AS1=3.0, AS2=3.0, 
    RS1=3.0, RS2=4.0, 
    L6=5.0, L7=6.0, 
    R12=5.0, R13=8.0, R17=9.0, R35=10.0, R7X=11.0, 
    X=12.0, Z=13.1)

  data0.__eq__(data1)
  data0.__eq__(deta2)