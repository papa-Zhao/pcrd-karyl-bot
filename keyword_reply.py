import random2 as random

def get_key_msg(str, name):

    msg = [ name + '，是你救了我嗎？嗯，既然這樣還是要謝謝你呢\nヽ(￣ω￣〃)ゝ',
            '其實啊，和' + name + '交情太好是不行的...\n不過，反正很開心就算了吧♪', 
            '我的魔法，挺厲害的吧？哼哼～♪\n' + name +  '你再多讚美讚美我幾句♪',
            '完美完美! 紮紮實實地越來越厲害了不是嘛♪\n我果然是想做就做得到！',
            '恢復魔法也多少會用了，要是有什麼萬一的話，也不是救不了'+ name + '你啦。不過這種萬一還是不要發生比較好啦><',
            '和那傢伙的心靈相連之力... 感覺還不賴呢。\n什麼！' + name + '你都聽到了嗎！？\n馬、馬上給我忘了，笨蛋啊啊～！',
            '我會用這股新的力量保護你的... 那個... \n' + name + '，你不准離開我身邊喔！',
            '我的魔力和' + name + '的力量逐漸合而為一... ! \n來，放馬過來吧！今天的我可是脫胎換骨了！',
            '這就是你和我的真正的力量呢...! \n只要和' + name + '再一起，感覺就不會輸！',
            ]

    num = random.randint(0,len(msg))

    return msg[num]

def get_url(str):
    
    index = -1
    key = ['街頭霸王', '開車', '表情包', '聯盟戰', '可愛', '抽卡', '吸貓']
    
    try:
        index = key.index(str)
        #print (key.index(str))
    except ValueError:
        print ('not found')
        return ''

    pic = [[]]* len(key)
    ##########  街頭霸王  ##########
    pic[0] = [ 'https://i.imgur.com/M4J9ITo.png', ]

    ##########  開車  ##########
    pic[1] = [  'https://i.imgur.com/LTulvSl.png',
                'https://i.imgur.com/WXqDg3U.jpg', 
                'https://i.imgur.com/O91uIEr.jpg',]

    ##########  表情包  ##########
    pic[2] = [ 'https://i.imgur.com/Pq4ZKbKundefined.jpg',
            'https://i.imgur.com/447X3SHundefined.jpg',
            'https://i.imgur.com/nRDwwfhundefined.png',]

    ##########  聯盟戰  ##########
    pic[3] = [ 'https://i.imgur.com/m5IHopB.jpg',]

    ##########  可愛  ##########
    pic[4] = [ 'https://i.imgur.com/OVyshBN.png',
               'https://i.imgur.com/oogUT8a.jpg',
             'https://i.imgur.com/RidaRp7.jpg',
             'https://i.imgur.com/N4KnPG3.jpg',
             'https://i.imgur.com/Bw5y2Gm.jpg',
             'https://i.imgur.com/XvyHsFN.jpg',
             'https://i.imgur.com/poLP1Fk.jpg',]

    ##########  抽卡  ##########
    pic[5] = [ 'https://i.imgur.com/zEIREkf.png',
            'https://i.imgur.com/iYMLtCL.jpg',
            'https://i.imgur.com/pVVmvXQ.jpg',]

    ##########  吸貓  ##########
    pic[6] = [ 'https://i.imgur.com/2RCwFWo.jpg',
            'https://i.imgur.com/raly7gr.jpg',
            'https://i.imgur.com/TzFraet.png',
            'https://i.imgur.com/KJgBCUj.png',
            'https://i.imgur.com/NU6IZ4q.jpg',]
    
    num = random.randint(1,len(pic[index]))%len(pic[index])
    url = pic[index][num]
    
    return url