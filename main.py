from DQN import *


def play():
    # initialise global variables
    global highscore
    gamespeed = 4
    gameOver = False
    gameQuit = False
    bg_speed = 4
    # scrolling of background to the left
    scrollingBg = Background(-1 * bg_speed)
    frame = 0

    penguin = (Penguin(72, 64))

    # define elements on screen
    enemies = pygame.sprite.Group()
    Enemy.containers = enemies
    fishes = pygame.sprite.Group()
    Fish.containers = fishes
    last_obstacle = pygame.sprite.Group()

    # start game
    while not gameQuit:
        while not gameOver:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = True
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = True

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            if penguin.rect.bottom == GROUND_LEVEL:
                                penguin.isJumping = True
                                penguin.movement[1] = -1 * penguin.jumpSpeed

                        if event.key == pygame.K_DOWN:
                            if not (penguin.isJumping and penguin.isDead):
                                penguin.isDucking = True

                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_DOWN:
                            penguin.isDucking = False

            a = 0
            for enemy in enemies:
                a += 1
                enemy.movement[0] = -1 * gamespeed
                if enemy.rect.left < 200:
                    print("Enemy " + str(a))
                    print(enemy.rect.bottom)
                    print(enemy.rect.left)
                if pygame.sprite.collide_mask(penguin, enemy):
                    penguin.isDead = True

            if len(enemies) < 2:
                if len(enemies) == 0:
                    last_obstacle.empty()
                    last_obstacle.add(Enemy(gamespeed))

            if len(fishes) < 5 and random.randrange(0, 300) == 10:
                Fish(45, 25)

            # Update screen
            penguin.update()
            enemies.update()
            fishes.update()
            scrollingBg.update()

            if pygame.display.get_surface() is not None:
                scrollingBg.draw()
                fishes.draw(screen)
                enemies.draw(screen)
                penguin.draw()
                show_score(penguin.score)

                pygame.display.update()
            clock.tick(FPS)

            # Penguin game over, save the new highscore
            if penguin.isDead:
                gameOver = True
                if penguin.score > highscore:
                    highscore = penguin.score
                    record = penguin
            # speed increases by time
            if frame % 800 == 799:
                bg_speed -= 1
                gamespeed += 1

            frame = (frame + 1)

        if gameQuit:
            break

        while gameOver:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                gameQuit = True
                gameOver = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        gameQuit = True
                        gameOver = False

                pygame.display.update()
            clock.tick(FPS)


def main():
    GameQuit = True
    play()


main()
