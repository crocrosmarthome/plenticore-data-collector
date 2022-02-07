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

        # 1. Récupérer les données du générateur photvoltaique 1
        data_pv1 = await client.get_process_data_values('devices:local:pv1', [
            "P"
        ])

        device_pv1_local = data_pv1['devices:local:pv1']
        pv1_p = device_pv1_local['P'].value
        writeMeasure(now, "plenticore", "pv1_P", pv1_p)


        # 2. Récupérer les données du générateur photvoltaique 1
        data_pv2 = await client.get_process_data_values('devices:local:pv2', [
            "P"
        ])
        device_pv2_local = data_pv2['devices:local:pv2']
        pv2_p = device_pv2_local['P'].value
        writeMeasure(now, "plenticore", "pv2_P", pv2_p)

        # 3. Calculer la production photovoltaique totale
        pv_p_total =pv1_p + pv2_p

        writeMeasure(now, "plenticore", "pv_all_P", pv_p_total)

        data = await client.get_process_data_values('devices:local', [
            "Inverter:State",
            "Dc_P",
            "Grid_P",
            "Home_P",
            "HomePv_P",
            "HomeGrid_P"
        ])

        device_local = data['devices:local']

        # 4. Obtenir l'alimentation du réseau (romande énergie)
        writeMeasure(now, "plenticore", "Grid_P", device_local['Grid_P'].value)

        # 5. Obtenir la consommation de la maison
        writeMeasure(now, "plenticore", "Home_P", device_local['Home_P'].value)

        data_battery = await client.get_process_data_values('devices:local:battery', [
            "P",
            "SoC",
            "Cycles"
        ])
        data_battery_local = data_battery['devices:local:battery']

        # 6. Obtenir la puissance utilisée de la batterie
        battery_p = data_battery_local['P'].value
        writeMeasure(now, "plenticore", "battery_P", battery_p)

        # 7. Obtenir le pourcentage de charge de la batterie
        batteryPourcentageCharge = data_battery_local['SoC'].value
        writeMeasure(now, "plenticore", "battery_SoC", batteryPourcentageCharge)

        # 8 Obtenir les cycles de la batterie
        batteryCycles = data_battery_local['Cycles'].value
        writeMeasure(now, "plenticore", "battery_Cycles", batteryCycles)

        # 9 Obtenir la puissance de l'inverter
        writeMeasure(now, "plenticore", "HomePv_P", device_local['HomePv_P'].value)

        # 10 Obtenir le DC_P - Je sais pas ce que c'est
        writeMeasure(now, "plenticore", "Dc_P", device_local['Dc_P'].value)

        # 11 Obtenir l'inverter state - Je sais pas ce que c'est
        writeMeasure(now, "plenticore", "Inverter_State", device_local['Inverter:State'].value)

asyncio.run(async_main(plenticore_ip, plenticore_password))
