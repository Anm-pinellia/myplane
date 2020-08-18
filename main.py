import pygame
import sys
import traceback
import myplane
import enemy
import bullet
import supply
from random import *
from pygame.locals import *


pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption('飞机大战')

BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)
WHITE = (255, 255, 255)

#导入素材
background = pygame.image.load('./images/background.png').convert()

#载入游戏音乐
pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)

def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)

def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)

def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)

#提升速度函数
def inc_speed(target, inc):
    for each in target:
        each.speed +=inc
    

def main():
    #播放背景音乐
    pygame.mixer.music.play(-1)


    clock = pygame.time.Clock()
    #生成一个飞机对象
    me = myplane.MyPlane(bg_size)

    #生成敌方飞机
    enemies = pygame.sprite.Group()

    small_enemies = pygame.sprite.Group()
    add_small_enemies(small_enemies, enemies, 15)

    mid_enemies = pygame.sprite.Group()
    add_mid_enemies(mid_enemies, enemies, 4)

    big_enemies = pygame.sprite.Group()
    add_big_enemies(big_enemies, enemies, 2)

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4
    for i in range(BULLET1_NUM):
        # 此处的midtop为一个二维元组，表示位置坐标
        bullet1.append(bullet.Bullet1(me.rect.midtop))

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 12
    for i in range(BULLET2_NUM//3):
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33,me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 30,me.rect.centery)))
        bullet2.append(bullet.Bullet2(me.rect.midtop))

    #飞机毁灭图片索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0

    #分数
    score = 0
    #导入字体并指定大小
    score_font = pygame.font.Font('./font/font.ttf', 36)
    
    #用于切换飞机状态图片标识
    switch_image = True

    #用于延时的变量
    delay = 100

    #暂停标识
    paused = False
    pause_nor_image = pygame.image.load('./images/pause_nor.png').convert_alpha()
    pause_pressed_image = pygame.image.load('./images/pause_pressed.png').convert_alpha()
    resume_nor_image = pygame.image.load('./images/resume_nor.png').convert_alpha()
    resume_pressed_image = pygame.image.load('./images/resume_pressed.png').convert_alpha()
    paused_rect = pause_nor_image.get_rect()
    paused_rect.left, paused_rect.top = width - paused_rect.width -10 , 10
    paused_image = pause_nor_image

    #游戏结束界面图片加载
    gameover_font = pygame.font.Font("./font/font.ttf", 48)
    again_image = pygame.image.load("./images/again.png").convert_alpha()
    again_rect = again_image.get_rect()
    gameover_image = pygame.image.load("./images/gameover.png").convert_alpha()
    gameover_rect = gameover_image.get_rect()

    #设置难度级别
    level = 1

    #全屏炸弹
    bomb_image = pygame.image.load('./images/bomb.png').convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font('./font/font.ttf', 48)
    bomb_num = 3

    #生命数量
    life_image = pygame.image.load('./images/life.png').convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 3

    #阻止结束时重复进行操作
    recorded = False


    #超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1

    #我方无敌时间定时器
    INVICIBLE_TIME = USEREVENT + 2

    #是否使用超级子弹
    is_double_bullet = False

    
    #没30秒发放一个补给包
    bullet_supply = supply.Bullet_Supply(bg_size)
    bomb_supply = supply.Bomb_Supply(bg_size)
    #自定义用户事件
    SUPPLY_TIME = USEREVENT
    #设置事件延迟
    pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
    
        
    running = True

    while running:
        
        for event in pygame.event.get():
            #友好退出设置
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            #点击暂停检测
            elif event.type == MOUSEBUTTONDOWN:
                #检测按下鼠标时，鼠标位置是否在暂停的矩形内部
                if event.button ==1 and paused_rect.collidepoint(event.pos):
                    paused = not paused
                    #实现暂停时的音效问题
                    if paused:
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        #每30s发放补给
                        pygame.time.set_timer(SUPPLY_TIME, 30*1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()

                        
                        
            #滑动鼠标图片变化检测
            #暂停时，检测鼠标位置是否在暂停的矩形中
            elif event.type == MOUSEMOTION:
                if paused_rect.collidepoint(event.pos):
                    if paused:
                        paused_image = resume_pressed_image
                    else:
                        paused_image = pause_pressed_image
                else:
                    if paused:
                        paused_image = resume_nor_image
                    else:
                        paused_image = pause_nor_image

            elif event.type == KEYDOWN:
                #如果按下空格，检测炸弹数量，同时消灭所有屏幕中的敌人
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        bomb_sound.play()
                        for each in enemies:
                            if each.rect.top>0:
                                each.active = False

            elif event.type == SUPPLY_TIME:
                supply_sound.play()
                #随机选择一种补给发放
                if choice([True,False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()

            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

            elif event.type == INVICIBLE_TIME:
                me.invicible = False
                #同时取消计时器
                pygame.time.set_timer(INVICIBLE_TIME, 0)

        #绘制背景
        screen.blit(background,(0,0))


        #根据用户得分增加难度
        if level == 1 and score > 5000:
            level = 2
            upgrade_sound.play()
            #增加3个小敌机，2个中飞机，1个大飞机
            add_small_enemies(small_enemies, enemies, 3)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            #提升敌机速度
            inc_speed(small_enemies, 1)
        elif level == 2 and score > 30000:
            level = 3
            upgrade_sound.play()
            #增加5个小敌机，3个中飞机，2个大飞机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            #提升敌机速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 3 and score > 600000:
            level = 4
            upgrade_sound.play()
            #增加5个小敌机，3个中飞机，2个大飞机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            #提升敌机速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            upgrade_sound.play()
            #增加5个小敌机，3个中飞机，2个大飞机
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            #提升敌机速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)

        
                    
                
        if life_num and not paused:
            #返回键盘按下时的序列布尔类型值
            key_pressed = pygame.key.get_pressed()
            
            #设置键盘按下的对象动作
            if key_pressed[K_w] or key_pressed[K_UP]:
                me.moveUP()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me.moveRight()
                
            #绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                #如果补给与我方飞机发生碰撞,则增加补给
                if pygame.sprite.collide_mask(bomb_supply, me):
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False

            #绘制强化子弹补给并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                #如果补给与我方飞机发生碰撞,则增加补给
                if pygame.sprite.collide_mask(bullet_supply, me):
                    get_bullet_sound.play()
                    is_double_bullet = True
                    #如果碰到补给，则设置超级子弹计时器
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 20*1000)
                    bullet_supply.active = False

            
            #绘制发射的子弹
            if not(delay % 10):
                bullet_sound.play()
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx-33, me.rect.centery))
                    bullets[bullet2_index+1].reset((me.rect.centerx+30, me.rect.centery))
                    bullets[bullet2_index+2].reset(me.rect.midtop)
                    bullet2_index = (bullet2_index + 3) % BULLET2_NUM
                    

                else:
                    #将对应列表赋值给bullets,方便统一修改
                    bullets = bullet1    
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM


            #检测子弹是否击中敌机
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                #如果子弹击中目标
                if enemy_hit:
                    b.active = False        #击中目标后子弹消失
                    for e in enemy_hit:
                        if e in mid_enemies or e in big_enemies:
                            e.hit = True
                            e.energy -= 1
                            if e.energy == 0:
                                e.active = False
                        else:
                            e.active = False
                    
            #绘制大型飞机
            for each in big_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        #如果被打，则绘制对应图片
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        if switch_image:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)

                    #绘制血条，包括起始位置终点以及宽度
                    pygame.draw.line(screen, BLACK,\
                                     (each.rect.left, each.rect.top-5),\
                                     (each.rect.right, each.rect.top-5),\
                                     2)
                    #当血条大于20%显示绿色，否则显示为红色
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color, \
                                        (each.rect.left, each.rect.top-5),\
                                         (each.rect.left + each.rect.width*energy_remain, each.rect.top-5),\
                                         2)
                    
                    
                    #进行预警
                    if each.rect.bottom == -50:
                        enemy3_fly_sound.play(-1)
                else:
                    #毁灭图片播放以及声音播放
                    if not(delay % 3):
                        if e3_destroy_index == 0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        #使数值在0~5之间的公式,且每次加一，当数值变为6时，数值会变为0
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            enemy3_fly_sound.stop()
                            score += 10000
                            each.reset()

            #绘制中型飞机
            for each in mid_enemies:
                if each.active:
                    each.move()
                    
                    #绘制血条，包括起始位置终点以及宽度
                    pygame.draw.line(screen, BLACK,\
                                     (each.rect.left, each.rect.top-5),\
                                     (each.rect.right, each.rect.top-5),\
                                     2)
                    #当血条大于20%显示绿色，否则显示为红色
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color, \
                                        (each.rect.left, each.rect.top-5),\
                                         (each.rect.left + each.rect.width*energy_remain, each.rect.top-5),\
                                         2)
                    #绘制被子弹击中后的图片
                    if each.hit:
                        screen.blit(each.image_hit , each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)
                else:
                    #毁灭
                    if not(delay % 3):
                        if e2_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 6000
                            each.reset()

            #绘制小型飞机
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    #毁灭
                    if not(delay % 3):
                        if e1_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 1000
                            each.reset()

            #检测飞机是否碰撞
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            #如果存在返回值则我方挂，将碰撞的敌机也设置为挂了
            if enemies_down and not me.invicible:
                me.active = False
                for e in enemies_down:
                    e.active = False
                    
            #绘制我的飞机
            if me.active:
                if switch_image:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                 #毁灭
                enemy1_down_sound.play()
                if not(delay % 3):
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                         life_num -= 1
                         me.reset()
                         # 设置3s延迟后响应INVICIBLE_TIME
                         pygame.time.set_timer(INVICIBLE_TIME, 3*1000)

            #将字符串渲染成图片，抗锯齿
            score_text = score_font.render('Score : %s' % str(score), True, WHITE)
            screen.blit(score_text, (10,5))

            #绘制炸弹状态
            bomb_text = bomb_font.render('X %d' % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (20 + bomb_rect.width, height -5- bomb_rect.height))

            #绘制我方飞机生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image,\
                                ((width-10-(i+1)*life_rect.width),\
                                height-10-life_rect.height))

            #绘制暂停按钮
            screen.blit(paused_image, paused_rect)

        elif life_num == 0:
            #停止游戏背景音乐和音效
            pygame.mixer.music.stop()
            pygame.mixer.stop()

            #停止相关计时器
            pygame.time.set_timer(SUPPLY_TIME, 0)

            if not recorded:
                 recorded = True
                 #读取历史最高分
                 with open ('./record.txt', 'r') as f:
                     record_score = int(f.read())

                 #比较得分大小
                 if score> record_score:
                     with open('./record.txt', 'w') as f:
                         f.write(str(score))

            #绘制结束的界面
            record_score_text = score_font.render("Best: %d" % record_score,True,WHITE)
            screen.blit(record_score_text, (50,50))
            
            gameover_text1 = gameover_font.render("Your Score: ", True, WHITE)
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = \
                                (width - gameover_text1_rect.width) // 2, height // 3
            screen.blit(gameover_text1, gameover_text1_rect)

            
            gameover_text2 = gameover_font.render(str(score), True, WHITE)
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = \
                                (width - gameover_text2_rect.width) // 2, \
                                gameover_text1_rect.bottom + 10
            screen.blit(gameover_text2, gameover_text2_rect)

            again_rect.left, again_rect.top = \
                        (width - again_rect.width) // 2,\
                        gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)

            gameover_rect.left, gameover_rect.top = \
                        (width - again_rect.width) // 2, \
                        again_rect.bottom + 10
            screen.blit(gameover_image, gameover_rect)

            # 检测用户的鼠标操作
            # 检测鼠标位置和图片位置区域重合的操作
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if again_rect.left < pos[0] < again_rect.right and \
                   again_rect.top < pos[1] < again_rect.bottom:
                    #重新执行主函数
                    main()
                elif gameover_rect.left < pos[0] < gameover_rect.right and \
                     gameover_rect.top < pos[1] < gameover_rect.bottom:
                     pygame.quit()
                     sys.exit()

        
        
        #进行图片切换
        if not(delay%5):
            switch_image = not switch_image
        
        #进行延迟
        delay -= 1
        if not delay:
            delay = 100

                
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()         #停留作用



