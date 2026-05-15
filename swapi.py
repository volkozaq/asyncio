import asyncio
from itertools import batched

import aiohttp

from db import DbSession, StarWarsPersons, open_orm, close_orm

MAX_REQUESTS = 5

async def get_all_sw(sw_id: int, http_session: aiohttp.ClientSession):
    response = await http_session.get(f"https://www.swapi.tech/api/people/{sw_id}/")
    json_data = await response.json()
    # If there is no data, return None
    if json_data['message'] != 'ok':
        return None
    # Getting all the needed fields from json data
    properties_dict = json_data['result']['properties']
    only_needed_properties_dict = {k:  properties_dict[k] for k in
                  ['name', 'birth_year', 'eye_color', 'gender', 'hair_color', 'homeworld', 'mass', 'skin_color']}
    sw_person = {'id': json_data['result']['uid']}
    sw_person.update(only_needed_properties_dict)
    return sw_person

async def insert_results(results: list[dict]):
    async with DbSession() as session:
        for sw_dict in results:
            # Only write to db if there is data
            if sw_dict:
                sw_obj = StarWarsPersons(json=sw_dict)
                session.add(sw_obj)
        await session.commit()


async def main():
    await open_orm()
    async with aiohttp.ClientSession() as http_session:
        for batch in batched(range(1, 2), MAX_REQUESTS):
            coros = [get_all_sw(i, http_session) for i in batch]
            results = await asyncio.gather(*coros)
            insert_results_task = asyncio.create_task(insert_results(results))
        tasks = asyncio.all_tasks()
        current = asyncio.current_task()
        tasks.remove(current)
        for task in tasks:
            await task
    await close_orm()

asyncio.run(main())