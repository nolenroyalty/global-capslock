import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Set, Dict
from datetime import datetime, timedelta
import asyncio
import json
import sys
import random

app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Global Capslock Key</title>
        <link rel="icon" type="image/png" href="/favicon.png">
        <meta name="viewport" content="width=device-width" />
        <meta property="og:title" content="The Global Capslock Key" />
        <meta property="og:url" content="https://globalcapslock.com" />
        <meta property="og:type" content="website" />

        <meta name="description" content="a synchronized global capslock key" />
        <meta property="og:description" content="a synchronized global capslock key" />
        <meta name="twitter:description" content="a synchronized global capslock key" />

        <meta property="og:image" content="https://globalcapslock.com/social.png" />
        <meta property="twitter:image" content="https://globalcapslock.com/social.png" />

        <meta name="twitter:card" content="summary" />
        <meta name="twitter:site" content="@itseieio" />
        <meta name="twitter:creator" content="@itseieio" />
        <meta name="twitter:title" content="The Global Capslock Key" />

        <style>
        * {
            margin: 0;
        }
        :root {
            --color-slate-100: #F1F5F9;
            --color-slate-200: #E2E8F0;
            --color-slate-300: #cbd5e1;
            --color-slate-400: #94A3B8;
            --color-slate-600: #475569;
            --color-slate-800: #1e293b;
            --color-yellow-400: #facc15;
            --color-sky-100: #e0f2fe;
            --color-blue-400: #60a5fa;
            --color-green-500: #22C55E;
        }
        body {
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            font-family: monospace;
            color: var(--color-slate-800);
            background-color: var(--color-slate-300);
        }

        p,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            overflow-wrap: break-word;
        }
        .wrapper {
            max-width: 1200px;
            margin: 0 auto;
        }

        .all-upper {
            text-transform: uppercase;
        }

        .all-lower {
            text-transform: lowercase;
        }

        #status {
            font-family: inherit;
            color: inherit;
            border: none;
            font-size: 3rem;
            padding: 1.5rem 1.25rem;
            margin: 1rem;
            border-radius: 8px;
            margin: 0 auto;
            min-width: 16ch;
            gap: 2.5rem;
            position: relative;

            display: flex;
            flex-direction: column;
            justify-content: center;

            @media (max-width: 950px) {
                font-size: 2.5rem;
            }

            @media (max-width: 700px) {
                font-size: 2rem;
            }

            @media (max-width: 600px) {
                font-size: 1.5rem;
            }

            transition: background-color ease 50ms;
        }

        #led {
            border-radius: 50%;
            width: 1rem;
            height: 1rem;
        }

        .led-off {
            background-color: var(--color-slate-800);
        }

        .led-on {
            background-color: var(--color-green-500);
        }

        .enabled {
            background-color: var(--color-yellow-400);
            text-transform: uppercase;
        }

        .disabled {
            background-color: var(--color-sky-100);
            text-transform: lowercase;
        }

        .site-header-title {
            font-size: 4rem;
            text-align: center;

            @media (max-width: 950px) {
                font-size: 3rem;
            }

            @media (max-width: 700px) {
                font-size: 2rem;
            }

            @media (max-width: 600px) {
                font-size: 1.5rem;
            }
        }

        .wrapper {
            display: flex;
            flex-direction: column;
            padding: 1rem;
            gap: 2rem;
        }

        .self-promo-outer {
            display: flex;
            flex-direction: column;
            align-self: flex-end;
            align-items: flex-end;
        }

        .self-promo-links {
            display: flex;
            flex-direction: row;
            gap: 1rem;
        }

        #connected {
            font-size: 0.75rem;
            transition: opacity 0.5s ease;
            text-align: center;
        }

        .not-visible {
            opacity: 0;
        }

        a {
            color: var(--color-blue-400);
        }

        #explainer {
            display: flex;
            flex-direction: column;
            max-width: min(40ch, 80vw);
            margin: 0 auto;
            font-size: 1.125rem;
            gap: 1.25rem;

            @media (max-width: 950px) {
                font-size: 1rem;
                gap 0.5rem;
            }
        }

        #caps-input {
            font-size: 1.125rem;
            padding: 0.5rem;
            background-color: var(--color-slate-300);
            border: 1px solid var(--color-slate-400);
            border-radius: 4px;
            max-width: min(40ch, 80vw);
            width: 100%;
            margin: 0 auto;
            font-family: monospace;
            height: 200px;
            color: var(--color-slate-600);
        }

        #caps-input:focus {
            outline: none;
        }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="self-promo-outer">
                <div class="self-promo-links">
                    <a href="https://x.com/itseieio">twitter</a>
                    <a href="https://bsky.app/profile/itseieio.bsky.social">bsky</a>
                    <a href="https://eieio.substack.com/">substack</a>
                    <a href="https://eieio.games/blog/the-global-capslock-key">?</a>
                    <a href="https://buymeacoffee.com/eieio">$</a>
                </div>
                <p>a utility from <a href="https://eieio.games">eieio</a></p>
            </div>
            <!--<h1 class="site-header-title">Global Caps Lock Status</h1>-->
            <button id="status" class="disabled" onclick='alert("Not so fast!!\n\nIf you want to toggle the caps lock key, download the client.\n\nThen other people can toggle caps lock for you too :)")'>
                <div id="led" class="led-off"></div>
                <p id="status-text">caps lock is off</p>
            </button>
            <div id="explainer">
                <p id="connected" class="not-visible">hey there</p>
                <p>
                    the world shares this caps lock key
                </p>
                <p>
                whenever anyone running <a href="https://github.com/nolenroyalty/global-capslock">the client</a> presses caps lock, it presses it for everyone else
                </p>
                <p>
                    finally we can all agree on when it's polite to use caps lock!
                </p>
                <p>
                    to join, <a href="https://github.com/nolenroyalty/global-capslock">download the client</a>
                </p>
            </div>
            <textarea id="caps-input" name="caps-input" rows="5" cols="40">if you're not ready to run the client, you can type some text here if you'd like...</textarea>
        </div>
        <script>
            const status = document.getElementById('status');
            const statusText = document.getElementById('status-text');
            const led = document.getElementById('led');
            const connected = document.getElementById('connected');
            let reconnectAttempts = 0;
            let capsOn = false;
            const maxDelay = 10000;

            function connect() {
                const ws = new WebSocket(`wss://${window.location.host}/status`);

                ws.onmessage = function(event) {
                    data = event.data;
                    console.log(data);
                    if (data.startsWith('c')) {
                        count = data.split(" ")[1];
                        if (count !== undefined) {
                            const word = count === "1" ? 'person is' : 'people are';
                            connected.innerText = `${count} ${word} syncing their capslock key`;
                            connected.classList.remove('not-visible');
                        }
                    }
                    else if (data === "1") {
                        statusText.textContent = "CAPS LOCK IS ON!";
                        capsOn = true;
                        document.title = "GLOBAL CAPSLOCK KEY";
                        status.className = "enabled"
                        led.className = "led-on";
                    } else if (data === "0") {
                        statusText.textContent = "caps lock is off";
                        capsOn = false;
                        document.title = "global capslock key";
                        status.className = "disabled";
                        led.className = "led-off";
                    }
                };

                ws.onclose = function () {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), maxDelay);
                    reconnectAttempts++;
                    setTimeout(connect, delay);
                };

                ws.onopen = function () {
                    reconnectAttempts = 0;
                };

                ws.onerror = function (error) {
                    console.error(`websocket error: ${error}`);
                };
            }

            const capsInput = document.getElementById("caps-input");

            capsInput.addEventListener("keydown", (event) => {
                if (event.ctrlKey || event.altKey || event.metaKey || event.key.length > 1) {
                    return;
                }

                event.preventDefault();

                const shift = event.shiftKey;
                let char = event.key;

                if (capsOn) {
                    char = shift ? char.toLowerCase() : char.toUpperCase();
                } else {
                    char = shift ? char.toUpperCase() : char.toLowerCase();
                }

                capsInput.value += char;
            });

            connect();
        </script>
    </body>
