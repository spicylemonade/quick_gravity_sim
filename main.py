import pygame
import random
import time
import asyncio
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1200,800))
pygame.display.set_caption('py_simulation test')
playerimg = pygame.image.load('pixil-frame-0 (1).png')
playerimg2 = pygame.image.load('pixil-frame-0.png')
playerX = 380 #380
playerY = 270#270
oplayerx=270
oplayery=380
changex = -.1
changey = -.1
ochangex = 0
ochangey = 0
green = 56,69,45
async def orbit(x,y):
    screen.blit(playerimg2, (x, y))

async def player(x,y):
    screen.blit(playerimg,(x,y))

async def ranmove():
    global oplayerx
    global oplayery
    global changex
    global changey
    global playerX
    global playerY
    playerX += changex
    playerY += changey

    if playerX > oplayerx:
        changex +=-0.00003
    if playerX < oplayerx:
        changex +=0.00003
    if playerY > oplayery:
        changey += -0.00003
    if playerY < oplayery:
        changey += 0.00003
async def ranmove2():
    global oplayerx
    global oplayery
    #oplayerx+=.03
    #oplayery+=.03
    #if you want to make the bigger plannet move



async def main():
    global oplayerx
    global oplayery
    global playerX
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((111,123,144))
        await player(playerX,playerY)
        await orbit(oplayerx,oplayery)
        await ranmove()
        await ranmove2()
        pygame.draw.line(screen,green, [playerX+1,playerY], [oplayerx,oplayery])
        if playerY == oplayery:
            await print('impact')
        if playerX == oplayerx:
            await print('impact')
        pygame.display.update()

asyncr = asyncio.run(main())
asyncr
