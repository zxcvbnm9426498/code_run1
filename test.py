import matplotlib.pyplot as plt
import numpy as np

# 创建数据
x = np.linspace(0, 2 * np.pi, 400)
y = np.sin(x ** 2)

# 创建图形
plt.figure()
plt.plot(x, y)
plt.show()

import tkinter as tk

# 创建主窗口
root = tk.Tk()

# 创建一个Canvas，设置其背景色为白色，尺寸为400x400
canvas = tk.Canvas(root, width=400, height=400, bg='white')
canvas.pack()

# 在Canvas上绘制一个红色的矩形（位置为(50, 50)到(150, 150)）
canvas.create_rectangle(50, 50, 150, 150, fill="red")

# 在Canvas上绘制一条蓝色的线（从(20, 20)到(300, 300)）
canvas.create_line(20, 20, 300, 300, fill="blue", width=2)

# 运行事件循环
root.mainloop()