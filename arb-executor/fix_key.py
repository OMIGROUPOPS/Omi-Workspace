key = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEArjxM2ctafmgbo2x+An3grOUu780Wa58UDfZe7a29D8VaYXzM
83WHwlRyIoor9TL8FLz0prhe7DxbwDENfL22owa1vyECjhaQEX4/iqSgG2GcvY+/
B6OPF8HYE3sP10IQcZnUHvx3vt835nFCLyc6vBVv+x9oAcNhlofli6Igp/MGtrPp
C3doAKAr0tUpFwGMOjr2ucQdHM5Hza3cJv+/UQ0z4wcyXdqTkXeqjaJbWAjOhkqK
AC4fHy1U/1h76r7fMPabhxdMMbVms2Ivku1aoavF0/xyAlaih2dgi0iz6btrSPaU
MVoWQbhTMtQxMDaDZoslFp9otbYUauEHHhrnQQIDAQABAoIBAAVX4P53Tv/AwoNe
QUhQ7CWCX6Kn8H6dpAlpb+tVRzNE3XHPRhcN/R/NSIcz/uvlkXv8U+iJ/UnO3eor
kBQlNfvA14hiGhhZokl/nui8TxLP5LUMOpdp2EXg/dt/8K2aUc7+DoQ9wH3tDb7Y
v4uIk8XcxpUxaWi9SmwJxKdl1p9TTY7PcDvin2sg1rggWDlKpWs7R7zi9KAFWH3d
gltuJx4A5Bc+CstBPDiM3eqnz3ynuikldDq0+ytZyXWY7KKLLvfMON5qgq0kUCsf
5rVN3IaeK8y6QFNKq6iScQswx/jfDBa5pdXbNzMqIksR2papO6eTZ9riQORm5QaD
eRaxI70CgYEA39hcyMQ7fhqEiSU7P2MdCXPcTzMaA/90Xqc3F4iWA6J+06ye9Go1
w25O+zohil1SmBEjHd2iKBisk4HiJF18iaRYXsorGDKguGyRhOX0BHJjHQg+UJbJ
K5o5zxBDwFjuiw3gB9AKWKQ6TEUrbsJgA3iG+htF6+WAo/sT8nRbj+UCgYEAx0Oa
gZCWkfb/b9eKTSM2NVsZf50jvUDbJOvRJM2omZytXH9ERImRp8X21er1fKOYwztO
is6hUzTyFGJ6bej7mCenet8TDLa86qalfWZU1gDLWf7tVrwKR5uYdQcA5B/y1YPN
bFJ5lvaUgBloQrKkkdT/ae+q1eorlgYd6gM2bC0CgYBw2nNE4PIhjJr/Td8GASE1
j80lvNzD4Tm5MtKqsbj4Eieg7mmhTh7W7bkyHcelK5GlixZKS2AimPYA1D3AGcXc
2xeWipSZeYTgFhRzjT+uMkFX9Lz+Aldf/Txh8ZBG3E8/mfo11iQxNnMR2tmf2K1x
coWSeMeSu71UbxRKa3FyJQKBgByTDzcBOvZXiy3IpOaG5CEmnTN1n0hmYoaa4nT6
oPDWTO30uh9x8tcyRkFK3kUvWJq2iH7TPsMl1okhzhiwzlN1bEjscFjkY5bqqtSe
tg+yMXcIXZSQhpDaOTSe+nu8MSB5NB4SfakuVwE/o3ndEEhxWOciHUdruzBaVDPY
nhdJAoGAI7D30RX9nHEoIvv//BxHO5cjllWs4YPwpvOVpzOk3+vLxJ/Ye9mvnq4K
e6FrqIzgqUVPWduP23Tv7ekNQnpAO1xFPRiVM57EN2VjkkKUAV3q3Gz7/2aGEXMn
uCqd9+Qe06086s/us3yM30hxWMUvWgEL1XBDWlsb6BaPIsr/Mdk=
-----END RSA PRIVATE KEY-----"""

import re
with open('arb_executor_v4.py', 'r') as f:
    content = f.read()

new_content = re.sub(r'KALSHI_PRIVATE_KEY = """.*?"""', 'KALSHI_PRIVATE_KEY = """' + key + '"""', content, flags=re.DOTALL)

with open('arb_executor_v4.py', 'w') as f:
    f.write(new_content)

print('Fixed!')
