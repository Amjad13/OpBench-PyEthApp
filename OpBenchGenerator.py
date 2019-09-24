import random
import json
from pyethereum import utils
from pyethereum import opcodes

opcodes = {
    # 0x40: ['BLOCKHASH', 1, 1, 20]
    # 0x55: ['SSTORE', 2, 0, 0],
    # 0x54: ['SLOAD', 1, 1, 50],
    # 0x01: ['ADD', 2, 1, 3],
    # 0x02: ['MUL', 2, 1, 5],
    # 0x04: ['DIV', 2, 1, 5],
    # 0x03: ['SUB', 2, 1, 3],
    # 0x50: ['POP', 1, 0, 2],
    # 0x20: ['SHA3', 2, 1, 30],
    # 0x52: ['MSTORE', 2, 0, 3],
    # 0x53: ['MSTORE8', 2, 0, 3]
    # 0x37: ['CALLDATACOPY', 3, 0, 3],
    # 0x20: ['SHA3', 2, 1, 30],
    # 0x51: ['MLOAD', 1, 1, 3]
    # 0x35: ['CALLDATALOAD', 1, 1, 3]
    0x3c: ['EXTCODECOPY', 4, 0, 20],
    # 0x39: ['CODECOPY', 3, 0, 3],
    # 0x3b: ['EXTCODESIZE', 1, 1, 20],
    # 0x0a: ['EXP', 2, 1, 10],
    # 0x01: ['ADD', 2, 1, 3],
    # 0x31: ['BALANCE', 1, 1, 20],
    # 0x01: ['ADD', 2, 1, 3],
    # 0x3d: ['RETURNDATASIZE', 0, 1, 2],
    # 0x3e: ['RETURNDATACOPY', 3, 0, 3],
            }
#
# for i in range(1, 33):
#     opcodes[0x5f + i] = ['PUSH' + str(i), 0, 1, 3]
# # # for i in range(1, 17):
# # #     opcodes[0x7f + i] = ['DUP' + str(i), i, i + 1, 3]
# # #     opcodes[0x8f + i] = ['SWAP' + str(i), i + 1, i + 1, 3]

push_params = [range(1, 3), range(4, 8), range(9, 16), range(17, 32)]
codesize_params = [[1000, 1000]]

# for i in range(11):
#     opcodes[0x5f + i] = ['PUSH' + str(i), 0, 1, 3]
# print opcodes


