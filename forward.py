from base import *

class Forward:

  datas = []

  x_min = KinematicsData()
  x_max = KinematicsData()
  z_min = KinematicsData()
  z_max = KinematicsData()

  start = KinematicsData()
  end = KinematicsData()

  standard = KinematicsData()

  x_values = []
  z_values = []

  x0_values = []
  x0_values_z_min = KinematicsData()
  x0_values_z_max = KinematicsData()

  AS190_values = []

  knee_x_values = []
  knee_z_values = []
  
  def F1_RS2_to_L6(self,RS2):
    '''
    L9**2 = L6**2 + L8**2 - 2*L6*L8*cos(RS2)
    L6**2 - 2*L6*L8*cos(RS2) + L8**2 - L9**2 = 0
    '''
    _a = 1
    _b = -2*L8*cos(RS2)
    _c = pow(L8,2) - pow(L9,2)
    D = pow(_b,2) - 4*_a*_c
    if D < 0:
      logger.error('%-20s: L9:%f, L8:%f, RS2:%f [ %f° ], _a:%f, _b:%f, _c:%f, D:%f' % (funcname(), L9, L8, RS2, degrees(RS2), _a, _b, _c, D))
      return 0
    L6 = (-_b + sqrt(D)) / (2*_a)
    logger.debug('%-20s: RS2=%f, L6=%f' % (funcname(), RS2, L6))
    return L6
  
  def F2_L6_to_R35(self,L6):
    T = (pow(L3,2)+pow(L5,2)-pow(L6,2))/(2*L3*L5)
    R35 = acos(T)
    logger.debug('%-20s: L3=%f, L5=%f, L6=%f, T=%f, R35=%f [ %f° ]' % (funcname(), L3, L5, L6, T, R35, degrees(R35)))
    return R35
  
  def F3_R15R35_to_R13(self,R15,R35):
    R13 = R15+R35
    logger.debug('%-20s: R15=%f [ %f° ], R35=%f [ %f° ], R13=%f [ %f° ]' % (funcname(), R15, degrees(R15), R35, degrees(R35), R13, degrees(R13)))
    return R13

  def F4_R13_to_R12(self,R13):
    R12 = pi - R13
    logger.debug('%-20s: R13=%f [ %f° ], R12=%f [ %f° ]' % (funcname(), R13, degrees(R13), R12, degrees(R12)))
    return R12

  def F5_R12_to_L7(self,R12):
    L7 = sqrt(pow(L1,2) + pow(L2,2) - 2*L1*L2*cos(R12))
    logger.debug('%-20s: L1=%f, L2=%f, R12=%f [ %f° ], L7=%f' % (funcname(), L1, L2, R12, degrees(R12), L7))
    return L7
  
  def F6_L7_to_R17(self,L7):
    T = (pow(L1,2) + pow(L7,2) - pow(L2,2)) / (2*L1*L7)
    R17 = acos(T)
    logger.debug('%-20s: L1=%f, L7=%f, T=%f, R17=%f [ %f° ]' % (funcname(), L1, L7, T, R17, degrees(R17)))
    return R17
  
  def F7_RS1R17_to_R7X(self,RS1,R17):
    R7X = RS1 + R17
    logger.debug('%-20s: RS1=%f [ %f° ], R17=%f [ %f° ], R7X=%f [ %f° ]' % (funcname(), RS1, degrees(RS1), R17, degrees(R17), R7X, degrees(R7X)))
    return R7X

  def F8_L7R7X_to_xz(self,L7,R7X):
    X = L7*cos(R7X)
    Z = L7*sin(R7X)
    
    if R7X > pi/2:
      X = -X
    elif R7X > pi:
      X = -X
      Z = -Z

    logger.debug('%-20s: L7=%f, R7X=%f [ %f° ], X=%f, Z=%f' % (funcname(), L7, R7X, degrees(R7X), X, Z))
    return X,Z

  def caculateFromAngles(self, AS1, AS2):

    if AS2 > 120:
      logger.error('AS2 [ %f° ] > 120' % AS2)
      AS2 = 120

    RS1 = radians(AS1)
    RS2 = radians(AS2)

    L6  = self.F1_RS2_to_L6(RS2)
    R35 = self.F2_L6_to_R35(L6)
    R13 = self.F3_R15R35_to_R13(R15,R35)
    R12 = self.F4_R13_to_R12(R13)
    L7  = self.F5_R12_to_L7(R12)
    R17 = self.F6_L7_to_R17(L7)
    R7X = self.F7_RS1R17_to_R7X(RS1,R17)
    X,Z = self.F8_L7R7X_to_xz(L7,R7X)
    if RS1+R17>pi/2: X=-X

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
    
  def caculateAllAngle(self):
    for AS1 in range(0, 181, 1):
      for AS2 in range(0, 121, 1):
        data = self.caculateFromAngles(AS1, AS2)
        self.datas.append(data)
        self.x_values.append(data.X)
        self.z_values.append(data.Z)
        self.knee_x_values.append(data.KX)
        self.knee_z_values.append(data.KZ)
        if AS1 == 90:
          self.AS190_values.append(data)
    self.x_min = min(self.datas, key=lambda x: x.X)
    self.x_max = max(self.datas, key=lambda x: x.X)
    self.z_min = min(self.datas, key=lambda x: x.Z)
    self.z_max = max(self.datas, key=lambda x: x.Z)
    self.start = self.datas[0]
    self.end = self.datas[-1]
    
    #查找X接近0的点
    for data in self.datas:
      if abs(data.X) < 2:
        self.x0_values.append(data)
    if len(self.x0_values) > 0:
      self.x0_values_z_min = min(self.x0_values, key=lambda x: x.Z)
      self.x0_values_z_max = max(self.x0_values, key=lambda x: x.Z)
    
    logger.info('总数据量: %d\n' % (len(self.datas)) )
    logger.info('X最小点: \n%s' % (self.x_min) )
    logger.info('X最大点: \n%s' % (self.x_max) )
    logger.info('Z最小点: \n%s' % (self.z_min) )
    logger.info('Z最大点: \n%s' % (self.z_max) )
    logger.info('起始点: \n%s' % (self.start) )
    logger.info('结束点: \n%s' % (self.end) )
    logger.info('X接近0的点的数量: %d\n' % (len( self.x0_values )) )
    logger.info('X接近0时Z最小的点: \n%s' % (self.x0_values_z_max) )
    logger.info('X接近0时Z最大的点: \n%s' % (self.x0_values_z_max) )

  def plot(self):
    #* 窗口设置
    plt.title('Kinematics Forward')#设置标题
    mng = plt.get_current_fig_manager()#最大化窗口显示
    mng.window.showMaximized()

    #* 设置坐标轴刻度
    plt.gca().set_xticks(np.arange(-200, 200, 10))#设置x轴刻度
    plt.gca().set_yticks(np.arange(-200, 200, 10))#设置y轴刻度
    plt.gca().set_xticklabels(np.arange(-200, 200, 10), rotation=45)#设置x轴刻度标签
    plt.gca().set_yticklabels(np.arange(-200, 200, 10), rotation=45)#设置y轴刻度标签
    plt.gca().set_aspect('equal', adjustable='box')#设置坐标轴比例相等
    plt.gca().set_navigate(True)# 启用鼠标滚轮缩放

    #* 绘制坐标系
    plt.axis('equal')#设置坐标轴比例相等
    plt.grid()#显示网格
    # plt.xlim(self.x_min.X-10, self.x_max.X+10)#设置坐标轴范围
    # plt.ylim(self.z_min.Z-10, self.z_max.Z+10)#设置坐标轴范围
    plt.xlim(self.x_max.X + 10, self.x_min.X - 10)  # 反转 X 轴范围
    plt.ylim(self.z_max.Z + 10, self.z_min.Z - 10)  # 反转 Y 轴范围
    plt.plot(0, 0, 'go', markersize=5)#绘制原点
    plt.axhline(0, color='black', lw=1)#绘制水平坐标轴
    plt.axvline(0, color='black', lw=1)#绘制垂直坐标轴
    plt.xlabel('X')#设置x轴标签
    plt.ylabel('Z')#设置y轴标签

    #* 数据绘制
    #绘制 AS1(0~180°) AS2(0~120°) 在所有角度的足尖轨迹
    # plt.plot(self.x_values, self.z_values, 'b', linewidth=0.5)#绘制足尖轨迹
    #绘制 足尖坐标散点
    plt.plot(self.x_values, self.z_values, 'b.', markersize=1)
    #绘制x_max点
    plt.plot(self.x_max.X, self.x_max.Z, 'ro', markersize=5)
    plt.text(self.x_max.X, self.x_max.Z, 'x_max', fontsize=10, ha='left', va='bottom')
    #绘制x_min点
    plt.plot(self.x_min.X, self.x_min.Z, 'ro', markersize=5)
    plt.text(self.x_min.X, self.x_min.Z, 'x_min', fontsize=10, ha='left', va='bottom')
    #绘制z_max点
    plt.plot(self.z_max.X, self.z_max.Z, 'ro', markersize=5)
    plt.text(self.z_max.X, self.z_max.Z, 'z_max', fontsize=10, ha='right', va='top')
    #绘制z_min点
    plt.plot(self.z_min.X, self.z_min.Z, 'ro', markersize=5)
    plt.text(self.z_min.X, self.z_min.Z, 'z_min', fontsize=10, ha='right', va='bottom')
    #绘制start点
    plt.plot(self.start.X, self.start.Z, 'ro', markersize=5)
    plt.text(self.start.X, self.start.Z, 'start', fontsize=10, ha='right', va='bottom')
    #绘制end点
    plt.plot(self.end.X, self.end.Z, 'ro', markersize=5)
    plt.text(self.end.X, self.end.Z, 'end', fontsize=10, ha='left', va='bottom')
    #绘制所有x接近0的点
    for data in self.x0_values:
      plt.plot(data.X, data.Z, 'r.', markersize=1)
    #绘制AS190点
    for data in self.AS190_values:
      plt.plot(data.X, data.Z, 'r.', markersize=1)
      
if __name__ == '__main__':
  #! 日志程序
  # logger.setLevel(logging.NOTSET)
  logger.setLevel(logging.INFO)
  # logger.setLevel(logging.DEBUG)
  #! 数据计算
  f = Forward()
  f.caculateAllAngle()
  #! Plot
  f.plot()
  plt.show()