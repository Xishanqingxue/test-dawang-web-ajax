# -*- coding:utf-8 -*-
from ajax.live_user_get_sun import UserGetSunAjax
from ajax.user_follow import AddFollowAjax,RelieveFollowAjax
from ajax.live_buy_sun import BuySunAjax
from ajax.live_new_server import LiveNewServer
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold
from base.base_case import BaseCase
import settings
import time


class TestGetSunAjax(BaseCase):
    """
    获取太阳
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def setUp(self, *args):
        super(TestGetSunAjax,self).setUp()
        MysqlOperation(user_id=self.user_id).fix_user_sun_num()
        RedisHold().clean_redis_user_detail(self.user_id)

    def test_user_get_sun_success(self):
        """
        测试获取太阳成功
        :return:
        """
        user_get_sun = UserGetSunAjax(self.user_mobile)
        user_get_sun.get({'room_id':self.room_id,'anchor_id':self.anchor_id})
        self.assertEqual(user_get_sun.get_resp_code(),0)

        result = user_get_sun.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['sun_num'],1)

    def test_user_get_sun_room_id_null(self):
        """
        测试请求接口房间ID为空，可以成功
        :return:
        """
        user_get_sun = UserGetSunAjax(self.user_mobile)
        user_get_sun.get({'room_id':None,'anchor_id':self.anchor_id})
        self.assertEqual(user_get_sun.get_resp_code(),0)

    def test_user_get_sun_room_id_error(self):
        """
        测试请求接口房间ID不存在，可以成功
        :return:
        """
        user_get_sun = UserGetSunAjax(self.user_mobile)
        user_get_sun.get({'room_id':111111,'anchor_id':self.anchor_id})
        self.assertEqual(user_get_sun.get_resp_code(),0)

    def test_user_get_sun_anchor_id_null(self):
        """
        测试请求接口主播ID为空，可以成功
        :return:
        """
        user_get_sun = UserGetSunAjax(self.user_mobile)
        user_get_sun.get({'room_id':self.room_id,'anchor_id':None})
        self.assertEqual(user_get_sun.get_resp_code(),402005)
        self.assertEqual(user_get_sun.get_resp_message(),'主播ID不能为空')

    def test_user_get_sun_anchor_id_error(self):
        """
        测试请求接口主播ID不存在，可以成功
        :return:
        """
        user_get_sun = UserGetSunAjax(self.user_mobile)
        user_get_sun.get({'room_id':self.room_id,'anchor_id':90909090})
        self.assertEqual(user_get_sun.get_resp_code(),0)

    def test_user_get_sun_reach_the_limit(self):
        """
        测试太阳达到上限后请求接口
        :return:
        """
        MysqlOperation(user_id=self.user_id).fix_user_sun_num(sun_num=50)
        RedisHold().clean_redis_user_detail(self.user_id)
        user_get_sun = UserGetSunAjax(self.user_mobile)
        user_get_sun.get({'room_id':self.room_id,'anchor_id':self.anchor_id})
        self.assertEqual(user_get_sun.get_resp_code(),402016)
        self.assertEqual(user_get_sun.get_resp_message(),'到达上限')

    def tearDown(self, *args):
        super(TestGetSunAjax,self).tearDown()
        MysqlOperation(user_id=self.user_id).fix_user_sun_num()
        RedisHold().clean_redis_user_detail(self.user_id)





class TestBuySunAjax(BaseCase):
    """
    购买太阳
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def setUp(self, *args):
        super(TestBuySunAjax, self).setUp()
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        time.sleep(0.3)

    def test_buy_sun_no_following_success(self):
        """
        测试未关注主播购买太阳
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=2000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']
        # 获取太阳数量
        sun_num = live_result['room_obj']['sun_num']

        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':self.room_id,'anchor_id':self.anchor_id})
        self.assertEqual(buy_sun.get_resp_code(),0)

        buy_sun_result = buy_sun.get_resp_result()

        anchor_obj = buy_sun_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(anchor_obj['anchor_experience'], 0)

        identity_obj = buy_sun_result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'],0)
        # 校验用户等级
        self.assertEqual(identity_obj['user_rank'],1)
        # 校验用户经验值增加
        self.assertEqual(identity_obj['user_experience'],2000)
        # 校验亲密度
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])

        # 获取购买太阳成功后房间热度
        after_buy_sun_hot_num = buy_sun_result['room_obj']['curr_hot_num']
        after_buy_sun_sun_num = buy_sun_result['room_obj']['sun_num']

        self.assertEqual(after_buy_sun_hot_num - hot_num , 0)
        self.assertEqual(after_buy_sun_sun_num - sun_num , 20)


    def test_buy_sun_following_success(self):
        """
        测试关注主播购买太阳
        :return:
        """

        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=2000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']
        # 获取太阳数量
        sun_num = live_result['room_obj']['sun_num']

        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':self.room_id,'anchor_id':self.anchor_id})
        self.assertEqual(buy_sun.get_resp_code(),0)

        buy_sun_result = buy_sun.get_resp_result()

        anchor_obj = buy_sun_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(anchor_obj['anchor_experience'], 0)

        identity_obj = buy_sun_result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'],0)
        # 校验用户等级
        self.assertEqual(identity_obj['user_rank'],1)
        # 校验用户经验值增加
        self.assertEqual(identity_obj['user_experience'],2000)
        # 校验亲密度
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],1)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],10000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)

        # 获取购买太阳成功后房间热度
        after_buy_sun_hot_num = buy_sun_result['room_obj']['curr_hot_num']
        after_buy_sun_sun_num = buy_sun_result['room_obj']['sun_num']

        self.assertEqual(after_buy_sun_hot_num - hot_num , 0)
        self.assertEqual(after_buy_sun_sun_num - sun_num , 20)

    def tearDown(self, *args):
        super(TestBuySunAjax, self).tearDown()
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        time.sleep(0.3)





class TestBuySunAjaxAbnormal(BaseCase):
    """
    购买太阳-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def test_buy_sun_gold_low(self):
        """
        测试购买太阳账户金币不足
        :return:
        """
        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':self.room_id,'anchor_id':self.anchor_id})
        self.assertEqual(buy_sun.get_resp_code(),100032)
        self.assertEqual(buy_sun.get_resp_message(),'账户金币不足')

    def test_buy_sun_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':None,'anchor_id':self.anchor_id})
        self.assertEqual(buy_sun.get_resp_code(),402000)
        self.assertEqual(buy_sun.get_resp_message(),'房间ID不能为空')

    def test_buy_sun_room_id_error(self):
        """
        测试请求接口房间ID不存在
        :return:
        """
        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':'909090','anchor_id':self.anchor_id})
        self.assertEqual(buy_sun.get_resp_code(),402004)
        self.assertEqual(buy_sun.get_resp_message(),'获取直播间数据错误:直播间不存在')

    def test_buy_sun_anchor_id_null(self):
        """
        测试请求接口主播ID为空
        :return:
        """
        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':self.room_id,'anchor_id':None})
        self.assertEqual(buy_sun.get_resp_code(),100032)
        self.assertEqual(buy_sun.get_resp_message(),'账户金币不足')

    def test_buy_sun_anchor_id_error(self):
        """
        测试请求接口主播ID不存在
        :return:
        """
        buy_sun = BuySunAjax(self.user_mobile)
        buy_sun.get({'room_id':self.room_id,'anchor_id':'90909090'})
        self.assertEqual(buy_sun.get_resp_code(),100032)
        self.assertEqual(buy_sun.get_resp_message(),'账户金币不足')