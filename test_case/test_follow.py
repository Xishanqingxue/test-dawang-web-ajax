# -*- coding:utf-8 -*-
from ajax.live_new_server import LiveNewServer
from ajax.user_follow import AddFollowAjax,RelieveFollowAjax,FollowListAjax
from base.base_case import BaseCase
import settings
import time


class TestAddFollowAjax(BaseCase):
    """
    关注/取消关注/关注列表
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID

    def setUp(self, *args):
        super(TestAddFollowAjax,self).setUp()
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})

    def test_add_follow_success(self):
        """
        测试关注主播成功
        :return:
        """
        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 获取关注前主播的粉丝数
        live_follow_num = live_result['room_obj']['anchor_obj']['follow_num']

        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)
        # 校验关注成功后亲密度
        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],1)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],10000)
        intimacy_level_obj = intimacy_obj['intimacy_level_obj']
        self.assertEqual(intimacy_level_obj['level'],1)
        self.assertEqual(intimacy_level_obj['level_name'],'喜爱')
        self.assertEqual(intimacy_level_obj['rank_start'],1)
        self.assertEqual(intimacy_level_obj['rank_end'],15)

        focus_anchor_intimacy_obj = result['focus_anchor']['intimacy_obj']
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_experience'],0)
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_rank'],1)
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_next_experience'],10000)
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_level_obj']['level'],1)
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_level_obj']['level_name'],'喜爱')
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_level_obj']['rank_start'],1)
        self.assertEqual(focus_anchor_intimacy_obj['intimacy_level_obj']['rank_end'],15)
        # 校验关注时间
        focus_time = result['focus_anchor']['focus_time']
        now_time = int(time.time())
        self.assertLessEqual(now_time - focus_time,5)
        # 关注成功后，校验主播粉丝数
        after_follow_num = result['focus_anchor']['anchor_room_obj']['anchor_obj']['follow_num']
        self.assertEqual(after_follow_num - live_follow_num,1)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()
        # 校验进入房间时关注状态为已关注
        self.assertEqual(live_result['identity_obj']['has_followed'],1)
        # 校验我的关注列表
        time.sleep(0.5)
        follow_list = FollowListAjax(self.user_mobile)
        follow_list.get()
        self.assertEqual(follow_list.get_resp_code(),0)
        follow_list_result = follow_list.get_resp_result()

        user_follow_list = follow_list_result['user_follow_list']
        self.assertEqual(len(user_follow_list),1)
        self.assertEqual(user_follow_list[0],int(self.anchor_id))

    def test_add_follow_room_id_null(self):
        """
        测试请求关注接口房间ID为空，可以关注成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': None, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)

    def test_add_follow_room_id_error(self):
        """
        测试请求关注接口房间ID不存在，可以关注成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': 909909, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)

    def test_add_follow_anchor_id_null(self):
        """
        测试请求关注接口主播ID为空，关注失败
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': None})
        self.assertEqual(add_follow.get_resp_code(),402005)
        self.assertEqual(add_follow.get_resp_message(),'主播ID不能为空')

    def test_add_follow_anchor_id_error(self):
        """
        测试请求关注接口主播ID不存在，关注失败
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': 90990909})
        self.assertEqual(add_follow.get_resp_code(),402008)
        self.assertEqual(add_follow.get_resp_message(), '主播信息不存在')

    def test_relieve_follow_success(self):
        """
        测试取消关注成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(relieve_follow.get_resp_code(),0)
        result = relieve_follow.get_resp_result()
        # 校验取消关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 0)

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)
        live_result = live_new_server_ajax.get_resp_result()

        identity_obj = live_result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],0)

        intimacy_obj = identity_obj['intimacy_obj']
        self.assertEqual(intimacy_obj['intimacy_experience'],0)
        self.assertEqual(intimacy_obj['intimacy_rank'],0)
        self.assertEqual(intimacy_obj['intimacy_next_experience'],0)
        self.assertIsNone(intimacy_obj['intimacy_level_obj'])

        # 校验我的关注列表
        follow_list = FollowListAjax(self.user_mobile)
        follow_list.get()
        self.assertEqual(follow_list.get_resp_code(),0)
        follow_list_result = follow_list.get_resp_result()

        user_follow_list = follow_list_result['user_follow_list']
        self.assertEqual(len(user_follow_list),0)

    def test_relieve_follow_room_id_null(self):
        """
        测试请求取消关注接口房间ID为空，可以成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': None, 'anchor_id': self.anchor_id})
        self.assertEqual(relieve_follow.get_resp_code(),0)

    def test_relieve_follow_room_id_error(self):
        """
        测试请求取消关注接口房间ID不存在，可以成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': 999888, 'anchor_id': self.anchor_id})
        self.assertEqual(relieve_follow.get_resp_code(), 0)

    def test_relieve_follow_anchor_id_null(self):
        """
        测试请求取消关注接口主播ID为空，可以成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(),0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'],1)

        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': None})
        self.assertEqual(relieve_follow.get_resp_code(),402005)
        self.assertEqual(relieve_follow.get_resp_message(),'主播ID不能为空')

    def test_relieve_follow_anchor_id_error(self):
        """
        测试请求取消关注接口主播ID不存在，可以成功
        :return:
        """
        add_follow = AddFollowAjax(self.user_mobile)
        add_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(add_follow.get_resp_code(), 0)
        result = add_follow.get_resp_result()
        # 校验关注成功后状态
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['has_followed'], 1)

        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': 99989898})
        self.assertEqual(relieve_follow.get_resp_code(), 402008)
        self.assertEqual(relieve_follow.get_resp_message(),'主播信息不存在')

    def test_relieve_follow_not_following(self):
        """
        测试未关注主播情况下取消关注该主播
        :return:
        """
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})
        self.assertEqual(relieve_follow.get_resp_code(), 402027)
        self.assertEqual(relieve_follow.get_resp_message(),'该主播未被关注')

    def tearDown(self, *args):
        super(TestAddFollowAjax,self).tearDown()
        relieve_follow = RelieveFollowAjax(self.user_mobile)
        relieve_follow.get({'room_id': self.room_id, 'anchor_id': self.anchor_id})