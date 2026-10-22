import sys
from pathlib import Path

scanner_dir = Path(__file__).resolve().parents[2] / "scanner"
sys.path.insert(0, str(scanner_dir))

from lexer import Lexer, Token # type: ignore

lexing_rules = r"""
(cls|CLS) : CLEAR
(jmp|JMP) [0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f] : JUMP
(mov|MOV) [0-9A-Fa-f] [0-9A-Fa-f][0-9A-Fa-f] : SET_REGISTER
(add|ADD) [0-9A-Fa-f] [0-9A-Fa-f][0-9A-Fa-f] : ADD_REGISTER
(mvi|MVI) [0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f] : SET_INDEX
(sprite|SPRITE) [0-9A-Fa-f] [0-9A-Fa-f] [0-9A-Fa-f] : DRAW_SPRITE

[a-zA-Z][a-zA-Z0-9]*\: : LABEL

[ \n\t]+ : WHITE
//[a-zA-Z0-9 ]*\n : COMMENT
"""

test_program = """
cls     // address 0x200
mvi 050 // Sprite of 0
mov 0 0c
mov 1 08
sprite 0 1 5
jmp 210 // loop back
"""

class ASM_Compiler(Lexer):

    def __init__(self, src: str, target: str):
        self.lexer = Lexer(text=lexing_rules)
        self.src = src
        self.tokens: list = self.lexer.tokenize(src)
        self.binaries = bytearray()
        self.compile()

        with open(target, "wb") as f:
            f.write(self.binaries)

    def emit_opcode(self, opcode: int):
        self.binaries.append((opcode >> 8) & 0xff)
        self.binaries.append(opcode & 0xff)

    def compile(self):
        for i in range(len(self.tokens)):
            token: Token = self.tokens[i]
            split = token.lexeme.split(" ")
            print(token.lexeme)

            match split[0]: # op
                case "cls" | "CLS":
                    self.emit_opcode(0x00e0)
                case "jmp" | "JMP":
                    op = 0x1
                    addr = int(split[1], 16)
                    self.emit_opcode((op << 12) | addr)
                case "mov" | "MOV":
                    op = 0x6
                    reg = int(split[1], 16)
                    val = int(split[2], 16)
                    self.emit_opcode((op << 12) | (reg << 8) | val)
                case "add" | "ADD":
                    op = 0x7
                    reg = int(split[1], 16)
                    val = int(split[2], 16)
                    self.emit_opcode((op << 12) | (reg << 8) | val)
                case "mvi" | "MVI":
                    op = 0xa
                    adr = int(split[1], 16)
                    self.emit_opcode((op << 12) | adr)
                case "sprite" | "SPRITE":
                    op = 0xd
                    x, y = int(split[1], 16), int(split[2], 16)
                    h = int(split[3], 16)
                    self.emit_opcode((op << 12) | (x << 8) | (y << 4) | h)

ASM_Compiler(test_program, "emulator/chip8/roms/test.ch8")