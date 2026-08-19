import asyncio
import base64
import hashlib
import hmac
import ipaddress
from io import BytesIO
import os
import secrets
import socket
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Cookie, FastAPI, HTTPException, Query, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.responses import Response as FileResponseResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import qrcode

from backend.database import (
    add_meeting,
    add_meeting_message,
    archive_expired_meetings,
    check_login,
    delete_meeting,
    get_all_meetings,
    get_meeting_by_id,
    get_meeting_messages,
    get_meeting_history,
    get_user,
    get_user_settings,
    register_user,
    save_user_settings,
    update_user,
)

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
app = FastAPI(title="MeetSphere Web")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

SESSION_SECRET = os.environ.get("MEETSPHERE_SESSION_SECRET", "local-development-secret").encode()
SESSION_DURATION_SECONDS = 5 * 60
sessions: dict[str, str] = {}
rooms: dict[str, dict[str, WebSocket]] = {}
participants: dict[str, dict[str, dict[str, Any]]] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str


class MeetingRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    date: str
    time: str
    duration: str
    description: str = ""


class MeetingMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class ProfileRequest(BaseModel):
    name: str
    email: str


class SettingsRequest(BaseModel):
    mic_enabled: bool = True
    camera_enabled: bool = True
    notifications_enabled: bool = True
    dark_mode: bool = False
    display_name: str = ""
    email: str = ""


