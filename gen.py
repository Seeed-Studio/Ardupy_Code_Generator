import json
import sys

licence = '''/**
* The MIT License (MIT)
*
* Author: PowerfulCat (x4495@outlook.com)
*
* Copyright (C) 2019  Seeed Technology Co.,Ltd.
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
* THE SOFTWARE.
*/
'''

inc_binding = '''
#include "py/mphal.h"
#include "py/objtype.h"
#include "py/runtime.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "shared-bindings/util.h"
'''

inc_hal = '''
#include <Arduino.h>

extern "C"{
    #include "py/mphal.h"
    #include "py/objtype.h"
    #include "py/runtime.h"
    #include "shared-bindings/util.h"
}
'''

meta_strcuture = '''
STATIC const mp_rom_map_elem_t %s_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&%s_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR___enter__), MP_ROM_PTR(&default___enter___obj) },
    { MP_ROM_QSTR(MP_QSTR___exit__), MP_ROM_PTR(&%s___exit___obj) },
%s
};

STATIC MP_DEFINE_CONST_DICT(%s_locals_dict, %s_locals_dict_table);

const mp_obj_type_t %s_type = {
    { &mp_type_type },
    .name = MP_QSTR_%s,
    .make_new = %s_make_new,
    .locals_dict = (mp_obj_dict_t*)&%s_locals_dict,
};
'''

def init_parse(min_arg_count, max_arg_count): 
    return '''\
    mp_arg_check_num(n_args, n_kw, %d, %d, false);
    mp_arg_parse_all_kw_array(n_args, n_kw, args, MP_ARRAY_SIZE(allowed_args), allowed_args, vals);'''

def normal_parse(min_arg_count, max_arg_count):
    return '    mp_arg_parse_all(n_args - 1, pos_args + 1, kw_args, MP_ARRAY_SIZE(allowed_args), allowed_args, vals);'


class meta_info:
    full_name = None
    name = None
    retn = None
    binding = None
    hal = None
    check = None
    min_arg_count = 0


