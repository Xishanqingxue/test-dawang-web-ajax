# -*- coding:utf-8 -*-
from ajax.user_follow import AddFollowAjax,RelieveFollowAjax
from ajax.live_new_server import LiveNewServer
from ajax.user_consumption import ConsumptionAjax
from base.base_helper import convert_to_timestamp
from ajax.live_guard import BuyGuardAjax
from base.base_case import BaseCase
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold, Redis
import settings
import time
import datetime


class TestBuyGuardAjaxNoFollowing(BaseCase):
    """
    未关注主播购买守护
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
        super(TestBuyGuardAjaxNoFollowing, self).setUp(user_id=self.user_id, anchor_id=self.anchor_id)
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
        self.assertEqual(user_guard_obj['rest_time_int'], days)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),
                      expire_time)
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
        self.assertEqual(user_guard_obj['rest_time_int'], days)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),
                      expire_time)

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
        self.assertEqual(user_guard_obj['rest_time_int'], days)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H:%M"),expire_time)

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

    def test_buy_bronze_no_following(self):
        """
        测试未关注主播购买一个月青铜守护
        :return:
        """
        data = {'guard_gold': 588000, 'guard_id': 1, 'user_rank': 9, 'user_experience': 88000, 'anchor_rank': 4,
                'anchor_experience': 88000}
        self.buy_guard_action(**data)

    def test_buy_silver_no_following(self):
        """
        测试未关注主播购买两个月白银守护
        :return:
        """
        data = {'guard_gold': 1176000, 'guard_id': 2, 'user_rank': 11, 'user_experience': 176000, 'anchor_rank': 5,
                'anchor_experience': 176000}
        self.buy_guard_action(**data)

    def test_buy_gold_three_month_no_following(self):
        """
        测试未关注主播购买三个月黄金守护
        :return:
        """
        data = {'guard_gold': 1764000, 'guard_id': 3, 'user_rank': 11, 'user_experience': 764000, 'anchor_rank': 5,
                'anchor_experience': 764000}
        self.buy_guard_action(**data)

    def test_buy_gold_six_month_no_following(self):
        """
        测试未关注主播购买六个月黄金守护
        :return:
        """
        data = {'guard_gold': 3528000, 'guard_id': 6, 'user_rank': 13, 'user_experience': 28000, 'anchor_rank': 6,
                'anchor_experience': 1528000}
        self.buy_guard_action(**data)

    def test_buy_diamond_one_year_no_following(self):
        """
        测试未关注主播购买一年钻石守护
        :return:
        """
        data = {'guard_gold': 7056000, 'guard_id': 12, 'user_rank': 14, 'user_experience': 2056000, 'anchor_rank': 7,
                'anchor_experience': 3056000}
        self.buy_guard_action(**data)

    def test_buy_diamond_two_year_no_following(self):
        """
        测试未关注主播购买两年钻石守护
        :return:
        """
        data = {'guard_gold': 14112000, 'guard_id': 13, 'user_rank': 16, 'user_experience': 4112000, 'anchor_rank': 9,
                'anchor_experience': 112000}
        self.buy_guard_action(**data)

    def tearDown(self, *args):
        super(TestBuyGuardAjaxNoFollowing, self).tearDown(user_id=self.user_id, anchor_id=self.anchor_id)
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)






class TestBuyGuardAjaxFollowing(BaseCase):
    """
    关注主播购买守护
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
        super(TestBuyGuardAjaxFollowing, self).setUp(user_id=self.user_id, anchor_id=self.anchor_id)
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
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

        def assert_intimacy(obj, guard_id):
            inti_dic = {}
            if guard_id == 1:
                inti_dic = {'intimacy_experience': 113000, 'intimacy_rank': 7, 'level': 1, 'level_name': u'喜爱'}
            elif guard_id == 2:
                inti_dic = {'intimacy_experience': 76000, 'intimacy_rank': 10, 'level': 1, 'level_name': u'喜爱'}
            elif guard_id == 3:
                inti_dic = {'intimacy_experience': 264000, 'intimacy_rank': 11, 'level': 1, 'level_name': u'喜爱'}
            elif guard_id == 6:
                inti_dic = {'intimacy_experience': 528000, 'intimacy_rank': 13, 'level': 1, 'level_name': u'喜爱'}
            elif guard_id == 12:
                inti_dic = {'intimacy_experience': 56000, 'intimacy_rank': 15, 'level': 1, 'level_name': u'喜爱'}
            elif guard_id == 13:
                inti_dic = {'intimacy_experience': 112000, 'intimacy_rank': 17, 'level': 2, 'level_name': u'真爱'}

            self.assertEqual(obj['intimacy_experience'], inti_dic['intimacy_experience'])
            self.assertEqual(obj['intimacy_rank'], inti_dic['intimacy_rank'])
            intimacy_level_obj = obj['intimacy_level_obj']
            self.assertEqual(intimacy_level_obj['level'], inti_dic['level'])
            self.assertEqual(intimacy_level_obj['level_name'], inti_dic['level_name'])
            if guard_id == 13:
                self.assertEqual(intimacy_level_obj['rank_start'], 16)
                self.assertEqual(intimacy_level_obj['rank_end'], 30)
            else:
                self.assertEqual(intimacy_level_obj['rank_start'], 1)
                self.assertEqual(intimacy_level_obj['rank_end'], 15)

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
        self.assertEqual(user_guard_obj['rest_time_int'], days)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        assert_intimacy(intimacy_obj,guard_id)

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
        self.assertEqual(user_guard_obj['rest_time_int'], days)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H"),
                      expire_time)

        intimacy_obj = identity_obj['intimacy_obj']
        assert_intimacy(intimacy_obj,guard_id)

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
        self.assertEqual(user_guard_obj['rest_time_int'], days)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(days))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+days)).strftime("%Y-%m-%d %H"),expire_time)

        intimacy_obj = identity_obj['intimacy_obj']
        assert_intimacy(intimacy_obj,guard_id)


    def test_buy_bronze_following(self):
        """
        测试关注主播购买一个月青铜守护
        :return:
        """
        data = {'guard_gold': 588000, 'guard_id': 1, 'user_rank': 9, 'user_experience': 88000, 'anchor_rank': 4,
                'anchor_experience': 88000}
        self.buy_guard_action(**data)

    def test_buy_silver_following(self):
        """
        测试关注主播购买两个月白银守护
        :return:
        """
        data = {'guard_gold': 1176000, 'guard_id': 2, 'user_rank': 11, 'user_experience': 176000, 'anchor_rank': 5,
                'anchor_experience': 176000}
        self.buy_guard_action(**data)

    def test_buy_gold_three_month_following(self):
        """
        测试关注主播购买三个月黄金守护
        :return:
        """
        data = {'guard_gold': 1764000, 'guard_id': 3, 'user_rank': 11, 'user_experience': 764000, 'anchor_rank': 5,
                'anchor_experience': 764000}
        self.buy_guard_action(**data)

    def test_buy_gold_six_month_following(self):
        """
        测试关注主播购买六个月黄金守护
        :return:
        """
        data = {'guard_gold': 3528000, 'guard_id': 6, 'user_rank': 13, 'user_experience': 28000, 'anchor_rank': 6,
                'anchor_experience': 1528000}
        self.buy_guard_action(**data)

    def test_buy_diamond_one_year_following(self):
        """
        测试关注主播购买一年钻石守护
        :return:
        """
        data = {'guard_gold': 7056000, 'guard_id': 12, 'user_rank': 14, 'user_experience': 2056000, 'anchor_rank': 7,
                'anchor_experience': 3056000}
        self.buy_guard_action(**data)

    def test_buy_diamond_two_year_following(self):
        """
        测试关注主播购买两年钻石守护
        :return:
        """
        data = {'guard_gold': 14112000, 'guard_id': 13, 'user_rank': 16, 'user_experience': 4112000, 'anchor_rank': 9,
                'anchor_experience': 112000}
        self.buy_guard_action(**data)

    def tearDown(self, *args):
        super(TestBuyGuardAjaxFollowing, self).tearDown(user_id=self.user_id, anchor_id=self.anchor_id)
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)





