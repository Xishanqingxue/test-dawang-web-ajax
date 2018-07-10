# -*- coding:utf-8 -*-
from ajax.ajax_anchor_group import OpenAnchorGroupAjax,AddAnchorToGroup
from ajax.live_guard import BuyGuardAjax
from ajax.user_consumption import ConsumptionAjax
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold,Redis
from base.base_helper import convert_to_timestamp
from base.base_case import BaseCase
import settings
import time
import datetime


class TestOpenAnchorGroupAjax(BaseCase):
    """
    开通主播团
    """
    user_mobile = settings.TEST_USER_MOBILE
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    user_rank = 12
    user_experience_all = 3000000

    def setUp(self, user_id=None, anchor_id=None):
        super(TestOpenAnchorGroupAjax,self).setUp(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).fix_anchor_group_gold().clean_user_anchor_group()
        Redis().clean_anchor_group(self.user_id, self.anchor_id)

    def test_open_anchor_group_rank_deficient(self):
        """
        测试开通主播团所需军衔
        :return:
        """
        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()
        self.assertEqual(open_anchor_group.get_resp_code(),200501)
        self.assertEqual(open_anchor_group.get_resp_message(),u'军衔达到1级上尉才可开通')

    def test_open_anchor_rank_insufficient_balance(self):
        """
        测试开通主播团金币不足
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)
        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()
        self.assertEqual(open_anchor_group.get_resp_code(),200502)
        self.assertEqual(open_anchor_group.get_resp_message(),u'金币不足，是否立即充值')

    def test_open_anchor_group_successful(self):
        """
        测试开通主播团成功
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
        mysql_operation.fix_user_account(gold_num=100000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()

        self.assertEqual(open_anchor_group.get_resp_code(),0)
        anchor_group_obj = open_anchor_group.get_resp_result()['anchor_group_obj']
        self.assertEqual(anchor_group_obj['user_id'], int(self.user_id))
        self.assertEqual(anchor_group_obj['gold'], 0)
        self.assertEqual(anchor_group_obj['max_num'], 2)
        self.assertEqual(anchor_group_obj['next_level'], 18)
        self.assertEqual(anchor_group_obj['next_level_name'], u'1级上校')
        self.assertEqual(anchor_group_obj['owend_anchor_count'], 0)

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
        self.assertEqual(consume_list[0]['type'],u'7')
        self.assertEqual(consume_list[0]['gold'],100000)
        self.assertEqual(consume_list[0]['corresponding_id'],0)
        self.assertEqual(consume_list[0]['corresponding_name'],'主播团')
        self.assertEqual(consume_list[0]['corresponding_num'],1)
        self.assertEqual(consume_list[0]['room_id'],'')
        self.assertEqual(consume_list[0]['status'],1)
        self.assertEqual(consume_list[0]['behavior_desc'],'开通主播团')
        self.assertEqual(consume_list[0]['consumption_type'],'{0}金币'.format(100000))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestOpenAnchorGroupAjax, self).tearDown(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).fix_anchor_group_gold().clean_user_anchor_group()
        Redis().clean_anchor_group(self.user_id, self.anchor_id)





