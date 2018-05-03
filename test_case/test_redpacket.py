# -*- coding:utf-8 -*-
from ajax.ajax_redpacket import SendRedPacketAjax,GetHistoryAjax,GetRedPacketAjax,GetGrabRedPacketLogAjax,GrabRedPacketAjax
from ajax.user_follow import AddFollowAjax,RelieveFollowAjax
from ajax.live_new_server import LiveNewServer
from base.base_helper import convert_to_timestamp
from ajax.user_consumption import ConsumptionAjax
from base.base_case import BaseCase
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold,Redis
import settings
import time
import datetime


class TestSendPacketAjax(BaseCase):
    """
    发红包/发红包记录/房间可抢红包列表
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    time_sleep = 0.5

    def setUp(self, *args):
        super(TestSendPacketAjax,self).setUp(user_id=self.user_id,anchor_id=self.anchor_id)
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        red_packet_ids = MysqlOperation(room_id=self.room_id).get_red_packet_ids()
        MysqlOperation(room_id=self.room_id).clean_red_packet()
        MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id).clean_send_gift()
        for i in red_packet_ids:
            Redis().clean_red_packet(self.room_id, i['id'])
        RedisHold().clean_redis_room_detail(self.room_id,self.anchor_id)

    def test_send_welfare_50(self):
        """
        测试发放50个福利包
        :return:
        """
        red_packet_gold = 50000
        num = 50
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        hot_num = live_result['room_obj']['curr_hot_num']

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1,'room_id': self.room_id,'num': num,'currency':'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(),0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],red_packet_gold * 0.2)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],2)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],40000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'],int(self.user_id))
        self.assertEqual(red_packet_id['room_id'],int(self.room_id))
        self.assertEqual(red_packet_id['num'],num)
        self.assertEqual(red_packet_id['gold'],red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_id['left_num'],num)
        self.assertEqual(red_packet_id['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'],44)
        self.assertEqual(red_packet_id['diamond'],0)
        self.assertEqual(red_packet_id['real_diamond'],0)
        self.assertEqual(red_packet_id['left_diamond'],0)
        self.assertEqual(red_packet_id['fact_diamond'],0)
        self.assertEqual(red_packet_id['red_status'],1)
        self.assertEqual(red_packet_id['type'],1)
        self.assertEqual(red_packet_id['status'],1)
        self.assertEqual(red_packet_id['name'],'福利包')
        self.assertLessEqual(red_packet_id['count_down_time'],60)
        self.assertLessEqual(50,red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']),86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num,red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'],1)
        self.assertEqual(anchor_obj['anchor_experience'],red_packet_gold * 0.2)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(),0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list),1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'],self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],44)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],1)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id':self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(),0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'],self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],44)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],1)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

        time.sleep(60)
        grab_ajax = GrabRedPacketAjax(self.user_mobile)
        grab_ajax.get({'red_packet_id':packet_id,'room_id':self.room_id})
        self.assertEqual(grab_ajax.get_resp_code(),0)
        red_packet_log_obj = grab_ajax.get_resp_result()['red_packet_log_obj']
        self.assertEqual(red_packet_log_obj['red_packet_id'],packet_id)
        self.assertEqual(red_packet_log_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_log_obj['room_id'],int(self.room_id))
        get_gold = red_packet_log_obj['get_gold']
        self.assertNotEqual(get_gold,0)
        self.assertEqual(red_packet_log_obj['get_diamond'],0)
        self.assertEqual(red_packet_log_obj['is_max'],'0')
        user_red_packet_list = grab_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),0)

        grab_log_ajax = GetGrabRedPacketLogAjax(self.user_mobile)
        grab_log_ajax.get({'red_packet_id':packet_id})
        self.assertEqual(grab_log_ajax.get_resp_code(),0)

        red_packet_obj = grab_log_ajax.get_resp_result()['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertLess(red_packet_obj['left_num'], num)
        self.assertNotEqual(red_packet_obj['left_num'],0)
        self.assertLess(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertNotEqual(red_packet_obj['left_gold'],0)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 44)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 1)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertEqual(red_packet_obj['count_down_time'],0)
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        red_packet_log_list = grab_log_ajax.get_resp_result()['red_packet_log_list']
        self.assertNotEqual(len(red_packet_log_list),0)

        identity_obj = grab_log_ajax.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],get_gold)


    def test_send_welfare_100(self):
        """
        测试发放100个福利包
        :return:
        """
        red_packet_gold = 50000
        num = 100
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        hot_num = live_result['room_obj']['curr_hot_num']

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1,'room_id': self.room_id,'num': num,'currency':'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(),0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],red_packet_gold * 0.2)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],2)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],40000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'],int(self.user_id))
        self.assertEqual(red_packet_id['room_id'],int(self.room_id))
        self.assertEqual(red_packet_id['num'],num)
        self.assertEqual(red_packet_id['gold'],red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_id['left_num'],num)
        self.assertEqual(red_packet_id['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'],44)
        self.assertEqual(red_packet_id['diamond'],0)
        self.assertEqual(red_packet_id['real_diamond'],0)
        self.assertEqual(red_packet_id['left_diamond'],0)
        self.assertEqual(red_packet_id['fact_diamond'],0)
        self.assertEqual(red_packet_id['red_status'],1)
        self.assertEqual(red_packet_id['type'],1)
        self.assertEqual(red_packet_id['status'],1)
        self.assertEqual(red_packet_id['name'],'福利包')
        self.assertLessEqual(red_packet_id['count_down_time'],60)
        self.assertLessEqual(50,red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']),86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num,red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'],1)
        self.assertEqual(anchor_obj['anchor_experience'],red_packet_gold * 0.2)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(),0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list),1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'],self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],44)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],1)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id':self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(),0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'],self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],44)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],1)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

    def test_send_welfare_200(self):
        """
        测试发放200个福利包
        :return:
        """
        red_packet_gold = 50000
        num = 200
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        hot_num = live_result['room_obj']['curr_hot_num']

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1,'room_id': self.room_id,'num': num,'currency':'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(),0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],red_packet_gold * 0.2)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],2)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],40000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'],int(self.user_id))
        self.assertEqual(red_packet_id['room_id'],int(self.room_id))
        self.assertEqual(red_packet_id['num'],num)
        self.assertEqual(red_packet_id['gold'],red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_id['left_num'],num)
        self.assertEqual(red_packet_id['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'],44)
        self.assertEqual(red_packet_id['diamond'],0)
        self.assertEqual(red_packet_id['real_diamond'],0)
        self.assertEqual(red_packet_id['left_diamond'],0)
        self.assertEqual(red_packet_id['fact_diamond'],0)
        self.assertEqual(red_packet_id['red_status'],1)
        self.assertEqual(red_packet_id['type'],1)
        self.assertEqual(red_packet_id['status'],1)
        self.assertEqual(red_packet_id['name'],'福利包')
        self.assertLessEqual(red_packet_id['count_down_time'],60)
        self.assertLessEqual(50,red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']),86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num,red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'],1)
        self.assertEqual(anchor_obj['anchor_experience'],red_packet_gold * 0.2)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(),0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list),1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'],self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],44)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],1)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id':self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(),0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'],self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],44)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],1)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'福利包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

    def test_send_tyrants_50(self):
        """
        测试发放50个土豪包
        :return:
        """
        red_packet_gold = 100000
        num = 50
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        hot_num = live_result['room_obj']['curr_hot_num']

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 2,'room_id': self.room_id,'num': num,'currency':'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(),0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],0)
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],red_packet_gold * 0.2)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],10000)
        self.assertEqual(intimacy_obj['intimacy_rank'],2)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],40000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'],int(self.user_id))
        self.assertEqual(red_packet_id['room_id'],int(self.room_id))
        self.assertEqual(red_packet_id['num'],num)
        self.assertEqual(red_packet_id['gold'],red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_id['left_num'],num)
        self.assertEqual(red_packet_id['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'],45)
        self.assertEqual(red_packet_id['diamond'],0)
        self.assertEqual(red_packet_id['real_diamond'],0)
        self.assertEqual(red_packet_id['left_diamond'],0)
        self.assertEqual(red_packet_id['fact_diamond'],0)
        self.assertEqual(red_packet_id['red_status'],1)
        self.assertEqual(red_packet_id['type'],2)
        self.assertEqual(red_packet_id['status'],1)
        self.assertEqual(red_packet_id['name'],'土豪包')
        self.assertLessEqual(red_packet_id['count_down_time'],60)
        self.assertLessEqual(50,red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']),86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num,red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'],1)
        self.assertEqual(anchor_obj['anchor_experience'],red_packet_gold * 0.2)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(),0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list),1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'],self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],45)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],2)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id':self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(),0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'],self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'],packet_id)
        self.assertEqual(red_packet_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'],int(self.room_id))
        self.assertEqual(red_packet_obj['num'],num)
        self.assertEqual(red_packet_obj['gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'],red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'],num)
        self.assertEqual(red_packet_obj['left_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'],red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'],45)
        self.assertEqual(red_packet_obj['diamond'],0)
        self.assertEqual(red_packet_obj['real_diamond'],0)
        self.assertEqual(red_packet_obj['left_diamond'],0)
        self.assertEqual(red_packet_obj['fact_diamond'],0)
        self.assertEqual(red_packet_obj['red_status'],1)
        self.assertEqual(red_packet_obj['type'],2)
        self.assertEqual(red_packet_obj['status'],1)
        self.assertEqual(red_packet_obj['name'],'土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'],60)
        self.assertLessEqual(50,red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'],1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"),red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']),86400)

        time.sleep(60)
        grab_ajax = GrabRedPacketAjax(self.user_mobile)
        grab_ajax.get({'red_packet_id':packet_id,'room_id':self.room_id})
        self.assertEqual(grab_ajax.get_resp_code(),0)
        red_packet_log_obj = grab_ajax.get_resp_result()['red_packet_log_obj']
        self.assertEqual(red_packet_log_obj['red_packet_id'],packet_id)
        self.assertEqual(red_packet_log_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_log_obj['room_id'],int(self.room_id))
        get_gold = red_packet_log_obj['get_gold']
        self.assertNotEqual(get_gold,0)
        self.assertEqual(red_packet_log_obj['get_diamond'],0)
        self.assertEqual(red_packet_log_obj['is_max'],'0')
        user_red_packet_list = grab_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),0)

        grab_log_ajax = GetGrabRedPacketLogAjax(self.user_mobile)
        grab_log_ajax.get({'red_packet_id':packet_id})
        self.assertEqual(grab_log_ajax.get_resp_code(),0)

        red_packet_obj = grab_log_ajax.get_resp_result()['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertLess(red_packet_obj['left_num'], num)
        self.assertNotEqual(red_packet_obj['left_num'],0)
        self.assertLess(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertNotEqual(red_packet_obj['left_gold'],0)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 45)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 2)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertEqual(red_packet_obj['count_down_time'],0)
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        red_packet_log_list = grab_log_ajax.get_resp_result()['red_packet_log_list']
        self.assertNotEqual(len(red_packet_log_list),0)

        identity_obj = grab_log_ajax.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],get_gold)

    def test_send_tyrants_100(self):
        """
        测试发放100个土豪包
        :return:
        """
        red_packet_gold = 100000
        num = 100
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

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 2, 'room_id': self.room_id, 'num': num, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['user_rank'], 1)
        self.assertEqual(identity_obj['user_experience'], red_packet_gold * 0.2)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 10000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 2)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 40000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'], 1)
        self.assertEqual(intimacy_level_obj['rank_end'], 15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'], int(self.user_id))
        self.assertEqual(red_packet_id['room_id'], int(self.room_id))
        self.assertEqual(red_packet_id['num'], num)
        self.assertEqual(red_packet_id['gold'], red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_id['left_num'], num)
        self.assertEqual(red_packet_id['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'], 45)
        self.assertEqual(red_packet_id['diamond'], 0)
        self.assertEqual(red_packet_id['real_diamond'], 0)
        self.assertEqual(red_packet_id['left_diamond'], 0)
        self.assertEqual(red_packet_id['fact_diamond'], 0)
        self.assertEqual(red_packet_id['red_status'], 1)
        self.assertEqual(red_packet_id['type'], 2)
        self.assertEqual(red_packet_id['status'], 1)
        self.assertEqual(red_packet_id['name'], '土豪包')
        self.assertLessEqual(red_packet_id['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']), 86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num, red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 1)
        self.assertEqual(anchor_obj['anchor_experience'], red_packet_gold * 0.2)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(), 0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list), 1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'], self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 45)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 2)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id': self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(), 0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list), 1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'], self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 45)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 2)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

    def test_send_tyrants_200(self):
        """
        测试发放200个土豪包
        :return:
        """
        red_packet_gold = 100000
        num = 200
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

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 2, 'room_id': self.room_id, 'num': num, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['user_rank'], 1)
        self.assertEqual(identity_obj['user_experience'], red_packet_gold * 0.2)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 10000)
        self.assertEqual(intimacy_obj['intimacy_rank'], 2)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 40000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'], 1)
        self.assertEqual(intimacy_level_obj['rank_end'], 15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'], int(self.user_id))
        self.assertEqual(red_packet_id['room_id'], int(self.room_id))
        self.assertEqual(red_packet_id['num'], num)
        self.assertEqual(red_packet_id['gold'], red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_id['left_num'], num)
        self.assertEqual(red_packet_id['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'], 45)
        self.assertEqual(red_packet_id['diamond'], 0)
        self.assertEqual(red_packet_id['real_diamond'], 0)
        self.assertEqual(red_packet_id['left_diamond'], 0)
        self.assertEqual(red_packet_id['fact_diamond'], 0)
        self.assertEqual(red_packet_id['red_status'], 1)
        self.assertEqual(red_packet_id['type'], 2)
        self.assertEqual(red_packet_id['status'], 1)
        self.assertEqual(red_packet_id['name'], '土豪包')
        self.assertLessEqual(red_packet_id['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']), 86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num, red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 1)
        self.assertEqual(anchor_obj['anchor_experience'], red_packet_gold * 0.2)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(), 0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list), 1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'], self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 45)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 2)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id': self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(), 0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list), 1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'], self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 45)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 2)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '土豪包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

    def test_send_supreme_50(self):
        """
        测试发放50个至尊包
        :return:
        """
        red_packet_gold = 588000
        num = 50
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

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 3, 'room_id': self.room_id, 'num': num, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['user_rank'], 3)
        self.assertEqual(identity_obj['user_experience'], 17600)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 17600)
        self.assertEqual(intimacy_obj['intimacy_rank'], 4)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 100000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'], 1)
        self.assertEqual(intimacy_level_obj['rank_end'], 15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'], int(self.user_id))
        self.assertEqual(red_packet_id['room_id'], int(self.room_id))
        self.assertEqual(red_packet_id['num'], num)
        self.assertEqual(red_packet_id['gold'], red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_id['left_num'], num)
        self.assertEqual(red_packet_id['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'], 46)
        self.assertEqual(red_packet_id['diamond'], 0)
        self.assertEqual(red_packet_id['real_diamond'], 0)
        self.assertEqual(red_packet_id['left_diamond'], 0)
        self.assertEqual(red_packet_id['fact_diamond'], 0)
        self.assertEqual(red_packet_id['red_status'], 1)
        self.assertEqual(red_packet_id['type'], 3)
        self.assertEqual(red_packet_id['status'], 1)
        self.assertEqual(red_packet_id['name'], '至尊包')
        self.assertLessEqual(red_packet_id['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']), 86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num, red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 2)
        self.assertEqual(anchor_obj['anchor_experience'], 67600)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(), 0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list), 1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'], self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id': self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(), 0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list), 1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'], self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        time.sleep(60)
        grab_ajax = GrabRedPacketAjax(self.user_mobile)
        grab_ajax.get({'red_packet_id':packet_id,'room_id':self.room_id})
        self.assertEqual(grab_ajax.get_resp_code(),0)
        red_packet_log_obj = grab_ajax.get_resp_result()['red_packet_log_obj']
        self.assertEqual(red_packet_log_obj['red_packet_id'],packet_id)
        self.assertEqual(red_packet_log_obj['user_id'],int(self.user_id))
        self.assertEqual(red_packet_log_obj['room_id'],int(self.room_id))
        get_gold = red_packet_log_obj['get_gold']
        self.assertNotEqual(get_gold,0)
        self.assertEqual(red_packet_log_obj['get_diamond'],0)
        self.assertEqual(red_packet_log_obj['is_max'],'0')
        user_red_packet_list = grab_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list),0)

        grab_log_ajax = GetGrabRedPacketLogAjax(self.user_mobile)
        grab_log_ajax.get({'red_packet_id':packet_id})
        self.assertEqual(grab_log_ajax.get_resp_code(),0)

        red_packet_obj = grab_log_ajax.get_resp_result()['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertLess(red_packet_obj['left_num'], num)
        self.assertNotEqual(red_packet_obj['left_num'],0)
        self.assertLess(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertNotEqual(red_packet_obj['left_gold'],0)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertEqual(red_packet_obj['count_down_time'],0)
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        red_packet_log_list = grab_log_ajax.get_resp_result()['red_packet_log_list']
        self.assertNotEqual(len(red_packet_log_list),0)

        identity_obj = grab_log_ajax.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'],get_gold)

    def test_send_supreme_100(self):
        """
        测试发放100个至尊包
        :return:
        """
        red_packet_gold = 588000
        num = 100
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

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 3, 'room_id': self.room_id, 'num': num, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['user_rank'], 3)
        self.assertEqual(identity_obj['user_experience'], 17600)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 17600)
        self.assertEqual(intimacy_obj['intimacy_rank'], 4)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 100000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'], 1)
        self.assertEqual(intimacy_level_obj['rank_end'], 15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'], int(self.user_id))
        self.assertEqual(red_packet_id['room_id'], int(self.room_id))
        self.assertEqual(red_packet_id['num'], num)
        self.assertEqual(red_packet_id['gold'], red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_id['left_num'], num)
        self.assertEqual(red_packet_id['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'], 46)
        self.assertEqual(red_packet_id['diamond'], 0)
        self.assertEqual(red_packet_id['real_diamond'], 0)
        self.assertEqual(red_packet_id['left_diamond'], 0)
        self.assertEqual(red_packet_id['fact_diamond'], 0)
        self.assertEqual(red_packet_id['red_status'], 1)
        self.assertEqual(red_packet_id['type'], 3)
        self.assertEqual(red_packet_id['status'], 1)
        self.assertEqual(red_packet_id['name'], '至尊包')
        self.assertLessEqual(red_packet_id['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']), 86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num, red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 2)
        self.assertEqual(anchor_obj['anchor_experience'], 67600)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(), 0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list), 1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'], self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id': self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(), 0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list), 1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'], self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

    def test_send_supreme_200(self):
        """
        测试发放200个至尊包
        :return:
        """
        red_packet_gold = 588000
        num = 200
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

        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=red_packet_gold)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(self.time_sleep)
        # 发红包
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 3, 'room_id': self.room_id, 'num': num, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 0)
        identity_obj = send_red_packet_api.get_resp_result()['identity_obj']
        self.assertEqual(identity_obj['gold'], 0)
        self.assertEqual(identity_obj['user_rank'], 3)
        self.assertEqual(identity_obj['user_experience'], 17600)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'], 17600)
        self.assertEqual(intimacy_obj['intimacy_rank'], 4)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 100000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'], 1)
        self.assertEqual(intimacy_level_obj['level_name'], '喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'], 1)
        self.assertEqual(intimacy_level_obj['rank_end'], 15)

        red_packet_id = send_red_packet_api.get_resp_result()['red_packet_id']
        packet_id = red_packet_id['id']
        self.assertEqual(red_packet_id['user_id'], int(self.user_id))
        self.assertEqual(red_packet_id['room_id'], int(self.room_id))
        self.assertEqual(red_packet_id['num'], num)
        self.assertEqual(red_packet_id['gold'], red_packet_gold)
        self.assertEqual(red_packet_id['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_id['left_num'], num)
        self.assertEqual(red_packet_id['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_id['red_gift_id'], 46)
        self.assertEqual(red_packet_id['diamond'], 0)
        self.assertEqual(red_packet_id['real_diamond'], 0)
        self.assertEqual(red_packet_id['left_diamond'], 0)
        self.assertEqual(red_packet_id['fact_diamond'], 0)
        self.assertEqual(red_packet_id['red_status'], 1)
        self.assertEqual(red_packet_id['type'], 3)
        self.assertEqual(red_packet_id['status'], 1)
        self.assertEqual(red_packet_id['name'], '至尊包')
        self.assertLessEqual(red_packet_id['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_id['count_down_time'])
        self.assertEqual(red_packet_id['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_id['add_date'])
        self.assertEqual(int(red_packet_id['end_time']) - int(red_packet_id['start_time']), 86400)

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
        self.assertEqual(consume_list[0]['type'], u'4')
        self.assertEqual(consume_list[0]['gold'], red_packet_gold)
        self.assertEqual(consume_list[0]['corresponding_id'], 0)
        self.assertEqual(consume_list[0]['corresponding_name'], '金币')
        self.assertEqual(consume_list[0]['corresponding_num'], 0)
        self.assertEqual(consume_list[0]['room_id'], self.room_id)
        self.assertEqual(consume_list[0]['status'], 1)
        self.assertEqual(consume_list[0]['behavior_desc'], '发红包')
        self.assertEqual(consume_list[0]['consumption_type'], '{0}金币'.format(red_packet_gold))
        self.assertIsNone(consume_list[0]['gift_obj'])
        self.assertIsNone(consume_list[0]['behavior'])

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        after_send_hot_num = live_result['room_obj']['curr_hot_num']
        self.assertEqual(after_send_hot_num - hot_num, red_packet_gold * 0.2)

        anchor_obj = live_result['room_obj']['anchor_obj']
        self.assertEqual(anchor_obj['anchor_rank'], 2)
        self.assertEqual(anchor_obj['anchor_experience'], 67600)
        time.sleep(1.5)

        get_history_ajax = GetHistoryAjax(self.user_mobile)
        get_history_ajax.get()
        self.assertEqual(get_history_ajax.get_resp_code(), 0)
        red_packet_history_list = get_history_ajax.get_resp_result()['red_packet_history_list']
        self.assertEqual(len(red_packet_history_list), 1)
        room_obj = red_packet_history_list[0]['room_obj']
        self.assertEqual(room_obj['id'], self.room_id)
        red_packet_obj = red_packet_history_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

        get_redpacket_ajax = GetRedPacketAjax(self.user_mobile)
        get_redpacket_ajax.get({'room_id': self.room_id})
        self.assertLessEqual(get_redpacket_ajax.get_resp_code(), 0)
        user_red_packet_list = get_redpacket_ajax.get_resp_result()['user_red_packet_list']
        self.assertEqual(len(user_red_packet_list), 1)
        user_obj = user_red_packet_list[0]['user_obj']
        self.assertEqual(user_obj['id'], self.user_id)
        red_packet_obj = user_red_packet_list[0]['red_packet_obj']
        self.assertEqual(red_packet_obj['id'], packet_id)
        self.assertEqual(red_packet_obj['user_id'], int(self.user_id))
        self.assertEqual(red_packet_obj['room_id'], int(self.room_id))
        self.assertEqual(red_packet_obj['num'], num)
        self.assertEqual(red_packet_obj['gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['real_gold'], red_packet_gold)
        self.assertEqual(red_packet_obj['left_num'], num)
        self.assertEqual(red_packet_obj['left_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['fact_gold'], red_packet_gold * 0.8)
        self.assertEqual(red_packet_obj['red_gift_id'], 46)
        self.assertEqual(red_packet_obj['diamond'], 0)
        self.assertEqual(red_packet_obj['real_diamond'], 0)
        self.assertEqual(red_packet_obj['left_diamond'], 0)
        self.assertEqual(red_packet_obj['fact_diamond'], 0)
        self.assertEqual(red_packet_obj['red_status'], 1)
        self.assertEqual(red_packet_obj['type'], 3)
        self.assertEqual(red_packet_obj['status'], 1)
        self.assertEqual(red_packet_obj['name'], '至尊包')
        self.assertLessEqual(red_packet_obj['count_down_time'], 60)
        self.assertLessEqual(50, red_packet_obj['count_down_time'])
        self.assertEqual(red_packet_obj['currency_type'], 1)
        self.assertIn((datetime.datetime.now()).strftime("%Y-%m-%d %H:%M"), red_packet_obj['add_date'])
        self.assertEqual(int(red_packet_obj['end_time']) - int(red_packet_obj['start_time']), 86400)

    def tearDown(self, *args):
        super(TestSendPacketAjax,self).tearDown(user_id=self.user_id,anchor_id=self.anchor_id)
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        red_packet_ids = MysqlOperation(room_id=self.room_id).get_red_packet_ids()
        MysqlOperation(room_id=self.room_id).clean_red_packet()
        MysqlOperation(user_id=self.user_id, anchor_id=self.anchor_id).clean_send_gift()
        for i in red_packet_ids:
            Redis().clean_red_packet(self.room_id, i['id'])
        RedisHold().clean_redis_room_detail(self.room_id,self.anchor_id)




class TestSendRedPacketAjaxAbnormal(BaseCase):
    """
    红包-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def test_send_red_packet_conf_id_null(self):
        """
        测试请求发红包接口红包配置ID为空
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': None, 'room_id': self.room_id, 'num': 50, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 505017)
        self.assertEqual(send_red_packet_api.get_resp_message(),'配置id不能为空')

    def test_send_red_packet_conf_id_error(self):
        """
        测试请求发红包接口红包配置ID不存在
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 111, 'room_id': self.room_id, 'num': 50, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 10112)
        self.assertEqual(send_red_packet_api.get_resp_message(),'参数异常')

    def test_send_red_packet_room_id_null(self):
        """
        测试请求发红包接口红包房间ID为空
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1, 'room_id': None, 'num': 50, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 402000)
        self.assertEqual(send_red_packet_api.get_resp_message(),'房间ID不能为空')

    def test_send_red_packet_room_id_error(self):
        """
        测试请求发红包接口红包房间ID不存在
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1, 'room_id': '909090', 'num': 50, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 100032)
        self.assertEqual(send_red_packet_api.get_resp_message(),'账户金币不足')

    def test_send_red_packet_num_null(self):
        """
        测试请求发红包接口红包数量为空
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1, 'room_id': self.room_id, 'num': None, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 505016)
        self.assertEqual(send_red_packet_api.get_resp_message(),'请选择红包份数')

    def test_send_red_packet_num_error(self):
        """
        测试请求发红包接口红包数量错误
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1, 'room_id': self.room_id, 'num': 555, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 10112)
        self.assertEqual(send_red_packet_api.get_resp_message(),'参数异常')

    def test_send_red_packet_gold_low(self):
        """
        测试请求发红包接口金币余额不足
        :return:
        """
        send_red_packet_api = SendRedPacketAjax(self.user_mobile)
        send_red_packet_api.get({'conf_id': 1, 'room_id': self.room_id, 'num': 50, 'currency': 'gold'})

        self.assertEqual(send_red_packet_api.get_resp_code(), 100032)
        self.assertEqual(send_red_packet_api.get_resp_message(),'账户金币不足')

    def test_grab_red_id_null(self):
        """
        测试请求抢红包接口红包ID为空
        :return:
        """
        grab_ajax = GrabRedPacketAjax(self.user_mobile)
        grab_ajax.get({'red_packet_id':None,'room_id':self.room_id})
        self.assertEqual(grab_ajax.get_resp_code(),505014)
        self.assertEqual(grab_ajax.get_resp_message(),'红包id不能为空')

    def test_grab_red_id_error(self):
        """
        测试请求抢红包接口红包ID不存在
        :return:
        """
        grab_ajax = GrabRedPacketAjax(self.user_mobile)
        grab_ajax.get({'red_packet_id':909090,'room_id':self.room_id})
        self.assertEqual(grab_ajax.get_resp_code(),505010)
        self.assertEqual(grab_ajax.get_resp_message(),'红包未开抢')

    def test_grab_log_red_id_null(self):
        """
        测试请求抢红包记录接口红包ID为空
        :return:
        """
        grab_log_ajax = GetGrabRedPacketLogAjax(self.user_mobile)
        grab_log_ajax.get({'red_packet_id':None})
        self.assertEqual(grab_log_ajax.get_resp_code(),505014)
        self.assertEqual(grab_log_ajax.get_resp_message(),'红包id不能为空')