class TestGuardRenewFollowing(BaseCase):
    """
    关注主播购买续费
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
    time_sleep = 0.5

    def setUp(self, *args):
        super(TestGuardRenewFollowing, self).setUp(user_id=self.user_id, anchor_id=self.anchor_id)
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)


    def follow_anchor(self):
        # 关注主播
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

    def test_bronze_renew_bronze(self):
        """
        测试青铜守护续费青铜守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 11)
        self.assertEqual(guard_list[0]['user_experience'], 176000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 2)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 76000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 10)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 11)
        self.assertEqual(identity_obj['user_experience'], 176000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 2)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 76000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 10)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 5)
        self.assertEqual(anchor_obj['anchor_experience'], 176000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num,588000 * 2)

    def test_bronze_renew_silver(self):
        """
        测试青铜守护续费白银守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 11)
        self.assertEqual(guard_list[0]['user_experience'], 764000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 264000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 11)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 11)
        self.assertEqual(identity_obj['user_experience'], 764000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 264000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 11)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 5)
        self.assertEqual(anchor_obj['anchor_experience'], 764000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num,588000 + 1176000)

    def test_bronze_renew_three_gold(self):
        """
        测试青铜守护续费三个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 12)
        self.assertEqual(guard_list[0]['user_experience'], 352000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.one_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 352000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 12)
        self.assertEqual(identity_obj['user_experience'], 352000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month  + self.one_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 352000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 6)
        self.assertEqual(anchor_obj['anchor_experience'], 352000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num,588000 + 1764000)

    def test_bronze_renew_six_gold(self):
        """
        测试青铜守护续费六个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=3528000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 6, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 13)
        self.assertEqual(guard_list[0]['user_experience'], 616000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.one_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1116000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 13)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 13)
        self.assertEqual(identity_obj['user_experience'], 616000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month  + self.one_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1116000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 13)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 7)
        self.assertEqual(anchor_obj['anchor_experience'], 116000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num,588000 + 3528000)

    def test_bronze_renew_one_diamond(self):
        """
        测试青铜守护续费一年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 15)
        self.assertEqual(guard_list[0]['user_experience'], 144000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.one_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 644000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 15)
        self.assertEqual(identity_obj['user_experience'], 144000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year  + self.one_month)).strftime("%Y-%m-%d %H"),expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 644000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 7)
        self.assertEqual(anchor_obj['anchor_experience'], 3644000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num,588000 + 7056000)

    def test_bronze_renew_two_diamond(self):
        """
        测试青铜守护续费两年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=14112000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 13, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 16)
        self.assertEqual(guard_list[0]['user_experience'], 4700000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.one_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 700000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 16)
        self.assertEqual(identity_obj['user_experience'], 4700000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.one_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 700000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 9)
        self.assertEqual(anchor_obj['anchor_experience'], 700000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 588000 + 14112000)



    def test_silver_renew_bronze(self):
        """
        测试白银守护续费青铜守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 11)
        self.assertEqual(guard_list[0]['user_experience'], 764000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month + self.one_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 264000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 11)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 11)
        self.assertEqual(identity_obj['user_experience'], 764000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month + self.one_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 264000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 11)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 5)
        self.assertEqual(anchor_obj['anchor_experience'], 764000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 588000 + 1176000)

    def test_silver_renew_silver(self):
        """
        测试白银守护续费白银守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 12)
        self.assertEqual(guard_list[0]['user_experience'], 352000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month * 2)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month * 2))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month * 2)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 352000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 12)
        self.assertEqual(identity_obj['user_experience'], 352000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month * 2)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month * 2))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month * 2)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 352000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 6)
        self.assertEqual(anchor_obj['anchor_experience'], 352000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1176000 + 1176000)

    def test_silver_renew_three_gold(self):
        """
        测试白银守护续费三个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 12)
        self.assertEqual(guard_list[0]['user_experience'], 940000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 940000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 12)
        self.assertEqual(identity_obj['user_experience'], 940000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 940000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 6)
        self.assertEqual(anchor_obj['anchor_experience'], 940000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1176000 + 1764000)

    def test_silver_renew_six_gold(self):
        """
        测试白银守护续费六个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=3528000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 6, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 13)
        self.assertEqual(guard_list[0]['user_experience'], 1204000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 204000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 14)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 13)
        self.assertEqual(identity_obj['user_experience'], 1204000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 204000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 14)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 7)
        self.assertEqual(anchor_obj['anchor_experience'], 704000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1176000 + 3528000)

    def test_silver_renew_one_diamond(self):
        """
        测试白银守护续费一年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 15)
        self.assertEqual(guard_list[0]['user_experience'], 732000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1232000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 15)
        self.assertEqual(identity_obj['user_experience'], 732000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1232000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 8)
        self.assertEqual(anchor_obj['anchor_experience'], 232000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1176000 + 7056000)

    def test_silver_renew_two_diamond(self):
        """
        测试白银守护续费两年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=14112000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 13, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 17)
        self.assertEqual(guard_list[0]['user_experience'], 288000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1288000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 17)
        self.assertEqual(identity_obj['user_experience'], 288000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.two_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.two_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.two_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1288000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 9)
        self.assertEqual(anchor_obj['anchor_experience'], 1288000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1176000 + 14112000)



    def test_gold_renew_bronze(self):
        """
        测试黄金守护续费青铜守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 12)
        self.assertEqual(guard_list[0]['user_experience'], 352000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.one_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 352000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 12)
        self.assertEqual(identity_obj['user_experience'], 352000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.one_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 352000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 6)
        self.assertEqual(anchor_obj['anchor_experience'], 352000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 588000 + 1764000)

    def test_gold_renew_silver(self):
        """
        测试黄金守护续费白银守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 12)
        self.assertEqual(guard_list[0]['user_experience'], 940000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month + self.three_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 940000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 12)
        self.assertEqual(identity_obj['user_experience'], 940000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month + self.three_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 940000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 12)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 6)
        self.assertEqual(anchor_obj['anchor_experience'], 940000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1764000 + 1176000)

    def test_gold_renew_three_gold(self):
        """
        测试黄金守护续费三个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 13)
        self.assertEqual(guard_list[0]['user_experience'], 28000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 528000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 13)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 13)
        self.assertEqual(identity_obj['user_experience'], 28000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 528000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 13)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 6)
        self.assertEqual(anchor_obj['anchor_experience'], 1528000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1764000 + 1764000)

    def test_gold_renew_six_gold(self):
        """
        测试黄金守护续费六个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=3528000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 6, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 14)
        self.assertEqual(guard_list[0]['user_experience'], 292000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 792000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 14)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 14)
        self.assertEqual(identity_obj['user_experience'], 292000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 792000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 14)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 7)
        self.assertEqual(anchor_obj['anchor_experience'], 1292000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1764000 + 3528000)

    def test_gold_renew_one_diamond(self):
        """
        测试黄金守护续费一年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 15)
        self.assertEqual(guard_list[0]['user_experience'], 1320000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1820000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 15)
        self.assertEqual(identity_obj['user_experience'], 1320000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1820000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 8)
        self.assertEqual(anchor_obj['anchor_experience'], 820000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1764000 + 7056000)

    def test_gold_renew_two_diamond(self):
        """
        测试黄金守护续费两年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=14112000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 13, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 17)
        self.assertEqual(guard_list[0]['user_experience'], 876000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1876000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 17)
        self.assertEqual(identity_obj['user_experience'], 876000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.three_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.three_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.three_month)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1876000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 9)
        self.assertEqual(anchor_obj['anchor_experience'], 1876000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1764000 + 14112000)





    def test_diamond_renew_bronze(self):
        """
        测试钻石守护续费青铜守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 15)
        self.assertEqual(guard_list[0]['user_experience'], 144000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.one_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 644000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 15)
        self.assertEqual(identity_obj['user_experience'], 144000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.one_month)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.one_month))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.one_month)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 644000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 7)
        self.assertEqual(anchor_obj['anchor_experience'], 3644000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 588000 + 7056000)

    def test_diamond_renew_silver(self):
        """
        测试钻石守护续费白银守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 15)
        self.assertEqual(guard_list[0]['user_experience'], 732000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month + self.one_year)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1232000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 15)
        self.assertEqual(identity_obj['user_experience'], 732000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_month + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_month + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_month + self.one_year)).strftime("%Y-%m-%d %H"),
                      expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1232000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 8)
        self.assertEqual(anchor_obj['anchor_experience'], 232000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 7056000 + 1176000)

    def test_diamond_renew_three_gold(self):
        """
        测试钻石守护续费三个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 15)
        self.assertEqual(guard_list[0]['user_experience'], 1320000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1820000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 15)
        self.assertEqual(identity_obj['user_experience'], 1320000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.three_month + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.three_month + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.three_month + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1820000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 15)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 8)
        self.assertEqual(anchor_obj['anchor_experience'], 820000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 1764000 + 7056000)

    def test_diamond_renew_six_gold(self):
        """
        测试钻石守护续费六个月黄金守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=3528000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 6, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 16)
        self.assertEqual(guard_list[0]['user_experience'], 584000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 584000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 16)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 16)
        self.assertEqual(identity_obj['user_experience'], 584000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.six_month + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.six_month + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.six_month + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 584000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 16)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 8)
        self.assertEqual(anchor_obj['anchor_experience'], 2584000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 7056000 + 3528000)

    def test_diamond_renew_one_diamond(self):
        """
        测试钻石守护续费一年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 16)
        self.assertEqual(guard_list[0]['user_experience'], 4112000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 112000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 16)
        self.assertEqual(identity_obj['user_experience'], 4112000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.one_year + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.one_year + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.one_year + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 112000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 17)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 9)
        self.assertEqual(anchor_obj['anchor_experience'], 112000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 7056000 + 7056000)

    def test_diamond_renew_two_diamond(self):
        """
        测试钻石守护续费两年钻石守护
        :return:
        """
        self.follow_anchor()
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']

        # 首次开通
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        buy_guard = BuyGuardAjax(self.user_mobile)
        buy_guard.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard.get_resp_code(), 0)
        time.sleep(1)
        # 续费
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=14112000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 13, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护列表
        guard_list = buy_guard_result['guard_list']
        self.assertEqual(len(guard_list), 1)
        self.assertEqual(guard_list[0]['id'], self.user_id)
        self.assertEqual(guard_list[0]['user_rank'], 18)
        self.assertEqual(guard_list[0]['user_experience'], 1168000)
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = guard_list[0]['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1168000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 18)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')

        # 校验identity_obj
        identity_obj = buy_guard_result['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['id'], self.user_id)
        self.assertEqual(identity_obj['user_rank'], 18)
        self.assertEqual(identity_obj['user_experience'], 1168000)
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)
        self.assertEqual(user_guard_obj['rest_time_int'], self.two_year + self.one_year)
        self.assertEqual(user_guard_obj['rest_time_str'], '{0}天'.format(self.two_year + self.one_year))
        expire_time = user_guard_obj['expire_time']
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+self.two_year + self.one_year)).strftime(
            "%Y-%m-%d %H"), expire_time)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 1168000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 18)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 2)
        self.assertEqual(intimacy_level_obj['level_name'], '真爱')
        # 校验主播等级和经验值
        anchor_obj = buy_guard_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 10)
        self.assertEqual(anchor_obj['anchor_experience'], 1168000)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        after_renew_hot_num = live_new_server_ajax.get_resp_result()['room_obj']['curr_hot_num']
        # 校验房间热度
        self.assertEqual(after_renew_hot_num - hot_num, 7056000 + 14112000)

    def tearDown(self, *args):
        super(TestGuardRenewFollowing, self).tearDown(user_id=self.user_id, anchor_id=self.anchor_id)
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)







