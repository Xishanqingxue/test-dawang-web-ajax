# -*- coding:utf-8 -*-
from base.base_redis import BaseRedis
import datetime
import json
import settings

class Redis(BaseRedis):

    def get_image_captcha(self, device_id):
        # 获取图形验证码
        redis_value = self.get("LOGIN_CODE_{0}".format(device_id))
        return redis_value

    def delete_image_captcha(self, device_id):
        # 删除图形验证码
        self.remove("LOGIN_CODE_{0}".format(device_id))

    def clean_user_bean(self,user_id):
        # 删除用户大王豆
        self.remove(key='REDIS##BEAN##{0}'.format(user_id))

    def clean_user_buy_guard(self, user_id, anchor_id):
        # 清除用户守护信息
        self.remove(key='ROOM_USER_GUARD_FROM_ANCHOR_{0}'.format(anchor_id))
        self.hdel(name='ROOM_USER_GUARD_LIST', key='{0}_{1}'.format(anchor_id, user_id))
        self.hdel(name='ROOM_USER_GUARD_INFO_LIST', key=anchor_id)
        self.remove(key='I_GUARD_ANCHORS_REDIS_{0}'.format(user_id))

    def clean_black_user(self, anchor_id):
        # 清除黑名单
        self.hdel(name='YL_ROOM_BLACK_USER', key=anchor_id)

    def clean_red_packet(self, room_id, red_packet_id):
        # 清除红包信息
        self.remove(key='ACT_RED_PACKET_REDIS_REDPACKET_{0}_{1}'.format(room_id, red_packet_id))
        self.remove(key='ACT_RED_PACKET_REDIS__GET_LIST_{0}_{1}'.format(room_id, red_packet_id))
        self.remove(key='ACT_RED_PACKET_REDIS_{0}'.format(room_id))
        self.hdel(name='ACT_RED_PACKET_REDIS__LIST_', key=room_id)

    def clean_anchor_group(self, user_id, anchor_id):
        # 清除主播团信息
        self.hdel(name='ANCHOR_GROUP_KEY', key=user_id)
        self.hdel(name='ANCHOR_GROUP_KEY_ANCHOR_INFO', key=anchor_id)
        self.srem('ANCHOR_GROUP_KEY_{0}'.format(user_id), '{0}'.format(anchor_id))

    def clean_user_plat_signin(self, user_id):
        # 清除平台签到
        self.hdel(name='PLAT_SIGN_IN_USER', key=user_id)

    def clean_check_mobile_code(self, user_id):
        # 清除用户是否绑定手机号
        self.remove(key='check_moble_code_{0}'.format(user_id))

    def clean_user_task(self, user_id):
        # 清除用户任务信息
        self.remove(key='YL_USER_DAILY_TASK_REDIS_{0}_{1}'.format(user_id, datetime.datetime.now().strftime("%Y%m%d")))
        self.hdel(name='YL_USER_ONCE_TASK_REDIS_bind_mobile', key=user_id)

    def set_anchor_group_anchor_end_time(self, anchor_id, end_time):
        # 修海主播在主播团内过期时间
        details = self.hget(name='ANCHOR_GROUP_KEY_ANCHOR_INFO', key=anchor_id)
        details_dic = json.loads(details)
        details_dic['end_time'] = int(end_time)
        self.hset(name='ANCHOR_GROUP_KEY_ANCHOR_INFO', key=anchor_id,content=json.dumps(details_dic))

    def set_red_packet_end_time(self, room_id, red_packet_id, end_time):
        # 修改红包过期时间
        details = self.hget(name='ACT_RED_PACKET_REDIS_{0}'.format(room_id),key='DATA_{0}'.format(red_packet_id))
        details_dic = json.loads(details)
        details_dic['end_time'] = int(end_time)
        self.hset(name='ACT_RED_PACKET_REDIS_{0}'.format(room_id),key='DATA_{0}'.format(red_packet_id), content=json.dumps(details_dic))

    def set_user_plat_signin_day(self,user_id, day_num):
        # 修改平台签到天数
        details = self.hget(name='PLAT_SIGN_IN_USER', key=user_id)
        details_dic = json.loads(details)
        details_dic['signin_next_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        details_dic['signin_last_date'] = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        details_dic['signin_series_num'] = int(day_num)
        self.hset(name='PLAT_SIGN_IN_USER', key=user_id, content=json.dumps(details_dic))

    def check_anchor_dynamic(self,dynamic_id, status=1):
        # 模拟审核主播动态
        details = self.hget(name='USER_DYNAMIC_REDIS_DATA', key=dynamic_id)
        details_dic = json.loads(details)
        details_dic['status'] = status
        self.hset( name='USER_DYNAMIC_REDIS_DATA', key=dynamic_id, content=json.dumps(details_dic))
        score = format(float(1) / float(dynamic_id), '.16f')
        self.zadd('USER_DYNAMIC_REDIS_SQUARE', score, dynamic_id)

    def fix_dynamic_created_time(self,dynamic_id, created_time):
        # 修改动态的创建时间
        details = self.hget(name='USER_DYNAMIC_REDIS_DATA', key=dynamic_id)
        details_dic = json.loads(details)
        details_dic['create_time'] = created_time
        self.hset(name='USER_DYNAMIC_REDIS_DATA', key=dynamic_id, content=json.dumps(details_dic))

    def clean_doll_log(self,user_id,doll_log_id=8888):
        self.hdel(name='doll_log_status', key=doll_log_id)
        self.hdel(name='DOLL_MACHINE_PLAY_SUCCESS_LOG_DATA', key=doll_log_id)
        self.remove('DOLL_MACHINE_USER_LOG_LIST_{0}'.format(user_id))

    def add_doll_log(self,user_id, room_id, start_time, end_time, doll_log_id=8888):
        self.hset(name='doll_log_status', key=doll_log_id, content='1')
        self.rpush('DOLL_MACHINE_USER_LOG_LIST_{0}'.format(user_id), doll_log_id)
        details = {
            "id": doll_log_id,
            "user_id": user_id,
            "machine_id": 1,
            "room_id": room_id,
            "doll_id": 1,
            "end_time": end_time,
            "start_time": start_time,
            "status": 1,
            "post_time": None,
            "name": None,
            "mobilephone": None,
            "area": None,
            "address": None,
            "post_id": None,
            "post_company": None,
            "remarks": "",
            "operator": None,
            "postage": None,
            "doll_num": 1,
            "apply_time": None,
            "order_id": "20158692_15110173654985469265879"
        }
        self.hset(name='DOLL_MACHINE_PLAY_SUCCESS_LOG_DATA', key=doll_log_id,content=json.dumps(details))

    def doll_fake_consignment(self,doll_id,post_id,post_company):
        details = self.hget(name='DOLL_MACHINE_PLAY_SUCCESS_LOG_DATA',key=doll_id)
        details_dic = json.loads(details)
        details_dic['status'] = 4
        details_dic['post_id'] = post_id
        details_dic['post_company'] = post_company
        self.hset(name='DOLL_MACHINE_PLAY_SUCCESS_LOG_DATA',key=doll_id,content=json.dumps(details_dic))

    def clean_quiz_questions(self,room_id,question_ids):
        self.hdel('JC_ROOM_INNINGS',key=room_id)
        self.remove('JC_QUESTION_IDS_1_{0}'.format(room_id))
        self.remove('JC_QUESTION_IDS_2_{0}'.format(room_id))
        for x in question_ids:
            self.remove('JC_QUESTION_{0}'.format(x))
            self.remove('JC_AMOUNT_{0}'.format(x))


class RedisHold(BaseRedis):
    redis_host = settings.HOLD_REDIS_CONFIG['host']
    redis_port = settings.HOLD_REDIS_CONFIG['port']


    def clean_redis_user_detail(self, user_id):
        # 清除用户信息
        self.remove(key='CACHED_USER_PROPERTIES_{0}'.format(user_id))
        self.hdel(name='USERID', key=user_id)
        Redis().clean_user_bean(user_id)

    def clean_redis_room_detail(self, room_id, anchor_id):
        # 清除房间信息
        self.hdel(name='ROOM', key=room_id)
        self.hdel(name='ANCHOR_ROOM', key=anchor_id)
        self.remove(key='RANK_ANCHOR_COST_{0}'.format(anchor_id))

    def add_user_package_gift(self,user_id, gift_id, gift_num):
        # 添加背包礼物
        self.hset(name='CACHED_USER_PROPERTIES_{0}'.format(user_id), key='package_{0}'.format(gift_id), content=gift_num)