class TestAddAnchorToGroupAjax(BaseCase):
    """
    将主播纳入主播团
    """
    user_mobile = settings.TEST_USER_MOBILE
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    room_id = settings.TEST_ROOM
    user_rank = 12
    user_experience_all = 2000000

    def setUp(self, user_id=None, anchor_id=None):
        super(TestAddAnchorToGroupAjax,self).setUp(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).fix_anchor_group_gold().clean_user_anchor_group()
        Redis().clean_anchor_group(self.user_id, self.anchor_id)
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)

    def test_add_bronze_to_group(self):
        """
        测试纳入青铜守护
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()

        self.assertEqual(open_anchor_group.get_resp_code(),0)
        anchor_group_obj = open_anchor_group.get_resp_result()['anchor_group_obj']
        self.assertEqual(anchor_group_obj['user_id'], int(self.user_id))
        self.assertEqual(anchor_group_obj['gold'], 0)
        self.assertEqual(anchor_group_obj['max_num'], 2)
        self.assertEqual(anchor_group_obj['next_level'], 18)
        self.assertEqual(anchor_group_obj['next_level_name'], u'1级上校')
        self.assertEqual(anchor_group_obj['owend_anchor_count'], 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=50000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        add_anchor_to_group = AddAnchorToGroup(self.user_mobile)
        add_anchor_to_group.post({'position': 1, 'anchor_id': self.anchor_id, 'grab_flag': 0,'change_flag': 0})
        self.assertEqual(add_anchor_to_group.get_resp_code(),0)

        anchor_group_list = add_anchor_to_group.get_resp_result()['anchor_group_list']
        self.assertEqual(len(anchor_group_list),2)
        self.assertIsNone(anchor_group_list[1])

        anchor_obj = anchor_group_list[0]['anchor_obj']
        self.assertEqual(anchor_obj['id'],self.anchor_id)

        anchor_group_anchor_obj = anchor_group_list[0]['anchor_group_anchor_obj']
        self.assertEqual(anchor_group_anchor_obj['user_id'],int(self.user_id))
        self.assertEqual(anchor_group_anchor_obj['anchor_id'],int(self.anchor_id))
        self.assertEqual(anchor_group_anchor_obj['room_id'],int(self.room_id))
        self.assertEqual(anchor_group_anchor_obj['position'],1)
        self.assertEqual(anchor_group_anchor_obj['income_gold'],0)
        self.assertEqual(anchor_group_anchor_obj['status'],1)
        self.assertLessEqual(anchor_group_anchor_obj['left_time'],604800)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['start_date_time'])
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+7)).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['end_date_time'])

        identity_obj = add_anchor_to_group.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(), 0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list), 3)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'], self.user_id)
        self.assertEqual(consume_list[0]['type'], '10')
        self.assertEqual(consume_list[0]['gold'], 50000)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '纳入主播团')
        self.assertEqual(consume_list[0]['corresponding_num'], 1)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '纳入主播团')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(50000))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_add_silver_to_group(self):
        """
        测试纳入白银守护
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()

        self.assertEqual(open_anchor_group.get_resp_code(),0)
        anchor_group_obj = open_anchor_group.get_resp_result()['anchor_group_obj']
        self.assertEqual(anchor_group_obj['user_id'], int(self.user_id))
        self.assertEqual(anchor_group_obj['gold'], 0)
        self.assertEqual(anchor_group_obj['max_num'], 2)
        self.assertEqual(anchor_group_obj['next_level'], 18)
        self.assertEqual(anchor_group_obj['next_level_name'], u'1级上校')
        self.assertEqual(anchor_group_obj['owend_anchor_count'], 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=50000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        add_anchor_to_group = AddAnchorToGroup(self.user_mobile)
        add_anchor_to_group.post({'position': 1, 'anchor_id': self.anchor_id, 'grab_flag': 0,'change_flag': 0})
        self.assertEqual(add_anchor_to_group.get_resp_code(),0)

        anchor_group_list = add_anchor_to_group.get_resp_result()['anchor_group_list']
        self.assertEqual(len(anchor_group_list),2)
        self.assertIsNone(anchor_group_list[1])

        anchor_obj = anchor_group_list[0]['anchor_obj']
        self.assertEqual(anchor_obj['id'],self.anchor_id)

        anchor_group_anchor_obj = anchor_group_list[0]['anchor_group_anchor_obj']
        self.assertEqual(anchor_group_anchor_obj['user_id'],int(self.user_id))
        self.assertEqual(anchor_group_anchor_obj['anchor_id'],int(self.anchor_id))
        self.assertEqual(anchor_group_anchor_obj['room_id'],int(self.room_id))
        self.assertEqual(anchor_group_anchor_obj['position'],1)
        self.assertEqual(anchor_group_anchor_obj['income_gold'],0)
        self.assertEqual(anchor_group_anchor_obj['status'],1)
        self.assertLessEqual(anchor_group_anchor_obj['left_time'],604800)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['start_date_time'])
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+7)).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['end_date_time'])

        identity_obj = add_anchor_to_group.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(), 0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list), 3)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'], self.user_id)
        self.assertEqual(consume_list[0]['type'], '10')
        self.assertEqual(consume_list[0]['gold'], 50000)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '纳入主播团')
        self.assertEqual(consume_list[0]['corresponding_num'], 1)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '纳入主播团')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(50000))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_add_gold_to_group(self):
        """
        测试纳入黄金守护
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()

        self.assertEqual(open_anchor_group.get_resp_code(),0)
        anchor_group_obj = open_anchor_group.get_resp_result()['anchor_group_obj']
        self.assertEqual(anchor_group_obj['user_id'], int(self.user_id))
        self.assertEqual(anchor_group_obj['gold'], 0)
        self.assertEqual(anchor_group_obj['max_num'], 2)
        self.assertEqual(anchor_group_obj['next_level'], 18)
        self.assertEqual(anchor_group_obj['next_level_name'], u'1级上校')
        self.assertEqual(anchor_group_obj['owend_anchor_count'], 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=50000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        add_anchor_to_group = AddAnchorToGroup(self.user_mobile)
        add_anchor_to_group.post({'position': 1, 'anchor_id': self.anchor_id, 'grab_flag': 0,'change_flag': 0})
        self.assertEqual(add_anchor_to_group.get_resp_code(),0)

        anchor_group_list = add_anchor_to_group.get_resp_result()['anchor_group_list']
        self.assertEqual(len(anchor_group_list),2)
        self.assertIsNone(anchor_group_list[1])

        anchor_obj = anchor_group_list[0]['anchor_obj']
        self.assertEqual(anchor_obj['id'],self.anchor_id)

        anchor_group_anchor_obj = anchor_group_list[0]['anchor_group_anchor_obj']
        self.assertEqual(anchor_group_anchor_obj['user_id'],int(self.user_id))
        self.assertEqual(anchor_group_anchor_obj['anchor_id'],int(self.anchor_id))
        self.assertEqual(anchor_group_anchor_obj['room_id'],int(self.room_id))
        self.assertEqual(anchor_group_anchor_obj['position'],1)
        self.assertEqual(anchor_group_anchor_obj['income_gold'],0)
        self.assertEqual(anchor_group_anchor_obj['status'],1)
        self.assertLessEqual(anchor_group_anchor_obj['left_time'],604800)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['start_date_time'])
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+7)).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['end_date_time'])

        identity_obj = add_anchor_to_group.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(), 0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list), 3)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'], self.user_id)
        self.assertEqual(consume_list[0]['type'], '10')
        self.assertEqual(consume_list[0]['gold'], 50000)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '纳入主播团')
        self.assertEqual(consume_list[0]['corresponding_num'], 1)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '纳入主播团')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(50000))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def test_add_diamond_to_group(self):
        """
        测试纳入钻石守护
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.5)

        open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
        open_anchor_group.get()

        self.assertEqual(open_anchor_group.get_resp_code(),0)
        anchor_group_obj = open_anchor_group.get_resp_result()['anchor_group_obj']
        self.assertEqual(anchor_group_obj['user_id'], int(self.user_id))
        self.assertEqual(anchor_group_obj['gold'], 0)
        self.assertEqual(anchor_group_obj['max_num'], 2)
        self.assertEqual(anchor_group_obj['next_level'], 18)
        self.assertEqual(anchor_group_obj['next_level_name'], u'1级上校')
        self.assertEqual(anchor_group_obj['owend_anchor_count'], 0)

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=50000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        add_anchor_to_group = AddAnchorToGroup(self.user_mobile)
        add_anchor_to_group.post({'position': 1, 'anchor_id': self.anchor_id, 'grab_flag': 0,'change_flag': 0})
        self.assertEqual(add_anchor_to_group.get_resp_code(),0)

        anchor_group_list = add_anchor_to_group.get_resp_result()['anchor_group_list']
        self.assertEqual(len(anchor_group_list),2)
        self.assertIsNone(anchor_group_list[1])

        anchor_obj = anchor_group_list[0]['anchor_obj']
        self.assertEqual(anchor_obj['id'],self.anchor_id)

        anchor_group_anchor_obj = anchor_group_list[0]['anchor_group_anchor_obj']
        self.assertEqual(anchor_group_anchor_obj['user_id'],int(self.user_id))
        self.assertEqual(anchor_group_anchor_obj['anchor_id'],int(self.anchor_id))
        self.assertEqual(anchor_group_anchor_obj['room_id'],int(self.room_id))
        self.assertEqual(anchor_group_anchor_obj['position'],1)
        self.assertEqual(anchor_group_anchor_obj['income_gold'],0)
        self.assertEqual(anchor_group_anchor_obj['status'],1)
        self.assertLessEqual(anchor_group_anchor_obj['left_time'],604800)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['start_date_time'])
        self.assertIn((datetime.datetime.now() + datetime.timedelta(days=+7)).strftime("%Y-%m-%d %H"),anchor_group_anchor_obj['end_date_time'])

        identity_obj = add_anchor_to_group.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)

        # 校验消费记录
        consumption_ajax = ConsumptionAjax(self.user_mobile)
        consumption_ajax.get()
        self.assertEqual(consumption_ajax.get_resp_code(), 0)

        consumption_result = consumption_ajax.get_resp_result()
        consume_list = consumption_result['consume_list']
        self.assertEqual(len(consume_list), 3)
        create_time = consume_list[0]['create_time']
        create_time_mk = convert_to_timestamp(create_time)
        self.assertLessEqual(int(time.time()) - create_time_mk, 5)
        self.assertEqual(consume_list[0]['user_id'], self.user_id)
        self.assertEqual(consume_list[0]['type'], '10')
        self.assertEqual(consume_list[0]['gold'], 50000)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '纳入主播团')
        self.assertEqual(consume_list[0]['corresponding_num'], 1)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '纳入主播团')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(50000))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestAddAnchorToGroupAjax, self).tearDown(user_id=self.user_id)
        MysqlOperation(user_id=self.user_id).fix_anchor_group_gold().clean_user_anchor_group()
        Redis().clean_anchor_group(self.user_id, self.anchor_id)
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)





