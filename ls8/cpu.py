"""CPU functionality."""

import sys

PUSH = 0b01000101
POP = 0b01000110
ADD = 0b10100000

CALL = 0b01010000
RET = 0b00010001

CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

LESS_THAN = 0b00000100
GREATER_THAN = 0b00000010
EQUAL = 0b00000001


SP = 7
STACK_START = 0xF4


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8  # 8 slots of general-purpose registers
        self.ram = [0] * 256  # 256 bytes
        self.pc = 0  # program counter set to 0
        self.reg[SP] = STACK_START
        self.fl = 0b00000000

    def load(self):
        """Load a program into memory."""
        program = "./examples/print8.ls8"  # base file when no arg passed

        if len(sys.argv) == 2:
            program = sys.argv[1]

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1
        with open(program) as f:
            for line in f:
                # split off comments
                line = line.split("#")
                # remove white space
                line = line[0].strip()
                # comment line ignore
                if line == "":
                    continue
                self.ram[address] = int(line, 2)  # base 2
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            regA_num = self.ram[self.pc + 1]
            regB_num = self.ram[self.pc + 2]
            # get the values from the registers
            valueA = self.reg[regA_num]
            valueB = self.reg[regB_num]

            # setting the flag register
            # equal
            if valueA == valueB:
                self.fl = EQUAL
            # less than
            elif valueA < valueB:
                self.fl = LESS_THAN
            # greater than
            else:
                self.fl = GREATER_THAN

            # # increment pc
            # self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        """Read and return value stored at particular Address

        Arguments:
            MAR {Int} -- Memory Address Register

        Returns:
            Value -- The value that is stored at the particular MAR
        """
        return self.ram[MAR]

    def write_ram(self, MDR, MAR):
        """Write a value to a particular address

        Arguments:
            MDR {DAta} -- Memory Data Register
            MAR {Int} -- Memory Address Register
        """
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        """Run
        IR - Instruction Register
        PC - Program counter
        """
        running = True

        while running:
            IR = self.ram_read(self.pc)

            if IR == 130:  # LDI
                self.reg[self.ram_read(self.pc + 1)
                         ] = self.ram_read(self.pc + 2)
                self.pc += 3  # 3 byte operation
            elif IR == 71:  # PRN
                print(self.reg[self.ram_read(self.pc + 1)])
                self.pc += 2  # 2 byte operation
            elif IR == 1:  # HLT
                running = False
            elif IR == 162:
                regA_num = self.ram[self.pc + 1]
                regB_num = self.ram[self.pc + 2]
                self.alu("MUL", regA_num, regB_num)
                self.pc += 3
            elif IR == PUSH:
                reg_num = self.ram[self.pc + 1]
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = self.reg[reg_num]
                # byte operation
                self.pc += 2
            elif IR == POP:
                reg_num = self.ram[self.pc + 1]

                stack_address = self.reg[SP]
                stack_value = self.ram[stack_address]
                self.reg[reg_num] = stack_value
                self.reg[SP] += 1
                # byte operation
                self.pc += 2
            elif IR == CALL:
                return_address = self.pc + 2
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = return_address

                reg_num = self.ram[self.pc + 1]
                dest_address = self.reg[reg_num]
                self.pc = dest_address
            elif IR == RET:
                return_address = self.ram[self.reg[SP]]
                self.reg[SP] += 1
                self.pc = return_address

            elif IR == ADD:
                regA_num = self.ram[self.pc + 1]
                regB_num = self.ram[self.pc + 2]

                self.alu("ADD", regA_num, regB_num)

                self.pc += 3
            elif IR == JMP:
                reg_num = self.ram[self.pc + 1]
                self.pc = self.reg[reg_num]
            elif IR == CMP:
                regA_num = self.ram[self.pc + 1]
                regB_num = self.ram[self.pc + 2]

                self.alu("CMP", regA_num, regB_num)
                self.pc += 3
            elif IR == JEQ:
                if self.fl == EQUAL:
                    reg_num = self.ram[self.pc + 1]
                    address = self.reg[reg_num]
                    self.pc = address
                else:
                    self.pc += 2
            elif IR == JNE:
                if self.fl != EQUAL:
                    reg_num = self.ram[self.pc + 1]
                    address = self.reg[reg_num]
                    self.pc = address
                else:
                    self.pc += 2
            else:  # didn't understand cmd
                print("The instruction provided was not understood.")
                sys.exit(1)
