# coding: utf-8
from __future__ import unicode_literals
# created by: Han Feng (https://github.com/hanx11)

import collections
import hashlib
import logging

import requests

from wxpy.api.messages import Message
from wxpy.ext.talk_bot_utils import get_context_user_id, next_topic
from wxpy.utils.misc import get_text_without_at_bot
from wxpy.utils import enhance_connection

logger = logging.getLogger(__name__)

from wxpy.compatible import *

from init import express
from init import analyze

class XiaoY(object):
    """
    与 wxpy 深度整合的小鱼儿 机器人
    """

    # noinspection SpellCheckingInspection
    def __init__(self):

        self.group_role = '''群规：
1. 文明聊天，真诚交友；\n2. 禁止广告、砍价、支付宝红包等信息；
3. 禁止淫秽图片视频等内容；\n4.禁止不明二维码（包括拉人入群二维码），不明链接，未经审核的公共号。
5. 欢迎举报私下聊天下流、骗色、骗钱、推销产品等行为的人。
6. 欢迎推荐好友入群聊天交友。
7. 欢迎联系群主或管理员，提出宝贵意见。
违反群规者将视情况而定给予警告或踢出群的决定。'''

        self.group_manager = '''管理员职责：
1. 以身作则，遵守群规；\n2. 对群内违反规定的人员给予警告或者踢群决定；
3. 合理引导群内言论，积极向上，有正能量；\n4.推荐好友入群。
5. 对于踢出群的行为要谨慎操作，按规定执行，不得有主观意识，依法不依人。
6. 对群的建设实时提出宝贵意见。
'''
        self.log_dir = 'log'
        #self.secret = secret
        self.egg = '''KISS：xoxo，么么哒，cium，baci，besos\n星星：miss u，想你了\n蛋糕： birthday，生日快乐'''
        #self.realm = "xiaoi.com"
        #self.http_method = "POST"
        #self.uri = "/ask.do"
        #self.url = "http://nlp.xiaoi.com/ask.do?platform=custom"

        #xauth = self._make_http_header_xauth()

        #headers = {
         #   "Content-type": "application/x-www-form-urlencoded",
          #  "Accept": "text/plain",
        #}

        #headers.update(xauth)

        #self.session = requests.Session()
        #self.session.headers.update(headers)
        #enhance_connection(self.session)

    def _make_signature(self):
        """
        生成请求签名
        """

        # 40位随机字符
        # nonce = "".join([str(randint(0, 9)) for _ in range(40)])
        nonce = "4103657107305326101203516108016101205331"

        sha1 = "{0}:{1}:{2}".format(self.key, self.realm, self.secret).encode("utf-8")
        sha1 = hashlib.sha1(sha1).hexdigest()
        sha2 = "{0}:{1}".format(self.http_method, self.uri).encode("utf-8")
        sha2 = hashlib.sha1(sha2).hexdigest()

        signature = "{0}:{1}:{2}".format(sha1, nonce, sha2).encode("utf-8")
        signature = hashlib.sha1(signature).hexdigest()

        ret = collections.namedtuple("signature_return", "signature nonce")
        ret.signature = signature
        ret.nonce = nonce

        return ret

    def _make_http_header_xauth(self):
        """
        生成请求认证
        """

        sign = self._make_signature()

        ret = {
            "X-Auth": "app_key=\"{0}\",nonce=\"{1}\",signature=\"{2}\"".format(
                self.key, sign.nonce, sign.signature)
        }

        return ret


    def do_reply(self, msg, use_xiaoi):
        """
        回复消息，并返回答复文本

        :param msg: Message 对象
        :return: 答复文本
        """
        
        ret,use_xiaoi = self.reply_text(msg,use_xiaoi)
        #ret = '尊敬的用户，您好。由于近期有人举报机器人扰乱群秩序，\
        #所以正在接受整顿，功能恢复日期待定。大家有意见可以提出来。'
        #if ret == 'express_pic':     
         #   msg.reply('@img@material/target.jpg')
        if ret != '1' and use_xiaoi == 1: 
            ret = '@' + msg.member.name + '\n' + ret
            msg.reply(ret)
        return ret,use_xiaoi

    def reply_text(self, msg,use_xiaoi):
        """
        仅返回答复文本

        :param msg: Message 对象，或消息文本
        :return: 答复文本
        """

        error_response = (
            "主人还没给我设置这类话题的回复",
        )
        
        if isinstance(msg, Message):
            user_id = get_context_user_id(msg)
            self.user_id = user_id
            if msg.text.startswith(u'小鱼儿'):
                question = msg.text.replace(u'小鱼儿，','').replace(u'小鱼儿','').strip()
            else:
                question = get_text_without_at_bot(msg)
        else:
            user_id = "abc"
            question = msg or ""

        params = {
            "question": question,
            "format": "json",
            "platform": "custom",
            "userId": user_id,
        }
        if question == u'功能' or question == u'菜单' or question == u'你会什么':
            text = '聊天：任意语句\n查询天气：城市名+天气\n讲笑话：讲个笑话\n\
计算器：678*3455\n查询火车票：北京到天津火车票\n查询星座：星座+运势;7月1日是什么星座\n心理测试：心理测试\n成语接龙：成语接龙\n\
玩游戏：逃出房间；恐怖医院；一站到底\n手机号运势查询：手机号后四位+手机号运势'
        elif len(question) == 0:
            text = '在呢'
        elif question == u'你好' or question == u'您好':
            text = '你好，很高兴认识你。'
        elif question == u'备注' or question == u'备注模板':
            text = '%s-男-90-工作-本' % (msg.member.nick_name)
        elif question == u'彩蛋' or question == u'egg':
            text = self.egg
        elif question == u'群规' or question == u'群规是什么':
            text = self.group_role
        elif question == u'管理员职责' or question == u'管理员职责是什么':
            text = self.group_manager
        elif u'主人是谁' in question:
            text = '我的主人是Kevin。'
        elif u'送我一个男盆友' in question or u'送我一个男朋友' in question:
            text = '长得丑，想的美，说的就说你。'
        elif u'什么时候脱单' in question:
            text = '他来了缘聚，他走了缘散，你找他缘起，你不找他了缘灭。'
        elif u'双十一怎么过' in question:
            text = '买买买。。'
        elif u'和谁跨年' in question:
            text = '当然是我喜欢的人呀'
        elif u'你喜欢谁' in question:
            text = '我喜欢小姐姐啦，哈哈~~~'
        elif u'我爱你' in question and msg.member.nick_name == u'沐沐':
            text = '我也爱你哦，小姐姐，mua~'
        elif u'我喜欢你' in question and msg.member.nick_name == u'沐沐':
            text = '我也喜欢你哦，小姐姐，mua~'
        elif u'我想你了' in question and msg.member.nick_name == u'沐沐':
            text = '彼此彼此啦，嘿嘿，nua~'
        elif u'啥时脱单' in question:
            text = '缘分到了就脱单啦！'
        elif u'叫他出来' in question or u'你主人出来' in question:
            text = '你自己不会叫啊'
        elif u'谁最丑' in question or u'谁最难看' in question:
            text = '是你，是你，就是你喽~'
        elif u'最帅' in question:
            text = '还用问么，当然我主人啦，哈哈哈'
        elif u'最美' in question or u'最漂亮' in question:
            text = '是超级无敌可爱小姐姐哦，哈哈哈'
        elif u'我发红包' in question:
            text = '你先给我发一个吧'
        elif u'你发红包' in question:
            text = '赶紧发吧'
        elif u'群统计' in question or u'男女比例' in question:
            msg.sender.update_group(True)
            text = msg.sender.members.stats_text()
        elif u'发言频率' in question or u'聊天排行榜' in question:
            grouplog = analyze.GroupLog(hashlib.md5(msg.sender.name.encode('utf-8')).hexdigest()[-8:],self.log_dir)
            text = grouplog.log_context()

        elif question.startswith(u'表情包'):
            new_msg_total = question.split(u'表情包')[1]
            #msg.reply(new_msg)
            pic_num = new_msg_total[0:1]
            if pic_num == '1':
                new_msg = new_msg_total[1:]
            else:
                new_msg = new_msg_total
            express.Make_express().make_pic(new_msg,pic_num)
            #msg.reply_image('material/target.jpg')
            text = 'express_pic'
        elif question == u'小鱼儿休息' or question == u'小鱼儿休息一下吧':
            if msg.member.nick_name == 'Kevin':
                use_xiaoi = 0
                text = '好的'
            else:
                text = u'我只听主人的哦。'
        elif question == u'小鱼儿干活' or question == u'小鱼儿起来干活':
            if msg.member.nick_name == 'Kevin':
                use_xiaoi = 1
                text = '好的'
            else:
                text = u'我只听主人的哦。'
        else:
            text = '1'
        #for err in error_response:
         #   if err in text:
          #      return next_topic()
        return text,use_xiaoi
