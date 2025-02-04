import Quartz
import time
import asyncio

class CapslockSync:
    def __init__(self):
        self.local_state = False

    def get_capslock_state(self):
        try:
            current = Quartz.CoreGraphics.CGEventSourceKeyState(
                Quartz.CoreGraphics.kCGEventSourceStateHIDSystemState,
                0x39
            )
            return bool(current)
        except Exception as e:
            print(f"Error getting caps lock state: {e}")
            return False

    async def set_capslock_state(self, enabled):
        try:
            current_state = self.get_capslock_state()
            if current_state != enabled:
                event = Quartz.CoreGraphics.CGEventCreateKeyboardEvent(None, 0x39, True)
                Quartz.CoreGraphics.CGEventPost(
                    Quartz.CoreGraphics.kCGHIDEventTap, 
                    event
                )
                time.sleep(0.1)
                event = Quartz.CoreGraphics.CGEventCreateKeyboardEvent(None, 0x39, False)
                Quartz.CoreGraphics.CGEventPost(
                    Quartz.CoreGraphics.kCGHIDEventTap, 
                    event
                )
                # Verify the change
                new_state = self.get_capslock_state()
                if new_state != enabled:
                    print("Warning: Failed to set caps lock state")
        except Exception as e:
            print(f"Error setting caps lock state: {e}")
            raise

import subprocess

def get_capslock_state():
    script = '''
    ObjC.import("IOKit")
    ObjC.import("CoreServices")
    (() => {
        var ioConnect = Ref();
        var state = Ref();
        $.IOServiceOpen(
            $.IOServiceGetMatchingService(
                $.kIOMasterPortDefault,
                $.IOServiceMatching($.kIOHIDSystemClass)
            ),
            $.mach_task_self_,
            $.kIOHIDParamConnectType,
            ioConnect
        );
        $.IOHIDGetModifierLockState(ioConnect, $.kIOHIDCapsLockState, state);
        console.log(state[0]);  // Let's debug what we're getting
        return Boolean(state[0]);
    })();
    '''
    result = subprocess.run(['osascript', '-l', 'JavaScript', '-e', script], 
                          capture_output=True, text=True)
    print(f"Raw output: {result.stdout!r}")  # Debug the raw output
    return result.stdout.strip() == "true"

def get_capslock_state2():
    script = '''
    ObjC.import("CoreGraphics")
    (() => {
        return Boolean($.CGEventSourceKeyState($.kCGEventSourceStateHIDSystemState, 0x39));
    })();
    '''
    result = subprocess.run(['osascript', '-l', 'JavaScript', '-e', script], 
                          capture_output=True, text=True)
    output = result.stdout.strip()
    print(f"Raw output 2: {output}")
    return output == "true"

from Quartz import CGEventSourceKeyState, kCGEventSourceStateHIDSystemState

def get_capslock_state3():
    # 0x39 is the caps lock key code
    return bool(CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x39))

# Test it
print(get_capslock_state())

print(get_capslock_state())
print(get_capslock_state2())
print(get_capslock_state3())

#c = CapslockSync()

#async def foo():
    #print(c.get_capslock_state())
    #await c.set_capslock_state(True);
    #print(c.get_capslock_state())

#asyncio.run(foo())
