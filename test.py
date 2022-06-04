def calc():
    history = []
    result = 0
    while True:
        x, y = (yield result)
        if x == 'h':
            print(history)
            continue
        result = x + y
        print(result)
        history.append(result)

c = calc()

# print type(c)

next(c)

c.send((4, 9))
c.send((6, 13))
c.send(('h', 0))
c.close()
