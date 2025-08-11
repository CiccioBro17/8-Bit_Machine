; example: print "HELLO" and halt
        LDI A, 'H'
        OUT A
        LDI A, 'e'
        OUT A
        LDI A, 'l'
        OUT A
        LDI A, 'l'
        OUT A
        LDI A, 'o'
        OUT A
        LDI A, ' '
        OUT A
        LDI A, 'W'
        OUT A
        LDI A, 'o'
        OUT A
        LDI A, 'r'
        OUT A
        LDI A, 'l'
        OUT A
        LDI A, 'd'
        OUT A
        LDI A, '!'
        OUT A
        LDI A, 10   ; newline
        OUT A
        HLT
