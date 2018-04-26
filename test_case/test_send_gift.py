# -*- coding:utf-8 -*-
from ajax.live_new_server import LiveNewServer
from ajax.live_send_gift import LiveSendGift
from ajax.user_follow import AddFollowAjax,RelieveFollowAjax
from ajax.user_consumption import ConsumptionAjax
from base.base_case import BaseCase
from base.base_helper import convert_to_timestamp
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold
import settings
import time


class TestLiveSendGiftAjaxAbnormal(BaseCase):
    """
    送礼物-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    gift_id = 60
    gift_gold = 100

    def test_send_gift_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': None, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 402000)
        self.assertEqual(send_gift_ajax.get_resp_message(),u'房间ID不能为空')

    def test_send_gift_room_id_error(self):
        """
        测试请求接口房间ID不存在
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': 111999, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 801017)
        self.assertEqual(send_gift_ajax.get_resp_message(),u'房间信息不存在')

    def test_send_gift_anchor_id_null(self):
        """
        测试请求接口主播ID为空
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': None, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 100032)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'账户金币不足')

    def test_send_gift_anchor_id_error(self):
        """
        测试请求接口主播ID不存在
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': 90909090, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 100032)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'账户金币不足')

    def test_send_gift_gift_id_null(self):
        """
        测试请求接口礼物ID为空
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': None,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 402009)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'礼物ID不存在')

    def test_send_gift_gift_id_error(self):
        """
        测试请求接口礼物ID不存在
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': 9999,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 402020)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'礼物信息不存在')

    def test_send_gift_gift_count_null(self):
        """
        测试请求接口礼物数量为空
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': None, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 402010)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'礼物数量不能是空')

    def test_send_gift_currency_null(self):
        """
        测试请求接口货币类型为空
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': None})
        self.assertEqual(send_gift_ajax.get_resp_code(), 460004)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'请选择货币类型')

    def test_send_gift_currency_error(self):
        """
        测试请求接口货币类型不存在
        :return:
        """
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'abc'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 460004)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'请选择货币类型')

    def test_send_gift_gold_low(self):
        """
        测试请求接口用户余额不足
        :return:
        """
        # 清除用户金币
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=0)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 100032)
        self.assertEqual(send_gift_ajax.get_resp_message(), u'账户金币不足')






class TestLiveSendGiftNoFollowing(BaseCase):
    """
    未关注主播送礼物
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    gift_id = 60
    gift_gold = 100

    def setUp(self, *args):
        super(TestLiveSendGiftNoFollowing, self).setUp()
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        time.sleep(0.3)

    def test_send_gift_1(self):
        """
        测试送出1个金币礼物
        :return:
        """
        gift_count = 1
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk,5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])


    def test_send_gift_66(self):
        """
        测试送出66个金币礼物
        :return:
        """
        gift_count = 1
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_send_gift_99(self):
        """
        测试送出99个金币礼物
        :return:
        """
        gift_count = 99
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_send_gift_188(self):
        """
        测试送出188个金币礼物
        :return:
        """
        gift_count = 188
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_send_gift_520(self):
        """
        测试送出520个金币礼物
        :return:
        """
        gift_count = 520
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count - 50000)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 2)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count - 50000)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_send_gift_1314(self):
        """
        测试送出1314个金币礼物
        :return:
        """
        gift_count = 1314
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count - 50000)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 3)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count - 100000)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def tearDown(self, *args):
        super(TestLiveSendGiftNoFollowing, self).tearDown()
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        time.sleep(0.3)




class TestLiveSendGiftFollowing(BaseCase):
    """
    关注主播送礼物
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    gift_id = 60
    gift_gold = 100

    def setUp(self, *args):
        super(TestLiveSendGiftFollowing, self).setUp()
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

    def test_following_send_gift_1(self):
        """
        测试关注主播送出1个金币礼物
        :return:
        """
        gift_count = 1
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_66(self):
        """
        测试关注主播送出66个金币礼物
        :return:
        """
        gift_count = 66
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_99(self):
        """
        测试关注主播送出99个金币礼物
        :return:
        """
        gift_count = 99
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_188(self):
        """
        测试关注主播送出188个金币礼物
        :return:
        """
        gift_count = 188
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count - 10000)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 2)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 40000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_520(self):
        """
        测试关注主播送出520个金币礼物
        :return:
        """
        gift_count = 520
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count - 50000)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 2)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count - 50000)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count - 50000)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 3)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 50000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])


    def test_following_send_gift_1314(self):
        """
        测试关注主播送出1314个金币礼物
        :return:
        """
        gift_count = 1314
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count - 50000)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 3)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count - 100000)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count - 100000)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 4)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 100000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'糖果')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def tearDown(self, *args):
        super(TestLiveSendGiftFollowing, self).tearDown()
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