# class TestAnchorGroupWithdraw(BaseCase):
#     """
#     金库提现
#     """
#     user_mobile = settings.TEST_USER_MOBILE
#     user_id = settings.TEST_USER_ID
#     anchor_id = settings.TEST_ANCHOR_ID
#     room_id = settings.TEST_ROOM
#     user_rank = 12
#     user_experience_all = 2000000
#
#     def setUp(self, user_id=None, anchor_id=None):
#         super(TestAnchorGroupWithdraw,self).setUp(user_id=self.user_id)
#         MysqlOperation(user_id=self.user_id).fix_anchor_group_gold().clean_user_anchor_group()
#         Redis().clean_anchor_group(self.user_id, self.anchor_id)
#         MysqlOperation(user_id=self.user_id).clean_user_guard()
#         Redis().clean_user_buy_guard(self.user_id, self.anchor_id)
#
#
#     def test_anchor_group_withdraw_success(self):
#         """
#         测试金库提现成功
#         :return:
#         """
#         mysql_operation = MysqlOperation(user_id=self.user_id)
#         mysql_operation.fix_user_rank_and_experience(user_rank=self.user_rank,experience_all=self.user_experience_all)
#         mysql_operation.fix_user_account(gold_num=588000)
#         RedisHold().clean_redis_user_detail(self.user_id)
#         time.sleep(0.3)
#
#         buy_guard_ajax = BuyGuardAjax(self.user_mobile)
#         buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
#         self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
#
#         mysql_operation = MysqlOperation(user_id=self.user_id)
#         mysql_operation.fix_user_account(gold_num=100000)
#         RedisHold().clean_redis_user_detail(self.user_id)
#         time.sleep(0.5)
#
#         open_anchor_group = OpenAnchorGroupAjax(self.user_mobile)
#         open_anchor_group.get()
#
#         self.assertEqual(open_anchor_group.get_resp_code(),0)
#         anchor_group_obj = open_anchor_group.get_resp_result()['anchor_group_obj']
#         self.assertEqual(anchor_group_obj['user_id'], int(self.user_id))
#         self.assertEqual(anchor_group_obj['gold'], 0)
#         self.assertEqual(anchor_group_obj['max_num'], 2)
#         self.assertEqual(anchor_group_obj['next_level'], 18)
#         self.assertEqual(anchor_group_obj['next_level_name'], u'1级上校')
#         self.assertEqual(anchor_group_obj['owend_anchor_count'], 0)
#
#         mysql_operation = MysqlOperation(user_id=self.user_id)
#         mysql_operation.fix_user_account(gold_num=50000)
#         RedisHold().clean_redis_user_detail(self.user_id)
#         time.sleep(0.3)
#
#         add_anchor_to_group = AddAnchorToGroup(self.user_mobile)
#         add_anchor_to_group.post({'position': 1, 'anchor_id': self.anchor_id, 'grab_flag': 0,'change_flag': 0})
#         self.assertEqual(add_anchor_to_group.get_resp_code(),0)
#
#         anchor_group_list = add_anchor_to_group.get_resp_result()['anchor_group_list']
#         self.assertEqual(len(anchor_group_list),2)
#         self.assertIsNone(anchor_group_list[1])
#
#         anchor_obj = anchor_group_list[0]['anchor_obj']
#         self.assertEqual(anchor_obj['id'],self.anchor_id)
