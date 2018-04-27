# -*- coding:utf-8 -*-
from ajax.live_new_server import LiveNewServer
from ajax.user_consumption import ConsumptionAjax
from base.base_helper import convert_to_timestamp
from ajax.live_guard import BuyGuardAjax
from base.base_case import BaseCase
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold, Redis
import settings
import time


class TestBuyGuardAjax(BaseCase):
    """
    贵买守护
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    one_month = 31
    two_month = 62
    three_month = 93
    six_month = 186
    one_year = 372
    two_year = 744

    def setUp(self, *args):
        super(TestBuyGuardAjax, self).setUp(user_id=self.user_id, anchor_id=self.anchor_id)
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)

    def buy_guard_action(self, **kwargs):
        days = None
        guard_gold = kwargs['guard_gold']
        guard_id = kwargs['guard_id']
        user_rank = kwargs['user_rank']
        user_experience = kwargs['user_experience']
        anchor_rank = kwargs['anchor_rank']
        anchor_experience = kwargs['anchor_experience']
        if guard_id == 1:
            days = self.one_month
        elif guard_id == 2:
            days = self.two_month
        elif guard_id == 3:
            days = self.three_month
        elif guard_id == 6:
            days = self.six_month
        elif guard_id == 12:
            days = self.one_year
        elif guard_id == 13:
            days = self.two_year

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        hot_num = live_result['room_obj']['curr_hot_num']

        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=guard_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': guard_id, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)

        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], user_rank)
        self.assertEqual(guard_list[0]['user_experience'], user_experience)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        if guard_id in [3,6]:
            self.assertEqual(user_guard_obj['guard_rank'], 3)
        elif guard_id in [12,13]:
            self.assertEqual(user_guard_obj['guard_rank'], 4)
        else:
            self.assertEqual(user_guard_obj['guard_rank'], guard_id)
        # self.assertEqual(user_guard_obj['rest_time_int'], days)
        # self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        # expire_time = user_guard_obj['expire_time']
        # self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),
        #               expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 0)
        self.assertEqual(intimacy_obj['intimacy_rank'], 0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])
        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], user_rank)
        self.assertEqual(identity_obj['user_experience'], user_experience)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        if guard_id in [3,6]:
            self.assertEqual(user_guard_obj['guard_rank'], 3)
        elif guard_id in [12,13]:
            self.assertEqual(user_guard_obj['guard_rank'], 4)
        else:
            self.assertEqual(user_guard_obj['guard_rank'], guard_id)
        # self.assertEqual(user_guard_obj['rest_time_int'], days)
        # self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        # expire_time = user_guard_obj['expire_time']
        # self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),
        #               expire_time)

        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 0)
        self.assertEqual(intimacy_obj['intimacy_rank'], 0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], anchor_rank)
        self.assertEqual(anchor_obj['anchor_experience'], anchor_experience)
        time.sleep(0.3)
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_buy_noble_hot_num = live_result['room_obj']['curr_hot_num']
        # 校验增加房间热度
        self.assertEqual(after_buy_noble_hot_num - hot_num, guard_gold)

        msg = live_result['enter_room_message']['msg']
        self.assertEqual(msg['m_action'], 'system_room')
        self.assertEqual(msg['m_switch'], 'coming')
        self.assertEqual(msg['from_user_id'], '0')
        self.assertEqual(msg['from_refer_type'], '2')
        user_obj = msg['user_obj']
        if guard_id in [3,6]:
            self.assertEqual(user_obj['guard_rank'], 3)
        elif guard_id in [12,13]:
            self.assertEqual(user_obj['guard_rank'], 4)
        else:
            self.assertEqual(user_obj['guard_rank'], guard_id)
        ani_obj = msg['obj']['ani_obj']
        self.assertEqual(ani_obj['ani_type'], 'entry_guard')

        if guard_id in [3,6]:
            self.assertEqual(ani_obj['ani_id'], 3)
        elif guard_id in [12,13]:
            self.assertEqual(ani_obj['ani_id'], 4)
        else:
            self.assertEqual(ani_obj['ani_id'], guard_id)
        self.assertEqual(ani_obj['ani_num'], 0)
        self.assertIsNone(ani_obj['category_type'])
        self.assertEqual(msg['obj']['msg_content'], '来了')
        # 校验主播等级和经验值
        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], anchor_rank)
        self.assertEqual(anchor_obj['anchor_experience'], anchor_experience)
        # 校验identity_obj
        identity_obj = live_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], user_rank)
        self.assertEqual(identity_obj['user_experience'], user_experience)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        if guard_id in [3,6]:
            self.assertEqual(user_guard_obj['guard_rank'], 3)
        elif guard_id in [12,13]:
            self.assertEqual(user_guard_obj['guard_rank'], 4)
        else:
            self.assertEqual(user_guard_obj['guard_rank'], guard_id)
        # self.assertEqual(user_guard_obj['rest_time_int'], days)
        # self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        # expire_time = user_guard_obj['expire_time']
        # self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),expire_time)

        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 0)
        self.assertEqual(intimacy_obj['intimacy_rank'], 0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])

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
        self.assertEqual(consume_list[0]['type'], u'3')
        self.assertEqual(consume_list[0]['gold'], guard_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], guard_id)
        self.assertEqual(consume_list[0]['corresponding_name'], '守护')
        self.assertEqual(consume_list[0]['corresponding_num'], 1)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '购买守护')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(guard_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_buy_bronze(self):
        """
        测试购买一个月青铜守护
        :return:
        """
        data = {'guard_gold': 588000, 'guard_id': 1, 'user_rank': 9, 'user_experience': 88000, 'anchor_rank': 4,
                'anchor_experience': 88000}
        self.buy_guard_action(**data)

    def test_buy_silver(self):
        """
        测试购买两个月白银守护
        :return:
        """
        data = {'guard_gold': 1176000, 'guard_id': 2, 'user_rank': 11, 'user_experience': 176000, 'anchor_rank': 5,
                'anchor_experience': 176000}
        self.buy_guard_action(**data)

    def test_buy_gold_three_month(self):
        """
        测试购买三个月黄金守护
        :return:
        """
        data = {'guard_gold': 1764000, 'guard_id': 3, 'user_rank': 11, 'user_experience': 764000, 'anchor_rank': 5,
                'anchor_experience': 764000}
        self.buy_guard_action(**data)

    def test_buy_gold_six_month(self):
        """
        测试购买六个月黄金守护
        :return:
        """
        data = {'guard_gold': 3528000, 'guard_id': 6, 'user_rank': 13, 'user_experience': 28000, 'anchor_rank': 6,
                'anchor_experience': 1528000}
        self.buy_guard_action(**data)

    def test_buy_diamond_one_year(self):
        """
        测试购买一年钻石守护
        :return:
        """
        data = {'guard_gold': 7056000, 'guard_id': 12, 'user_rank': 14, 'user_experience': 2056000, 'anchor_rank': 7,
                'anchor_experience': 3056000}
        self.buy_guard_action(**data)

    def test_buy_diamond_two_year(self):
        """
        测试购买两年钻石守护
        :return:
        """
        data = {'guard_gold': 14112000, 'guard_id': 13, 'user_rank': 16, 'user_experience': 4112000, 'anchor_rank': 9,
                'anchor_experience': 112000}
        self.buy_guard_action(**data)

    def tearDown(self, *args):
        super(TestBuyGuardAjax, self).tearDown(user_id=self.user_id, anchor_id=self.anchor_id)
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)
