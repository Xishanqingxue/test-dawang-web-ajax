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


class TestBuyNobleAjax(BaseCase):
    """
    贵买贵族
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    one_month = 29

    def setUp(self, *args):
        super(TestBuyNobleAjax, self).setUp(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

    def buy_noble_action(self, **kwargs):
        noble_gold = kwargs['noble_gold']
        noble_id = kwargs['noble_id']
        noble_num = kwargs['noble_num']
        user_rank = kwargs['user_rank']
        user_experience = kwargs['user_experience']

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
        # self.assertEqual(identity_obj['noble_rest_time_int'],self.one_month)
        # self.assertEqual(identity_obj['noble_rest_time_str'],'{0}天'.format(self.one_month))
        # noble_expiretime = identity_obj['noble_expiretime']
        # self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_month)).strftime("%Y-%m-%d %H:%M"),noble_expiretime)

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
        # self.assertEqual(identity_obj['noble_rest_time_int'],self.one_month)
        # self.assertEqual(identity_obj['noble_rest_time_str'],'{0}天'.format(self.one_month))
        # noble_expiretime = identity_obj['noble_expiretime']
        # self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_month)).strftime("%Y-%m-%d %H:%M"),noble_expiretime)
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
