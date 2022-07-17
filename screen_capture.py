import cv2
import numpy
import win32api, win32ui, win32gui, win32con


class ScreenCapture():
    
    def __init__(self, name="Window", top=0, left=0, width=640, height=480, window=None, monitor=None, border=True, d3d=None):
        
        self.hwnd = None
        self.name, self.top, self.left, self.width, self.height = name, top, left, width, height

        if window is not None:
            
            self.hwnd = win32gui.FindWindow(None, window)
            
            if not self.hwnd:
                raise Exception(f"Window: {window} not found.")

            window_rect = win32gui.GetWindowRect(self.hwnd)
            client_rect = win32gui.GetClientRect(self.hwnd)
            self.border_width = (window_rect[2] - window_rect[0]) - client_rect[2]
            self.border_height = (window_rect[3] - window_rect[1]) - client_rect[3]
            self.width = window_rect[2] - window_rect[0]
            self.height = window_rect[3] - window_rect[1]

            if border:

                if d3d:
                    self.left = window_rect[0]
                    self.top = window_rect[1]
                else:
                    self.left = -(self.border_width // 2)
                    self.top = -(self.border_height - self.border_width // 2)

            else:

                if d3d:
                    self.left = window_rect[0] + (self.border_width // 2)
                    self.top = window_rect[1] + (self.border_height - self.border_width // 2)

                self.width -= self.border_width
                self.height -= self.border_height

        if monitor is not None:

            try:
                get_monitors = win32api.EnumDisplayMonitors(None, None)
                monitor_left, monitor_top, monitor_right, monitor_bottom = get_monitors[monitor][2]
                self.top = monitor_top
                self.left = monitor_left
                self.width = (monitor_right - monitor_left)
                self.height = (monitor_bottom - monitor_top)
            except:
                raise Exception(f"Display {monitor} not found.")

        if d3d:
            self.hwnd = None

        self.hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(self.hwnd))
        self.cdc = self.hdc.CreateCompatibleDC()
        self.hbit = win32ui.CreateBitmap()
        self.hbit.CreateCompatibleBitmap(self.hdc, self.width, self.height)

    def __del__(self):
        
        cv2.destroyAllWindows()

        if hasattr(self, "hdc"):
            self.hdc.DeleteDC()

        if hasattr(self, "cdc"):
            self.cdc.DeleteDC()

        if hasattr(self, "hbit"):
            win32gui.DeleteObject(self.hbit.GetHandle())

    def read(self, color=True):
        
        self.cdc.SelectObject(self.hbit)
        self.cdc.BitBlt((0, 0), (self.width, self.height), self.hdc, (self.left, self.top), win32con.SRCCOPY)
        signedIntsArray = self.hbit.GetBitmapBits(True)
        image = numpy.frombuffer(signedIntsArray, dtype="uint8")
        image.shape = (self.height, self.width, 4)

        if not color:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

        return image


def list_monitors():

    for k, v in enumerate(win32api.EnumDisplayMonitors(None, None)):
        print( f"{k}: " + str(win32api.GetMonitorInfo(v[0])) )


def main():

    cap = ScreenCapture()

    while True:

        frame = cap.read()

        cv2.imshow(cap.name, frame)

        key = cv2.pollKey()
        if key == ord("q"):
            break

        if not cv2.getWindowProperty(cap.name, cv2.WND_PROP_VISIBLE):
            break


if __name__ == "__main__":
    main()
