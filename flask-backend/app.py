from flask import Flask, request

import tapo
import asyncio
import os

import network

# Create an application instance
app = Flask(__name__)

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
client = tapo.ApiClient(username, password)
n = network.Network(client)    

asyncio.run(n.get_device_list())

async def fade_brightness(device, duration, start, target):

    start = max(1, start)
    target = min(target, 100)

    step_n = abs(target - start)

    step_duration = duration/step_n

    step_current = 1

    while step_current <= step_n:

        if target < start:
            value = start - step_current
        else:
            value = start + step_current

        # print(value)

        if value <= 0:
            await device.off()
        else:
            if isinstance(device, tapo.PlugHandler):
                await device.on()
            else:
                await device.set_brightness(value)

        step_current += 1

        await asyncio.sleep(step_duration)

@app.route('/fade')
def handle_fade():
    device = request.args.get('device')

    if device in n.devices:
        device = n.devices[device]
        duration = int(request.args.get('duration'))
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
        asyncio.run(fade_brightness(device, duration, start, end))

    return "FADE STARTED"


@app.route('/all')
def handle_all():
    value = request.args.get('value')

    for device in n.devices.values():
        match value:
            case 'on':
                asyncio.run(device.on())
            case 'off':
                asyncio.run(device.off())

    return f"Turned all lights {value}"

@app.route('/group')
def handle_group():
    group_name = request.args.get('name')

    value = request.args.get('value')
    if value.isdigit():
        value = int(value)

    if group_name in n.groups:
        devices = n.groups[group_name]

        for name in devices:
            if name in n.devices:
                device = n.devices[name]

                match value:
                    case 'on':
                        asyncio.run(device.on())
                    case 'off':
                        asyncio.run(device.off())
                    case int():
                        if value <= 0:
                            asyncio.run(device.off())
                        else:
                            if isinstance(device, tapo.PlugHandler):
                                asyncio.run(device.on())
                            else:
                                asyncio.run(device.set_brightness(value))
                        

        return f"Set group '{group_name}' to '{value}'"
    
    return 'ERROR'

@app.route('/single')
def handle_single():
    device_name = request.args.get('name')

    value = request.args.get('value')

    if value.isdigit():
        value = int(value)

    if device_name in n.devices:
        device = n.devices[device_name]

        match value:
            case 'on':
                asyncio.run(device.on())
            case 'off':
                asyncio.run(device.off())
            case int():
                if value <= 0:
                    asyncio.run(device.off())
                else:
                    if isinstance(device, tapo.PlugHandler):
                        asyncio.run(device.on())
                    else:
                        asyncio.run(device.set_brightness(value))
                        

        return f"Set device '{device_name}' to '{value}'"
    
    return 'ERROR'


if __name__ == '__main__':
    app.run(debug=True)
