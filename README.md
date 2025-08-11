# 8bit — Tiny 8-bit emulator + assembler

## Quickstart
1. Put this folder in your Linux machine (or clone the repo).
2. Make Python scripts executable:
    ```chmod +x emulator.py asm.py run```
3. Compile the assembly file:
    ```./asm.py examples/helloworld.asm -o examples/helloworld.bin```
4. Run the emulator:
    ### Run script
    ```./run```

    or

    ### Python script
    ```./emulator.py examples/helloworld.bin```