def generate_op_tests():
    out = {}
    for opcode, (name, inargs, outargs, _) in opcodes.items():
        _subid = 0
        for push_depths in push_params:
            for jump_num, code_size in codesize_params:
                if name in ['DELEGATECALL', 'LOG0', 'LOG1', 'LOG2', 'LOG3', 'LOG4', 'CALL', 'CREATE', 'CALLCODE', 'RETURNDATACOPY', 'RETURNDATASIZE', 'CALLBLACKBOX', 'STATICCALL', 'REVERT', 'RETURN', 'STOP', 'INVALID', 'JUMP', 'JUMPI', 'SUICIDE']:
                    continue
                if name == 'SSTORE':
                    jump_num /= 10
                c = ''
                if name[:4] == 'PUSH':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        v = int(name[4:])
                        w = random.randrange(256**v)
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                elif name[:3] == 'DUP':
                    if push_depths != push_params[0]:
                        continue
                    for _ in range(inargs):
                        v = push_depths[_ * len(push_depths) // code_size]
                        w = random.randrange(256**v)
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                    for i in range(code_size):
                        c += chr(opcode)
                    for i in range(outargs):
                        c += chr(0x50)
                elif name[:4] == "SWAP":
                    if push_depths != push_params[0]:
                        continue
                    for _ in range(inargs):
                        v = push_depths[_ * len(push_depths) // code_size]
                        w = random.randrange(256**v)
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                    for i in range(code_size):
                        c += chr(opcode)
                    for i in range(outargs):
                        c += chr(0x50)
                elif name == "POP":
                    if push_depths != push_params[0]:
                        continue
                    for _ in range(code_size):
                        v = push_depths[_ * len(push_depths) // code_size]
                        w = random.randrange(256**v)
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                        c += '\x50'
                    # for i in range(code_size):
                    #     c += chr(opcode)
                elif name == 'SHA3':
                    if push_depths != push_params[0]:
                        continue
                    v = 32
                    w = random.randrange(256**v)
                    c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                    _w = 0
                    c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                    c += '\x52' 
                    c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)   
                    _w += 32
                    c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                    c += '\x52'
                    c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)   
                    _w += 64
                    c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                    c += '\x52'
                    c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)   
                    _w += 128
                    c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                    c += '\x52'
                    # c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)   
                    for i in range(code_size):
                        c += chr(0x59)
                        c += '\x60\x00'
                        c += chr(opcode)
                        c += '\x50'
                    c += '\x60\x48' + '\x60\x00' + '\x53' + '\x60\x45' + '\x60\x01' + '\x53' + '\x60\x4c' + '\x60\x02' + '\x53' + '\x60\x4c' + '\x60\x03' + '\x53' + '\x60\x4f' + '\x60\x04' + '\x53' + '\x60\x48' + '\x60\x05' + '\x53' + '\x60\x45' + '\x60\x06' + '\x53' + '\x60\x4c' + '\x60\x07' + '\x53' + '\x60\x4c' + '\x60\x08' + '\x53' + '\x60\x4f' + '\x60\x09' + '\x53'+ '\x60\x48' + '\x60\x0a' + '\x53' + '\x60\x45' + '\x60\x0b' + '\x53' + '\x60\x4c' + '\x60\x0c' + '\x53' + '\x60\x4c' + '\x60\x0d' + '\x53' + '\x60\x4f' + '\x60\x0e' + '\x53'+ '\x60\x48' + '\x60\x0f' + '\x53' + '\x60\x45' + '\x60\x10' + '\x53' + '\x60\x4c' + '\x60\x11' + '\x53' + '\x60\x4c' + '\x60\x12' + '\x53' + '\x60\x4f' + '\x60\x13' + '\x53'+ '\x60\x48' + '\x60\x14' + '\x53' + '\x60\x45' + '\x60\x15' + '\x53' + '\x60\x4c' + '\x60\x16' + '\x53' + '\x60\x4c' + '\x60\x17' + '\x53' + '\x60\x4f' + '\x60\x18' + '\x53'+ '\x60\x48' + '\x60\x19' + '\x53' + '\x60\x45' + '\x60\x1a' + '\x53' + '\x60\x4c' + '\x60\x1b' + '\x53' + '\x60\x4c' + '\x60\x1c' + '\x53' + '\x60\x4f' + '\x60\x1d' + '\x53'+ '\x60\x48' + '\x60\x1e' + '\x53' + '\x60\x45' + '\x60\x1f' + '\x53' + '\x60\x1f' + '\x60\x00'
                    for i in range(code_size):
                        c += chr(opcode)
                        c += '\x50'
                elif name == 'MLOAD':
                    if push_depths != push_params[0]:
                        continue
                    w = random.randrange(256**32)
                    c += chr(0x7f) + utils.zpad(utils.encode_int(w), 32)
                    c += '\x60\x00' + '\x52' + '\x60\x00'
                    for i in range(code_size):
                        c += chr(opcode)
                        c += '\x50' + '\x60\x00'
                elif name == 'MSTORE':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        v = 32
                        w = random.randrange(256**v)
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                        _w = random.randrange(256**1)
                        c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                        c += chr(opcode)
                elif name == 'MSTORE8':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        w = random.randrange(256)
                        c += chr(0x5f + 1) + utils.zpad(utils.encode_int(w), 1)
                        _w = random.randrange(32)
                        c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                        c += chr(opcode)
                elif name == 'CALLDATALOAD':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        c += '\x60\x00'
                        c += chr(opcode)
                        c += '\x50'
                elif name == 'CALLDATACOPY':
                    if push_depths != push_params[0]:
                        continue
                    v = 32
                    w = random.randrange(256**v)
                    c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                    _w = 0
                    c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                    c += '\x52'     
                    for i in range(code_size):
                        c += '\x36\x60\x00'
                        _w = 256
                        c += chr(0x5f + 2) + utils.zpad(utils.encode_int(_w), 1)
                        c += chr(opcode)
                elif name == 'EXTCODECOPY':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        c += '\x73\xee\xefSt\xfc\xe5\xed\xbc\x8e*\x86\x97\xc1S1g~n\xbf\x0b' + '\x3b' + '\x60\x00\x60\x00' '\x73\xee\xefSt\xfc\xe5\xed\xbc\x8e*\x86\x97\xc1S1g~n\xbf\x0b'
                        c += chr(opcode)
                elif name == 'EXTCODESIZE':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        c += '\x73\x0fW.R\x95\xc5\x7f\x15\x88o\x9b&>/m-l{^\xc6'
                        c += chr(opcode)
                elif name == 'CODECOPY':
                    if push_depths != push_params[0]:
                        continue
                    # coded = '`r`\xb5\x01P`\xb9`\xb4\x01P`\x8a`S\x01P`\xa4`z\x01P`\x92`\xc3\x01P`J'
                    # c += coded
                    for i in range(code_size):
                        c += '\x73\x0fW.R\x95\xc5\x7f\x15\x88o\x9b&>/m-l{^\xc6' 
                        c += '\x38\x60\x00\x60\x00' + chr(opcode)
                elif name == "BALANCE":
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        c += '\x73\x0fW.R\x95\xc5\x7f\x15\x88o\x9b&>/m-l{^\xc6'
                        c += chr(opcode)
                elif name == 'SSTORE':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        v = 32
                        w = random.randrange(256**v)
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                        _w = 86
                        c += chr(0x5f + 1) + utils.zpad(utils.encode_int(_w), 1)
                        c += chr(opcode)
                elif name == 'SLOAD':
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        v = 1
                        w = 86
                        c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                        c += chr(opcode)
                elif name == "BLOCKHASH":
                    for i in range(code_size):
                        for i in range(inargs):
                            v = 1
                            w = random.randrange(256**v)
                            c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), 1)
                        c += chr(opcode)
                        # for _ in range(outargs):
                        #     c += chr(0x50)
                elif name == "EXP":
                    if push_depths != push_params[0]:
                        continue
                    for i in range(code_size):
                        for _ in range(inargs):
                            v = 32
                            w = random.randrange(256**v)
                            c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), 1)
                        c += chr(opcode)
                        for _ in range(outargs):
                            c += chr(0x50)
                # elif name == "RETURNDATACOPY":
                #     if push_depths != push_params[0]:
                #         continue
                #     for i in range(code_size):
                #         c += '\x60\x00\x60\x00\x60\x00'
                #         c += chr(opcode)
                # elif name == "RETURNDATASIZE":
                #     if push_depths != push_params[0]:
                #         continue
                #     for i in range(code_size):
                #         c += chr(opcode)
                else:
                    for i in range(code_size):
                        for _ in range(inargs):
                            v = push_depths[i * len(push_depths) // code_size]
                            w = random.randrange(256**v)
                            c += chr(0x5f + v) + utils.zpad(utils.encode_int(w), v)
                        c += chr(opcode)
                        for _ in range(outargs):
                            c += chr(0x50)
                # PUSH1 0 MLOAD . DUP1 . PUSH1 1 ADD PUSH1 0 MSTORE . PUSH2 <jumps> GT PUSH1 0 JUMPI
                # c += '\x60\x00\x51' + '\x80' + '\x60\x01\x01\x60\x00\x52' + \
                #     '\x61'+chr(jump_num // 256) + chr(jump_num % 256) + '\x11\x60\x00\x57'

                o = o = {
                    "callcreates": [],
                    "env": {
                        "currentCoinbase": "2adc25665018aa1fe0e6bc666dac8fc2697ff9ba",
                        "currentDifficulty": "256",
                        "currentGasLimit": "1000000000",
                        "currentNumber": "257",
                        "currentTimestamp": "1",
                        "previousHash": "5e20a0453cecd065ea59c37ac63e079ee08998b6045136a8ce6635c7912ec0b6"
                    },
                    "exec": {
                        "address": "0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6",
                        "caller": "0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6",
                        "code": "0x"+c.encode('hex'),
                        "data": "0xc4ede3d3c49e38e7351405f35621bafce3a2ef3cef0af0a119fe3772ffcc2a8a0aa48ac7dc2bdc26dfad6de18cd9ea15a119bd676f5b3e492f2c2a5cc3ed6f6182041cda117a1fdc958df9e53b3f957d676f15003da9d6792800b612d8f9ec6d85ea7ca5f70789cf04137db582e89c73fcd3fafeb24db17c91ef9950eca6d3c194be97be7ecae7c2892fb915619d4845dcbd9510544a9cb88a54a7baa313d85c196387eeaeaddf8c03d2d0a222bf3b94c87c9ad20180f821db4f85347247e650200bc5b1b045f0da19aee3e94c585bb08bc47586962ec3269f66318ab2356e6a786dc5b0b51af3dc0d7751f22a63301baa9383c2c5e4d953e558b09af532e075",
                        "gas": "100000000",
                        "gasPrice": "100000000000000",
                        "origin": "cd1722f3947def4cf144679da39c4c32bdc35681",
                        "value": "1000000000000000000"
                    },
                    "pre": {
                        "0f572e5295c57f15886f9b263e2f6d2d6c7b5ec6": {
                            "balance": "1000000000000000000",
                            "code": "0x36303732363062353031353036306239363062343031353036303861363035",
                            "nonce": "0",
                            "storage": {"0x56": "0x0f5b2ebf118c64ede45e3d5f4436fd219110d1f20442c6f153a22c39a70bf7df"}
                        }
                    },
                    "gas": "1000000000",
                    "logs": [],
                    "out": "0x"
                }
                out[name + str(_subid)] = o
                _subid += 1
    return out


open('codyts.json', 'w').write(json.dumps(generate_op_tests(), indent=4))
