import re

# 示例文本
text = """ AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 1 - 2/2/2024 11:36:52


       1/       0 :                     ;=====> Lauflicht_Zeit.asm <=========================================================
       2/       0 :                     ; - realisiert ein zeitgesteuertes LED-Lauflicht (LOW-aktiv) an Port 4
       3/       0 :                     ; - Frequenz = 1Hz, Periodendauer = 1s
       4/       0 :                     
       5/       0 :                     ;=====> Primaere Steueranweisungen <=================================================
       6/       0 :                                 CPU     80515               ; Festlegung auf 80C515-CPU
       7/       0 :                     
       8/       0 :                                 INCLUDE stddef51            ; Bibliotheken mit Symbolen, Adressen usw.
(1)    1/       0 : =>UNDEFINED         		ifndef  stddef51inc     ; avoid multiple inclusion
(1)    2/       0 : =1H                 stddef51inc     equ     1
(1)    3/       0 :                     
(1)    4/       0 :                                     save
(1)  371/       0 : ALL                                 restore                 ; re-allow listing
(1)  372/       0 :                     
(1)  373/       0 : [1]                                 endif			; stddef51inc
(1)  374/       0 :                     
       9/       0 :                                 INCLUDE bitfuncs
(1)    1/       0 : =>UNDEFINED         		ifndef   bitfuncsinc    ; avoid multiple inclusion
(1)    2/       0 : =1H                 bitfuncsinc     equ      1
(1)    3/       0 :                     
(1)    4/       0 :                                     save
(1)   77/       0 : ALL                                 restore                 ; allow listing again
(1)   78/       0 :                     
(1)   79/       0 : [1]                                 endif			; bitfuncsinc
(1)   80/       0 :                     
(1)   81/       0 :                     
      10/       0 :                     
      11/       0 : (MACRO)                         USING   bank0               ; nutze Registerbank 0
      11/       0 : =>FALSE                             if      (BANK0<0)||(BANK0>3)          ; only BANK0 0..3 allowed
      11/       0 :                                      error  "Falsche Banknummer: \{BANK0}"
      11/       0 : [11]                                endif
      11/       0 :                     
      11/       0 : =>UNDEFINED                         ifdef   RegUsage        ; Book-Keeping about Used Banks
      11/       0 :                     RegUsage         set    RegUsage|(2^BANK0)
      11/       0 : =>TRUE                              elseif
      11/       0 : =1H                 RegUsage         set    2^BANK0
      11/       0 : [11]                                endif
      11/       0 :                     
      11/       0 : =0H                 ar0             set     BANK0*8          ; Set Symbols
      11/       0 : =1H                 ar1             set     ar0+1
      11/       0 : =2H                 ar2             set     ar0+2
      11/       0 : =3H                 ar3             set     ar0+3
      11/       0 : =4H                 ar4             set     ar0+4
      11/       0 : =5H                 ar5             set     ar0+5
      11/       0 : =6H                 ar6             set     ar0+6
      11/       0 : =7H                 ar7             set     ar0+7
      12/       0 :                     
      13/       0 :                     ;=====> Symbol-Definitionen <========================================================
      14/       0 : =0H                 reset       EQU     0000h               ; Einsprungadresse bei Reset
      15/       0 :                     
      16/       0 :                     ;=====> Programmspeicher <===========================================================
      17/       0 :                                 SEGMENT CODE
      18/       0 :                     
      19/       0 :                                 ORG     reset               ; Einsprungpunkt bei Power-On
      20/       0 : 02 00 03                        LJMP    program_init        ; springe an Programmstartpunkt
      21/       3 :                     
      22/       3 :                     ;-----> Hauptprogramm <--------------------------------------------------------------
      23/       3 :                     
      24/       3 :                     program_init:
      25/       3 : 75 E8 FE                        MOV     p4, #00FEh          ; initialisiere LED-Leiste (P4)
 AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 2 - 2/2/2024 11:36:52


      26/       6 :                     
      27/       6 :                     program_loop:
      28/       6 : 78 14                           MOV     r0, #20             ; setze R0 auf 2
      29/       8 :                     program_wait:
      30/       8 : 11 13                           ACALL   wait_50ms           ; warte 20x 50ms
      31/       A : D8 FC                           DJNZ    r0, program_wait    ; solange R0 > 0, warte
      32/       C :                     
      33/       C : E5 E8                           MOV     a, p4               ; schreibe LED-Leiste (P4) an Akkumulator
      34/       E : 23                              RL      a                   ; rotiere Inhalt von Akkumulator nach links
      35/       F : F5 E8                           MOV     p4, a               ; schreibe Akkumulator an LED-Leiste (P4)
      36/      11 : 80 F3                           SJMP    program_loop        ; wiederhole Programm
      37/      13 :                     
      38/      13 :                     ;-----> Unterprogramme <-------------------------------------------------------------
      39/      13 :                     
      40/      13 :                     ; Unterprogramm "wait_50ms":            ; BERECHNUNG: 1 Cyclus (C) entspricht 1us
      41/      13 :                     ; - fuegt eine 50ms Pause ein           ; -----------------------------------------
      42/      13 :                     wait_50ms:                              ; ACALL = 2C :   (2            ) =      2us
      43/      13 : C0 01                           PUSH    ar1                 ; PUSH  = 2C : + (2            ) =      2us
      44/      15 : C0 00                           PUSH    ar0                 ; PUSH       : + (2            ) =      2us
      45/      17 :                                                             ; MOV   = 1C : + (1            ) =      1us
      46/      17 : 79 C1                           MOV     r1, #193            ; MOV        : + (1       * 193) =    193us
      47/      19 :                     wait_loop:                              ; DJNZ  = 2C : + (2 * 128 * 193) = 49.408us
      48/      19 : 78 80                           MOV     r0, #128            ; DJNZ       : + (2       * 193) =    386us
      49/      1B : D8 FE                           DJNZ    r0, $               ; POP   = 2C : + (2            ) =      2us
      50/      1D : D9 FA                           DJNZ    r1, wait_loop       ; POP        : + (2            ) =      2us
      51/      1F :                                                             ; RET   = 2C : + (2            ) =      2us
      52/      1F : D0 00                           POP     ar0                 ; -----------------------------------------
      53/      21 : D0 01                           POP     ar1                 ;              =                   50.000us
      54/      23 : 22                              RET                         ; =========================================
      55/      24 :                     
      56/      24 :                     ;=====> ENDE <=======================================================================
      57/      24 :                                 END
 AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 3 - 2/2/2024 11:36:52


  Symbol Table (* = unused):
  --------------------------

*AC :                            D6 B | *ACC :                          0E0 D |
 ADCON :                        0D8 D | *ADDAT :                        0D9 D |
*ADM :                           DB B |  AR0 :                            0 - |
 AR1 :                            1 - | *AR2 :                            2 - |
*AR3 :                            3 - | *AR4 :                            4 - |
*AR5 :                            5 - | *AR6 :                            6 - |
*AR7 :                            7 - |
*ARCHITECTURE :                                        "i386-unknown-win32" - |
*B :                            0F0 D |  BANK0 :                          0 - |
*BANK1 :                          1 - | *BANK2 :                          2 - |
*BANK3 :                          3 - | *BD :                            DF B |
*BIGENDIAN :                      0 - | *BITFUNCSINC :                    1 - |
*BSY :                           DC B | *CASESENSITIVE :                  0 - |
*CCEN :                         0C1 D | *CCH1 :                         0C3 D |
*CCH2 :                         0C5 D | *CCH3 :                         0C7 D |
*CCL1 :                         0C2 D | *CCL2 :                         0C4 D |
*CCL3 :                         0C6 D | *CLK :                           DE B |
*CONSTPI :        3.141592653589793 - | *CRCH :                         0CB D |
*CRCL :                         0CA D | *CY :                            D7 B |
*DAPR :                         0DA D | *DATE :                  "2/2/2024" - |
*DPH :                           83 D | *DPL :                           82 D |
*EADC :                          B8 B | *EAL :                           AF B |
*ES :                            AC B | *ET0 :                           A9 B |
*ET1 :                           AB B | *ET2 :                           AD B |
*EX0 :                           A8 B | *EX1 :                           AA B |
*EX2 :                           B9 B | *EX3 :                           BA B |
*EX4 :                           BB B | *EX5 :                           BC B |
*EX6 :                           BD B | *EXEN2 :                         BF B |
*EXF2 :                          C7 B | *F0 :                            D5 B |
*FALSE :                          0 - | *FULLPMMU :                       1 - |
*HAS64 :                          0 - | *HASFPU :                         0 - |
*HASPMMU :                        0 - | *I2FR :                          CD B |
*I3FR :                          CE B | *IADC :                          C0 B |
*IE0 :                           89 B | *IE1 :                           8B B |
 IEN0 :                         0A8 D |  IEN1 :                         0B8 D |
*IEX2 :                          C1 B | *IEX3 :                          C2 B |
*IEX4 :                          C3 B | *IEX5 :                          C4 B |
*IEX6 :                          C5 B | *INSRCMODE :                      0 - |
*INSUPMODE :                      0 - | *INT0 :                          B2 B |
*INT1 :                          B3 B | *IP0 :                          0A9 D |
*IP1 :                          0B9 D |  IRCON :                        0C0 D |
*IT0 :                           88 B | *IT1 :                           8A B |
*LISTON :                         1 - | *MACEXP :                         7 - |
 MOMCPU :                     80515 - |  MOMCPUNAME :               "80515" - |
*MX0 :                           D8 B | *MX1 :                           D9 B |
*MX2 :                           DA B | *NESTMAX :                      100 - |
*OV :                            D2 B | *P :                             D0 B |
*P0 :                            80 D | *P1 :                            90 D |
*P2 :                           0A0 D |  P3 :                           0B0 D |
 P4 :                           0E8 D | *P5 :                           0F8 D |
*P6 :                           0DB D | *PADDING :                        1 - |
*PCON :                          87 D |  PROGRAM_INIT :                   3 C |
 PROGRAM_LOOP :                   6 C |  PROGRAM_WAIT :                   8 C |
 PSW :                          0D0 D | *RB8 :                           9A B |
*RD :                            B7 B | *REGUSAGE :                       1 - |
*RELAXED :                        0 - | *REN :                           9C B |
 RESET :                          0 - | *RI :                            98 B |
 AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 4 - 2/2/2024 11:36:52


*RS0 :                           D3 B | *RS1 :                           D4 B |
*RXD :                           B0 B | *SBUF :                          99 D |
 SCON :                          98 D | *SM0 :                           9F B |
*SM1 :                           9E B | *SM2 :                           9D B |
*SP :                            81 D | *STDDEF51INC :                    1 - |
*SWDT :                          BE B | *T0 :                            B4 B |
*T1 :                            B5 B | *T2CM :                          CA B |
 T2CON :                        0C8 D | *T2I0 :                          C8 B |
*T2I1 :                          C9 B | *T2PS :                          CF B |
*T2R0 :                          CB B | *T2R1 :                          CC B |
*TB8 :                           9B B |  TCON :                          88 D |
*TF0 :                           8D B | *TF1 :                           8F B |
*TF2 :                           C6 B | *TH0 :                           8C D |
*TH1 :                           8D D | *TH2 :                          0CD D |
*TI :                            99 B | *TIME :                  "11:36:52" - |
*TL0 :                           8A D | *TL1 :                           8B D |
*TL2 :                          0CC D | *TMOD :                          89 D |
*TR0 :                           8C B | *TR1 :                           8E B |
*TRUE :                           1 - | *TXD :                           B1 B |
*VERSION :                     142F - |  WAIT_50MS :                     13 C |
 WAIT_LOOP :                     19 C | *WDT :                           AE B |
*WR :                            B6 B |

    155 symbols
    134 unused symbols

 AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 5 - 2/2/2024 11:36:52


  Defined Macros:
  ---------------

USING                                 |

      1 macro

 AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 6 - 2/2/2024 11:36:52


  Defined Functions:
  ------------------

ROTRN                                 | ROTLN                                
SHRN                                  | SHLN                                 
GETBIT                                | EVEN                                 
ODD                                   | LOWORD                               
HIWORD                                | LO                                   
HI                                    | CUTOUT                               
INVMASK                               | MASK                                 

 AS V1.42 Beta [Bld 246] - Source File Lauflicht_Zeit.asm - Page 7 - 2/2/2024 11:36:52


  Code Pages:
  ----------

STANDARD (0 changed characters)

1 code page

0.05 seconds assembly time

    513 lines source file
    531 lines incl. macro expansions
      2 passes
      0 errors
      0 warnings

"""
# 匹配地址的正则表达式

address_pattern = re.compile(r'\s+\d+/(.+?);',re.MULTILINE)

# 提取地址和内容
addresses = address_pattern.findall(text)
# 输出匹配结果
lines = addresses
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

