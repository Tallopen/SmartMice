# -*- coding: utf-8 -*-
# created at: 2022/11/28 10:13
# author    : Gao Kai
# Email     : gaosimin1@163.com

import matplotlib

import matplotlib.pyplot as plt
import numpy as np
import serial
import time
matplotlib.use('TkAgg')

ball_data = np.zeros((202, 7))
s = serial.Serial("COM5", 115200)

if s.isOpen():
    begin_time = time.time()

    for data_id in range(202):
        try:
            _l = s.readline()[:-2].decode(encoding="utf8")
            xy_raw = _l.split(",")
            ball_data[data_id, 0] = time.time() - begin_time

            ball_data[data_id, 1] = int(xy_raw[0])
            ball_data[data_id, 2] = int(xy_raw[1])

            if data_id >= 2:
                ball_data[data_id, 3] = 0.0095*ball_data[data_id, 1] + 0.019*ball_data[data_id-1, 1] + 0.095*ball_data[data_id-2, 1] + 1.71*ball_data[data_id-1, 3] - 0.744*ball_data[data_id-2, 3]
                ball_data[data_id, 4] = 0.64*ball_data[data_id, 2] + 1.28*ball_data[data_id-1, 2] + 0.64*ball_data[data_id-2, 2] + 1.143*ball_data[data_id-1, 4] - 0.413*ball_data[data_id-2, 4]

                ball_data[data_id, 5] = ball_data[data_id, 3] + ball_data[data_id-1, 5]
                ball_data[data_id, 6] = ball_data[data_id, 4] + ball_data[data_id-1, 6]
            time.sleep(0.01)
        except:
            print("fuck")
            continue

    s.close()

    plt.plot(ball_data[:, 0], ball_data[:, 1])
    plt.plot(ball_data[:, 0], ball_data[:, 3])
    plt.show()

else:

    print("serial error")
