# -*- coding:utf-8 -*-
from ajax.ajax_anchor_group import OpenAnchorGroupAjax
from ajax.user_consumption import ConsumptionAjax
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold,Redis
from base.base_helper import convert_to_timestamp
from base.base_case import BaseCase
import settings
import time


class TestOpenAnchorGroupAjax(BaseCase):
    """
    开通主播团
    """
    user_mobile = settings.TEST_USER_MOBILE
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    user_rank = 12
    user_experience_all = 2000000

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

