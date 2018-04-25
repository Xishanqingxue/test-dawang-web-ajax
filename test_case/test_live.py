# -*- coding:utf-8 -*-
from ajax.live_new_server import LiveNewServer
from base.base_case import BaseCase
from utilities.mysql_helper import MysqlOperation
import settings
import requests


class TestLiveNewServerAjax(BaseCase):
    """
    获取直播间信息
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def test_get_live_ajax_success(self):
        """
        测试获取直播间信息成功
        :return:
        """
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        result = live_new_server_ajax.get_resp_result()

        self.assertEqual(result['game_enter_config'], [])
        self.assertEqual(result['lucky_slot_config'], [])
        self.assertEqual(result['callback'], '')
        self.assertEqual(result['is_show_ourgame'], 0)
        self.assertFalse(result['anchor_in_any_group'])
        self.assertEqual(result['rename_cost_gold'], 20000)
        self.assertEqual(result['channel_id'], u'0')
        self.assertEqual(result['ratio'], u'10')
        self.assertEqual(result['show_guess'], 1)

        enter_room_message = result['enter_room_message']
        self.assertEqual(enter_room_message['act'], u'send_group_message')
        self.assertEqual(enter_room_message['uid'], self.user_id)
        self.assertEqual(enter_room_message['room_id'], self.room_id)
        self.assertIsNone(enter_room_message['to_uid'])
        self.assertIsNone(enter_room_message['expire_time'])
        msg = enter_room_message['msg']
        self.assertEqual(msg['m_action'], u'system_room')
        self.assertEqual(msg['m_switch'], u'coming')
        self.assertEqual(msg['from_user_id'], u'0')
        self.assertEqual(msg['from_refer_type'], u'2')
        user_obj = msg['user_obj']
        self.assertEqual(user_obj['id'], self.user_id)
        self.assertEqual(user_obj['nickname'], MysqlOperation(user_id=self.user_id).get_user_details()['nickname'])
        self.assertEqual(user_obj['noble_rank'], 0)
        self.assertEqual(user_obj['user_rank'], 1)
        self.assertEqual(user_obj['anchor_rank'], 0)
        self.assertEqual(user_obj['intimacy_rank'], 0)
        self.assertIsNone(user_obj['intimacy_level'])
        self.assertEqual(user_obj['guard_rank'], 0)
        self.assertEqual(user_obj['user_type'], 1)
        self.assertEqual(user_obj['is_anchor'], 0)
        small_head_url = '/images/heads/55/ce/20180425150305863.png'
        self.assertEqual(user_obj['small_head_url'], small_head_url)
        resp = requests.get(url=settings.PIC_TEST_BASE_URL + small_head_url)
        self.assertEqual(resp.status_code,200)
        obj = msg['obj']
        self.assertEqual(obj['msg_content'], u'来了')
        self.assertIsNone(obj['ani_obj'])

        room_obj = result['room_obj']
        self.assertEqual(room_obj['id'],self.room_id)
        self.assertEqual(room_obj['room_type'],1)
        self.assertEqual(room_obj['room_style'],2)
        self.assertEqual(room_obj['room_style_extend'],0)
        max_img_path = room_obj['max_img_path']
        self.assertIsNotNone(max_img_path)
        min_img_path = room_obj['min_img_path']
        self.assertIsNotNone(min_img_path)
        self.assertEqual(room_obj['room_status'],0)
        self.assertIsNone(room_obj['play_url'])
        room_details = MysqlOperation(room_id=self.room_id).get_room_details()
        self.assertEqual(room_obj['introduce'], room_details['introduce'])
        self.assertEqual(room_obj['notice'], room_details['notice'])
        self.assertEqual(room_obj['title'], room_details['title'])
        self.assertEqual(room_obj['curr_online_num'],0)
        self.assertIsNotNone(room_obj['curr_hot_num'])
        self.assertEqual(room_obj['sun_num'],0)
        self.assertEqual(room_obj['screen_mode'],0)
        self.assertEqual(room_obj['orientation'],0)
        self.assertEqual(room_obj['publish_tool'],0)
        self.assertEqual(room_obj['bg_pic_small'],'')
        self.assertEqual(room_obj['column_id'],103002)
        self.assertEqual(room_obj['status'], 1)
        self.assertEqual(room_obj['room_daily_sign_num'], 0)
        user_guard_url = u'/live/user/123176.html#3'
        self.assertEqual(room_obj['user_guard_url'], user_guard_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + user_guard_url)
        self.assertEqual(resp.status_code, 200)

        user_vip_url = u'/live/user/123176.html#1'
        self.assertEqual(room_obj['user_vip_url'], user_vip_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + user_vip_url)
        self.assertEqual(resp.status_code, 200)

        user_contribution_url = u'/live/contribution/123176.html'
        self.assertEqual(room_obj['user_contribution_url'], user_contribution_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + user_contribution_url)
        self.assertEqual(resp.status_code, 200)

        new_user_guard_url = u'/h5live/user/room_id/123176#3'
        self.assertEqual(room_obj['new_user_guard_url'], new_user_guard_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + new_user_guard_url)
        self.assertEqual(resp.status_code, 200)

        new_user_vip_url = u'/h5live/user/room_id/123176#1'
        self.assertEqual(room_obj['new_user_vip_url'], new_user_vip_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + new_user_vip_url)
        self.assertEqual(resp.status_code, 200)

        new_user_contribution_url = u'/h5live/contribution/room_id/123176'
        self.assertEqual(room_obj['new_user_contribution_url'], new_user_contribution_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + new_user_contribution_url)
        self.assertEqual(resp.status_code, 200)

        helper_live_url = u'/h5live/helperlist/room_id/123176#1'
        self.assertEqual(room_obj['helper_live_url'], helper_live_url)
        resp = requests.get(url=settings.AJAX_TEST_BASE_URL + helper_live_url)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(room_obj['is_week_star'], 0)
        self.assertEqual(room_obj['best_type'], 0)
        app_bg_pic_squre = '/images/zb/9e/99/20170323035017960.jpeg'
        self.assertEqual(room_obj['app_bg_pic_squre'], app_bg_pic_squre)
        resp = requests.get(url=settings.PIC_TEST_BASE_URL + app_bg_pic_squre)
        self.assertEqual(resp.status_code, 200)

        app_bg_pic_big = '/images/zb/0f/c0/20170420150411181.jpeg'
        self.assertEqual(room_obj['app_bg_pic_big'], app_bg_pic_big)
        resp = requests.get(url=settings.PIC_TEST_BASE_URL + app_bg_pic_big)
        self.assertEqual(resp.status_code, 200)

        app_home_pic_big = '/images/zb/78/31/20170323035028346.jpeg'
        self.assertEqual(room_obj['app_home_pic_big'], app_home_pic_big)
        resp = requests.get(url=settings.PIC_TEST_BASE_URL + app_home_pic_big)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(room_obj['is_activity_room'], 0)
        self.assertEqual(room_obj['push_stream_channel_id'], 3)
        self.assertEqual(room_obj['is_live_transcoded'], 0)
        self.assertEqual(room_obj['mobile_push_stream_channel_id'], 7)
        self.assertEqual(room_obj['is_mobile_live_transcoded'], 0)
        self.assertEqual(room_obj['mobile_push_stream_bitrate'], 1000)
        self.assertEqual(room_obj['socket_domain'], u'chat.t.dwtv.tv')
        self.assertEqual(room_obj['socket_port'], u'80')
        self.assertIsNone(room_obj['link_mic'])
        self.assertIsNone(room_obj['room_live_tags'])
        intimacy_config = room_obj['intimacy_config']
        self.assertEqual(len(intimacy_config),3)
        self.assertEqual(intimacy_config[0]['level'],1)
        self.assertEqual(intimacy_config[0]['level_name'],u'喜爱')
        self.assertEqual(intimacy_config[0]['rank_start'],1)
        self.assertEqual(intimacy_config[0]['rank_end'],15)
        self.assertEqual(intimacy_config[1]['level'], 2)
        self.assertEqual(intimacy_config[1]['level_name'], u'真爱')
        self.assertEqual(intimacy_config[1]['rank_start'], 16)
        self.assertEqual(intimacy_config[1]['rank_end'], 30)
        self.assertEqual(intimacy_config[2]['level'], 3)
        self.assertEqual(intimacy_config[2]['level_name'], u'独爱')
        self.assertEqual(intimacy_config[2]['rank_start'], 31)
        self.assertEqual(intimacy_config[2]['rank_end'], 50)
        welcome_tip = room_obj['welcome_tip']
        self.assertEqual(welcome_tip['id'],1)
        self.assertIsNotNone(welcome_tip['tip'])
        self.assertIsNotNone(welcome_tip['link_url'])

        anchor_obj = room_obj['anchor_obj']
        self.assertEqual(anchor_obj['id'],self.anchor_id)
        self.assertEqual(anchor_obj['nickname'],MysqlOperation(user_id=self.anchor_id).get_user_details()['nickname'])
        small_head_url = '/images/heads/67/4b/20160726115433397.jpg'
        self.assertEqual(anchor_obj['small_head_url'],small_head_url)
        resp = requests.get(url=settings.PIC_TEST_BASE_URL + small_head_url)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(anchor_obj['user_rank'],1)
        self.assertEqual(anchor_obj['user_experience'], 0)
        self.assertEqual(anchor_obj['user_experience_all'], 0)
        self.assertEqual(anchor_obj['current_rank_user_need_total_experience'], 50000)
        self.assertEqual(anchor_obj['anchor_rank'], 1)
        self.assertEqual(anchor_obj['anchor_experience'], 0)
        self.assertEqual(anchor_obj['anchor_experience_all'], 0)
        self.assertEqual(anchor_obj['current_rank_anchor_need_total_experience'], 50000)
        self.assertEqual(anchor_obj['is_anchor'], 1)
        self.assertEqual(anchor_obj['sun_resumed_time'], 180)
        self.assertEqual(anchor_obj['sun_max_num'], 50)
        self.assertEqual(anchor_obj['follow_num'], 6667)
        self.assertEqual(anchor_obj['user_type'], 1)
        self.assertEqual(anchor_obj['guard_top_num'], 12)
        self.assertIsNone(anchor_obj['blacker_type'])
        self.assertEqual(anchor_obj['has_followed'], 0)
        self.assertEqual(anchor_obj['today_is_sign'], 0)
        self.assertEqual(anchor_obj['noble_rank'], 0)
        self.assertEqual(anchor_obj['noble_expiretime'], '')
        self.assertEqual(anchor_obj['noble_rest_time_int'], 0)
        self.assertEqual(anchor_obj['noble_rest_time_str'], '')
        self.assertEqual(anchor_obj['play_area'], -1)
        self.assertEqual(anchor_obj['play_area_name'], u'其他')
        self.assertEqual(anchor_obj['anchor_weight'], 1)
        self.assertEqual(anchor_obj['channel_id'], 10000001)
        self.assertEqual(anchor_obj['sns_id'], 0)
        self.assertEqual(anchor_obj['sns_from'], 0)
        self.assertEqual(anchor_obj['status'], 1)
        self.assertEqual(anchor_obj['left_rename_num'], 1)
        self.assertEqual(anchor_obj['has_plat_signin'], 0)
        self.assertEqual(anchor_obj['plat_signin_days'], 0)
        user_guard_obj = anchor_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'],'')
        self.assertEqual(user_guard_obj['expire_time'],'')
        self.assertEqual(user_guard_obj['guard_rank'],0)
        intimacy_obj = anchor_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])

        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['id'],self.user_id)
        self.assertEqual(identity_obj['nickname'],MysqlOperation(user_id=self.user_id).get_user_details()['nickname'])
        self.assertEqual(identity_obj['introduction'],'')
        self.assertEqual(identity_obj['email'],'')
        self.assertEqual(identity_obj['login_name'],self.user_mobile)
        small_head_url = '/images/heads/55/ce/20180425150305863.png'
        self.assertEqual(identity_obj['small_head_url'],small_head_url)
        resp = requests.get(url=settings.PIC_TEST_BASE_URL + small_head_url)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(identity_obj['mobilephone'],self.user_mobile)
        self.assertEqual(identity_obj['gold'],0)
        self.assertEqual(identity_obj['diamond'],u'0')
        self.assertEqual(identity_obj['ticket'],0)
        self.assertEqual(identity_obj['user_rank'],1)
        self.assertEqual(identity_obj['user_experience'],0)
        self.assertEqual(identity_obj['current_rank_user_need_total_experience'],50000)
        self.assertEqual(identity_obj['anchor_rank'],0)
        self.assertEqual(identity_obj['anchor_experience'],0)
        self.assertEqual(identity_obj['current_rank_anchor_need_total_experience'],1)
        self.assertEqual(identity_obj['sun_num'],5)
        self.assertEqual(identity_obj['follow_num'],0)
        self.assertIsNone(identity_obj['user_signin_obj'])
        self.assertEqual(identity_obj['user_type'],1)
        self.assertIsNotNone(identity_obj['identity'])
        self.assertIsNotNone(identity_obj['user_sign'])
        self.assertEqual(identity_obj['guard_top_num'],0)
        self.assertEqual(identity_obj['has_followed'],0)
        self.assertEqual(identity_obj['sun_resumed_time'],180)
        self.assertEqual(identity_obj['sun_max_num'],50)
        self.assertEqual(identity_obj['chat_resumed_time'],1)
        self.assertEqual(identity_obj['shout_resumed_time'],5)
        self.assertEqual(identity_obj['today_is_sign'],0)
        self.assertEqual(identity_obj['signin_date'],'')
        self.assertEqual(identity_obj['signin_max_num'],0)
        self.assertEqual(identity_obj['noble_rank'],0)
        self.assertEqual(identity_obj['noble_expiretime'],'')
        self.assertEqual(identity_obj['noble_rest_time_int'],0)
        self.assertEqual(identity_obj['noble_rest_time_str'],'')
        self.assertEqual(identity_obj['if_receive_push'],1)
        self.assertEqual(identity_obj['play_area'],-1)
        self.assertEqual(identity_obj['user_package'],[])
        self.assertEqual(identity_obj['is_anchor'],0)
        self.assertEqual(identity_obj['kz_id'],'')
        self.assertEqual(identity_obj['left_rename_num'],1)
        self.assertEqual(identity_obj['sns_id'],0)
        self.assertEqual(identity_obj['sns_from'],0)
        self.assertIsNotNone(identity_obj['token_client'])
        self.assertEqual(identity_obj['status'],1)
        self.assertEqual(identity_obj['has_plat_signin'],0)
        self.assertEqual(identity_obj['plat_signin_days'],0)
        blacker_type = identity_obj['blacker_type']
        self.assertEqual(blacker_type['forbid_speak'],0)
        self.assertEqual(blacker_type['forbid_visit'], 0)
        self.assertEqual(blacker_type['forbid_shout'], 0)
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'], 0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'], 0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])
        user_guard_obj = identity_obj['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'],'')
        self.assertEqual(user_guard_obj['expire_time'], '')
        self.assertEqual(user_guard_obj['guard_rank'], 0)

    def test_get_live_ajax_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': None})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 402000)
        self.assertEqual(live_new_server_ajax.get_resp_message(),u'房间ID不能为空')

    def test_get_live_ajax_room_id_error(self):
        """
        测试请求接口房间ID不存在
        :return:
        """
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': 991299})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 200417)
        self.assertEqual(live_new_server_ajax.get_resp_message(),u'房间已被禁播')









