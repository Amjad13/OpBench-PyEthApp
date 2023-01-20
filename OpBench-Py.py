import json
import os
import transactions
from state import State
from config import Env
import messages as pb
import utils as u
import block
import time
import db_leveldb
import sys
import numpy as np
import scipy as sp
import scipy.stats
import statistics
import xlrd


sys.setrecursionlimit(100000)
_env = Env(EphemDB())
# configure(':trace')

ExcelFileName = 'NonICO.xlsx'
workbook = xlrd.open_workbook(ExcelFileName)
worksheet = workbook.sheet_by_name("Non-ICO contracts' functions") # We need to read the data

num_rows = worksheet.nrows  #Number of Rows
num_cols = worksheet.ncols  #Number of Columns

result_data = []

def profile_vm_test(params, _):
    # file = open("Extime.csv", "a")
    pre = params['pre']
    exek = params['exec']
    env = params['env']
    # setup env
    blkh = block.BlockHeader(prevhash=env['previousHash'].decode('hex'), number=int(env['currentNumber']),
                             coinbase=env['currentCoinbase'],
                             difficulty=int(env['currentDifficulty']),
                             gas_limit=int(env['currentGasLimit']),
                             timestamp=int(env['currentTimestamp']))
    block.Block(blkh, db=_env)
    state = State(env=_env, block_number=int(env['currentNumber']),
                  block_coinbase=env['currentCoinbase'],
                  block_difficulty=int(env['currentDifficulty']),
                  gas_limit=int(env['currentGasLimit']),
                  timestamp=int(env['currentTimestamp']))
    # setup state
    for address, h in pre.items():
        state.set_nonce(address, int(h['nonce']))
        state.set_balance(address, int(h['balance']))
        state.set_balance("cd1722f3947def4cf144679da39c4c32bdc35681", int(h['balance']))
        state.set_code(address, h['code'][2:].decode('hex'))
        for k, v in h['storage'].iteritems():
            state.set_storage_data(address,
                                   u.big_endian_to_int(k[2:].decode('hex')),
                                   u.big_endian_to_int(v[2:].decode('hex')))
    # execute transactions
    sender = exek['origin']  # a party that originates a call
    recvaddr = exek['address']
    tx = transactions.Transaction(
                nonce=state.get_nonce(exek['caller']),
                gasprice=int(exek['gasPrice']),
                startgas=int(exek['gas']),
                to=recvaddr,
                value=int(exek['value']),
                data=exek['data'][2:].decode('hex'), r=1, s=2, v=27)
    tx._sender = sender
    ext = pb.VMExt(state, tx)
    def blkhash(n):
        if n >= ext.block_number or n < ext.block_number -256:
            return ''
        else:
            return u.sha3(str(n))
    ext.block_hash = blkhash        
    exTime = []
    _nonce = 0
    final_result = []
    gasUsed = []
    for curr_row in range(0, num_rows, 1):
        row_data = []

        for curr_col in range(0, num_cols, 1):
            data = worksheet.cell_value(curr_row, curr_col) # Read the data in the current cell
            # print(data)
            row_data.append(data)

        result_data.append(row_data)
        # ext = pb.VMExt(state, tx)

        def blkhash(n):
            if n >= ext.block_number or n < ext.block_number - 256:
                return ''
            else:
                return u.sha3(str(n))
        # ext.block_hash = blkhash
        _nonce1 = _nonce
        # print _nonce1
        exTime = []
        gasUsed = []
        for i in range(10):
            tx = transactions.Transaction(
                nonce=_nonce1,
                gasprice=int(exek['gasPrice']),
                startgas=int(exek['gas']),
                to="",
                value=int(exek['value']),
                data=result_data[curr_row][2][2:].decode('hex'),
                r=1, s=2, v=27)
            _nonce1 = _nonce1 + 1
            tx._sender = sender
            success, output, ext, gasused = pb.apply_transaction(state, tx)

            exTime.append(ext)
            gasUsed.append(gasused)
        _nonce = _nonce1
    # recorder = LogRecorder()
    # recorder = LogRecorder(log_config=":trace")
    
    from messages import ExTime, CreationTime
    t1 = time.time()
    # print "Balance before mining is: ", state.get_balance(sender)

    # tx1 = transactions.Transaction(
    #     nonce=1,
    #     gasprice=int(exek['gasPrice']),
    #     startgas=int(exek['gas']),
    #     to=output,
    #     value=int(exek['value']),
    #     data="".decode('hex'),
    #     r=1, s=2, v=27)
    # tx1._sender = sender
    # s2, o2 = pb.apply_transaction(state, tx1)

    # tx2 = transactions.Transaction(
    #     nonce=2,
    #     gasprice=int(exek['gasPrice']),
    #     startgas=int(exek['gas']),
    #     to=output,
    #     value=int(exek['value']),
    #     data="".decode('hex'),
    #     r=1, s=2, v=27)
    # tx2._sender = sender
    # s3, o3 = pb.apply_transaction(state, tx2)
    # print "Balance after mining is: ", state.get_balance(sender)
    # print ext.log_storage(output)
    from _vm import vm_execute, Message, CallData, lisexTime, _list
    msg = Message(tx.sender, tx.to, tx.value, tx.startgas, CallData([ord(x) for x in tx.data]))
    # vm_execute(ext, msg, ext.get_code(msg.code_address))
    success, gas_remained, comStack = vm_execute(ext, msg, exek['code'][2:].decode('hex'))
    state.commit()
    t2 = time.time()
    trace = recorder.pop_records()
    _time = [x['Time'] for x in trace if x['event'] == 'vm']
    average = []
    ops = [x['op'] for x in trace if x['event'] == 'vm']
    opdict = {}
    for op in ops:
        opdict[op] = opdict.get(op, 0) + 1
    for i in _time:
        for s, (t, ops) in i.iteritems():
            if ops == "PUSH1":
                average.append(t)
    _average = float(sum(average))/len(average)
    return {"ops": opdict, "time": t2 - t1}
    return {"Ops": exTime.get(0), "totalTime": t2 - t1, "Average": exTime.get(1)}
    average = []
    _average1 = []
    Gas = []
    print 'most ccommon', Most_Common(_list)
    print 'least common', least_common(_list)
    print _list.count("PUSH1")
    if _[:3] not in ['PUS', 'SWA', 'DUP', 'SHA', 'MST']:
        opo = filter(lambda c: not c.isdigit(), _)
    else:
        opo = _[:-1]
    for p in lisexTime:
        if p["opcs"] == opo:
            _average1.append(p["Time"])
    for p in lisexTime:
        if p["opcs"] == opo:
            average.append(p["Time"])
            Gas.append(p["GasUsed"])
    print opo        
    print lisexTime
    print opo
    _average = float(sum(average))/len(average)
    lisexTime.append({"average": _average})
    lower, upper = mean_confidence_interval(_average1, confidence=0.95)
    stdv = statistics.stdev(_average1)
    print len(_list)
    print {"average": _average}
    print Gas
    return {'Opcode': _, 'Occurrence': _list.count(opo), "Mean": _average, "Upper bound": upper, "Lower bound": lower, "95% Confidence Interval": (upper - lower)/2, "Used Gas": Gas[0], "Standard Deviation": stdv}
