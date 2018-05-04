from bittrex import Bittrex
from time import sleep, time
from sys import exit
from datetime import datetime
from csv import reader


def find_order(big, small):
    output = {}
    for i in big:
        output['found'] = False
        for j in small:
            if i['OrderUuid'] == j['OrderUuid']:
                    output['found'] = True
                    break
        if output['found']:
                continue
        else:
            output['result'] = i
            break
    return output


def write_debug(text, file):
    file.write(text)
    file.write('\n')

fl = open('Debug.txt', 'w')
ts = time()
st = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
print('Application started...', st)
config = reader(open("config.csv"))
data = [i for i in config]
print('Reading configuration file...')
slaves = len(data[0]) - 1
print(slaves, ' Slave accounts detected')
master_api_key = data[0][1]
master_api_secret = data[1][1]
count = 1
slave_api = []
order_mapping = []
while count <= slaves:
    slave_api.append([data[2][count], data[3][count]])
    order_mapping.append({})
    count += 1
master_bittrex = Bittrex(api_key=master_api_key, api_secret=master_api_secret)
print ('Opening Master Account...')
master_open_orders = master_bittrex.get_open_orders()
if master_open_orders['success']:
    print('Master Open Orders = ', len(master_open_orders['result']))
else:
    print ('Error....', master_open_orders['message'], 'Application cannot run...please correct errors and restart application')
    print ('Application will terminate after 10 seconds...')
    sleep(10)
    exit()

master_order_history = master_bittrex.get_order_history()
print('Master History Orders = ', len(master_order_history['result']))
print('Opening Slave Accounts...')
slave_number = 0
for i in slave_api:
    slave_bittrex = Bittrex(api_key=i[0], api_secret=i[1])
    slave_open_orders = slave_bittrex.get_open_orders()
    slave_number += 1
    if slave_open_orders['success']:
        print('Slave', slave_number, 'Success')
    else:
        print ('Error....Slave', slave_number, slave_open_orders['message'], 'Application cannot run...please correct errors and restart application')
        print ('Application will terminate after 10 seconds...')
        sleep(10)
        exit()
print('Will start copying from now...please place a new order on Bittrex')

