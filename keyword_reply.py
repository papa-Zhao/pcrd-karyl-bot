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

        num = random.randint(0,len(msg)-1)

        return msg[num]

        
def get_key_sticker(index):
    
        key_url = ['https://i.imgur.com/gqQChYE.png', 'https://i.imgur.com/If10Ro6.png', 'https://i.imgur.com/Fiv2GrA.png', 'https://i.imgur.com/LtVXZk8.png',
                'https://i.imgur.com/TKAA7ae.png', 'https://i.imgur.com/ctyb23o.png', 'https://i.imgur.com/65rertq.png', 'https://i.imgur.com/pluh4iW.png',
                'https://i.imgur.com/2ifRR0Y.png', 'https://i.imgur.com/q9fGATO.png', 'https://i.imgur.com/reLCrko.png', 'https://i.imgur.com/7zkiHZp.png',
                'https://i.imgur.com/nOf8YQ9.png', 'https://i.imgur.com/3nPO6Uj.png', 'https://i.imgur.com/A5oN2vd.png', 'https://i.imgur.com/98iH6u1.png', 
                'https://i.imgur.com/7C2Pf7I.png', 'https://i.imgur.com/q1WbaKj.png', 'https://i.imgur.com/h7ZnaIp.png', 'https://i.imgur.com/W25wzZi.png',
                'https://i.imgur.com/TpGirhX.png', 'https://i.imgur.com/aGAR4c1.png', 'https://i.imgur.com/awE4VVQ.png', 'https://i.imgur.com/2Z2Tqad.png',
                'https://i.imgur.com/kFavn96.png', 'https://i.imgur.com/QnSUj0X.png',  'https://i.imgur.com/2PFcjKE.png',
                'https://i.imgur.com/x9zqDy8.jpg', 'https://i.imgur.com/Pq4ZKbK.jpg', 'https://i.imgur.com/447X3SH.jpg', 'https://i.imgur.com/nRDwwfh.png',
                'https://i.imgur.com/UHXCPLF.jpg', 'https://i.imgur.com/EFdFnQL.jpg', 'https://i.imgur.com/88BT0c9.jpg', 'https://i.imgur.com/aRjLcpr.jpg'
                ]

        return key_url[index]

        