#     _crt = exTime
#     _crt1 = gasUsed
#     with open("_Extime3.csv", "a") as f:
#         w = csv.writer(f)
#         _crt.append("Break")
#         for v in _crt:
#             w.writerow([v])
#     with open("_Extime4.csv", "a") as f:
#         w = csv.writer(f)
#         for v in _crt1:
#             w.writerow([v])
#     return {'Result': " "}

def recursive_list(d):
    files = []
    dirs = [d]
    i = 0
    while i < len(dirs):
        if os.path.isdir(dirs[i]):
            children = [os.path.join(dirs[i], f) for f in os.listdir(dirs[i])]
            for f in children:
                dirs.append(f)
        elif dirs[i][-5:] == '.json':
                files.append(dirs[i])
        i += 1
    return files


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m-h, m+h


def prepare_files(vm_files):
    o = []
    # op = []
    for i, f in enumerate(vm_files):
        j = json.load(open(f))
        for _, t in j.items():
            o.append(profile_vm_test(t, _))
    # for i, f in enumerate(state_files):
    #     j = json.load(open(f))x
    #     for _, t in j.items():
    #         o.append(prepare_state_test(t))
    #         if not o[-1]["ops"]:
    #             o.pop()
    return o


open('GeneratorByteCodes.json', 'w').write(json.dumps(prepare_files(recursive_list(sys.argv[1])), indent=4))
