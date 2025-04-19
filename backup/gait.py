from base import *
from forward import *
from inverse import *

class Gait:

  forward = Forward()
  inverse = Inverse()

  period = 0
  dutyFactorOfSwing = 0
  lengthOfStep = 0
  hightOfStep = 0

  x_base = 1
  z_base = 110

  datas = []
  x_vales = []
  z_vales = []

  def __init__(self, period=1000, dutyFactorOfSwing=0.5, lengthOfStep=30, hightOfStep=30):
    self.period = period
    self.dutyFactorOfSwing = dutyFactorOfSwing
    self.lengthOfStep = lengthOfStep
    self.hightOfStep = hightOfStep
    self.forward.caculateAllAngle()
    self.inverse.caculateAllAngle()

  def phaseOfSwing(self, x_start, x_end, t , period, dutyFactorOfSwing ):
    sigma = 2*pi*t / (period*dutyFactorOfSwing) 
    x_expect = (x_end-x_start) * ( (sigma-sin(sigma)) / (2*pi) ) + x_start
    z_expect = self.hightOfStep * (1-cos(sigma)) / 2
    return x_expect, z_expect
  
  def phaseOfSupport(self, x_start, x_end, t , period, dutyFactorOfSwing ):
    sigma = 2*pi*(t-self.period*self.dutyFactorOfSwing) / (period*dutyFactorOfSwing)
    x_expect = (x_start-x_end) * ( (sigma-sin(sigma)) / (2*pi) ) + x_end
    z_expect = 0
    return x_expect, z_expect

  def coordMap(self, x, z):
    return -x, -z
  
  def caculate(self):
    t_values = np.linspace(0, self.period, 1001)
    x_start = 0
    x_end = self.lengthOfStep

    for t in t_values:
      if t <= self.period * self.dutyFactorOfSwing:
        x_expect, z_expect = self.phaseOfSwing(x_start, x_end, t, self.period, self.dutyFactorOfSwing)
      elif t > self.period * self.dutyFactorOfSwing and t <= self.period:
        x_expect, z_expect = self.phaseOfSupport(x_start, x_end, t, self.period, self.dutyFactorOfSwing)
      x_expect, z_expect = self.coordMap(x_expect, z_expect)
      x_expect += self.x_base
      z_expect += self.z_base
      logger.info('x_expect: %f, z_expect: %f' % (x_expect, z_expect))
      data = self.inverse.caculateFromXZ(x_expect, z_expect)
      self.datas.append(data)
      self.x_vales.append(x_expect)
      self.z_vales.append(z_expect)
   
  def plot(self):
    plt.plot(self.x_vales, self.z_vales, label='Gait', color='red', lw=2)
    plt.xlabel('X')
    plt.ylabel('Z')
    plt.title('Gait')
    plt.legend()
    plt.grid()
    plt.axis('equal')
    plt.axhline(0, color='black', lw=1)
    plt.axvline(0, color='black', lw=1)
    plt.plot(0, 0, 'go', markersize=5)

  def plot_anim(self):
    #在原图上绘制动画
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_aspect('equal')
    ax.axhline(0, color='black', lw=1)
    ax.axvline(0, color='black', lw=1)
    ax.plot(0, 0, 'go', markersize=5)
    line, = ax.plot([], [], 'r-', lw=2)
    def init():
      line.set_data([], [])
      return line,
    def animate(i):
      x = self.x_vales[i]
      z = self.z_vales[i]
      line.set_data(x, z)
      return line,
    ani = anim.FuncAnimation(fig, animate, frames=len(self.datas), init_func=init, blit=True, interval=50)

if __name__ == "__main__":
  # logger.setLevel(logging.NOTSET)
  logger.setLevel(logging.INFO)
  # logger.setLevel(logging.DEBUG)
  g = Gait(period=1000, dutyFactorOfSwing=0.5, lengthOfStep=40, hightOfStep=30)
  g.forward.caculateAllAngle()
  # g.forward.plot()
  g.caculate()
  g.plot()
  g.plot_anim()
  plt.show()
