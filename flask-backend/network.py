import tapo
import asyncio
import os

class Network:

    devices = {}
    groups = {
        'LR': 
        [
            'LR Cupboard',
            'LR Reading Lamp',
            'LR Sun Light',
            'LR Globe',
            'LR Main 1',
            'LR Main 2'
        ],
        'LR-ambient': 
        [
            'LR Cupboard',
            'LR Reading Lamp',
            'LR Sun Light',
            'LR Globe',
        ],
        'LR-main': 
        [
            'LR Main 1',
            'LR Main 2'
        ],
        'BR': 
        [
            'BR Main',
            'BR Fairy Lights',
            'BR Bedside'
        ],
        'BR-ambient': 
        [
            'BR Fairy Lights',
            'BR Bedside'
        ]
    }

    def __init__(self, client: tapo.ApiClient):
        self.client = client

    async def get_device_list(self):

        target = os.getenv("TARGET", "192.168.1.255")
        timeout_s = int(os.getenv("TIMEOUT", 1))

        discovery = await self.client.discover_devices(target, timeout_s)

        async for discovery_result in discovery:
            try:
                device = discovery_result.get()

                match device:
                    case tapo.DiscoveryResult.ColorLight(device_info, _handler):
                        print(f"Found {device_info.nickname}")
                        if device_info.model == "L530":
                            self.devices[device_info.nickname] = await self.client.l530(device_info.ip)
                    case tapo.DiscoveryResult.Plug(device_info, _handler):
                        print(f"Found {device_info.nickname}")
                        if device_info.model == 'P100':
                            self.devices[device_info.nickname] = await self.client.p100(device_info.ip)
                    case tapo.DiscoveryResult.Hub(device_info, _handler):
                        print(
                            f"Found '{device_info.nickname}' of model '{device_info.model}' at IP address '{device_info.ip}'."
                        )

            except Exception as e:
                print(f"Error discovering device: {e}")