def create_session(username: str) -> str:
    payload = f"{username}:{int(time.time())}".encode()
    encoded = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    signature = hmac.new(SESSION_SECRET, encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def user_from_token(token: str | None) -> str:
    if token and token in sessions:
        return sessions[token]
    try:
        encoded, signature = (token or "").split(".", 1)
        expected = hmac.new(SESSION_SECRET, encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError
        payload = base64.urlsafe_b64decode(encoded + "=").decode()
        username, issued_at = payload.rsplit(":", 1)
        if time.time() - int(issued_at) > SESSION_DURATION_SECONDS:
            raise ValueError
        return username
    except (ValueError, TypeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Please sign in first.")


def meeting_json(row: tuple) -> dict[str, Any]:
    return {
        "id": row[0],
        "title": row[1],
        "date": row[2],
        "time": row[3],
        "duration": row[4],
        "description": row[5] or "",
        "link": row[6] or "",
        "archivedAt": row[8] if len(row) > 8 else None,
    }


def local_network_url() -> str:
    candidates: list[str] = []
    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, type=socket.SOCK_DGRAM)
        for family, _, _, _, sockaddr in infos:
            if family != socket.AF_INET:
                continue
            address = sockaddr[0]
            try:
                parsed = ipaddress.ip_address(address)
            except ValueError:
                continue
            if address in {"0.0.0.0", "127.0.0.1", "::1"}:
                continue
            if parsed.is_private or parsed.is_link_local:
                candidates.append(address)
    except OSError:
        candidates = []

    if not candidates:
        try:
            _, _, host_addresses = socket.gethostbyname_ex(socket.gethostname())
            for address in host_addresses:
                if address in {"0.0.0.0", "127.0.0.1"}:
                    continue
                try:
                    parsed = ipaddress.ip_address(address)
                except ValueError:
                    continue
                if parsed.is_private or parsed.is_link_local:
                    candidates.append(address)
        except OSError:
            candidates = []

    if not candidates:
        return "http://127.0.0.1:8000"
    return f"http://{candidates[0]}:8000"


@app.get("/", response_class=FileResponse)
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/network-url")
async def network_url() -> dict[str, str]:
    return {"baseUrl": local_network_url()}


@app.post("/api/auth/login")
async def login(payload: LoginRequest, response: Response) -> dict[str, Any]:
    if not check_login(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    username = payload.username.strip()
    user = get_user(username)
    settings = get_user_settings(username)
    token = create_session(username)
    sessions[token] = username
    response.set_cookie("meetsphere_session", token, httponly=True, samesite="lax", secure=False, max_age=SESSION_DURATION_SECONDS)
    return {
        "username": username,
        "name": user[1] if user else username,
        "email": user[2] if user else "",
        "settings": {
            "mic_enabled": bool(settings[1]) if settings else True,
            "camera_enabled": bool(settings[2]) if settings else True,
            "notifications_enabled": bool(settings[3]) if settings else True,
            "dark_mode": bool(settings[4]) if settings else False,
        },
    }


@app.post("/api/auth/register")
async def register(payload: RegisterRequest) -> dict[str, str]:
    try:
        register_user(payload.name.strip(), payload.email.strip(), payload.username.strip(), payload.password)
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="That username is already registered.") from error
    return {"message": "Account created. You can now sign in."}


@app.post("/api/auth/logout")
async def logout(response: Response, token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> dict[str, bool]:
    sessions.pop(token or session_cookie or "", None)
    response.delete_cookie("meetsphere_session")
    return {"ok": True}


@app.get("/api/me")
async def current_user(token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> dict[str, Any]:
    username = user_from_token(token or session_cookie)
    user = get_user(username)
    settings = get_user_settings(username)
    return {
        "username": username,
        "name": user[1] if user else username,
        "email": user[2] if user else "",
        "settings": {
            "mic_enabled": bool(settings[1]) if settings else True,
            "camera_enabled": bool(settings[2]) if settings else True,
            "notifications_enabled": bool(settings[3]) if settings else True,
            "dark_mode": bool(settings[4]) if settings else False,
        },
    }


@app.get("/api/meetings")
async def meetings(token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> list[dict[str, Any]]:
    username = user_from_token(token or session_cookie)
    archive_expired_meetings()
    return [meeting_json(row) for row in get_all_meetings(username)]


@app.get("/api/meetings/history")
async def meeting_history(token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> list[dict[str, Any]]:
    username = user_from_token(token or session_cookie)
    archive_expired_meetings()
    return [meeting_json(row) for row in get_meeting_history(username)]


@app.post("/api/meetings")
async def create_meeting(payload: MeetingRequest, token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> dict[str, Any]:
    username = user_from_token(token or session_cookie)
    link = add_meeting(payload.title, payload.date, payload.time, payload.duration, payload.description, username)
    meeting_id = int(link.rsplit("/", 1)[-1])
    return meeting_json(get_meeting_by_id(meeting_id))


@app.get("/api/meetings/{meeting_id}/qr")
async def meeting_qr(
    meeting_id: int,
    base_url: str = Query(default=""),
    token: str | None = Query(default=None),
    session_cookie: str | None = Cookie(default=None, alias="meetsphere_session"),
) -> FileResponseResponse:
    user_from_token(token or session_cookie)
    if not get_meeting_by_id(meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found.")
    join_base = local_network_url() if not base_url or "127.0.0.1" in base_url or "localhost" in base_url else base_url.rstrip("/")
    join_url = f"{join_base}/?meeting={meeting_id}"
    image = qrcode.make(join_url)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return FileResponseResponse(content=buffer.getvalue(), media_type="image/png")


@app.get("/api/meetings/{meeting_id}/messages")
async def meeting_messages(
    meeting_id: int,
    token: str | None = Query(default=None),
    session_cookie: str | None = Cookie(default=None, alias="meetsphere_session"),
) -> list[dict[str, Any]]:
    user_from_token(token or session_cookie)
    if not get_meeting_by_id(meeting_id):
        raise HTTPException(status_code=404, detail="Meeting not found.")
    return [
        {"id": row[0], "senderUsername": row[1], "senderName": row[2], "message": row[3], "createdAt": row[4]}
        for row in get_meeting_messages(meeting_id)
    ]


@app.post("/api/meetings/{meeting_id}/messages")
async def post_meeting_message(
    meeting_id: int,
    payload: MeetingMessageRequest,
    token: str | None = Query(default=None),
    session_cookie: str | None = Cookie(default=None, alias="meetsphere_session"),
) -> dict[str, Any]:
    username = user_from_token(token or session_cookie)
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    user = get_user(username)
    sender_name = user[1] if user else username
    message_id = add_meeting_message(meeting_id, username, sender_name, payload.message.strip())
    return {"id": message_id, "senderUsername": username, "senderName": sender_name, "message": payload.message.strip()}


@app.delete("/api/meetings/{meeting_id}")
async def remove_meeting(meeting_id: int, token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> dict[str, bool]:
    username = user_from_token(token or session_cookie)
    meeting = get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found.")
    owner_username = meeting[7] if len(meeting) > 7 else None
    if owner_username and owner_username != username:
        raise HTTPException(status_code=403, detail="You cannot delete another user's meeting.")
    if not delete_meeting(meeting_id, username):
        raise HTTPException(status_code=403, detail="This meeting has no web owner and cannot be deleted here.")
    return {"ok": True}


@app.put("/api/profile")
async def profile(payload: ProfileRequest, token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> dict[str, bool]:
    username = user_from_token(token or session_cookie)
    update_user(username, payload.name.strip(), payload.email.strip())
    return {"ok": True}


@app.put("/api/settings")
async def settings(payload: SettingsRequest, token: str | None = Query(default=None), session_cookie: str | None = Cookie(default=None, alias="meetsphere_session")) -> dict[str, bool]:
    username = user_from_token(token or session_cookie)
    save_user_settings(
        username,
        payload.mic_enabled,
        payload.camera_enabled,
        payload.notifications_enabled,
        payload.dark_mode,
        payload.display_name,
        payload.email,
    )
    return {"ok": True}


async def send_json(socket: WebSocket, message: dict[str, Any]) -> None:
    try:
        await socket.send_json(message)
    except Exception:
        pass


async def room_broadcast(room_code: str, message: dict[str, Any], exclude: str | None = None) -> None:
    sockets = list(rooms.get(room_code, {}).items())
    await asyncio.gather(*(send_json(socket, message) for participant_id, socket in sockets if participant_id != exclude))

async def room_route(room_code: str, message: dict[str, Any], target_id: str | None, exclude: str | None = None) -> None:
    if target_id and target_id in rooms.get(room_code, {}):
        await send_json(rooms[room_code][target_id], message)
        return
    await room_broadcast(room_code, message, exclude=exclude)


@app.websocket("/ws/meetings/{room_code}")
async def meeting_socket(websocket: WebSocket, room_code: str, token: str | None = Query(default=None), name: str = Query(...)) -> None:
    session_token = token or websocket.cookies.get("meetsphere_session")
    if not session_token or not room_code.isdigit() or not get_meeting_by_id(int(room_code)):
        await websocket.close(code=1008, reason="Invalid meeting or session")
        return

    await websocket.accept()
    participant_id = secrets.token_urlsafe(10)
    try:
        username = user_from_token(session_token)
    except HTTPException:
        await websocket.close(code=1008, reason="Invalid session")
        return
    participant = {
        "id": participant_id,
        "name": name.strip() or username,
        "username": username,
        "isHost": not participants.get(room_code),
        "micEnabled": True,
        "cameraEnabled": True,
        "sharing": False,
    }
    rooms.setdefault(room_code, {})[participant_id] = websocket
    participants.setdefault(room_code, {})[participant_id] = participant

    existing = [item for key, item in participants[room_code].items() if key != participant_id]
    await send_json(websocket, {"type": "joined", "participantId": participant_id, "participants": existing})
    await room_broadcast(room_code, {"type": "participant-joined", "participant": participant}, exclude=participant_id)

    try:
        while True:
            message = await websocket.receive_json()
            message["senderId"] = participant_id
            message["senderName"] = participant["name"]
            message["roomCode"] = room_code
            message.setdefault("timestamp", datetime.now(timezone.utc).isoformat())

            if message.get("type") == "media-state":
                participant["micEnabled"] = bool(message.get("micEnabled", True))
                participant["cameraEnabled"] = bool(message.get("cameraEnabled", True))
                participant["sharing"] = bool(message.get("sharing", False))
            elif message.get("type") == "chat-message":
                message["isHost"] = participant["isHost"]
            await room_route(room_code, message, message.get("targetId"), exclude=participant_id)
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        rooms.get(room_code, {}).pop(participant_id, None)
        participants.get(room_code, {}).pop(participant_id, None)
        await room_broadcast(room_code, {"type": "participant-left", "participantId": participant_id})
        if not rooms.get(room_code):
            rooms.pop(room_code, None)
            participants.pop(room_code, None)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("web_server:app", host="0.0.0.0", port=8000)