i_open_count = len(master_open_orders['result'])
i_history_count = len(master_order_history['result'])
i_count = i_open_count + i_history_count
time = 0
order_list = master_open_orders['result']
write_debug('Start loop', fl)
while time == 0:

    master_open_orders = master_bittrex.get_open_orders()
    if master_open_orders['success']:
        print('.')
        write_debug(str([len(master_open_orders['result']), len(master_order_history), master_open_orders]), fl)
    else:
        print('Connection problem...try again after 10 seconds')
        sleep(10)
        continue
    master_order_history = master_bittrex.get_order_history()
    if master_order_history['success']:
        print('.')

    else:
        print('Connection problem...try again after 10 seconds')
        sleep(10)
        continue
    count = len(master_open_orders['result']) + len(master_order_history['result'])

    if count == i_count:
        write_debug('Count = i_count', fl)
        i_open_count = len(master_open_orders['result'])
        i_history_count = len(master_order_history['result'])
        print('.')
        sleep(10)
        continue
    elif len(master_open_orders['result']) > i_open_count:
        write_debug('Open > i_Open', fl)
        slave_number = 0
        new_order = find_order(master_open_orders['result'], order_list)
        new_order = new_order['result']
        write_debug('New order is' + str(new_order), fl)
        order_list.append(new_order)
        print('\n New order detected in open orders', ',Time = ', new_order['Opened'].split('T')[0], new_order['Opened'].split('T')[1], ',Type =', new_order['OrderType'], ',Exchange =', new_order['Exchange'], ',Quantity =', new_order['Quantity'])
        for i in slave_api:
            slave_bittrex = Bittrex(api_key=i[0], api_secret=i[1])
            slave_number += 1
            if new_order['OrderType'] == 'LIMIT_SELL':
                write_debug('Limit sell in slave', fl)
                new_slave_order = slave_bittrex.sell_limit(market=new_order['Exchange'], quantity=new_order['Quantity'], rate=new_order['Limit'])
                if new_slave_order['success']:
                    print ('Order Copied Successfully to Slave', slave_number)
                    order_mapping[slave_number - 1][new_order['OrderUuid']] = new_slave_order['result']['uuid']
                else:
                    print ('Error in slave', slave_number, new_slave_order['message'])
                    order_mapping[slave_number - 1][new_order['OrderUuid']] = 0
            elif new_order['OrderType'] == 'LIMIT_BUY':
                write_debug('Limit buy in slave', fl)
                new_slave_order = slave_bittrex.buy_limit(market=new_order['Exchange'], quantity=new_order['Quantity'], rate=new_order['Limit'])
                if new_slave_order['success']:
                    print ('Order Copied Successfully to Slave', slave_number)
                    order_mapping[slave_number - 1][new_order['OrderUuid']] = new_slave_order['result']['uuid']
                else:
                    print ('Error in slave', slave_number, new_slave_order['message'])
                    order_mapping[slave_number - 1][new_order['OrderUuid']] = 0
            else:
                print ('Order type not supported')
        i_open_count += 1
        i_count = i_open_count + i_history_count
        sleep(10)
    elif len(master_order_history['result']) > i_history_count:
        slave_number = 0
        new_order = master_order_history['result'][0]
        print('\n New order detected in history orders', ',Time = ', new_order['TimeStamp'].split('T')[0], new_order['TimeStamp'].split('T')[1], ',Type =', new_order['OrderType'], ',Exchange =', new_order['Exchange'], ',Quantity =', new_order['Quantity'])
        write_debug('History > i_History', fl)
        for i in slave_api:
            slave_bittrex = Bittrex(api_key=i[0], api_secret=i[1])
            slave_number += 1
            if new_order['OrderType'] == 'LIMIT_SELL':
                new_slave_order = slave_bittrex.sell_limit(market=new_order['Exchange'], quantity=new_order['Quantity'], rate=new_order['Limit'])
                if new_slave_order['success']:
                    print ('Order Copied Successfully to Slave', slave_number)
                else:
                    print ('Error in slave', slave_number, new_slave_order['message'])
            elif new_order['OrderType'] == 'LIMIT_BUY':
                new_slave_order = slave_bittrex.buy_limit(market=new_order['Exchange'], quantity=new_order['Quantity'], rate=new_order['Limit'])
                if new_slave_order['success']:
                    print ('Order Copied Successfully to Slave', slave_number)
                else:
                    print ('Error in slave', slave_number, new_slave_order['message'])
        i_history_count += 1
        i_count = i_open_count + i_history_count
        sleep(10)
    else:
        print('\n Order cancellation detected...scanning open orders in slave accounts')
        cancelled_order = 0
        for i in order_list:
            found = False
            for j in master_open_orders['result']:
                if i['OrderUuid'] == j['OrderUuid']:
                    found = True
                    break
            if found:
                continue
            else:
                cancelled_order = i
                write_debug('Cancel found', fl)
                order_list.remove(i)
                break
        if cancelled_order == 0:
            print('Cancelled order not found...order was not placed while the program is running')
        else:
            print('Cancelled order found...', ',Time = ', cancelled_order['Opened'].split('T')[0], cancelled_order['Opened'].split('T')[1], ',Type =', cancelled_order['OrderType'], ',Exchange =', cancelled_order['Exchange'], ',Quantity =', cancelled_order['Quantity'])
            slave_number = 0
            for i in order_mapping:
                slave_bittrex = Bittrex(api_key=slave_api[slave_number][0], api_secret=slave_api[slave_number][1])
                slave_number += 1
                if i[cancelled_order['OrderUuid']] == 0:
                    print ('Order was not executed to slave', slave_number)
                else:
                    new_slave_cancel = slave_bittrex.cancel(uuid=i[cancelled_order['OrderUuid']])
                    i[cancelled_order['OrderUuid']] = 0
                    if new_slave_cancel:
                        print ('Order Cancelled Successfully from Slave', slave_number)
                    else:
                        print ('Error in slave', slave_number, new_slave_cancel['message'])
        i_open_count -= 1
        i_count = i_open_count + i_history_count
        sleep(10)
