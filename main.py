import asyncio
from aiohttp import ClientSession
from pykoplenti import ApiClient
import os
from dbsvc import *
from datetime import datetime
now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

plenticore_ip = os.environ['PLENTICORE_IP']
plenticore_password = os.environ['PLENTICORE_PASSWORD']


async def async_main(host, passwd):
    async with ClientSession() as session:
        client = ApiClient(session, host)
        await client.login(passwd)

        data = await client.get_process_data_values('devices:local', [
            "Inverter:State",
            "Dc_P",
            "Grid_P",
            "Home_P"
        ])

        device_local = data['devices:local']
        writeMeasure(now, "plenticore", "dc.p", device_local['Dc_P'].value) # production photovoltaique
        writeMeasure(now, "plenticore", "inverter.p", device_local['Inverter:State'].value)  # production batterie
        writeMeasure(now, "plenticore", "grid.p", device_local['Grid_P'].value) # consommation réseau
        writeMeasure(now, "plenticore", "home.p", device_local['Home_P'].value) # consommation maison

asyncio.run(async_main(plenticore_ip, plenticore_password))
