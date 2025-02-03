import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
KEYEVENTF_EXTENDEDKEY = 0x1
KEYEVENTF_KEYUP = 0x2
VK_CAPITAL = 0x14
CAPSLOCK_SCANCODE = 0x45

user32.GetKeyState.restype = wintypes.SHORT
user32.GetKeyState.argtypes = [wintypes.INT]

user32.keybd_event.argtypes = [
    wintypes.BYTE,
    wintypes.BYTE,
    wintypes.DWORD,
    wintypes.ULONG,
]
user32.keybd_event.restype = None


def get_capslock_state():
    return bool(user32.GetKeyState(VK_CAPITAL) & 1)


def toggle_capslock():
    user32.keybd_event(VK_CAPITAL, CAPSLOCK_SCANCODE, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(
        VK_CAPITAL, CAPSLOCK_SCANCODE, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0
    )


print(get_capslock_state())
toggle_capslock()
