from Quartz import CGEventSourceKeyState, kCGEventSourceStateHIDSystemState
import asyncio
import websockets
import subprocess
import time
import json
from websockets.exceptions import ConnectionClosedError, WebSocketException

def get_capslock_state():
    return bool(CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x39))

# huge thank you to https://github.com/erikpt/caps-lock-shell-script for showing me how to do this
def set_capslock_state(enabled):
    script = '''
    ObjC.import("IOKit");
    ObjC.import("CoreServices");
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
        $.IOHIDSetModifierLockState(ioConnect, $.kIOHIDCapsLockState, %d);
        $.IOServiceClose(ioConnect);
    })();
    ''' % (1 if enabled else 0)
    subprocess.run(['osascript', '-l', 'JavaScript', '-e', script])

async def run_client():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        last_state = False
        while True:
            current_state = get_capslock_state()
            
            if current_state != last_state:
                print(f"CHANGED {last_state} => {current_state}")
                await websocket.send(json.dumps({"toggle": current_state}))
                last_state = current_state

            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(message)
                if "enabled" in data:
                    d = bool(data["enabled"])
                    if d != current_state:
                        set_capslock_state(d)
                        current_state = d
            except asyncio.TimeoutError as e:
                pass

            try:
                await asyncio.sleep(0.1)
            except Exception as e:
                print(e)
                return


async def run_client_loop():
    while True:
        try:
            await run_client()
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\nExiting.")
            return
        except (OSError, ConnectionClosedError, WebSocketException, ConnectionResetError) as e:
            print(f"Error talking to server: {e}. Sleeping and trying again...")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_client_loop())
