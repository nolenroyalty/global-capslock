from Quartz import CGEventSourceKeyState, kCGEventSourceStateHIDSystemState
import asyncio
import websockets
import subprocess
import time
import json

def get_capslock_state():
    return bool(CGEventSourceKeyState(kCGEventSourceStateHIDSystemState, 0x39))

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
    last_state = False
    
    async with websockets.connect(uri) as websocket:
        while True:
            # Check local caps lock state
            current_state = get_capslock_state()
            #print(current_state)
            
            # If state changed, notify server
            if current_state != last_state:
                print("CHANGED")
                await websocket.send(json.dumps({"toggle": current_state}))
                last_state = current_state
            
            # Handle incoming state updates
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                data = json.loads(message)
                if "enabled" in data and data["enabled"] != current_state:
                    set_capslock_state(data["enabled"])
            except asyncio.TimeoutError:
                pass  # No message received, continue polling
            
            await asyncio.sleep(0.1)  # Poll every 100ms

if __name__ == "__main__":
    asyncio.run(run_client())
