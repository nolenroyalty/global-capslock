import asyncio
import websockets
import json
from websockets.exceptions import ConnectionClosedError, WebSocketException
from datetime import datetime
from zoneinfo import ZoneInfo

async def run_client():
    #uri = "ws://localhost:8000/ws"
    uri = "wss://globalcapslock.com/status"

    with open("counts.txt", "a") as file:
        async with websockets.connect(uri) as websocket:
            while True:
                data = await websocket.recv()
                now = datetime.now(ZoneInfo("America/New_York")).isoformat()
                try:
                    if data.startswith("c"):
                        count = data.split(" ")[1]
                        line = f"{now}|COUNT|{count}"
                        file.write(line + "\n")
                        print(line)
                    elif data == "1":
                        line = f"{now}|ON"
                        file.write(line + "\n")
                        print(line)
                    elif data == "0":
                        line = f"{now}|OFF"
                        file.write(line + "\n")
                        print(line)
                    else:
                        line = f"{now}|INVALID|{data}"
                        file.write(line + "\n")
                        print(line)
                    file.flush()
                except Exception as e:
                    print(f"EXCEPTION: {e}")

async def run_client_loop():
    while True:
        try:
            await run_client()
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\nExiting.")
            return
        except (
            OSError,
            ConnectionClosedError,
            WebSocketException,
            ConnectionResetError,
        ) as e:
            print(f"Error talking to server: {e}. Sleeping and trying again...")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_client_loop())
