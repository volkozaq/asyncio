import asyncio
from itertools import batched

import aiohttp

from db import DbSession, StarWarsPersons, open_orm, close_orm
from sqlalchemy import insert

MAX_REQUESTS = 5

async def get_all_sw(sw_id: int, http_session: aiohttp.ClientSession):
    try:
        response = await http_session.get(f"https://www.swapi.tech/api/people/{sw_id}/")
        response.raise_for_status()
        json_data = await response.json()
        # If there is no data, return None
        if json_data['message'] != 'ok':
            return None
        # Getting all the needed fields from json data
        properties_dict = json_data['result']['properties']
        only_needed_properties_dict = {k: properties_dict[k] for k in
                                       ['name', 'birth_year', 'eye_color', 'gender', 'hair_color', 'mass',
                                        'skin_color']}
        sw_person = {'sw_id': int(json_data['result']['uid'])}
        sw_person.update(only_needed_properties_dict)
        try:
            planet_res = await http_session.get(properties_dict['homeworld'])
            planet_res.raise_for_status()
            planet_data = await planet_res.json()
            sw_person['homeworld'] = planet_data['result']['properties']['name']
            return sw_person
        except aiohttp.ClientError as e:
            print(f"Ошибка при запросе данных: {e}")
        except asyncio.TimeoutError:
            print("Запрос превысил время ожидания")
    except aiohttp.ClientError as e:
        print(f"Ошибка при запросе данных: {e}")
    except asyncio.TimeoutError:
        print("Запрос превысил время ожидания")

async def async_bulk_insert(list_of_sw_dicts: list[dict]) -> None:
    async with DbSession() as session:
        await session.execute(insert(StarWarsPersons), list_of_sw_dicts)
        await session.commit()

async def insert_results(results: list[dict]):
    async with DbSession() as session:
        list_of_sw_dicts = []
        for sw_dict in results:
            if sw_dict:
                list_of_sw_dicts.append(sw_dict)
        if list_of_sw_dicts:
            await async_bulk_insert(list_of_sw_dicts)

async def main():
    await open_orm()
    async with aiohttp.ClientSession() as http_session:
        for batch in batched(range(1, 100), MAX_REQUESTS):
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