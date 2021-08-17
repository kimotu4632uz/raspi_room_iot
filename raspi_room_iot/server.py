from flask import Flask, request, jsonify
import time

import iothub
from bme280i2c import BME280I2C


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/iot/light', methods=['POST'])
def light():
  param = request.get_json()

  if int(param['level']) == 0:
    level = 3
  elif 0 < int(param['level']) and int(param['level']) <= 30:
    level = 2
  elif 30 < int(param['level']) and int(param['level']) <= 70:
    level = 1
  else:
    level = 0

  if 'channel' in param:
    code = iothub.light(level, int(param['channel']))
  else:
    code = iothub.light(level)

  result = iothub.send(code)
  
  if result:
    return jsonify({ 'status': 'OK' })
  else:
    return jsonify({ 'status': 'Err' })

@app.route('/iot/aircon', methods=['POST'])
def aircon():
  param = request.get_json()

  mode_dict = { 'auto': 0, 'cool': 1, 'dry': 2, 'clear': 3, 'hot': 4 }
  wind_level_dict = { 'auto': 0, 'min': 1, 'mid': 2, 'max': 3 }
  timer_type_dict = { 'sleep': 1, 'on': 2, 'on/off': 4, 'off': 5 }
  
  if param['wind_v'] == 'swing':
    wind_v = 1
  elif param['wind_v'] != 0:
    wind_v = int(param['wind_v']) + 1
  else:
    wind_v = int(param['wind_v'])
  
  if param['wind_h'] == 'swing':
    wind_h = 8
  else:
    wind_h = int(param['wind_h'])
  
  if param['power']:
    power = 1
  else:
    power = 0
  
  if 'timer_type' in param and 'timer_time' in param:
    time_remain = int((int(param['timer_time']) - int(time.time())) / 60)
    code= iothub.aircon(power, mode_dict[param['mode']], int(param['temp']), wind_level_dict[param['wind_level']], wind_v, wind_h, timer_type_dict[param['timer_type']], time_remain)
  else: 
    code= iothub.aircon(power, mode_dict[param['mode']], int(param['temp']), wind_level_dict[param['wind_level']], wind_v, wind_h)
  result = iothub.send(code)

  if result:
    return jsonify({ 'status': 'OK' })
  else:
    return jsonify({ 'status': 'Err' })

@app.route('/iot/room')
def room():
  bme = BME280I2C()

  if bme.meas():
    result = { 'status': 'OK', 'temp': bme.temp(), 'humid': bme.humid() }
  else:
    result = { 'status': 'Err' }
  
  return jsonify(result)

#app.run(host='0.0.0.0', port=80, debug=True)
