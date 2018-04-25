# -*- coding:utf-8 -*-
from ajax.live_new_server import LiveNewServer
from ajax.live_send_gift import LiveSendGift
from base.base_case import BaseCase
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
