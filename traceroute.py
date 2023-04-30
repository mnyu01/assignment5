from socket import *
import os
import sys
import struct
import time
import select
import binascii
import pandas as pd

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 60
TIMEOUT = 2.0
TRIES = 1


def checksum(string):

    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def build_packet():

    C_S = 0

    if sys.platform == 'darwin':

        C_S = htons(C_S) & 0xffff
    else:
        C_S = htons(C_S)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, C_S, MAX_HOPS, TRIES)
    data = struct.pack("d", time.time())
    packet = header + data
    return packet


def get_route(hostname):
    timeLeft = TIMEOUT
    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
    destAddr = gethostbyname(hostname)

    for ttl in range(1, MAX_HOPS):
        for tries in range(TRIES):
            mySocket = socket(AF_INET, SOCK_RAW, ICMP_ECHO_REQUEST)
            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)
            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t = time.time()
                startedSelect = time.time()
                whatReady = select.select([mySocket], [], [], timeLeft)
                # print(whatReady)
                howLongInSelect = (time.time() - startedSelect)
                if whatReady[0] == []:  # Timeout
                    # print(whatReady[0])
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame({'Hop Count': ttl, 'Try': TRIES, 'IP': destAddr, 'Hostname': hostname,
                                'Response Code': 'timeout'}, index=[ttl])
                df = pd.concat([df, response])
                print(df)
                recvPacket, addr = mySocket.recvfrom(1024)
                print(mySocket)
                print(recvPacket)
                print(addr)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect
                if timeLeft <= 0:
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame({'Hop Count': ttl, 'Try': ttl, 'IP': 'timeout', 'Hostname': 'timeout',
                                             'Response Code': 0}, index=[ttl])
                    df = pd.concat([df, response])
                    print(df)

            except Exception as e:
                print(e)  # uncomment to view exceptions
                continue

            else:

                try:  # try to fetch the hostname of the router that returned the packet - don't confuse with the hostname that you are tracing
                    # Fill in start
                    icmp = recvPacket[20:28]
                    # print(icmp)
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame({'Hop Count': ttl, 'Try': TRIES, 'IP': destAddr, 'Hostname': hostname,
                                             'Response Code': 0}, index=[ttl])
                    df = pd.concat([df, response])
                    print(df)
                    # Fill in end
                except error:  # if the router host does not provide a hostname use "hostname not returnable"
                    # Fill in start
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame(
                        {'Hop Count': ttl, 'Try': TRIES, 'IP': 'timeout', 'Hostname': 'hostname not returnable',
                         'Response Code': 0}, index=[ttl])
                    df = pd.concat([df, response])
                    # Fill in end

                if type == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    # Fill in start
                    rtt = timeReceived - timeSent
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame(
                        {'Hop Count': ttl, 'Try': TRIES, 'IP': destAddr, 'Hostname': hostname,
                         'Response Code': 11}, index=[ttl])
                    df = pd.concat([df, response])
                    print(df)
                    # You should update your dataframe with the required column field responses here
                    # Fill in end
                elif type == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    # Fill in start
                    rtt = timeReceived - timeSent
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame(
                        {'Hop Count': ttl, 'Try': TRIES, 'IP': destAddr, 'Hostname': hostname,
                         'Response Code': 3}, index=[ttl])
                    df = pd.concat([df, response])
                    print(df)
                    # You should update your dataframe with the required column field responses here
                    # Fill in end
                elif type == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    # Fill in start
                    rtt = timeReceived - timeSent
                    df = pd.DataFrame(columns=['Hop Count', 'Try', 'IP', 'Hostname', 'Response Code'])
                    response = pd.DataFrame(
                        {'Hop Count': ttl, 'Try': TRIES, 'IP': destAddr, 'Hostname': hostname,
                         'Response Code': type}, index=[ttl])
                    df = pd.concat([df, 0])
                    print(df)
                    # You should update your dataframe with the required column field responses here
                    # Fill in end
                    return df
                else:
                    # Fill in start
                    print('DataFrame extension!')
                    # If there is an exception/error to your if statements, you should append that to your df here
                    # Fill in end
                    break
    return df


if __name__ == '__main__':
    get_route("google.co.il")