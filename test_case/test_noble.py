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
    one_month = 29

    def setUp(self, *args):
        super(TestBuyNobleAjax,self).setUp(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

    def test_buy_knight_one_month(self):
        """
        测试购买一个月骑士
        :return:
        """
        noble_gold = 24000
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=noble_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(),0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'],0)
        # 校验用户等级、经验值
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],noble_gold)
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'],1)
        # 校验有效天数
        self.assertEqual(identity_obj['noble_rest_time_int'],self.one_month)
        self.assertEqual(identity_obj['noble_rest_time_str'],'{0}天'.format(self.one_month))
        noble_expiretime = identity_obj['noble_expiretime']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_month)).strftime("%Y-%m-%d %H:%M"),noble_expiretime)

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
        self.assertEqual(consume_list[0]['type'],u'2')
        self.assertEqual(consume_list[0]['gold'],noble_gold)
        self.assertEqual(consume_list[0]['corresponding_id'],1)
        self.assertEqual(consume_list[0]['corresponding_name'],'贵族')
        self.assertEqual(consume_list[0]['corresponding_num'],1)
        self.assertEqual(consume_list[0]['room_id'],'')
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'购买贵族')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(noble_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        time.sleep(0.3)
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()

        identity_obj = live_result['identity_obj']
        # 校验用户余额
        self.assertEqual(identity_obj['gold'],0)
        # 校验用户等级、经验值
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],noble_gold)

        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'],1)
        # 校验有效天数
        self.assertEqual(identity_obj['noble_rest_time_int'],self.one_month)
        self.assertEqual(identity_obj['noble_rest_time_str'],'{0}天'.format(self.one_month))
        noble_expiretime = identity_obj['noble_expiretime']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_month)).strftime("%Y-%m-%d %H:%M"),noble_expiretime)
        # 校验进场动画
        msg = live_result['enter_room_message']['msg']
        self.assertEqual(msg['m_action'],'system_room')
        self.assertEqual(msg['m_switch'],'coming')
        self.assertEqual(msg['from_user_id'],'0')
        self.assertEqual(msg['from_refer_type'],'2')
        user_obj = msg['user_obj']
        self.assertEqual(user_obj['noble_rank'],1)
        ani_obj = msg['obj']['ani_obj']
        self.assertEqual(ani_obj['ani_type'],'entry_noble')
        self.assertEqual(ani_obj['ani_id'],1)
        self.assertEqual(ani_obj['ani_num'],0)
        self.assertIsNone(ani_obj['category_type'])

        self.assertEqual(msg['obj']['msg_content'],'来了')

    def tearDown(self, *args):
        super(TestBuyNobleAjax,self).tearDown(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)