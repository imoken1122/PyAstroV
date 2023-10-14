import asyncio

async def func1():
    print('func1() started')
    a = 0
    for i in range(1000000):
        await asyncio.sleep(0.000000000001)
        a += i
    print('func1() finished')
    return a 

async def func2():
    print('func2() started')
    await asyncio.sleep(1)
    print('func2() finished')

async def main():
    task1 = asyncio.create_task(func1())
    task2 = asyncio.create_task(func2())

    a = await task1
    await task2

asyncio.run(main())
