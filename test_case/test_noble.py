# -*- coding:utf-8 -*-
from ajax.live_new_server import LiveNewServer
from ajax.user_consumption import ConsumptionAjax
from base.base_helper import convert_to_timestamp
from ajax.live_noble import BuyNobleAjax
from base.base_case import BaseCase
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold
import settings
import time
import datetime


class TestBuyNobleAjax(BaseCase):
    """
    贵买贵族
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    one_month = 30
    two_month = 60
    three_month = 91
    six_month = 183

    def setUp(self, *args):
        super(TestBuyNobleAjax, self).setUp(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

    def buy_noble_action(self, **kwargs):
        days = None
        noble_gold = kwargs['noble_gold']
        noble_id = kwargs['noble_id']
        noble_num = kwargs['noble_num']
        user_rank = kwargs['user_rank']
        user_experience = kwargs['user_experience']
        if noble_num == 1:
            days = self.one_month
        elif noble_num == 2:
            days = self.two_month
        elif noble_num == 3:
            days = self.three_month
        elif noble_num == 6:
            days = self.six_month
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        hot_num = live_result['room_obj']['curr_hot_num']
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=noble_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': noble_id,
                            'num': noble_num, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'], 0)
        # 校验用户等级、经验值
        self.assertEqual(identity_obj['user_rank'], user_rank)
        self.assertEqual(identity_obj['user_experience'], user_experience)

        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], noble_id)
        # 校验有效天数
        self.assertEqual(identity_obj['noble_rest_time_int'], days)
        self.assertEqual(identity_obj['noble_rest_time_str'], '{0}天'.format(days))
        noble_expiretime = identity_obj['noble_expiretime']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),
                      noble_expiretime)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(), 0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list), 1)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'], self.user_id)
        self.assertEqual(consume_list[0]['type'], u'2')
        self.assertEqual(consume_list[0]['gold'], noble_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], noble_id)
        self.assertEqual(consume_list[0]['corresponding_name'], '贵族')
        self.assertEqual(consume_list[0]['corresponding_num'], 1)
        self.assertEqual(consume_list[0]['room_id'], '')
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '购买贵族')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(noble_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        time.sleep(0.3)
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_buy_noble_hot_num = live_result['room_obj']['curr_hot_num']

        self.assertEqual(after_buy_noble_hot_num, hot_num)

        identity_obj = live_result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'], 0)
        # 校验用户等级、经验值
        self.assertEqual(identity_obj['user_rank'], user_rank)
        self.assertEqual(identity_obj['user_experience'], user_experience)

        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], noble_id)
        # 校验有效天数
        self.assertEqual(identity_obj['noble_rest_time_int'], days)
        self.assertEqual(identity_obj['noble_rest_time_str'], '{0}天'.format(days))
        noble_expiretime = identity_obj['noble_expiretime']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),
                      noble_expiretime)
        # 校验进场动画
        msg = live_result['enter_room_message']['msg']
        self.assertEqual(msg['m_action'], 'system_room')
        self.assertEqual(msg['m_switch'], 'coming')
        self.assertEqual(msg['from_user_id'], '0')
        self.assertEqual(msg['from_refer_type'], '2')
        user_obj = msg['user_obj']
        self.assertEqual(user_obj['noble_rank'], noble_id)
        ani_obj = msg['obj']['ani_obj']
        self.assertEqual(ani_obj['ani_type'], 'entry_noble')
        self.assertEqual(ani_obj['ani_id'], noble_id)
        self.assertEqual(ani_obj['ani_num'], 0)
        self.assertIsNone(ani_obj['category_type'])
        self.assertEqual(msg['obj']['msg_content'], '来了')

    def test_buy_knight_one_month(self):
        """
        测试购买一个月骑士
        :return:
        """
        data = {'noble_gold': 24000, 'noble_id': 1, 'noble_num': 1, 'user_rank': 1, 'user_experience': 24000}
        self.buy_noble_action(**data)

    def test_buy_baron_one_month(self):
        """
        测试购买一个月男爵
        :return:
        """
        data = {'noble_gold': 40000, 'noble_id': 2, 'noble_num': 1, 'user_rank': 1, 'user_experience': 40000}
        self.buy_noble_action(**data)

    def test_buy_viscount_one_month(self):
        """
        测试购买一个月子爵
        :return:
        """
        data = {'noble_gold': 80000, 'noble_id': 3, 'noble_num': 1, 'user_rank': 2, 'user_experience': 30000}
        self.buy_noble_action(**data)

    def test_buy_earl_one_month(self):
        """
        测试购买一个月伯爵
        :return:
        """
        data = {'noble_gold': 400000, 'noble_id': 4, 'noble_num': 1, 'user_rank': 8, 'user_experience': 0}
        self.buy_noble_action(**data)

    def test_buy_marquis_one_month(self):
        """
        测试购买一个月侯爵
        :return:
        """
        data = {'noble_gold': 800000, 'noble_id': 5, 'noble_num': 1, 'user_rank': 10, 'user_experience': 50000}
        self.buy_noble_action(**data)

    def test_buy_duck_one_month(self):
        """
        测试购买一个月公爵
        :return:
        """
        data = {'noble_gold': 2400000, 'noble_id': 6, 'noble_num': 1, 'user_rank': 12, 'user_experience': 400000}
        self.buy_noble_action(**data)

    def test_buy_emperor_one_month(self):
        """
        测试购买一个月帝王
        :return:
        """
        data = {'noble_gold': 24000000, 'noble_id': 7, 'noble_num': 1, 'user_rank': 18, 'user_experience': 4000000}
        self.buy_noble_action(**data)

    def test_buy_knight_two_month(self):
        """
        测试购买两个月骑士
        :return:
        """
        data = {'noble_gold': 48000, 'noble_id': 1, 'noble_num': 2, 'user_rank': 1, 'user_experience': 48000}
        self.buy_noble_action(**data)

    def test_buy_baron_two_month(self):
        """
        测试购买两个月男爵
        :return:
        """
        data = {'noble_gold': 80000, 'noble_id': 2, 'noble_num': 2, 'user_rank': 2, 'user_experience': 30000}
        self.buy_noble_action(**data)

    def test_buy_viscount_two_month(self):
        """
        测试购买两个月子爵
        :return:
        """
        data = {'noble_gold': 160000, 'noble_id': 3, 'noble_num': 2, 'user_rank': 4, 'user_experience': 10000}
        self.buy_noble_action(**data)

    def test_buy_earl_two_month(self):
        """
        测试购买两个月伯爵
        :return:
        """
        data = {'noble_gold': 800000, 'noble_id': 4, 'noble_num': 2, 'user_rank': 10, 'user_experience': 50000}
        self.buy_noble_action(**data)

    def test_buy_marquis_two_month(self):
        """
        测试购买两个月侯爵
        :return:
        """
        data = {'noble_gold': 1600000, 'noble_id': 5, 'noble_num': 2, 'user_rank': 11, 'user_experience': 600000}
        self.buy_noble_action(**data)

    def test_buy_duck_two_month(self):
        """
        测试购买两个月公爵
        :return:
        """
        data = {'noble_gold': 4800000, 'noble_id': 6, 'noble_num': 2, 'user_rank': 13, 'user_experience': 1300000}
        self.buy_noble_action(**data)

    def test_buy_emperor_two_month(self):
        """
        测试购买两个月帝王
        :return:
        """
        data = {'noble_gold': 48000000, 'noble_id': 7, 'noble_num': 2, 'user_rank': 19, 'user_experience': 13000000}
        self.buy_noble_action(**data)

    def test_buy_knight_three_month(self):
        """
        测试购买三个月骑士
        :return:
        """
        data = {'noble_gold': 72000, 'noble_id': 1, 'noble_num': 3, 'user_rank': 2, 'user_experience': 22000}
        self.buy_noble_action(**data)

    def test_buy_baron_three_month(self):
        """
        测试购买三个月男爵
        :return:
        """
        data = {'noble_gold': 120000, 'noble_id': 2, 'noble_num': 3, 'user_rank': 3, 'user_experience': 20000}
        self.buy_noble_action(**data)

    def test_buy_viscount_three_month(self):
        """
        测试购买三个月子爵
        :return:
        """
        data = {'noble_gold': 240000, 'noble_id': 3, 'noble_num': 3, 'user_rank': 5, 'user_experience': 40000}
        self.buy_noble_action(**data)

    def test_buy_earl_three_month(self):
        """
        测试购买三个月伯爵
        :return:
        """
        data = {'noble_gold': 1200000, 'noble_id': 4, 'noble_num': 3, 'user_rank': 11, 'user_experience': 200000}
        self.buy_noble_action(**data)

    def test_buy_marquis_three_month(self):
        """
        测试购买三个月侯爵
        :return:
        """
        data = {'noble_gold': 2400000, 'noble_id': 5, 'noble_num': 3, 'user_rank': 12, 'user_experience': 400000}
        self.buy_noble_action(**data)

    def test_buy_duck_three_month(self):
        """
        测试购买三个月公爵
        :return:
        """
        data = {'noble_gold': 7200000, 'noble_id': 6, 'noble_num': 3, 'user_rank': 14, 'user_experience': 2200000}
        self.buy_noble_action(**data)

    def test_buy_emperor_three_month(self):
        """
        测试购买三个月帝王
        :return:
        """
        data = {'noble_gold': 72000000, 'noble_id': 7, 'noble_num': 3, 'user_rank': 21, 'user_experience': 7000000}
        self.buy_noble_action(**data)

    def test_buy_knight_six_month(self):
        """
        测试购买六个月骑士
        :return:
        """
        data = {'noble_gold': 144000, 'noble_id': 1, 'noble_num': 6, 'user_rank': 3, 'user_experience': 44000}
        self.buy_noble_action(**data)

    def test_buy_baron_six_month(self):
        """
        测试购买六个月男爵
        :return:
        """
        data = {'noble_gold': 240000, 'noble_id': 2, 'noble_num': 6, 'user_rank': 5, 'user_experience': 40000}
        self.buy_noble_action(**data)

    def test_buy_viscount_six_month(self):
        """
        测试购买六个月子爵
        :return:
        """
        data = {'noble_gold': 480000, 'noble_id': 3, 'noble_num': 6, 'user_rank': 8, 'user_experience': 80000}
        self.buy_noble_action(**data)

    def test_buy_earl_six_month(self):
        """
        测试购买六个月伯爵
        :return:
        """
        data = {'noble_gold': 2400000, 'noble_id': 4, 'noble_num': 6, 'user_rank': 12, 'user_experience': 400000}
        self.buy_noble_action(**data)

    def test_buy_marquis_six_month(self):
        """
        测试购买六个月侯爵
        :return:
        """
        data = {'noble_gold': 4800000, 'noble_id': 5, 'noble_num': 6, 'user_rank': 13, 'user_experience': 1300000}
        self.buy_noble_action(**data)

    def test_buy_duck_six_month(self):
        """
        测试购买六个月公爵
        :return:
        """
        data = {'noble_gold': 14400000, 'noble_id': 6, 'noble_num': 6, 'user_rank': 16, 'user_experience': 4400000}
        self.buy_noble_action(**data)

    def test_buy_emperor_six_month(self):
        """
        测试购买六个月帝王
        :return:
        """
        data = {'noble_gold': 144000000, 'noble_id': 7, 'noble_num': 6, 'user_rank': 24, 'user_experience': 24000000}
        self.buy_noble_action(**data)

    def tearDown(self, *args):
        super(TestBuyNobleAjax, self).tearDown(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)


class TestBuyNobleAjaxAbnormal(BaseCase):
    """
    贵买贵族-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def test_buy_noble_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': None, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 402000)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '房间ID不能为空')

    def test_buy_noble_room_id_error(self):
        """
        测试请求接口房间ID不存在
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': '909090', 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 801017)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '房间信息不存在')

    def test_buy_noble_anchor_id_null(self):
        """
        测试请求接口主播ID为空
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': None, 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 100032)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '账户金币不足')

    def test_buy_noble_anchor_id_error(self):
        """
        测试请求接口主播ID不存在
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': '90909090', 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 100032)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '账户金币不足')

    def test_buy_noble_noble_id_null(self):
        """
        测试请求接口贵族ID为空
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': None,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 402028)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '贵族ID不符合规则')

    def test_buy_noble_noble_id_error(self):
        """
        测试请求接口贵族ID不存在
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 99,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 402025)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '贵族信息不存在')

    def test_buy_noble_noble_num_null(self):
        """
        测试请求接口贵族月数为空
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': None, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 402029)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '贵族购买数量有误')

    def test_buy_noble_noble_num_error(self):
        """
        测试请求接口贵族月数不正确
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 111, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 100032)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '账户金币不足')

    def test_buy_noble_noble_currency_null(self):
        """
        测试请求接口贵族货币类型为空
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': None})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 460004)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '请选择货币类型')

    def test_buy_noble_noble_currency_error(self):
        """
        测试请求接口贵族货币类型不正确
        :return:
        """
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': 'abc'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 460004)
        self.assertEqual(buy_noble_ajax.get_resp_message(), '请选择货币类型')


