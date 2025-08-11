#!/usr/bin/env python3
"""
Tiny 8-bit emulator
Usage:
  ./emulator.py program.bin
  ./emulator.py        # runs REPL monitor (blank memory)
Features:
- 256 bytes of RAM
- 8-bit registers (A, B), 8-bit flags, 8-bit PC (wraps)
- simple instruction set (listed below)
- I/O: OUT (prints ascii from A), IN (reads a byte into A)
- Monitor commands: load, run, step, regs, mem, exit
"""

import sys
import argparse

RAM_SIZE = 256

# Opcodes
OP = {
    'NOP': 0x00,
    'LDI': 0x10,  # LDI <reg> <imm8>   reg: 0=A,1=B
    'MOV': 0x11,  # MOV <reg> <addr>   load from mem to reg
    'STR': 0x12,  # STR <reg> <addr>   store reg to mem
    'ADD': 0x20,  # ADD <reg> <reg>    reg+reg -> A
    'SUB': 0x21,  # SUB <reg> <reg>    A = reg1 - reg2 (wrap)
    'JMP': 0x30,  # JMP <addr>
    'JZ' : 0x31,  # JZ  <addr> (jump if zero flag set)
    'JNZ': 0x32,  # JNZ <addr>
    'OUT': 0x40,  # OUT <reg>   print ASCII from reg
    'IN' : 0x41,  # IN  <reg>   read one char into reg
    'HLT': 0xFF,
}

REG_A = 0
REG_B = 1

class CPU:
    def __init__(self):
        self.ram = [0]*RAM_SIZE
        self.reg = [0,0]   # A, B
        self.pc = 0
        self.zero = False
        self.running = False
        self.trace = False

    def load_bin(self, data, addr=0):
        for i, b in enumerate(data):
            self.ram[(addr + i) % RAM_SIZE] = b & 0xFF

    def step(self):
        opcode = self.ram[self.pc]
        if self.trace:
            print(f"[PC={self.pc:02X}] OPCODE {opcode:02X}")
        self.pc = (self.pc + 1) % RAM_SIZE

        if opcode == OP['NOP']:
            return True

        if opcode == OP['LDI']:
            reg = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            imm = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            self.reg[reg] = imm & 0xFF
            self.zero = (self.reg[REG_A] == 0)
            return True

        if opcode == OP['MOV']:
            reg = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            addr = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            self.reg[reg] = self.ram[addr]
            self.zero = (self.reg[REG_A] == 0)
            return True

        if opcode == OP['STR']:
            reg = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            addr = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            self.ram[addr] = self.reg[reg] & 0xFF
            return True

        if opcode == OP['ADD']:
            r1 = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            r2 = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            self.reg[REG_A] = (self.reg[r1] + self.reg[r2]) & 0xFF
            self.zero = (self.reg[REG_A] == 0)
            return True

        if opcode == OP['SUB']:
            r1 = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            r2 = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            self.reg[REG_A] = (self.reg[r1] - self.reg[r2]) & 0xFF
            self.zero = (self.reg[REG_A] == 0)
            return True

        if opcode == OP['JMP']:
            addr = self.ram[self.pc]; self.pc = addr % RAM_SIZE
            return True

        if opcode == OP['JZ']:
            addr = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            if self.zero:
                self.pc = addr % RAM_SIZE
            return True

        if opcode == OP['JNZ']:
            addr = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            if not self.zero:
                self.pc = addr % RAM_SIZE
            return True

        if opcode == OP['OUT']:
            reg = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            sys.stdout.write(chr(self.reg[reg] & 0xFF))
            sys.stdout.flush()
            return True

        if opcode == OP['IN']:
            reg = self.ram[self.pc]; self.pc = (self.pc+1)%RAM_SIZE
            ch = sys.stdin.read(1)
            if ch == '':
                val = 0
            else:
                val = ord(ch[0])
            self.reg[reg] = val & 0xFF
            self.zero = (self.reg[REG_A] == 0)
            return True

        if opcode == OP['HLT']:
            return False

        # Unknown opcode
        print(f"Unknown opcode {opcode:02X} at {self.pc-1:02X}")
        return False

    def run(self, start=0, trace=False):
        self.pc = start % RAM_SIZE
        self.trace = trace
        self.running = True
        while True:
            cont = self.step()
            if not cont:
                break
        self.running = False

    def dump_regs(self):
        print(f"PC: {self.pc:02X}  A: {self.reg[0]:02X}  B: {self.reg[1]:02X}  Z:{int(self.zero)}")

    def dump_mem(self, start=0, length=32):
        for addr in range(start, start+length):
            a = addr % RAM_SIZE
            if (a-start)%16==0:
                print(f"\n{a:02X}: ", end='')
            print(f"{self.ram[a]:02X} ", end='')
        print()

def load_file_bytes(path):
    with open(path, "rb") as f:
        return list(f.read())

def repl(cpu):
    print("8bit emulator monitor. Type 'help' for commands.")
    while True:
        try:
            cmd = input(">>> ").strip()
        except EOFError:
            break
        if cmd == "exit" or cmd == "quit":
            break
        if cmd == "help":
            print("commands: load <file> [addr], run [addr], step, regs, mem [addr] [len], trace on/off, reset, exit")
            continue
        parts = cmd.split()
        if not parts: continue
        if parts[0] == "load":
            if len(parts) < 2:
                print("usage: load file [addr]")
                continue
            data = load_file_bytes(parts[1])
            addr = int(parts[2],0) if len(parts) > 2 else 0
            cpu.load_bin(data, addr)
            print(f"Loaded {len(data)} bytes at {addr:02X}")
            continue
        if parts[0] == "run":
            addr = int(parts[1],0) if len(parts) > 1 else 0
            cpu.run(addr, trace=cpu.trace)
            print("\n[Halted]")
            continue
        if parts[0] == "step":
            ok = cpu.step()
            cpu.dump_regs()
            if not ok:
                print("[Halted]")
            continue
        if parts[0] == "regs":
            cpu.dump_regs()
            continue
        if parts[0] == "mem":
            addr = int(parts[1],0) if len(parts) > 1 else 0
            length = int(parts[2],0) if len(parts) > 2 else 64
            cpu.dump_mem(addr, length)
            continue
        if parts[0] == "trace":
            if len(parts) > 1 and parts[1] in ("on","off"):
                cpu.trace = (parts[1]=="on")
                print("trace", cpu.trace)
            else:
                print("trace on/off")
            continue
        if parts[0] == "reset":
            cpu.__init__()
            print("reset")
            continue
        print("unknown command")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binfile", nargs="?", help="binary to load")
    parser.add_argument("-a","--addr", type=lambda x: int(x,0), default=0, help="load address (hex ok)")
    parser.add_argument("-t","--trace", action="store_true", help="trace CPU")
    args = parser.parse_args()

    cpu = CPU()
    if args.binfile:
        data = load_file_bytes(args.binfile)
        cpu.load_bin(data, args.addr)
        cpu.run(args.addr, trace=args.trace)
        print("\n[Halted]")
        cpu.dump_regs()
    else:
        repl(cpu)

if __name__ == "__main__":
    main()