class TestLiveSendGiftFollowingAtDiscount(BaseCase):
    """
    关注主播送礼物打折
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    gift_id = 4001
    gift_gold = 100

    def setUp(self, *args):
        super(TestLiveSendGiftFollowingAtDiscount, self).setUp()
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

    def test_following_send_gift_1(self):
        """
        测试关注主播送出1个金币礼物不打折
        :return:
        """
        gift_count = 1
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'金币弹')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_66(self):
        """
        测试关注主播送出66个金币礼物不打折
        :return:
        """
        gift_count = 66
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count)
        self.assertEqual(consume_list[0]['corresponding_id'],self.gift_id)
        self.assertEqual(consume_list[0]['corresponding_name'],'金币弹')
        self.assertEqual(consume_list[0]['corresponding_num'],gift_count)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(self.gift_gold * gift_count))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_99(self):
        """
        测试关注主播送出99个金币礼物95折
        :return:
        """
        gift_count = 99
        ratio = 0.95
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count * ratio)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count * ratio)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count * ratio)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count * ratio)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count * ratio)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count * ratio)
        self.assertEqual(consume_list[0]['corresponding_id'],int(str(self.gift_id) + '9900'))
        self.assertEqual(consume_list[0]['corresponding_name'],'金币弹 {0}个'.format(gift_count))
        self.assertEqual(consume_list[0]['corresponding_num'],1)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(int(self.gift_gold * gift_count * ratio)))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_188(self):
        """
        测试关注主播送出188个金币礼物9折
        :return:
        """
        gift_count = 188
        ratio = 0.9
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count * ratio)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count * ratio)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count * ratio)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count * ratio - 10000)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 2)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 40000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count * ratio)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count * ratio)
        self.assertEqual(consume_list[0]['corresponding_id'],int(str(self.gift_id) + '1880'))
        self.assertEqual(consume_list[0]['corresponding_name'],'金币弹 {0}个'.format(gift_count))
        self.assertEqual(consume_list[0]['corresponding_num'],1)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(int(self.gift_gold * gift_count * ratio)))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_following_send_gift_520(self):
        """
        测试关注主播送出520个金币礼物85折
        :return:
        """
        gift_count = 520
        ratio = 0.85
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count * ratio)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count * ratio)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count * ratio)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count * ratio - 10000)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 2)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 40000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count * ratio)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count * ratio)
        self.assertEqual(consume_list[0]['corresponding_id'],int(str(self.gift_id) + '5200'))
        self.assertEqual(consume_list[0]['corresponding_name'],'金币弹 {0}个'.format(gift_count))
        self.assertEqual(consume_list[0]['corresponding_num'],1)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(int(self.gift_gold * gift_count * ratio)))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])


    def test_following_send_gift_1314(self):
        """
        测试关注主播送出1314个金币礼物8折
        :return:
        """
        gift_count = 1314
        ratio = 0.8
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=self.gift_gold * gift_count * ratio)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])
        gift_intimacy = int(gift_details['add_intimacy'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count * ratio - 50000)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 3)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count * ratio - 100000)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], gift_intimacy * gift_count * ratio - 100000)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 4)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 100000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count * ratio)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'],self.user_id)
        self.assertEqual(consume_list[0]['type'],u'1')
        self.assertEqual(consume_list[0]['gold'],self.gift_gold * gift_count * ratio)
        self.assertEqual(consume_list[0]['corresponding_id'],int(str(self.gift_id) + '1314'))
        self.assertEqual(consume_list[0]['corresponding_name'],'金币弹 {0}个'.format(gift_count))
        self.assertEqual(consume_list[0]['corresponding_num'],1)
        self.assertEqual(consume_list[0]['room_id'],self.room_id)
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'送礼')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(int(self.gift_gold * gift_count * ratio)))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def tearDown(self, *args):
        super(TestLiveSendGiftFollowingAtDiscount, self).tearDown()
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







class TestLiveSendPackageGiftFollowing(BaseCase):
    """
    关注主播送背包礼物
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    gift_id = 1009

    def setUp(self, *args):
        super(TestLiveSendPackageGiftFollowing, self).setUp()
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

    def test_send_package_gift_following(self):
        """
        测试关注主播送出1个为你伴舞礼物
        :return:
        """
        # 添加背包礼物
        RedisHold().add_user_package_gift(self.user_id, gift_id=self.gift_id, gift_num=1)
        time.sleep(0.3)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']
        # 校验背包礼物
        user_package = live_result['identity_obj']['user_package']
        self.assertEqual(len(user_package),1)
        self.assertEqual(user_package[0]['tool_id'],self.gift_id)
        self.assertEqual(user_package[0]['tool_num'],1)

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp - 50000)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 3)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], 0)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 4)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 100000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot)
        # 校验无消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),0)

    def test_send_package_gift_not_following(self):
        """
        测试未关注主播送出1个为你伴舞礼物
        :return:
        """
        # 添加背包礼物
        RedisHold().add_user_package_gift(self.user_id, gift_id=self.gift_id, gift_num=1)
        time.sleep(0.3)

        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']
        # 校验背包礼物
        user_package = live_result['identity_obj']['user_package']
        self.assertEqual(len(user_package),1)
        self.assertEqual(user_package[0]['tool_id'],self.gift_id)
        self.assertEqual(user_package[0]['tool_num'],1)

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 2)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp - 50000)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 3)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], 0)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot)
        # 校验无消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),0)

    def tearDown(self, *args):
        super(TestLiveSendPackageGiftFollowing, self).tearDown()
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






