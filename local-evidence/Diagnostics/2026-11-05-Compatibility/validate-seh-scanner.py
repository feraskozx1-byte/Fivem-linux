#!/usr/bin/env python3
"""Check actual FindCallFromAddress termination with a mocked udis86 decoder.

No real machine code is decoded. This checks EOF handling/control flow only;
the existing INT32_MAX input range and readable-memory bounds are unchanged.
Requires Python 3 and host C++17 compiler. All build outputs are temporary.
"""
from pathlib import Path
import os
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[2] / 'Original-PR4050-Source' /
          'code/client/citicore/SEHTableHandler.Win32.cpp').read_text()
start = source.index('static void* FindCallFromAddress(')
end = source.index('\n#ifdef _M_AMD64\nstruct FUNCTION_TABLE_DATA', start)
production = source[start:end]
prelude = r'''
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <stdexcept>
#include <vector>
#define _M_AMD64
using ud_mnemonic_code = int;
constexpr int UD_Icall = 1, UD_Ijmp = 2, UD_Iint3 = 3, UD_Inop = 4, UD_Iother = 5;
constexpr int UD_OP_JIMM = 1, UD_OP_REG = 2;
struct operand { int type; union { int32_t sdword; } lval; };
struct instruction { int mnemonic, kind; unsigned length; uint64_t address; int32_t displacement; };
struct ud_t { size_t index; instruction current; operand op; };
static std::vector<instruction> input;
static unsigned decodeCalls;
static void ud_init(ud_t* ud) { *ud = {}; }
static void ud_set_mode(ud_t*, int mode) { assert(mode == 64); }
static void ud_set_pc(ud_t*, uint64_t) {}
static void ud_set_input_buffer(ud_t*, uint8_t*, size_t length) { assert(length == INT32_MAX); }
static unsigned ud_disassemble(ud_t* ud)
{
    if (++decodeCalls > 16) throw std::runtime_error("decoder call budget exceeded at EOF");
    if (ud->index == input.size()) return 0;
    ud->current = input[ud->index++];
    ud->op.type = ud->current.kind;
    ud->op.lval.sdword = ud->current.displacement;
    return ud->current.length;
}
static int ud_insn_mnemonic(ud_t* ud) { return ud->current.mnemonic; }
static operand* ud_insn_opr(ud_t* ud, unsigned index) { assert(index == 0); return &ud->op; }
static unsigned ud_insn_len(ud_t* ud) { return ud->current.length; }
static uint64_t ud_insn_off(ud_t* ud) { return ud->current.address; }
'''
tests = r'''
static void reset(std::vector<instruction> instructions)
{
    input = instructions; decodeCalls = 0;
}
int main()
{
    try
    {
        reset({});
        assert(FindCallFromAddress(nullptr) == nullptr && decodeCalls == 1);
        reset({{UD_Iother, UD_OP_REG, 1, 0x1000, 0}});
        assert(FindCallFromAddress(nullptr) == nullptr && decodeCalls == 2);
        reset({{UD_Icall, UD_OP_JIMM, 5, 0x1000, 0x20}});
        assert(FindCallFromAddress(nullptr) == reinterpret_cast<void*>(0x1025) && decodeCalls == 2);
        reset({{UD_Icall, UD_OP_JIMM, 5, 0x1000, 0x20}, {UD_Icall, UD_OP_JIMM, 5, 0x1005, 0x30}});
        assert(FindCallFromAddress(nullptr) == nullptr && decodeCalls == 2);
        reset({{UD_Icall, UD_OP_JIMM, 5, 0x1000, -0x20}, {UD_Icall, UD_OP_JIMM, 5, 0x1005, 0x30}});
        assert(FindCallFromAddress(nullptr, UD_Icall, true) == reinterpret_cast<void*>(0xFE5) && decodeCalls == 1);
        for (int stop : {UD_Iint3, UD_Inop})
        {
            reset({{stop, UD_OP_REG, 1, 0x1000, 0}});
            assert(FindCallFromAddress(nullptr) == nullptr && decodeCalls == 1);
        }
        reset({{UD_Ijmp, UD_OP_JIMM, 5, 0x1000, 0x20}});
        assert(FindCallFromAddress(nullptr, UD_Ijmp) == reinterpret_cast<void*>(0x1025) && decodeCalls == 2);
        reset({{UD_Icall, UD_OP_REG, 2, 0x1000, 0}});
        assert(FindCallFromAddress(nullptr) == nullptr && decodeCalls == 2);
        std::puts("PASS: scanner EOF termination and existing branch/call selection (mock decoder only).");
        return 0;
    }
    catch (const std::runtime_error& error)
    {
        std::fprintf(stderr, "FAIL: %s\n", error.what());
        return 2;
    }
}
'''
with tempfile.TemporaryDirectory(prefix='fivem-seh-scanner-') as tmp:
    cpp = Path(tmp) / 'scanner.cpp'
    binary = Path(tmp) / 'scanner'
    compile_command = [os.environ.get('CXX', 'g++'), '-std=c++17', '-Wall', '-Wextra',
                       '-Werror', '-fsanitize=address,undefined', '-fno-omit-frame-pointer',
                       '-g', str(cpp), '-o', str(binary)]
    cpp.write_text(prelude + production + tests)
    subprocess.run(compile_command, check=True)
    subprocess.run([str(binary)], check=True)
    # Prove the first test catches the old infinite loop, bounded by mock budget.
    guard = 'if (ud_disassemble(&ud) == 0)\n\t\t{\n\t\t\tbreak;\n\t\t}'
    assert production.count(guard) == 1
    regression = production.replace(guard, 'ud_disassemble(&ud);')
    cpp.write_text(prelude + regression + tests)
    subprocess.run(compile_command, check=True)
    result = subprocess.run([str(binary)], capture_output=True, text=True)
    assert result.returncode == 2 and 'decoder call budget exceeded at EOF' in result.stderr, result
    print('PASS: pre-fix scanner fails the EOF test via mock call budget (regression detected).')
