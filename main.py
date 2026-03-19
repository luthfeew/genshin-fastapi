from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional
import enka
import genshin
import os
import asyncio

load_dotenv()

ltuid = os.getenv("LTUID")
ltoken = os.getenv("LTOKEN")
cookies = {"ltuid_v2": ltuid, "ltoken_v2": ltoken}

hoyolab_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global hoyolab_client
    hoyolab_client = genshin.Client(cookies)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "heya~ heya~ ini API HoyoLab & Enka.Network hasil gabut wkwk (≧▽≦)/", "status": "online uwu ✨", "dev": "TahuBulat"}

@app.get("/update")
async def update_assets():
    try:
        async with enka.GenshinClient() as client:
            await client.update_assets()
        return {"status": "Assets updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/genshin/{uid}")
@app.get("/genshin")
async def read_genshin_user(uid: Optional[int] = None):
    if uid is None:
        raise HTTPException(status_code=400, detail="UID tidak boleh kosong")

    async with enka.GenshinClient(enka.gi.Language.ENGLISH) as enka_client:
        results = await asyncio.gather(
            hoyolab_client.get_full_genshin_user(uid),
            enka_client.fetch_showcase(uid),
            return_exceptions=True
        )

    data, data2 = results

    hoyolab_result = None
    if isinstance(data, Exception):
        hoyolab_result = {"error": str(data)}
    else:
        hoyolab_result = data

    enka_result = None
    if isinstance(data2, Exception):
        enka_result = {"error": str(data2)}
    else:
        enka_result = data2.player

    if isinstance(data, Exception) and isinstance(data2, Exception):
        raise HTTPException(status_code=502, detail="Both data sources failed")

    return {
        "uid": uid,
        "info": enka_result,
        "data": hoyolab_result
    }