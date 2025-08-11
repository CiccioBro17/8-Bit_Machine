; example: print "Yo Mr White" and halt
        LDI A, 'Y'
        OUT A
        LDI A, 'o'
        OUT A
        LDI A, ' '
        OUT A
        LDI A, 'M'
        OUT A
        LDI A, 'r'
        OUT A
        LDI A, '.'
        OUT A
        LDI A, ' '
        OUT A
        LDI A, 'W'
        OUT A
        LDI A, 'h'
        OUT A
        LDI A, 'i'
        OUT A
        LDI A, 't'
        OUT A
        LDI A, 'e'
        OUT A
        LDI A, 10   ; newline
        OUT A
        HLT