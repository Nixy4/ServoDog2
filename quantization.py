from base import *
from forward import *
from inverse import *

# 设置日志级别
logger.setLevel(logging.NOTSET)

# 正解
f = Forward()
f.caculateAllAngle()

def forward_data_to_c_code():
  # 生成 forward_data.h 文件
  with open ('D:/Python/ServoDog2/cfile/forward.h','w') as hfile:
    hfile.write('#ifndef FORWARD_H\n')
    hfile.write('#define FORWARD_H\n')
    hfile.write('\n')
    hfile.write('typedef struct {\n')
    hfile.write('\tdouble x;\n')
    hfile.write('\tdouble z;\n')
    hfile.write('} forward_data_t;\n')
    hfile.write('\n')
    hfile.write('extern const forward_data_t forward_data[181][121];\n')
    hfile.write('\n')
    hfile.write('#endif // FORWARD_H\n')
    hfile.write('\n')
  # 生成 forward_data.c 文件
  with open ('D:/Python/ServoDog2/cfile/forward_datas.c','w') as cfile:
    cfile.write('#include "forward.h"\n')
    cfile.write('\n')
    cfile.write('const forward_data_t forward_data[181][121] = {\n')
    for i in range(0,181,1):
      cfile.write('\t{ //AS1 = %d\n'% i)
      for j in range(0,121,1):
          cfile.write('\t\t{%f,%f}, //AS2 = %d\n' % (f.x_values[i*121+j], f.z_values[i*121+j], j))
      cfile.write('\t},\n')
    cfile.write('};\n')
    cfile.write('\n')

def forward_x_values_to_c_code():
  with open ('D:/Python/ServoDog2/cfile/forward_x_values.c','w') as cfile:
    cfile.write('const int forward_x_values[181][121] = {\n')
    for i in range(0,181,1):
      cfile.write('\t{ //AS1 = %d\n'% i)
      for j in range(0,121,1):
        cfile.write('\t\t%d, //AS2 = %d\n' % (f.x_values[i*121+j], j))
      cfile.write('\t},\n')
    cfile.write('};\n')
    cfile.write('\n')

def forward_z_values_to_c_code():
  with open ('D:/Python/ServoDog2/cfile/forward_z_values.c','w') as cfile:
    cfile.write('const int forward_z_values[181][121] = {\n')
    for i in range(0,181,1):
      cfile.write('\t{ //AS1 = %d\n'% i)
      for j in range(0,121,1):
        cfile.write('\t\t%d, //AS2 = %d\n' % (f.z_values[i*121+j], j))
      cfile.write('\t},\n')
    cfile.write('};\n')
    cfile.write('\n')

forward_data_to_c_code()
forward_x_values_to_c_code()
forward_z_values_to_c_code()