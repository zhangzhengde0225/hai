
import cv2
from copy import deepcopy
import time

class ImageProcessor:
    def __init__(self):
        self.points = []
        self.rect = None
        self.img = None

    def on_mouse(self, event, x, y, flags, param):
        """param即图片"""
        # 检查是否是左键点击事件
        if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
            if len(self.points) >= 2:
                print(f'{len(self.points)} pionts already, not added.')
                return
            print(f'add point: {x}, {y}')
            self.points.append((x, y))
            self.repaint()
        # elif event == cv2.EVENT_RBUTTONDOWN:  # 右键点击，但是会带自动的右键菜单
        #     # 阻止cv2自带的右键菜单
        #     print(f'delete last point: {x}, {y}')
        #     self.points.pop()  # 删除最后一个点
        #     self.repaint()
        elif event == cv2.EVENT_MOUSEMOVE:  # 鼠标移动
            if len(self.points) == 1:
                x1, y1 = self.points[0]
                print(f'show rect: {x1}, {y1}, {x}, {y}')
                self.rect = (x1, y1, x, y)
                self.repaint()
            print(f'mouse move: {x}, {y}. points: {self.points}')
            
    def repaint(self, **kwargs):
        rimg = deepcopy(self.img)
        for point in self.points:
            x, y = point
            rimg = cv2.circle(rimg, (x, y), 3, (0, 0, 255), -1)
        if self.rect:
            rimg = cv2.rectangle(rimg, (self.rect[0], self.rect[1]), (self.rect[2], self.rect[3]), (0, 0, 255), 2)
        cv2.imshow('image', rimg)
    
    def reset(self):
        self.points = []
        self.rect = None
        self.img = None

    def roi_by_mouse(self, img_path):
        # img = cv2.imread(img_path)
        self.img = cv2.imread(img_path)
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.on_mouse, self.img)
        cv2.imshow("image", self.img)
        # cv2.waitKey(0)
        while True:
            if cv2.getWindowProperty('image', cv2.WND_PROP_VISIBLE) < 1:  # 按关闭按钮退出
                break
            key = cv2.waitKey(20) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('y') or key == ord(' '):
                print("You confirmed!")
                break
            elif key == ord('n'):
                print("You cancelled!")
                self.reset()
                break
            elif key == 27:  # esc取消
                print('esc pressed')
                # 删除最后一个点
                if len(self.points) == 2:
                    self.points = []
                    self.rect = None
                elif len(self.points) > 0:
                    self.points.pop()
                print(f'points: {self.points} self.rect: {self.rect}')
                self.rect = None
                self.img = cv2.imread(img_path)
                self.repaint()
                continue
        points = deepcopy(self.points)
        self.points = []
        cv2.destroyAllWindows()
        # print(self.points)
        if len(points) != 2:
            return None
        return points

if __name__ == '__main__':
    processor = ImageProcessor()
    points = processor.roi_by_mouse('image.png')
    print(points)
