#!/usr/bin/env python3
"""
Tiny assembler for the 8-bit emulator.
Usage:
  ./asm.py input.asm -o program.bin
Assembly syntax (examples below):
  ; comment
  LDI A, 65      ; load immediate 65 into A
  STR A, 0x80    ; store A to memory address 0x80
  JMP start
  DB 0x41, 0x42  ; raw bytes
Labels:
  start:
  ... JMP start
Registers: A or B
Supported mnemonics: NOP, LDI, MOV, STR, ADD, SUB, JMP, JZ, JNZ, OUT, IN, HLT, DB
"""
import sys, re, argparse

OP = {
    'NOP': 0x00,
    'LDI': 0x10,
    'MOV': 0x11,
    'STR': 0x12,
    'ADD': 0x20,
    'SUB': 0x21,
    'JMP': 0x30,
    'JZ' : 0x31,
    'JNZ': 0x32,
    'OUT': 0x40,
    'IN' : 0x41,
    'HLT': 0xFF,
}

REGS = {'A':0, 'B':1}

def tokenize(line):
    # remove comments
    line = line.split(';',1)[0].strip()
    if not line:
        return []
    # split respecting quotes (both ' and ")
    tokens = []
    current = ''
    in_quote = False
    quote_char = ''
    for ch in line:
        if in_quote:
            current += ch
            if ch == quote_char:
                in_quote = False
        else:
            if ch in ('"', "'"):
                in_quote = True
                quote_char = ch
                current += ch
            elif ch in (' ', '\t', ','):
                if current:
                    tokens.append(current)
                    current = ''
            else:
                current += ch
    if current:
        tokens.append(current)
    return tokens

def parse_value(token, labels):
    # number (hex 0x.. or decimal) or label
    token = token.strip()
    if token.startswith("'") and token.endswith("'") and len(token)==3:
        return ord(token[1])
    if token.startswith("0x"):
        return int(token,16)
    if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
        return int(token,10) & 0xFF
    if token in labels:
        return labels[token]
    raise ValueError(f"Unknown value: {token}")

def assemble(lines):
    # first pass: labels and DB size
    labels = {}
    pc = 0
    parsed = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(';'):
            continue
        if line.endswith(':'):
            lbl = line[:-1].strip()
            labels[lbl] = pc
            continue
        toks = tokenize(line)
        if not toks: continue
        op = toks[0].upper()
        parsed.append((pc, op, toks[1:]))
        # estimate size
        if op == 'DB':
            # count of following values (split by commas already removed)
            args = ' '.join(toks[1:]).split(',')
            pc += len(args)
        elif op in ('LDI', 'MOV', 'STR'):
            pc += 3
        elif op in ('ADD','SUB'):
            pc += 3
        elif op in ('JMP','JZ','JNZ'):
            pc += 2
        elif op in ('OUT','IN'):
            pc += 2
        elif op in ('NOP','HLT'):
            pc += 1
        else:
            raise ValueError(f"Unknown op {op}")
    # second pass: generate bytes
    out = []
    for (addr, op, args) in parsed:
        o = op.upper()
        if o == 'DB':
            # args might be comma separated in one token; handle split by comma
            data_tokens = []
            for a in args:
                data_tokens.extend([x for x in a.split(',') if x!=''])
            for tok in data_tokens:
                tok = tok.strip()
                if tok.startswith('"') and tok.endswith('"'):
                    s = tok[1:-1]
                    for ch in s:
                        out.append(ord(ch) & 0xFF)
                else:
                    out.append(parse_value(tok, labels) & 0xFF)
            continue
        if o == 'LDI':
            # LDI A, imm
            reg = args[0].strip().rstrip(',').upper()
            imm = args[1].strip()
            out.append(OP['LDI'])
            out.append(REGS[reg])
            out.append(parse_value(imm, labels) & 0xFF)
            continue
        if o == 'MOV':
            # MOV A, addr
            reg = args[0].strip().rstrip(',').upper()
            addr_tok = args[1].strip()
            out.append(OP['MOV'])
            out.append(REGS[reg])
            out.append(parse_value(addr_tok, labels) & 0xFF)
            continue
        if o == 'STR':
            reg = args[0].strip().rstrip(',').upper()
            addr_tok = args[1].strip()
            out.append(OP['STR'])
            out.append(REGS[reg])
            out.append(parse_value(addr_tok, labels) & 0xFF)
            continue
        if o == 'ADD':
            r1 = args[0].strip().rstrip(',').upper()
            r2 = args[1].strip().upper()
            out.append(OP['ADD'])
            out.append(REGS[r1])
            out.append(REGS[r2])
            continue
        if o == 'SUB':
            r1 = args[0].strip().rstrip(',').upper()
            r2 = args[1].strip().upper()
            out.append(OP['SUB'])
            out.append(REGS[r1])
            out.append(REGS[r2])
            continue
        if o in ('JMP','JZ','JNZ'):
            out.append(OP[o])
            addr_tok = args[0].strip()
            out.append(parse_value(addr_tok, labels) & 0xFF)
            continue
        if o == 'OUT':
            reg = args[0].strip().upper()
            out.append(OP['OUT'])
            out.append(REGS[reg])
            continue
        if o == 'IN':
            reg = args[0].strip().upper()
            out.append(OP['IN'])
            out.append(REGS[reg])
            continue
        if o == 'NOP':
            out.append(OP['NOP'])
            continue
        if o == 'HLT':
            out.append(OP['HLT'])
            continue
        raise ValueError(f"Unhandled op {o}")
    return bytes(out)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("-o","--outfile", default="out.bin")
    args = parser.parse_args()
    with open(args.infile, "r") as f:
        lines = f.readlines()
    try:
        data = assemble(lines)
    except Exception as e:
        print("Assembly error:", e)
        sys.exit(1)
    with open(args.outfile, "wb") as f:
        f.write(data)
    print(f"Wrote {len(data)} bytes to {args.outfile}")

if __name__ == "__main__":
    main()
