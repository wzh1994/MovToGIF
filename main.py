from tkinter import *
from tkinter import ttk
import cv2
from PIL import ImageTk, Image
from itertools import count

root = Tk()
root.title("GIF表情制作器 - powered by Wang Zhihong")

class MyCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        Widget.bind(self, "<Button-1>", self.mouseDown)
        Widget.bind(self, "<ButtonRelease-1>", self.mouseUp)
        Widget.bind(self, "<B1-Motion>", self.mouseMove)
        self.height = kwargs.get('height', 300)
        self.width = kwargs.get('width', 300)
        self.l, self.r = IntVar(), IntVar()       
        self.curr = 0

    def mouseDown(self, event):
        self.startx = event.x
        self.starty = event.y

    def mouseUp(self, event):
        self.endx = event.x
        self.endy = event.y

    def mouseMove(self, event):
        if hasattr(self, 'rec'):
            self.delete(self.rec)
        self.rec = self.create_rectangle(self.startx, self.starty, event.x, event.y)

    def plotCv2Mov(self):
        if hasattr(self, "plot_img"):
            self.delete(self.plot_img)
        self.img = ImageTk.PhotoImage(image=Image.fromarray(self.cv2_imgs[self.curr + self.l.get()]))
        self.plot_img = self.create_image(int(self.width / 2), int(self.height / 2), image=self.img)

    def readMov(self, path):
        self.cv2_mov = cv2.VideoCapture(path)
        self.cv2_imgs = []
        while True:
            frame, img = self.cv2_mov.read()
            if frame == False:
                break
            else:
                self.cv2_imgs.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        self.l.set(0)
        self.r.set(len(self.cv2_imgs) - 1)
        height, width = self.cv2_imgs[0].shape[0], self.cv2_imgs[0].shape[1]
        if height > self.height or width > self.width:
            scale = max(height / self.height, width / self.width)	
            self.cv2_imgs = [cv2.resize(img, [int(width / scale), int(height / scale)]) for img in self.cv2_imgs]
        self.plotCv2Mov()

    def resizeMov(self):
        if not hasattr(self, 'endx'):
            return
        self.delete(self.rec)
        top = int((self.height - self.cv2_imgs[0].shape[0]) / 2)
        left = int((self.width - self.cv2_imgs[0].shape[1]) / 2)
        t, d = max(self.starty - top, 0), min(self.endy - top, self.cv2_imgs[0].shape[0])
        l, r = max(self.startx - left, 0), min(self.endx - left, self.cv2_imgs[0].shape[1])
        self.cv2_imgs = [img[t:d, l:r, :] for img in self.cv2_imgs]
        self.plotCv2Mov()

    def toGIF(self):
        import imageio
        imageio.mimsave('test.gif', self.cv2_imgs[self.l.get() : self.r.get()], fps=20)

class MyProcessbar(object):
    def __init__(self, c, frm, idx):
        self.canvas = c
        self.lButton = ttk.Button(frm, text="左截取", command=self.setLeft)
        self.lLabel = ttk.Label(frm, textvariable=c.l)
        self.bar = ttk.Progressbar(frm, length=300, maximum=c.r.get())
        self.rLabel = ttk.Label(frm, textvariable=c.r)
        self.rButton = ttk.Button(frm, text="右截取", command=self.setRight)

        self.lButton.grid(row=0, column=next(idx))
        self.lLabel.grid(row=0, column=next(idx))
        self.bar.grid(row=0, column=next(idx))
        self.rLabel.grid(row=0, column=next(idx))
        self.rButton.grid(row=0, column=next(idx))

        self.bar.bind("<Button-1>", self.mouseDown)

    def mouseDown(self, event):
        value = int(event.x / 300 * self.bar['maximum'])
        self.bar['value'] = value
        self.canvas.curr = value
        self.canvas.plotCv2Mov()

    def setLeft(self):
        self.canvas.l.set(self.canvas.l.get() + self.bar['value'])
        self.bar['maximum'] -= self.bar['value']
        self.bar['value'] = self.canvas.curr = 0
        self.canvas.plotCv2Mov()

    def setRight(self):
        self.canvas.r.set(self.canvas.l.get() + self.bar['value'])
        self.bar['maximum'] = self.bar['value']
        self.canvas.plotCv2Mov()

    def play(self):
        for i, self.canvas.curr in enumerate(range(self.canvas.l.get(), self.canvas.r.get())):
            self.bar['value'] = i
            self.canvas.plotCv2Mov()
            global root       
            root.update()

def getFrames(n):
    frames = tuple(ttk.Frame(root, padding=10) for i in range(n))
    for frame in frames:
        frame.grid()
    return frames

frm1, frm2, frm3 = getFrames(3)
ttk.Label(frm1, text="欢迎使用本工具，请读取一个视频").grid(column=0, row=0)
ttk.Button(frm1, text="读取视频", command=root.destroy).grid(column=1, row=0)


# frame2: canvas, show current picture of given video
c = MyCanvas(frm2, height=500, width=800)
c.grid(row=1, column=0)
c.readMov("test.mov")

# frame3: processbar, change current picture
idx = count()
bar = MyProcessbar(c, frm3, idx)
ttk.Button(frm3, text="剪裁", command=c.resizeMov).grid(row=0, column=next(idx))
ttk.Button(frm3, text="播放", command=bar.play).grid(row=0, column=next(idx))
ttk.Button(frm3, text="存为gif", command=c.toGIF).grid(row=0, column=next(idx))

root.mainloop()