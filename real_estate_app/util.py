def get_valid_input(inputstr, valid_options):
    inputstr += " ({}) ".format(", ".join(valid_options))
    response = input(inputstr)
    while response.lower() not in valid_options:
        response = input(inputstr)
    return response