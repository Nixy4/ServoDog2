from base import *
from forward import *

class Inverse:

  datas = []

  def I1_XZ_to_L7(self, X:float, Z:float) -> float:
    L7 = sqrt(pow(X,2) + pow(Z,2))
    logger.debug('%-20s: X=%f, Z=%f, L7=%f' % (funcname(), X, Z, L7))
    return L7
  
  def I2_L7_to_R17(self, L7:float) -> float:
    R17 = acos((pow(L1,2) + pow(L7,2) - pow(L2,2)) / (2*L1*L7))
    logger.debug('%-20s: L1=%f, L7=%f, R17=%f [ %f° ]' % (funcname(), L1, L7, R17, degrees(R17)))
    return R17

  def I3_L7_to_R12(self, L7:float) -> float:
    T = (pow(L1,2) + pow(L2,2) - pow(L7,2)) / (2*L1*L2)
    R12 = acos(T)
    logger.debug('%-20s: L1=%f, L2=%f, L7=%f\n' \
    '                             T=%f, R12=%f [ %f° ]' 
    % (funcname(), L1, L2, L7, T, R12, degrees(R12)))
    return R12

  def I4_XZ_to_RX7(self, X:float, Z:float) -> float:

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
  
  def I5_R17R7X_to_RS1(self, R17:float, R7X:float) -> float:
    RS1 = R7X - R17
    logger.debug('%-20s: R17=%f [ %f° ], R7X=%f [ %f° ]\n' \
    '                             RS1=%f [ %f° ]' 
    % (funcname(), R17, degrees(R17), R7X, degrees(R7X), RS1, degrees(RS1)))
    return RS1

  def I6_R12_to_R35(self,R12:float) -> float:
    R35 = pi - R12 - R15
    logger.debug('%-20s: R12=%f [ %f° ], R15=%f [ %f° ]\n' \
    '                             R35=%f [ %f° ]' 
    % (funcname(), R12, degrees(R12), R15, degrees(R15), R35, degrees(R35)))
    return R35

  def I7_R35_to_L6(self, R35:float) -> float:
    '''
    L6**2 = L3**2 + L5**2 - 2*L3*L5*cos(R35)
    L6 = sqrt(L3**2 + L5**2 - 2*L3*L5*cos(R35))
    '''
    L6 = sqrt(pow(L3,2) + pow(L5,2) - 2*L3*L5*cos(R35))
    if L6 > L8 + L9:
      logger.error('%-20s: L6值异常 L6[%f] > L8 + L9[%f]' % (funcname(), L6, L8+L9))
      logger.error('%-20s: L3=%f, L5=%f, R35=%f [ %f° ], L6=%f' % (funcname(), L3, L5, R35, degrees(R35), L6))
    else:
      logger.debug('%-20s: L3=%f, L5=%f, R35=%f [ %f° ], L6=%f' % (funcname(), L3, L5, R35, degrees(R35), L6))
    return L6

  def I8_L6_to_RS2(self, L6:float) -> float:
    T = (pow(L6,2) + pow(L8,2) - pow(L9,2)) / (2*L6*L8)
    RS2 = acos(T)
    logger.debug('%-20s: L6=%f, L8=%f, T=%f, RS2=%f [ %f° ]' % (funcname(), L6, L8, T, RS2, degrees(RS2)))
    return RS2

  def caculateFromXZ(self, X, Z):
    L7 = self.I1_XZ_to_L7(X, Z)
    R17 = self.I2_L7_to_R17(L7)
    R12 = self.I3_L7_to_R12(L7)
    R7X = self.I4_XZ_to_RX7(X, Z)
    RS1 = self.I5_R17R7X_to_RS1(R17, R7X)
    R35 = self.I6_R12_to_R35(R12)
    L6 = self.I7_R35_to_L6(R35)
    RS2 = self.I8_L6_to_RS2(L6)
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

  def caculateAllCoord(self, x_values, z_values):
    for x, z in zip(x_values, z_values):
      data = self.caculateFromXZ(x, z)
      self.datas.append(data)
    return self.datas
    
if __name__ == '__main__':

  #! 日志程序
  logger.setLevel(logging.NOTSET)
  logger.setLevel(logging.INFO)
  logger.setLevel(logging.DEBUG)

  #! 正解数据计算
  kf = Forward()
  kf.caculateAllAngle()

  #* 复制数据

  #! 逆解数据计算
  ki = Inverse()
  _x_min = ki.caculateFromXZ(kf.x_min.X, kf.x_min.Z)
  _x_max = ki.caculateFromXZ(kf.x_max.X, kf.x_max.Z)
  _z_min = ki.caculateFromXZ(kf.z_min.X, kf.z_min.Z)
  _z_max = ki.caculateFromXZ(kf.z_max.X, kf.z_max.Z)
  _start = ki.caculateFromXZ(kf.start.X, kf.start.Z)
  _end = ki.caculateFromXZ(kf.end.X, kf.end.Z)

  #! 正解逆解数据对比
  if kf.x_min == _x_min:
    logger.info('x_min 正解和逆解一致')
  else:
    logger.error('x_min 正解和逆解不一致')

  if kf.x_max == _x_max:
    logger.info('x_max 正解和逆解一致')
  else:
    logger.error('x_max 正解和逆解不一致')

  if kf.z_min == _z_min:
    logger.info('z_min 正解和逆解一致')
  else:
    logger.error('z_min 正解和逆解不一致')

  if kf.z_max == _z_max:
    logger.info('z_max 正解和逆解一致')
  else:
    logger.error('z_max 正解和逆解不一致')
    
  if kf.start == _start:
    logger.info('start 正解和逆解一致')
  else:
    logger.error('start 正解和逆解不一致')

  if kf.end == _end:
    logger.info('end 正解和逆解一致')
  else:
    logger.error('end 正解和逆解不一致')

  #测试f.datas所有值的逆解
  logger.info('测试kf.datas所有值的逆解')
  for data in kf.datas:
    _data = ki.caculateFromXZ(data.X, data.Z)
    if data != _data:
      logger.error('KinematicsData[%f,%f] 正解和逆解不一致' % (data.X, data.Z))
  logger.info('测试kf.datas所有值的逆解完成, 均在误差范围内')

  x0 = ki.caculateFromXZ( 0, 100)
  print(x0)