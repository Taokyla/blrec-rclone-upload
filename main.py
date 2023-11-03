import asyncio
import json
import os
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID

import uvicorn
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel


class Escape:
    reserved_chars: str = r'''?&|!{}[]()^~*:\"'+- '''
    replace: List[str] = ['\\' + l for l in reserved_chars]
    trans: Dict[str, str] = str.maketrans(dict(zip(reserved_chars, replace)))

    @staticmethod
    def add_escape(value: str) -> str:
        return value.translate(Escape.trans)

    @staticmethod
    def __matmul__(other: str) -> str:
        return Escape.add_escape(other)

    @staticmethod
    def __rmatmul__(other: str) -> str:
        return Escape.add_escape(other)

    @staticmethod
    def __rshift__(other: str) -> str:
        return Escape.add_escape(other)

    @staticmethod
    def __rlshift__(other: str) -> str:
        return Escape.add_escape(other)


escape = Escape()

api = FastAPI()


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


config = json.load(Path('config.json').open(encoding="utf8"))

RELATIVE_PATH_SLICE = len(config["docker"]) if "docker" in config else len(config["source"])


@api.post('/rec')
async def rec(event: Event):
    logger.info(f"receive {event.type}")
    if event.type in ('RecordingFinishedEvent', 'RecordingCancelledEvent'):
        room_info = RoomInfo(**event.data['room_info'])
        logger.info(f"房间号 {room_info.room_id} 录制完成,标题 {room_info.title}")
    elif event.type == 'VideoPostprocessingCompletedEvent':
        relative_path = event.data['path'][RELATIVE_PATH_SLICE:]
        file_real_path = config["source"] + relative_path
        image_path = file_real_path[:-4] + '.jpg'
        if os.path.exists(image_path):
            des = config["des"] + relative_path[:-4] + '.jpg'
            cmd = f'rclone moveto {image_path @ escape} {des @ escape}'
            await asyncio.subprocess.create_subprocess_shell(cmd)
        else:
            image_path = file_real_path[:-4] + '.png'
            if os.path.exists(image_path):
                des = config["des"] + relative_path[:-4] + '.png'
                cmd = f'rclone moveto {image_path @ escape} {des @ escape}'
                await asyncio.subprocess.create_subprocess_shell(cmd)
        if os.path.exists(file_real_path):
            des = config["des"] + relative_path
            cmd = f'rclone moveto {file_real_path @ escape} {des @ escape}'
            await asyncio.subprocess.create_subprocess_shell(cmd)
    elif event.type == 'DanmakuFileCompletedEvent':
        relative_path = event.data['path'][RELATIVE_PATH_SLICE:]
        file_real_path = config["source"] + relative_path
        if os.path.exists(file_real_path):
            des = config["des"] + relative_path
            cmd = f'rclone moveto {file_real_path @ escape} {des @ escape}'
            await asyncio.subprocess.create_subprocess_shell(cmd)
    elif event.type == 'SpaceNoEnoughEvent':
        data = json.dumps(event.data, ensure_ascii=False)
        logger.error(f"空间不足:{data}")
    else:
        logger.info(event.json())
    return {"code": 0}


if __name__ == '__main__':
    uvicorn.run("main:api", **config["api"])