class TestBuyGuardAjaxAbnormal(BaseCase):
    """
    购买守护-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID


    def test_buy_guard_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': None, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 402000)
        self.assertEqual(buy_guard_ajax.get_resp_message(),'房间ID不能为空')

    def test_buy_guard_room_id_error(self):
        """
        测试请求接口房间ID不存在
        :return:
        """
        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': '909090', 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 200412)
        self.assertEqual(buy_guard_ajax.get_resp_message(),'参数异常')

    def test_buy_guard_id_null(self):
        """
        测试请求接口守护ID为空
        :return:
        """
        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': None, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 402012)
        self.assertEqual(buy_guard_ajax.get_resp_message(),'守护ID不能为空')

    def test_buy_guard_id_error(self):
        """
        测试请求接口守护ID不存在
        :return:
        """
        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 30, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 411148)
        self.assertEqual(buy_guard_ajax.get_resp_message(),'无此守护类型')

    def test_buy_guard_currency_null(self):
        """
        测试请求接口货币类型为空
        :return:
        """
        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': None})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 460004)
        self.assertEqual(buy_guard_ajax.get_resp_message(), '请选择货币类型')

    def test_buy_guard_currency_error(self):
        """
        测试请求接口货币类型不存在
        :return:
        """
        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'abc'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 460004)
        self.assertEqual(buy_guard_ajax.get_resp_message(), '请选择货币类型')

