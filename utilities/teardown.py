# -*- coding:utf-8 -*-
from utilities.mysql_helper import MysqlOperation
from api.follow_api import RelieveFollowingApi
from utilities.redis_helper import Redis,RedisHold
from api.super_visor_api import DelSuperVisorApi
import time



class TearDown(object):
    time_sleep = 1
    dynamic_ids = []


    def guard_teardown(self,login_name=None,user_id=None,anchor_id=None,following=False):
        if following:
            relieve_following_api = RelieveFollowingApi(login_name)
            relieve_following_api.get({'anchor_id': anchor_id})
        Redis().clean_user_buy_guard(user_id, anchor_id)
        MysqlOperation(user_id=user_id).clean_user_guard()

    def register_teardown(self,login_name):
        RedisHold().clean_redis_user_detail(MysqlOperation(mobile=login_name).get_user_id())
        Redis().clean_user_bean(MysqlOperation(mobile=login_name).get_user_id())
        MysqlOperation(mobile=login_name).delete_user()

    def platform_signin_teardown(self,user_id):
        # RedisHold().clean_redis_user_detail(user_id)
        # Redis().clean_user_bean(user_id)
        MysqlOperation(user_id=user_id).clean_user_platform_sign()
        Redis().clean_user_plat_signin(user_id)
        # time.sleep(0.2)

    def gold_exchange_diamond_teardowm(self,user_id):
        #金币转换大王豆
        mysql_operation = MysqlOperation(user_id=user_id)
        # mysql_operation.fix_user_account().clean_user_account_log()
        mysql_operation.clean_exchange_log()
        # RedisHold().clean_redis_user_detail(user_id)
        # time.sleep(self.time_sleep)

    def update_nickname_api_teardown(self,user_id,rename_num,nick_name):
        #修改昵称
        mysql_operation = MysqlOperation(user_id=user_id)
        mysql_operation.fix_user_nickname(nickname=nick_name)
        mysql_operation.fix_user_update_nick_num(rename_num=rename_num)
        # mysql_operation.clean_user_account_log()
        RedisHold().clean_redis_user_detail(user_id)
        # Redis().clean_user_bean(user_id)

    def noble_teardown(self,user_id):
        #购买贵族和贵族续费
        MysqlOperation(user_id=user_id).clean_user_noble()
        # RedisHold().clean_redis_user_detail(user_id)
        time.sleep(0.3)

    def get_sun_api_teardown(self,user_id):
        #获得阳光
        MysqlOperation(user_id=user_id).fix_user_sun_num()
        # RedisHold().clean_redis_user_detail(user_id)
        # Redis().clean_user_bean(user_id)

    def report_anchor(self,user_id):
        #举报主播
        MysqlOperation(user_id=user_id).clean_user_report()

    def change_mobile_teardown(self,new_mobile,login_name,mobile_phone):
        #修改手机号
        user_id = MysqlOperation(mobile=new_mobile).get_user_id()
        mysql_operation = MysqlOperation(user_id=user_id)
        mysql_operation.fix_user_bind_mobile(login_name, mobile_phone, phone_confirm=1)
        RedisHold().clean_redis_user_detail(user_id)

    def bind_phone_teardown(self,user_id,login_name,mobile_phone=None,phone_confirm=0):
        #绑定手机号
        MysqlOperation(user_id=user_id).fix_user_bind_mobile(login_name,mobile_phone,phone_confirm)
        Redis().clean_check_mobile_code(user_id)
        # RedisHold().clean_redis_user_detail(user_id)
        time.sleep(0.2)

    def send_red_package_teardown(self,room_id,user_id,anchor_id):
        red_packet_ids = MysqlOperation(room_id=room_id).get_red_packet_ids()
        MysqlOperation(room_id=room_id).clean_red_packet()
        MysqlOperation(user_id=user_id, anchor_id=anchor_id).clean_send_gift()
        for i in red_packet_ids:
            Redis().clean_red_packet(room_id, i['id'])
        RedisHold().clean_redis_room_detail(room_id,anchor_id)
        # for x in [user_id,anchor_id]:
        #     MysqlOperation(user_id=x).fix_user_rank_and_experience().clean_user_account_log()
        #     RedisHold().clean_redis_user_detail(user_id)
        # time.sleep(self.time_sleep)

    def send_gift_teardown(self,login_name=None,anchor_id=None,user_id=None,room_id=None,following=True):
        if following:
            relieve_following_api = RelieveFollowingApi(login_name)
            relieve_following_api.get({'anchor_id':anchor_id})
        mysql_operation = MysqlOperation(user_id=user_id, anchor_id=anchor_id)
        # mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        # MysqlOperation(anchor_id=anchor_id).fix_anchor_rank_and_exp()
        # for x in [user_id, anchor_id]:
        #     MysqlOperation(user_id=x).fix_user_rank_and_experience()
        #     RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(room_id,anchor_id)
        # time.sleep(self.time_sleep)

    def add_anchor_to_group_teardown(self,user_id,anchor_id):
        mysql_operation = MysqlOperation(user_id=user_id)
        mysql_operation.fix_user_rank_and_experience()
        mysql_operation.fix_user_account()
        Redis().clean_anchor_group(user_id, anchor_id)
        for i in [user_id, anchor_id]:
            RedisHold().clean_redis_user_detail(i)
            MysqlOperation(user_id=i).clean_user_anchor_group().clean_user_account_log()
        Redis().clean_user_buy_guard(user_id, anchor_id)
        time.sleep(self.time_sleep)

    def anchor_num_teardown(self,room_id,user_id,anchor_id):
        mysql_operation = MysqlOperation(user_id=user_id)
        mysql_operation.clean_user_anchor_group()
        Redis().clean_anchor_group(user_id, anchor_id)
        mysql_operation.fix_user_rank_and_experience()
        mysql_operation.fix_user_account().clean_user_account_log()
        RedisHold().clean_redis_user_detail(user_id)
        Redis().clean_user_bean(user_id)
        RedisHold().clean_redis_room_detail(room_id, anchor_id)

    def add_black_teardown(self,anchor_login_name,user_id,anchor_id,other_anchor_id):
        del_super_visor_api = DelSuperVisorApi(anchor_login_name)
        del_super_visor_api.get({'user_id':user_id, 'anchor_id':anchor_id})
        for x in [user_id, other_anchor_id]:
            MysqlOperation(user_id=x).clean_black_user()
        Redis().clean_black_user(anchor_id)
        time.sleep(1)