class TestLiveSendSunAjax(BaseCase):
    """
    送太阳
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    gift_id = 0

    def test_send_sun_no_following(self):
        """
        测试未关注主播送1个太阳
        :return:
        """
        gift_count = 1
        # 用户加太阳
        MysqlOperation(user_id=self.user_id).fix_user_sun_num(sun_num=1)
        RedisHold().clean_redis_user_detail(self.user_id)
        # 获取礼物配置信息
        gift_details = MysqlOperation().get_gift_details(self.gift_id)
        gift_user_exp = int(gift_details['add_user_experience'])
        gift_anchor_exp = int(gift_details['add_anchor_experience'])
        gift_room_hot = int(gift_details['add_hot_num'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']
        sun_num = live_result['room_obj']['sun_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': gift_count, 'currency': 'sun'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], gift_anchor_exp * gift_count)
        # 校验亲密度
        send_gift_anchor_intimacy = send_gift_anchor_obj['intimacy_obj']
        self.assertEqual(send_gift_anchor_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_anchor_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_anchor_intimacy['intimacy_level_obj'])

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], gift_user_exp * gift_count)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 0)
        self.assertIsNone(send_gift_user_intimacy['intimacy_level_obj'])
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        after_send_gift_sun_num = send_gift_result['room_obj']['sun_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, gift_room_hot * gift_count)
        # 校验房间获得的太阳数量
        self.assertEqual(after_send_gift_sun_num - sun_num, 1)
        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(), 0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list), 0)

    def test_send_sun_following(self):
        """
        测试关注主播送出1个太阳
        :return:
        """
        # 用户加太阳
        MysqlOperation(user_id=self.user_id).fix_user_sun_num(sun_num=1)
        RedisHold().clean_redis_user_detail(self.user_id)
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 送礼物前获取房间热度
        hot_num = live_result['room_obj']['curr_hot_num']
        sun_num = live_result['room_obj']['sun_num']

        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'sun'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        send_gift_result = send_gift_ajax.get_resp_result()

        send_gift_anchor_obj = send_gift_result['room_obj']['anchor_obj']
        # 校验主播等级
        self.assertEqual(send_gift_anchor_obj['anchor_rank'], 1)
        # 校验主播经验值
        self.assertEqual(send_gift_anchor_obj['anchor_experience'], 0)

        send_gift_identity_obj = send_gift_result['identity_obj']
        # 校验用户等级
        self.assertEqual(send_gift_identity_obj['user_rank'], 1)
        # 校验用户经验值
        self.assertEqual(send_gift_identity_obj['user_experience'], 0)
        # 校验亲密度
        send_gift_user_intimacy = send_gift_identity_obj['intimacy_obj']
        self.assertEqual(send_gift_user_intimacy['intimacy_experience'], 0)
        self.assertEqual(send_gift_user_intimacy['intimacy_rank'], 1)
        self.assertEqual(send_gift_user_intimacy['intimacy_next_experience'], 10000)
        intimacy_level_obj = send_gift_user_intimacy['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)
        # 获取送礼物成功后房间热度
        after_send_gift_hot_num = send_gift_result['room_obj']['curr_hot_num']
        after_send_gift_sun_num = send_gift_result['room_obj']['sun_num']
        # 校验房间热度
        self.assertEqual(after_send_gift_hot_num - hot_num, 0)
        # 校验房间获得的太阳数量
        self.assertEqual(after_send_gift_sun_num - sun_num, 1)
        # 校验无消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(),0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list),0)

    def test_send_sun_num_low(self):
        """
        测试送出太阳数量不足
        :return:
        """
        # 清除用户太阳
        MysqlOperation(user_id=self.user_id).fix_user_sun_num(sun_num=0)
        RedisHold().clean_redis_user_detail(self.user_id)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': self.gift_id,
                            'gift_count': 1, 'currency': 'sun'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 402011)
        self.assertEqual(send_gift_ajax.get_resp_message(),'太阳余额不足')

    def tearDown(self, *args):
        super(TestLiveSendSunAjax, self).tearDown()
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