</html>
"""

# there are some memory leaks here because it was the easiest way to prevent someone reconnecting to
# reset their rate limit. don't think about it too hard.

capslock_enabled = False
listening_clients = set()
connected_clients = {} # websocket -> IP
last_websocket_update: Dict[str, datetime] = {} # websocket rate limit
token_buckets = {} # per-ip token bucket limit
RATE_LIMIT_SECONDS = 0.33
MAX_TOKENS = 10
REFILL_TOKENS_PER_SECOND = 1.5

SPECIAL_RATE_LIMITS = {}

def refill_tokens(bucket):
    now = datetime.now()
    elapsed = (now - bucket["last_refill"]).total_seconds()
    if elapsed > 0:
        tokens = min(MAX_TOKENS, bucket["tokens"] + elapsed * REFILL_TOKENS_PER_SECOND)
        bucket["tokens"] = tokens
        bucket["last_refill"] = now

def _can_update_token_bucket(ip):
    if ip not in token_buckets:
        token_buckets[ip] = { "tokens": MAX_TOKENS, "last_refill": datetime.now() }
    bucket = token_buckets[ip]
    refill_tokens(bucket)
    if bucket["tokens"] >= 1:
        bucket["tokens"] -= 1
        return True
    return False

def _can_update_websocket_ratelimit(websocket, ip):
    if ip is None:
        logger.error(f"NO CLIENT IP?")
        return True
    now = datetime.now()
    if websocket in last_websocket_update:
        limit_seconds = SPECIAL_RATE_LIMITS.get(ip, RATE_LIMIT_SECONDS)
        if now - last_websocket_update[websocket] < timedelta(seconds=limit_seconds):
            return False
    last_websocket_update[websocket] = now
    return True

def can_update(websocket):
    ip = connected_clients.get(websocket)
    has_tokens = _can_update_token_bucket(ip)
    limit_ok = _can_update_websocket_ratelimit(websocket, ip)
    return has_tokens and limit_ok

def client_ip_of_websocket(websocket):
    headers = dict(websocket.headers)
    client_ip = websocket.client.host

    if headers.get("cf-connecting-ip"):
        return headers.get("cf-connecting-ip")
    elif headers.get("x-forwarded-for"):
        s = headers.get("x-forwarded-for", "").split(",")
        return s[-1]

    logger.error(f"USING RAW CLIENT IP? {client_ip}")
    return client_ip

@app.get("/")
async def get():
    return HTMLResponse(html)

def message_for_state():
    return "1" if capslock_enabled else "0"

async def broadcast_state(message):
    """Send current state to all connected clients"""
    if connected_clients:
        for websocket in connected_clients.copy():  # Copy to avoid modification during iteration
            try:
                ip = connected_clients.get(websocket, "")
                await websocket.send_text(message)
            except:
                ip = connected_clients.get(websocket)
                connected_clients.pop(websocket, None)
                last_websocket_update.pop(websocket, None)
                #token_buckets.pop(ip, None)
    if listening_clients:
        for websocket in listening_clients.copy():
            try:
                await websocket.send_text(message)
            except:
                try:
                    listening_clients.remove(websocket)
                except KeyError:
                    pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global capslock_enabled
    await websocket.accept()
    client_ip = client_ip_of_websocket(websocket)
    connected_clients[websocket] = client_ip
    logger.info(f"{client_ip} CONNECTED")
    
    try:
        await websocket.send_text(message_for_state())
        while True:
            try:
                data = await websocket.receive_text()
                if not can_update(websocket):
                    continue
                if len(data) > 1:
                    logger.info(f"received invalid data (length: {len(data)} | client: {client_ip})")
                elif data == "1" and capslock_enabled != True:
                    capslock_enabled = True
                elif data == "0" and capslock_enabled != False:
                    capslock_enabled = False
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        try:
            #ip = connected_clients.get(websocket)
            #if ip and ip in token_buckets:
                #token_buckets.pop(ip)
            connected_clients.pop(websocket)
        except KeyError:
            return

def connected_client_count():
    return f"c {len(connected_clients)}"

@app.websocket("/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    listening_clients.add(websocket)

    try:
        await websocket.send_text(connected_client_count())
        await websocket.send_text(message_for_state())
        while True:
            await asyncio.sleep(5)
            await websocket.send_text(connected_client_count())
    except:
        try:
            listening_clients.remove(websocket)
        except KeyError:
            pass

@app.on_event("startup")
async def startup_event():
    async def periodic_broadcast():
        last_message = None
        while True:
            message = message_for_state()
            if last_message is None or last_message != message:
                last_message = message
                await broadcast_state(message)
            await asyncio.sleep(0.05)

    asyncio.create_task(periodic_broadcast())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
