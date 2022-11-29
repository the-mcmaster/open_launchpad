#this test assumes file stream is empty
def test(row, column, state):
    if row == 0 and column == 8:
        return None
    
    instr = ""
    if state == 0:
        instr += "Please press "
    else:
        instr += "Please release "

    if row == 0:
        print(instr + f"row special button on column {column+1}")
    elif column != 8:
        print(instr + f"square button on row {row} and column {column+1}")
    else:
        print(instr + f"column special button on row {row+1}")

    return I_STREAM.read(3)

if __name__ == "__main__":
    I_STREAM = open("/dev/midi5", 'rb', buffering=0)
    
    button_map = {}

    for row in range(9):
        for column in range(9):
            for state in range(2):
                button = (row, column, state)
                button_in = test(button[0], button[1], button[2])
                button_map[button_in] = button
    
    print(f"\n\n{button_map}")