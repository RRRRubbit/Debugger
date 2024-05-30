# 示例文本
lines = [
    '       0 :                     ',
    '       0 :                     ',
    '       0 :                     ',
    '       0 :                     ',
    '       0 :                                 CPU     80515               ',
    '       0 :                                 INCLUDE stddef51            ',
    '       0 : =>UNDEFINED         \t\tifndef  stddef51inc     ',
    '       0 : ALL                                 restore                 ',
    '       0 : [1]                                 endif\t\t\t',
    '       0 : =>UNDEFINED         \t\tifndef   bitfuncsinc    ',
    '       0 : ALL                                 restore                 ',
    '       0 : [1]                                 endif\t\t\t',
    '       0 : (MACRO)                         USING   bank0               ',
    '       0 : =>FALSE                             if      (BANK0<0)||(BANK0>3)          ',
    '       0 : =>UNDEFINED                         ifdef   RegUsage        ',
    '       0 : =0H                 ar0             set     BANK0*8          ',
    '       0 :                     ',
    '       0 : =0H                 reset       EQU     0000h               ',
    '       0 :                     ',
    '       0 :                                 ORG     reset               ',
    '       0 : 02 00 03                        LJMP    program_init        ',
    '       3 :                     ',
    '       3 : 75 E8 FE                        MOV     p4, #00FEh          ',
    '       6 : 78 14                           MOV     r0, #20             ',
    '       8 : 11 13                           ACALL   wait_50ms           ',
    '       A : D8 FC                           DJNZ    r0, program_wait    ',
    '       C : E5 E8                           MOV     a, p4               ',
    '       E : 23                              RL      a                   ',
    '       F : F5 E8                           MOV     p4, a               ',
    '      11 : 80 F3                           SJMP    program_loop        ',
    '      13 :                     ',
    '      13 :                     ',
    '      13 :                     ',
    '      13 :                     wait_50ms:                              ',
    '      13 : C0 01                           PUSH    ar1                 ',
    '      15 : C0 00                           PUSH    ar0                 ',
    '      17 :                                                             ',
    '      17 : 79 C1                           MOV     r1, #193            ',
    '      19 :                     wait_loop:                              ',
    '      19 : 78 80                           MOV     r0, #128            ',
    '      1B : D8 FE                           DJNZ    r0, $               ',
    '      1D : D9 FA                           DJNZ    r1, wait_loop       ',
    '      1F :                                                             ',
    '      1F : D0 00                           POP     ar0                 ',
    '      21 : D0 01                           POP     ar1                 ',
    '      23 : 22                              RET                         ',
    '      24 :                     '
]

# 保存相同地址的最后一行的字典
address_lines = {}

# 遍历每一行
for line in lines:
    parts = line.split(':')
    address = parts[0].strip()  # 获取地址部分
    content = parts[1].strip() if len(parts) > 1 else ''  # 获取内容部分（如果有）
    address_lines[address] = content  # 更新字典

# 输出结果
for address, content in address_lines.items():
    print("地址:", address)
    print("内容:", content)
