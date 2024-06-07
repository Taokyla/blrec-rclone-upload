import asyncio
import json
import os
from datetime import datetime
from enum import IntEnum
from typing import Any
from uuid import UUID

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

app = FastAPI()


class Event(BaseModel):
    type: str
    id: UUID
    date: datetime
    data: Any


class LiveStatus(IntEnum):
    PREPARING = 0
    LIVE = 1
    ROUND = 2


class RoomInfo(BaseModel):
    uid: int
    room_id: int
    short_room_id: int
    area_id: int
    area_name: str
    parent_area_id: int
    parent_area_name: str
    live_status: LiveStatus
    live_start_time: int  # A integer in seconds
    online: int
    title: str
    cover: str
    tags: str
    description: str


REPLACE_DIR = os.getenv("RECORD_REPLACE_DIR", "/rec")
RELATIVE_PATH_SLICE = len(REPLACE_DIR)
SOURCE_DIR = os.getenv("RECORD_SOURCE_DIR", REPLACE_DIR)
DESTINATION_DIR = os.getenv("RECORD_DESTINATION_DIR", "onedrive:record")


@app.post("/rec")
async def rec(event: Event):
    logger.info(f"receive {event.type}")
    if event.type in {"RecordingFinishedEvent", "RecordingCancelledEvent"}:
        room_info = RoomInfo(**event.data["room_info"])
        logger.info(f"房间号 {room_info.room_id} 录制完成,标题 {room_info.title}")
    elif event.type == "VideoPostprocessingCompletedEvent":
        relative_path = event.data["path"][RELATIVE_PATH_SLICE:]
        file_real_path = SOURCE_DIR + relative_path
        image_path = file_real_path[:-4] + ".jpg"
        if os.path.exists(image_path):
            des = DESTINATION_DIR + relative_path[:-4] + ".jpg"
            await asyncio.create_subprocess_exec("rclone", "moveto", image_path, des)
        else:
            image_path = file_real_path[:-4] + ".png"
            if os.path.exists(image_path):
                des = DESTINATION_DIR + relative_path[:-4] + ".png"
                await asyncio.create_subprocess_exec("rclone", "moveto", image_path, des)
        if os.path.exists(file_real_path):
            des = DESTINATION_DIR + relative_path
            await asyncio.create_subprocess_exec("rclone", "moveto", file_real_path, des)
    elif event.type == "DanmakuFileCompletedEvent":
        relative_path = event.data["path"][RELATIVE_PATH_SLICE:]
        file_real_path = SOURCE_DIR + relative_path
        if os.path.exists(file_real_path):
            des = DESTINATION_DIR + relative_path
            await asyncio.create_subprocess_exec("rclone", "moveto", file_real_path, des)
    elif event.type == "SpaceNoEnoughEvent":
        data = json.dumps(event.data, ensure_ascii=False)
        logger.error(f"空间不足:{data}")
    else:
        logger.debug(f"event:{event.model_dump_json()}")
    return {"code": 0}
