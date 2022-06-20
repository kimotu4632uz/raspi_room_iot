import math
import pigpio

def send(code):
  pi = pigpio.pi()
  if not pi.connected:
    return False
  
  # LEDにつながっているGPIO番号
  gpio_send = 13

  pi.set_mode(gpio_send, pigpio.OUTPUT)

  # 生成できる波形の長さには制限があるので、種類とcodeの長さごとにまとめて節約する
  mark_wids = {}  # Mark(38kHzパルス)波形, key:長さ, value:ID
  space_wids = {}  # Speace(待機)波形, key:長さ, value:ID
  send_wids = [0] * len(code)  # 送信する波形IDのリスト

  pi.wave_clear()

  for i in range(len(code)):
    if i % 2 == 0:
      # 同じ長さのMark波形が無い場合は新しく生成
      if code[i] not in mark_wids:
        pulses = []
        n = code[i] // 26  # 38kHz = 26us周期の繰り返し回数
        for j in range(n):
          pulses.append(pigpio.pulse(1 << gpio_send, 0, 8))  # 8us highパルス
          pulses.append(pigpio.pulse(0, 1 << gpio_send, 18))  # 18us lowパルス
        pi.wave_add_generic(pulses)
        mark_wids[code[i]] = pi.wave_create()
      send_wids[i] = mark_wids[code[i]]
    else:
      # 同じ長さのSpace波形が無い場合は新しく生成
      if code[i] not in space_wids:
        pi.wave_add_generic([pigpio.pulse(0, 0, code[i])])
        space_wids[code[i]] = pi.wave_create()
      send_wids[i] = space_wids[code[i]]

  pi.wave_chain(send_wids)
  pi.wave_clear()
  pi.stop()

  return True


def aeha_encode(cc, d0, dn, chksum=None):
  cc_p = (cc[0] >> 4) ^ (cc[0] & 0x0f) ^ (cc[1] >> 4) ^ (cc[1] & 0x0f)
  cc.append((d0 << 4) | cc_p)
  data = cc + dn

  if chksum is not None:
    chksum(data)

  t = 425
  code = []

  # Leader
  code.append(t * 8)
  code.append(t * 4)

  # Data
  for byte in data:
    d = byte
    for i in range(8):
      bit = d & 1
      if bit == 0:
        code.append(t)
        code.append(t)
      else:
        code.append(t)
        code.append(t * 3)
      d = d >> 1
  
  # stop bit
  code.append(t)

  return code


def nec_encode(cc, dn):
  data = cc + dn

  t = 560
  code = []

  # Leader
  code.append(t * 16)
  code.append(t * 8)

  # Data
  for byte in data:
    d = byte
    for i in range(8):
      bit = d & 1
      if bit == 0:
        code.append(t)
        code.append(t)
      else:
        code.append(t)
        code.append(t * 3)
      d = d >> 1
  
  # stop bit
  code.append(t)

  return code


# father light
#def light(level, channel=1):
#  cc = [0x03, 0x74]
#  d0 = 1 << 4 | level << 2 | 1
#  d1 = d0 ^ 0xFF
#
#  return nec_encode(cc, [d0,d1])


# me light
def light(level, channel=1):
  cc = [0x2C, 0x52]
  d0 = 0x0
  d1 = 1 << 5 | channel << 3 | 1 << 2 | level

  return aeha_encode(cc, d0, [d1], lambda d: d.append(d[2] ^ d[3]))


def aircon(power, mode, temp, wind_level, wind_v, wind_h, timer_type=0, timer_time=0):
  cc = [0x52, 0xAE]
  d0 = 0xC
  dn = [0x26, 0xD9]

  if wind_h == 0:
    b_wind_h_1 = 0b00
    b_wind_h_2 = 0b00
  elif wind_h == 8:
    b_wind_h_1 = 0b10
    b_wind_h_2 = 0b00
  else:
    b_wind_h_1 = (wind_h - 1) % 4
    b_wind_h_2 = math.ceil(wind_h / 4)
  
  b_wind_v = wind_v + 1 if wind_v > 0 else wind_v
  b_wind_level = wind_level + 1 if wind_level > 0 else wind_level

  b_temp = temp - 17

  d7 = b_wind_h_1 << 6 | b_wind_h_2 << 2 | (b_wind_v >> 2) << 1
  dn.append(d7 ^ 0xff)
  dn.append(d7)

  d9 = b_wind_level << 5 | (b_wind_v & 0b011) << 3 | timer_type
  dn.append(d9 ^ 0xff)
  dn.append(d9)

  d11 = b_temp << 4 | power << 3 | mode
  dn.append(d11 ^ 0xff)
  dn.append(d11)

  if timer_type != 0:
    if timer_type & 1 == 1:
      timer_bin = '{:03x}000'.format(timer_time)
    else:
      timer_bin = '{:06x}'.format(timer_time)

    timer_bytes = []

    for i in [0,2,4]:
      timer_bytes.append(int(timer_bin[i:i+2], 16))
      timer_bytes.append(int(timer_bin[i:i+2], 16) ^ 0xff)

    dn.extend(reversed(timer_bytes))

  return aeha_encode(cc, d0, dn)
