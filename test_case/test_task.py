# -*- coding:utf-8 -*-
from ajax.live_task import TaskListAjax
from ajax.live_task import GetTaskRewardAjax
from ajax.live_send_gift import LiveSendGift
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import Redis,RedisHold
from base.base_case import BaseCase
import settings
import time
import datetime


class TestTaskListAjax(BaseCase):
    """
    任务
    """
    user_mobile = '13309090909'
    room_id = settings.TEST_ROOM
    user_id = '22017468'
    anchor_id = settings.TEST_ANCHOR_ID

    def setUp(self, *args):
        super(TestTaskListAjax,self).setUp()
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        MysqlOperation(user_id=self.user_id).fix_user_bind_mobile(login_name=self.user_mobile).clean_user_task()
        Redis().clean_check_mobile_code(self.user_id)
        Redis().clean_user_task(self.user_id)
        time.sleep(0.2)


    def test_get_task_list_success(self):
        """
        测试获取任务列表成功
        :return:
        """
        task_list_ajax = TaskListAjax(self.user_mobile)
        task_list_ajax.get()
        self.assertEqual(task_list_ajax.get_resp_code(),0)
        task_list = task_list_ajax.get_resp_result()['task_list']

        self.assertEqual(len(task_list),4)

        bind_mobile_task_obj = task_list[0]
        self.assertEqual(bind_mobile_task_obj['id'],1)
        self.assertEqual(bind_mobile_task_obj['task_type'],'once')
        self.assertEqual(bind_mobile_task_obj['task_behavior'],'bind_mobile')
        self.assertEqual(bind_mobile_task_obj['task_name'],'绑定手机')
        self.assertEqual(bind_mobile_task_obj['task_desc'],'绑定手机号送5000大王豆')
        self.assertEqual(bind_mobile_task_obj['task_num'],1)
        self.assertEqual(bind_mobile_task_obj['task_icon'],'/images/heads/20160328093828364.png')
        self.assertEqual(bind_mobile_task_obj['unit'],'大王豆')
        self.assertIsNone(bind_mobile_task_obj['user_task_obj'])
        task_award_config = bind_mobile_task_obj['task_award_config']
        self.assertEqual(len(task_award_config),1)
        self.assertEqual(task_award_config[0]['type'],'diamond')
        self.assertEqual(task_award_config[0]['id'],0)
        self.assertEqual(task_award_config[0]['num'],5000)

        recharging_task_obj = task_list[1]
        self.assertEqual(recharging_task_obj['id'],3)
        self.assertEqual(recharging_task_obj['task_type'],'daily')
        self.assertEqual(recharging_task_obj['task_behavior'],'recharging')
        self.assertEqual(recharging_task_obj['task_name'],'充值')
        self.assertEqual(recharging_task_obj['task_desc'],'充值送288大王豆')
        self.assertEqual(recharging_task_obj['task_num'],1)
        self.assertEqual(recharging_task_obj['task_icon'],'/images/heads/20160328093828364.png')
        self.assertEqual(recharging_task_obj['unit'],'大王豆')
        self.assertIsNone(recharging_task_obj['user_task_obj'])
        task_award_config = recharging_task_obj['task_award_config']
        self.assertEqual(len(task_award_config),1)
        self.assertEqual(task_award_config[0]['type'],'diamond')
        self.assertEqual(task_award_config[0]['id'],0)
        self.assertEqual(task_award_config[0]['num'],288)

        share_to_sns_task_obj = task_list[2]
        self.assertEqual(share_to_sns_task_obj['id'],4)
        self.assertEqual(share_to_sns_task_obj['task_type'],'daily')
        self.assertEqual(share_to_sns_task_obj['task_behavior'],'share_to_sns')
        self.assertEqual(share_to_sns_task_obj['task_name'],'分享')
        self.assertEqual(share_to_sns_task_obj['task_desc'],'分享三次送88大王豆')
        self.assertEqual(share_to_sns_task_obj['task_num'],3)
        self.assertEqual(share_to_sns_task_obj['task_icon'],'/images/heads/20160328093828364.png')
        self.assertEqual(share_to_sns_task_obj['unit'],'大王豆')
        self.assertIsNone(share_to_sns_task_obj['user_task_obj'])
        task_award_config = share_to_sns_task_obj['task_award_config']
        self.assertEqual(len(task_award_config),1)
        self.assertEqual(task_award_config[0]['type'],'diamond')
        self.assertEqual(task_award_config[0]['id'],0)
        self.assertEqual(task_award_config[0]['num'],88)

        send_gift_task_obj = task_list[3]
        self.assertEqual(send_gift_task_obj['id'],5)
        self.assertEqual(send_gift_task_obj['task_type'],'daily')
        self.assertEqual(send_gift_task_obj['task_behavior'],'send_gift')
        self.assertEqual(send_gift_task_obj['task_name'],'送礼')
        self.assertEqual(send_gift_task_obj['task_desc'],'送任意金额的礼物送500经验')
        self.assertEqual(send_gift_task_obj['task_num'],1)
        self.assertEqual(send_gift_task_obj['task_icon'],'/images/heads/20160328093828364.png')
        self.assertEqual(send_gift_task_obj['unit'],'经验')
        self.assertIsNone(send_gift_task_obj['user_task_obj'])
        task_award_config = send_gift_task_obj['task_award_config']
        self.assertEqual(len(task_award_config),1)
        self.assertEqual(task_award_config[0]['type'],'exp')
        self.assertEqual(task_award_config[0]['id'],0)
        self.assertEqual(task_award_config[0]['num'],500)

    def test_send_gift_task(self):
        """
        测试完成送礼物任务并领取奖励
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': 60,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        time.sleep(3)
        task_list_ajax = TaskListAjax(self.user_mobile)
        task_list_ajax.get()
        self.assertEqual(task_list_ajax.get_resp_code(), 0)
        task_list = task_list_ajax.get_resp_result()['task_list']

        send_gift_task_obj = task_list[3]
        self.assertEqual(send_gift_task_obj['id'], 5)
        self.assertEqual(send_gift_task_obj['task_type'], 'daily')
        self.assertEqual(send_gift_task_obj['task_behavior'], 'send_gift')
        self.assertEqual(send_gift_task_obj['task_name'], '送礼')
        self.assertEqual(send_gift_task_obj['task_desc'], '送任意金额的礼物送500经验')
        self.assertEqual(send_gift_task_obj['task_num'], 1)
        self.assertEqual(send_gift_task_obj['task_icon'], '/images/heads/20160328093828364.png')
        self.assertEqual(send_gift_task_obj['unit'], '经验')
        user_task_obj = send_gift_task_obj['user_task_obj']
        self.assertEqual(user_task_obj['id'],0)
        self.assertEqual(user_task_obj['user_id'],self.user_id)
        self.assertEqual(user_task_obj['task_behavior'],'send_gift')
        self.assertEqual(user_task_obj['num'],1)
        self.assertEqual(user_task_obj['status'],2)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),user_task_obj['last_modify_date'])
        task_award_config = send_gift_task_obj['task_award_config']
        self.assertEqual(len(task_award_config), 1)
        self.assertEqual(task_award_config[0]['type'], 'exp')
        self.assertEqual(task_award_config[0]['id'], 0)
        self.assertEqual(task_award_config[0]['num'], 500)

        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior':'send_gift','room_id':self.room_id,'anchor_id':self.anchor_id})
        self.assertEqual(get_task_reward_ajax.get_resp_code(),0)
        task_rewards = get_task_reward_ajax.get_resp_result()['task_rewards']
        self.assertEqual(task_rewards['upgrade'],0)
        self.assertEqual(task_rewards['exp'],500)
        identity_obj = get_task_reward_ajax.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['gold'],0)
        self.assertEqual(identity_obj['diamond'],'0')
        self.assertEqual(identity_obj['user_experience'],600)


        task_list_ajax = TaskListAjax(self.user_mobile)
        task_list_ajax.get()
        self.assertEqual(task_list_ajax.get_resp_code(), 0)
        task_list = task_list_ajax.get_resp_result()['task_list']

        send_gift_task_obj = task_list[3]
        self.assertEqual(send_gift_task_obj['task_name'], '送礼')
        user_task_obj = send_gift_task_obj['user_task_obj']
        self.assertEqual(user_task_obj['status'],3)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),user_task_obj['last_modify_date'])


    def tearDown(self, *args):
        super(TestTaskListAjax,self).tearDown()
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        MysqlOperation(user_id=self.user_id).fix_user_bind_mobile(login_name=self.user_mobile).clean_user_task()
        Redis().clean_check_mobile_code(self.user_id)
        Redis().clean_user_task(self.user_id)
        time.sleep(0.2)







class TestGetTaskRewardAbnormal(BaseCase):
    """
    领取任务奖励-异常
    """
    user_mobile = '13309090909'
    room_id = settings.TEST_ROOM
    user_id = '22017468'
    anchor_id = settings.TEST_ANCHOR_ID

    def setUp(self, *args):
        super(TestGetTaskRewardAbnormal,self).setUp()
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        MysqlOperation(user_id=self.user_id).fix_user_bind_mobile(login_name=self.user_mobile).clean_user_task()
        Redis().clean_check_mobile_code(self.user_id)
        Redis().clean_user_task(self.user_id)
        time.sleep(0.2)

    def test_get_task_reward_room_id_null(self):
        """
        测试请求接口房间ID为空,可以成功
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': 60,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        time.sleep(3)

        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior': 'send_gift', 'room_id': None, 'anchor_id': self.anchor_id})
        self.assertEqual(get_task_reward_ajax.get_resp_code(), 0)

    def test_get_task_reward_room_id_error(self):
        """
        测试请求接口房间ID不存在,可以成功
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': 60,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        time.sleep(3)

        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior': 'send_gift', 'room_id': '909090', 'anchor_id': self.anchor_id})
        self.assertEqual(get_task_reward_ajax.get_resp_code(), 0)

    def test_get_task_reward_anchor_id_null(self):
        """
        测试请求接口主播ID为空,可以成功
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': 60,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        time.sleep(3)

        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior': 'send_gift', 'room_id': self.room_id, 'anchor_id': None})
        self.assertEqual(get_task_reward_ajax.get_resp_code(), 0)

    def test_get_task_reward_anchor_id_error(self):
        """
        测试请求接口主播ID不存在,可以成功
        :return:
        """
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=100)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        send_gift_ajax = LiveSendGift(self.user_mobile)
        send_gift_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'gift_id': 60,
                            'gift_count': 1, 'currency': 'gold'})
        self.assertEqual(send_gift_ajax.get_resp_code(), 0)
        time.sleep(3)

        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior': 'send_gift', 'room_id': self.room_id, 'anchor_id': '90909090'})
        self.assertEqual(get_task_reward_ajax.get_resp_code(), 0)

    def test_get_task_reward_task_behavior_null(self):
        """
        测试请求接口任务描述为空
        :return:
        """
        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior': None, 'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(get_task_reward_ajax.get_resp_code(), 430004)
        self.assertEqual(get_task_reward_ajax.get_resp_message(), '任务类型不能为空')

    def test_get_task_reward_task_behavior_error(self):
        """
        测试请求接口任务描述不存在
        :return:
        """
        get_task_reward_ajax = GetTaskRewardAjax(self.user_mobile)
        get_task_reward_ajax.get({'task_behavior': 'abc', 'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(get_task_reward_ajax.get_resp_code(), 430001)
        self.assertEqual(get_task_reward_ajax.get_resp_message(), '任务不存在')

    def tearDown(self, *args):
        super(TestGetTaskRewardAbnormal,self).tearDown()
        mysql_operation = MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id)
        mysql_operation.fix_user_account().clean_user_intimacy_rank().clean_user_account_log()
        mysql_operation.clean_send_gift().clean_user_package_gift().clean_user_contribution()
        MysqlOperation(anchor_id=self.anchor_id).fix_anchor_rank_and_exp()
        for x in [self.user_id, self.anchor_id]:
            MysqlOperation(user_id=x).fix_user_rank_and_experience()
            RedisHold().clean_redis_user_detail(x)
        RedisHold().clean_redis_room_detail(self.room_id, self.anchor_id)
        MysqlOperation(user_id=self.user_id).fix_user_bind_mobile(login_name=self.user_mobile).clean_user_task()
        Redis().clean_check_mobile_code(self.user_id)
        Redis().clean_user_task(self.user_id)
        time.sleep(0.2)