class decl_list:
    pin_dic = {
        "D0": "pin_D0",
        "D1": "pin_D1",
        "D2": "pin_D2",
        "D3": "pin_D3",
        "D4": "pin_D4",
        "D5": "pin_D5",
        "D6": "pin_D6",
        "D7": "pin_D7",
        "D8": "pin_D8",
        "D9": "pin_D9",
        "D10": "pin_D10",
        "D11": "pin_D11",
        "D12": "pin_D12",
        "D13": "pin_D13",
        "A0": "pin_A0",
        "A1": "pin_A1",
        "A2": "pin_A2",
        "A3": "pin_A3",
        "A4": "pin_A4",
        "A5": "pin_A5",
        "SDA": "pin_SDA",
        "SCL": "pin_SCL",
        "SCK": "pin_SCK",
        "MOSI": "pin_MOSI",
        "MISO": "pin_MISO",
    }

    def __init__(self, file_path):
        self.info = open(file_path, 'r')
        self.info = json.loads(self.info.read())

    def function_binding(self, key, line, rules, code):
        line = line.split('(')
        args = line[1].replace(')', '')
        line = line[0].split(' ')
        retn_type = str.rstrip(str.strip(line[0]))
        func_name = str.rstrip(str.strip(line[1]))
        arg_type = ['abstract_module_t *']
        arg_name = ['self']
        pin_name = []
        decl_arg = []
        parse_list = ['    static const mp_arg_t allowed_args[] = {']
        enum_list = ['    enum { ']
        min_arg_count = 0
        code.hal = ''

        if func_name == key:
            hal_def = '    extern void common_hal_%s_construct(%s)'
            code.full_name = func_name
            parse = init_parse
            code.binding = ['m_generic_make(%s){' % key]
            code.binding.append('    abstract_module_t * self = new_abstruct_module(type);')
        else:
            hal_def = '    extern ' + retn_type + ' common_hal_%s(%s)'
            parse = normal_parse
            code.full_name = '%s_%s' % (key, func_name)
            code.binding = ['mp_obj_t %s(size_t n_args, const mp_obj_t * pos_args, mp_map_t * kw_args){' % func_name]
            code.binding.append(hal_def % (code.full_name, ', '.join(arg_type)) + ';')
            code.binding.append('    abstract_module_t * self = (abstract_module_t *)(pos_args[0]);')

        if retn_type == 'bool':
            retn = '    return mp_obj_new_bool(result);'
        elif retn_type == 'int':
            retn = '    return mp_obj_new_int(result);'
        elif retn_type == 'obj':
            retn = '    return result;'
        elif retn_type == 'float':
            retn = '    return mp_obj_new_float(result);'
        elif retn_type == 'str':
            retn = '    return mp_obj_new_float(result, result_length);'
        elif retn_type == 'void':
            retn = '    return mp_const_none;'
        else:
            raise NotImplementedError()

        if len(args) != 0:
            for arg in args.split(','):
                arg = arg.split(' ')
                if arg[0] == '':
                    arg = arg[1:]
                is_pin = False

                if arg[0] == 'bool':
                    type_enum = 'MP_ARG_BOOL'
                    type_var = 'u_bool'
                    type = 'bool'
                elif arg[0] == 'int':
                    type_enum = 'MP_ARG_INT'
                    type_var = 'u_int'
                    type = 'int'
                elif arg[0] == 'obj':
                    type_enum = 'MP_ARG_OBJ'
                    type_var = 'u_obj'
                    type = 'mp_obj_t'
                elif arg[0] == 'pin':
                    type_enum = 'MP_ARG_OBJ'
                    type_var = 'u_obj'
                    type = 'mp_obj_t'
                    is_pin = True
                elif arg[0] == 'float':
                    type_enum = 'MP_ARG_FLOAT'
                    type_var = 'u_float'
                    type = 'float'
                elif arg[0] == 'str':
                    type_enum = 'MP_ARG_STR'
                    type_var = 'u_str'
                    type = 'const char * '
                else:
                    raise NotImplementedError()

                for i in range(1, len(arg)):
                    kv = arg[i].split('=')
                    name = str.strip(str.strip(kv[0]))
                    arg_type.append(type)
                    arg_name.append(name)
                    if is_pin:
                        pin_name.append(name)
                    if len(kv) == 1:
                        min_arg_count = min_arg_count + 1
                        parse_list.append('        { MP_QSTR_%s, MP_ARG_REQUIRED | %s },' % (name, type_enum))
                    else:
                        value = str.strip(str.strip(kv[1]))
                        parse_list.append('        { MP_QSTR_%s, %s, { .%s = %s } },' % (name, type_enum, type_var, value))
                    enum_list.append('ARG_%s, ' % name)
                    decl_arg.append('    %s %s = vals[ARG_%s].%s;' % (type, name, name, type_var))

            enum_list.append('};')
            parse_list.append('    };')
            rest = [
                '    mp_arg_val_t vals[MP_ARRAY_SIZE(allowed_args)];',
                parse(min_arg_count, len(arg_name))
            ] + decl_arg

            for pin in pin_name:
                rest.append('    assert_pin(%s, true);' % pin)
            for pin in pin_name:
                rest.append('    assert_pin_free(%s);' % pin)
            code.binding.append(''.join(enum_list))
            code.binding = code.binding + parse_list + rest

            if rules is not None:
                self.check(rules, code)

            hal_arg = []
            for type, name in zip(arg_type, arg_name):
                if type == 'pin':
                    hal_arg.append('m_get_pin(ARG_%s)->number' % name)
                else:
                    hal_arg.append(name)
        else:
            hal_arg = []

        code.name = func_name
        code.retn = retn
        code.min_arg_count = min_arg_count

        if func_name == key:
            code.hal = '    extern void common_hal_%s_deinit(abstract_module_t * self) {}\n' % key
            code.binding.append(hal_def % (key, ', '.join(arg_type)) + ';')
            code.binding.append('    common_hal_%s_construct(%s);' % (key, ', '.join(hal_arg)))
            code.binding.append('    return self;')
            code.binding.append('}\n')
        else:
            code.binding.append('    //TODO--------------------------------------------------------')
            code.binding.append(code.retn)
            code.binding.append('}')
            code.binding.append('MP_DEFINE_CONST_FUN_OBJ_KW(%s_obj, %d, %s);\n' %
                                (code.full_name, code.min_arg_count, code.full_name))
        hal_arg = ['%s %s' % (a, b) for a, b in zip(arg_type, arg_name)] 
        code.hal = code.hal + (hal_def % (code.full_name, ', '.join(hal_arg))) + '{}'

    operator_map = {
        '(': ' > ',
        '[': ' >= ',
        ')': ' < ',
        ']': ' <= ',
    }
    raise_if = '    raise_error_if(!(%s), "parameter \'%s\' mismatch: \\r\\n\\t%s");'

    def check(self, rules, code):
        def equal_value_check(chk, arg, equ):
            chk.append(arg)
            chk.append(' == ')
            equ = ''.join(equ)
            if equ in self.pin_dic.keys():
                chk.append('&')
                chk.append(self.pin_dic[equ])
            else:
                chk.append(equ)

        for arg in rules:
            chk = []
            equ = []
            right = []
            rule = rules[arg]
            has_left_value, has_right_value, has_equal_value = False, False, False
            wait_left_value, wait_right_value, wait_white_space = False, False, False
            for char in rule:
                if wait_white_space:
                    if char == ' ':
                        continue
                    wait_white_space = False
                if char == '(' or char == '[':
                    has_left_value = False
                    wait_left_value = True
                    left_cmp = self.operator_map[char]
                elif char == ')' or char == ']':
                    if has_right_value:
                        if has_left_value:
                            chk.append(' and ')
                        has_right_value = False
                        chk.append(arg)
                        chk.append(self.operator_map[char])
                        chk.append(''.join(right))
                    wait_right_value = False
                elif char == ',':
                    if wait_left_value:
                        wait_left_value = False
                        wait_right_value = True
                        if has_left_value:
                            chk.append(left_cmp)
                            chk.append(arg)
                    else:
                        if has_equal_value:
                            has_equal_value = False
                            equal_value_check(chk, arg, equ)
                        chk.append(' or ')
                    wait_white_space = True
                elif wait_left_value:
                    has_left_value = True
                    chk.append(char)
                elif wait_right_value:
                    if not has_right_value:
                        has_right_value = True
                        right = []
                    right.append(char)
                else:
                    if not has_equal_value:
                        has_equal_value = True
                        equ = []
                    equ.append(char)
            if has_equal_value:
                has_equal_value = False
                equal_value_check(chk, arg, equ)
            chk = ''.join(chk)
            code.binding.append(self.raise_if % (chk, arg, chk))

    def make(self):
        for key in self.info:
            funcs = self.info[key]
            func_list = []
            bind = [licence, inc_binding]
            hal = [licence, inc_hal]
            hal.append('extern "C" {')
            for line in funcs:
                code = meta_info()
                func = funcs[line]
                self.function_binding(key, line, func['chk'] if 'chk' in func else None, code)
                if code.name != key:
                    func_list.append('    { MP_ROM_QSTR(MP_QSTR_%s), MP_ROM_PTR(&%s_obj) },' % 
                                     (code.name, code.full_name))
                bind.append('\n'.join(code.binding))
                hal.append(code.hal)
            bind.append(meta_strcuture % (key, key, key, '\n'.join(func_list), key, key, key, key, key, key))
            hal.append('}')
            with open('%s.c' % key, 'w') as f:
                f.write('\n'.join(bind))
                f.close()
            with open('%s.cpp' % key, 'w') as f:
                f.writelines('\n'.join(hal))
                f.close()


gen = decl_list(sys.argv[1])
gen.make()