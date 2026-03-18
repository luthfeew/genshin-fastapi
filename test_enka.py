import enka
import asyncio
import json

async def main() -> None:
    async with enka.GenshinClient(enka.gi.Language.ENGLISH) as client:
        data2 = await client.fetch_showcase(809407269)
        output = data2.player.model_dump()

        print(json.dumps(output, indent=2, ensure_ascii=False))

asyncio.run(main())