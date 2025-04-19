from base import *
from forward import *
from inverse import *
from matplotlib.animation import FuncAnimation

#! 日志程序
# logger.setLevel(logging.NOTSET)
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)

#! 数据计算
kf = Forward()
kf.caculateAllAngle()
ki = Inverse()
ki.caculateAllCoord(kf.x_values, kf.z_values)

class Gait:

  tag = None
  period = 0
  swingDuty = 0
  swingLength = 0
  swingHeight = 0
  swingTime = 0
  frameCount = 0
  x_base = 0
  z_base = 0

  x_values = []
  z_values = []
  knee_x_values = []
  knee_z_values = []

  t_values = []

  kdatas = []

  pltAnimationFrame    = None
  pltAnimationToeObj   = None
  pltAnimationKneeObj  = None
  pltAnimationThighObj = None
  pltAnimationShankObj = None
  
  def __init__(self, tag:str=None, period=1000, swingDuty=0.5, swingLength=30, swingHeight=30, frameCount=1000, x_base=0, z_base=0):
    self.tag = tag
    self.period = period
    self.swingDuty = swingDuty
    self.swingLength = swingLength
    self.swingHeight = swingHeight
    self.swingTime = period * swingDuty
    self.supportTime = period * (1-swingDuty)
    self.frameCount = frameCount
    self.x_base = x_base
    self.z_base = z_base
    self.t_values = np.linspace(0, self.period, self.frameCount)

    self.caculateOnePeriod()

    logger.info('t_values length: %d' % len(self.t_values))

  def swingPhase(self, t):
    T = 2*pi* t / (self.swingTime)
    x = (self.swingLength * (T - sin(T))) / (2*pi)
    z = self.swingHeight * (1 - cos(T)) / 2
    return x, z
  
  def supportPhase(self, t):
    T = 2*pi* (t - self.swingTime) / (self.supportTime)
    x = (-self.swingLength * (T - sin(T))) / (2*pi) + self.swingLength
    z = 0
    return x, z

  def coordMap(self, x, z):
    return -x, -z
  
  def caculateOnePeriod(self):
    for t in self.t_values:
      logger.debug('t: %f' % t)
      if t <= self.swingTime:
        x, z = self.swingPhase(t)
      elif t > self.swingTime and t <= self.period:
        x, z = self.supportPhase(t)
      x, z = self.coordMap(x, z)
      x += self.x_base
      z += self.z_base 
      self.x_values.append(x)
      self.z_values.append(z)
      kdata = ki.caculateFromXZ(x, z)
      self.knee_x_values.append(kdata.KX)
      self.knee_z_values.append(kdata.KZ)
      self.kdatas.append(kdata)
    return self.kdatas

  def plotOnePeriod(self):
    #绘制一个周期的步态
    plt.plot(self.x_values, self.z_values, 'g')
    plt.title(self.tag)

  '''动画函数'''
  def plotAnimation(self):

    kf.plot()
  
    self.pltAnimationFrame = int(len(self.t_values)/20)

    '''动画初始化函数'''
    def animInit():
      pass

    '''动画更新函数'''
    def animUpdate(frame):

      #清除上一帧
      if self.pltAnimationToeObj is not None:
        self.pltAnimationToeObj[0].remove()
      if self.pltAnimationKneeObj is not None:
        self.pltAnimationKneeObj[0].remove()
      if self.pltAnimationThighObj is not None:
        self.pltAnimationThighObj[0].remove()
      if self.pltAnimationShankObj is not None:
        self.pltAnimationShankObj[0].remove()

      #绘制当前帧
      self.pltAnimationThighObj = plt.plot([0, self.kdatas[frame*20].KX], [0, self.kdatas[frame*20].KZ], 'black', linewidth=5)
      self.pltAnimationShankObj = plt.plot([self.kdatas[frame*20].KX, self.x_values[frame*20]], [self.kdatas[frame*20].KZ, self.z_values[frame*20]], 'black', linewidth=5)
      self.pltAnimationToeObj = plt.plot(self.x_values[frame*20], self.z_values[frame*20], 'go', markersize=10)
      self.pltAnimationKneeObj = plt.plot(self.kdatas[frame*20].KX, self.kdatas[frame*20].KZ, 'go', markersize=10)

    #创建动画
    self.pltAnimationObj = FuncAnimation(
      fig       = plt.gcf(),          #figure对象
      func      = animUpdate,         #动画更新函数
      frames    = self.pltAnimationFrame,
      init_func = animInit,           #动画初始化函数
      interval  = 0
      )

if __name__ == '__main__':

  walk = Gait(
    tag='walk', 
    period=1000, swingDuty=0.5, swingLength=40, swingHeight=40, frameCount=1000, 
    x_base=0, z_base=110
    )

  #! 日志程序
  logger.setLevel(logging.NOTSET)
  # logger.setLevel(logging.INFO)
  # logger.setLevel(logging.DEBUG)

  #! 步态数据计算
  walk.caculateOnePeriod()
  walk.plotAnimation()

  plt.show()