class TestNobleRenewAjax(BaseCase):
    """
    贵族续费
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    one_month = 30
    two_month = 61

    def setUp(self, *args):
        super(TestNobleRenewAjax, self).setUp(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

    def renew_action(self, **kwargs):
        first_noble_gold = kwargs['first_noble_gold']
        first_noble_id = kwargs['first_noble_id']
        second_noble_gold = kwargs['second_noble_gold']
        second_noble_id = kwargs['second_noble_id']
        second_user_rank = kwargs['second_user_rank']
        second_user_exp = kwargs['second_user_exp']
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=first_noble_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': first_noble_id, 'num': 1,
                            'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'], 0)

        self.assertEqual(identity_obj['noble_rank'], first_noble_id)
        # 校验有效天数
        self.assertEqual(identity_obj['noble_rest_time_int'], self.one_month)
        self.assertEqual(identity_obj['noble_rest_time_str'], '{0}天'.format(self.one_month))
        time.sleep(1)
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=second_noble_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': second_noble_id, 'num': 1,
                            'currency': 'gold'})
        if second_noble_id < first_noble_id:
            self.assertEqual(buy_noble_ajax.get_resp_code(), 402026)
            self.assertEqual(buy_noble_ajax.get_resp_message(),'您选择的贵族低于您当前已拥有的贵族等级，无法开通')
        else:
            self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

            result = buy_noble_ajax.get_resp_result()
            identity_obj = result['identity_obj']
            # 校验用户余额
            self.assertEqual(identity_obj['gold'], 0)
            # 校验贵族等级
            if second_noble_id > first_noble_id:
                self.assertEqual(identity_obj['noble_rank'], second_noble_id)
                # 校验有效天数
                self.assertEqual(identity_obj['noble_rest_time_int'], self.one_month)
                self.assertEqual(identity_obj['noble_rest_time_str'], '{0}天'.format(self.one_month))
                self.assertEqual(identity_obj['user_rank'], second_user_rank)
                self.assertEqual(identity_obj['user_experience'], second_user_exp)
            else:
                self.assertEqual(identity_obj['noble_rank'], first_noble_id)
                # 校验有效天数
                self.assertEqual(identity_obj['noble_rest_time_int'], self.two_month)
                self.assertEqual(identity_obj['noble_rest_time_str'], '{0}天'.format(self.two_month))
                self.assertEqual(identity_obj['user_rank'], second_user_rank)
                self.assertEqual(identity_obj['user_experience'], second_user_exp)

    def test_knight_renew_knight(self):
        """
        测试骑士续费骑士
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_knight_renew_baron(self):
        """
        测试骑士续费男爵
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 40000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 14000}
        self.renew_action(**data)

    def test_knight_renew_viscount(self):
        """
        测试骑士续费子爵
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 80000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 4000}
        self.renew_action(**data)

    def test_knight_renew_earl(self):
        """
        测试骑士续费伯爵
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 400000, 'second_noble_id': 4,
                'second_user_rank': 8, 'second_user_exp': 24000}
        self.renew_action(**data)

    def test_knight_renew_marquis(self):
        """
        测试骑士续费侯爵
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 800000, 'second_noble_id': 5,
                'second_user_rank': 10, 'second_user_exp': 74000}
        self.renew_action(**data)

    def test_knight_renew_duck(self):
        """
        测试骑士续费公爵
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 2400000, 'second_noble_id': 6,
                'second_user_rank': 12, 'second_user_exp': 424000}
        self.renew_action(**data)

    def test_knight_renew_emperor(self):
        """
        测试骑士续费帝王
        :return:
        """
        data = {'first_noble_gold': 24000, 'first_noble_id': 1, 'second_noble_gold': 24000000, 'second_noble_id': 7,
                'second_user_rank': 18, 'second_user_exp': 4024000}
        self.renew_action(**data)


    def test_baron_renew_knight(self):
        """
        测试男爵续费骑士,失败
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_baron_renew_baron(self):
        """
        测试男爵续费男爵
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 30000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_baron_renew_viscount(self):
        """
        测试男爵续费子爵
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 80000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_baron_renew_earl(self):
        """
        测试男爵续费伯爵
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 400000, 'second_noble_id': 4,
                'second_user_rank': 8, 'second_user_exp': 40000}
        self.renew_action(**data)

    def test_baron_renew_marquis(self):
        """
        测试男爵续费侯爵
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 800000, 'second_noble_id': 5,
                'second_user_rank': 10, 'second_user_exp': 90000}
        self.renew_action(**data)

    def test_baron_renew_duck(self):
        """
        测试男爵续费公爵
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 2400000, 'second_noble_id': 6,
                'second_user_rank': 12, 'second_user_exp': 440000}
        self.renew_action(**data)

    def test_baron_renew_emperor(self):
        """
        测试男爵续费帝王
        :return:
        """
        data = {'first_noble_gold': 40000, 'first_noble_id': 2, 'second_noble_gold': 24000000, 'second_noble_id': 7,
                'second_user_rank': 18, 'second_user_exp': 4040000}
        self.renew_action(**data)

    def test_viscount_renew_knight(self):
        """
        测试子爵续费骑士,失败
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_viscount_renew_baron(self):
        """
        测试子爵续费男爵,失败
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 30000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_viscount_renew_viscount(self):
        """
        测试子爵续费子爵
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 60000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 40000}
        self.renew_action(**data)

    def test_viscount_renew_earl(self):
        """
        测试子爵续费伯爵
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 400000, 'second_noble_id': 4,
                'second_user_rank': 8, 'second_user_exp': 80000}
        self.renew_action(**data)

    def test_viscount_renew_marquis(self):
        """
        测试子爵续费侯爵
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 800000, 'second_noble_id': 5,
                'second_user_rank': 10, 'second_user_exp': 130000}
        self.renew_action(**data)

    def test_viscount_renew_duck(self):
        """
        测试子爵续费公爵
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 2400000, 'second_noble_id': 6,
                'second_user_rank': 12, 'second_user_exp': 480000}
        self.renew_action(**data)

    def test_viscount_renew_emperor(self):
        """
        测试子爵续费帝王
        :return:
        """
        data = {'first_noble_gold': 80000, 'first_noble_id': 3, 'second_noble_gold': 24000000, 'second_noble_id': 7,
                'second_user_rank': 18, 'second_user_exp': 4080000}
        self.renew_action(**data)



    def test_earl_renew_knight(self):
        """
        测试伯爵续费骑士,失败
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_earl_renew_baron(self):
        """
        测试伯爵续费男爵,失败
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 30000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_earl_renew_viscount(self):
        """
        测试伯爵续费子爵,失败
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 60000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 40000}
        self.renew_action(**data)

    def test_earl_renew_earl(self):
        """
        测试伯爵续费伯爵
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 300000, 'second_noble_id': 4,
                'second_user_rank': 9, 'second_user_exp': 200000}
        self.renew_action(**data)

    def test_earl_renew_marquis(self):
        """
        测试伯爵续费侯爵
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 800000, 'second_noble_id': 5,
                'second_user_rank': 11, 'second_user_exp': 200000}
        self.renew_action(**data)

    def test_earl_renew_duck(self):
        """
        测试伯爵续费公爵
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 2400000, 'second_noble_id': 6,
                'second_user_rank': 12, 'second_user_exp': 800000}
        self.renew_action(**data)

    def test_earl_renew_emperor(self):
        """
        测试伯爵续费帝王
        :return:
        """
        data = {'first_noble_gold': 400000, 'first_noble_id': 4, 'second_noble_gold': 24000000, 'second_noble_id': 7,
                'second_user_rank': 18, 'second_user_exp': 4400000}
        self.renew_action(**data)


    def test_marquis_renew_knight(self):
        """
        测试侯爵续费骑士,失败
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_marquis_renew_baron(self):
        """
        测试侯爵续费男爵,失败
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 30000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_marquis_renew_viscount(self):
        """
        测试侯爵续费子爵,失败
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 60000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 40000}
        self.renew_action(**data)

    def test_marquis_renew_earl(self):
        """
        测试侯爵续费伯爵,失败
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 300000, 'second_noble_id': 4,
                'second_user_rank': 9, 'second_user_exp': 200000}
        self.renew_action(**data)

    def test_marquis_renew_marquis(self):
        """
        测试侯爵续费侯爵
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 600000, 'second_noble_id': 5,
                'second_user_rank': 11, 'second_user_exp': 400000}
        self.renew_action(**data)

    def test_marquis_renew_duck(self):
        """
        测试侯爵续费公爵
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 2400000, 'second_noble_id': 6,
                'second_user_rank': 12, 'second_user_exp': 1200000}
        self.renew_action(**data)

    def test_marquis_renew_emperor(self):
        """
        测试侯爵续费帝王
        :return:
        """
        data = {'first_noble_gold': 800000, 'first_noble_id': 5, 'second_noble_gold': 24000000, 'second_noble_id': 7,
                'second_user_rank': 18, 'second_user_exp': 4800000}
        self.renew_action(**data)


    def test_duck_renew_knight(self):
        """
        测试公爵续费骑士,失败
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_duck_renew_baron(self):
        """
        测试公爵续费男爵,失败
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 30000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_duck_renew_viscount(self):
        """
        测试公爵续费子爵,失败
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 60000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 40000}
        self.renew_action(**data)

    def test_duck_renew_earl(self):
        """
        测试公爵续费伯爵,失败
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 300000, 'second_noble_id': 4,
                'second_user_rank': 9, 'second_user_exp': 200000}
        self.renew_action(**data)

    def test_duck_renew_marquis(self):
        """
        测试公爵续费侯爵,失败
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 600000, 'second_noble_id': 5,
                'second_user_rank': 11, 'second_user_exp': 400000}
        self.renew_action(**data)

    def test_duck_renew_duck(self):
        """
        测试公爵续费公爵
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 1800000, 'second_noble_id': 6,
                'second_user_rank': 13, 'second_user_exp': 700000}
        self.renew_action(**data)

    def test_duck_renew_emperor(self):
        """
        测试公爵续费帝王
        :return:
        """
        data = {'first_noble_gold': 2400000, 'first_noble_id': 6, 'second_noble_gold': 24000000, 'second_noble_id': 7,
                'second_user_rank': 18, 'second_user_exp': 6400000}
        self.renew_action(**data)

    def test_emperor_renew_knight(self):
        """
        测试帝王续费骑士,失败
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 18000, 'second_noble_id': 1,
                'second_user_rank': 1, 'second_user_exp': 42000}
        self.renew_action(**data)

    def test_emperor_renew_baron(self):
        """
        测试帝王续费男爵,失败
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 30000, 'second_noble_id': 2,
                'second_user_rank': 2, 'second_user_exp': 20000}
        self.renew_action(**data)

    def test_emperor_renew_viscount(self):
        """
        测试帝王续费子爵,失败
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 60000, 'second_noble_id': 3,
                'second_user_rank': 3, 'second_user_exp': 40000}
        self.renew_action(**data)

    def test_emperor_renew_earl(self):
        """
        测试帝王续费伯爵,失败
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 300000, 'second_noble_id': 4,
                'second_user_rank': 9, 'second_user_exp': 200000}
        self.renew_action(**data)

    def test_emperor_renew_marquis(self):
        """
        测试帝王续费侯爵,失败
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 600000, 'second_noble_id': 5,
                'second_user_rank': 11, 'second_user_exp': 400000}
        self.renew_action(**data)

    def test_emperor_renew_duck(self):
        """
        测试帝王续费公爵,失败
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 1800000, 'second_noble_id': 6,
                'second_user_rank': 13, 'second_user_exp': 700000}
        self.renew_action(**data)

    def test_emperor_renew_emperor(self):
        """
        测试帝王续费帝王
        :return:
        """
        data = {'first_noble_gold': 24000000, 'first_noble_id': 7, 'second_noble_gold': 18000000, 'second_noble_id': 7,
                'second_user_rank': 19, 'second_user_exp': 7000000}
        self.renew_action(**data)

    def tearDown(self, *args):
        super(TestNobleRenewAjax, self).tearDown(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
