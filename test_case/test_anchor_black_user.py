# -*- coding:utf-8 -*-
from ajax.live_black_user import AddBlackUserAjax,DelBlackUserAjax
from ajax.live_supervisor import AddSupervisorAjax,DelSupervisorAjax
from ajax.live_guard import BuyGuardAjax
from ajax.live_noble import BuyNobleAjax
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold,Redis
from ajax.live_new_server import LiveNewServer
from base.base_case import BaseCase
import settings
import time


class TestBlackUserAjaxAbnormal(BaseCase):
    """
    黑名单-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAbnormal,self).setUp()
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})


    def test_add_black_room_id_null(self):
        """
        测试请求添加黑名单接口房间ID为空，可以成功
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': None, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)

    def test_add_black_room_id_error(self):
        """
        测试请求添加黑名单接口房间ID不存在，可以成功
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': '909090', 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)

    def test_add_black_anchor_id_null(self):
        """
        测试请求添加黑名单接口主播ID为空
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': None, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),402005)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'主播ID不能为空')

    def test_add_black_anchor_id_error(self):
        """
        测试请求添加黑名单接口主播ID不存在
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': '90909090', 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801017)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'房间信息不存在')

    def test_add_black_user_id_null(self):
        """
        测试请求添加黑名单接口用户ID为空
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': None,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801020)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'用户id不能为空')

    def test_add_black_user_id_error(self):
        """
        测试请求添加黑名单接口用户ID不存在
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': '90909090','blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801027)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'用户信息不存在')

    def test_add_black_type_null(self):
        """
        测试请求添加黑名单接口类型为空
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': None})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801013)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'请求参数错误')

    def test_add_black_type_error(self):
        """
        测试请求添加黑名单接口类型不存在
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'abc'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801026)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'黑名单类型不合法')

    def test_del_black_room_id_null(self):
        """
        测试请求取消黑名单接口房间ID为空，可以成功
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': None, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(del_black_user_ajax.get_resp_code(),0)

    def test_del_black_room_id_error(self):
        """
        测试请求取消黑名单接口房间ID不存在，可以成功
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': '909090', 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(del_black_user_ajax.get_resp_code(),0)

    def test_del_black_anchor_id_null(self):
        """
        测试请求取消黑名单接口主播ID为空
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': None, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(del_black_user_ajax.get_resp_code(), 402005)
        self.assertEqual(del_black_user_ajax.get_resp_message(), '主播ID不能为空')

    def test_del_black_anchor_id_error(self):
        """
        测试请求取消黑名单接口主播ID不存在
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': '90909090', 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(del_black_user_ajax.get_resp_code(),801017)
        self.assertEqual(del_black_user_ajax.get_resp_message(),'房间信息不存在')

    def test_del_black_user_id_null(self):
        """
        测试请求取消黑名单接口用户ID为空
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': None,'blacker_type': 'forbid_speak'})
        self.assertEqual(del_black_user_ajax.get_resp_code(), 801020)
        self.assertEqual(del_black_user_ajax.get_resp_message(), '用户id不能为空')

    def test_del_black_user_id_error(self):
        """
        测试请求取消黑名单接口用户ID不存在,可以成功
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': '90909090','blacker_type': 'forbid_speak'})
        self.assertEqual(del_black_user_ajax.get_resp_code(),0)

    def test_del_black_type_null(self):
        """
        测试请求取消黑名单接口类型为空
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': None})
        self.assertEqual(del_black_user_ajax.get_resp_code(), 801026)
        self.assertEqual(del_black_user_ajax.get_resp_message(), '黑名单类型不合法')

    def test_del_black_type_error(self):
        """
        测试请求取消黑名单接口类型不存在,可以成功
        :return:
        """
        del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
        del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'abc'})
        self.assertEqual(del_black_user_ajax.get_resp_code(),0)

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAbnormal,self).tearDown()
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})







class TestBlackUserAjaxAnchorToUser(BaseCase):
    """
    黑名单(主播对普通用户)
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToUser,self).setUp()
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})

    def test_anchor_to_user_forbid_speak(self):
        """
        测试主播对普通用户禁言
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def test_anchor_to_user_forbid_shout(self):
        """
        测试主播对普通用户禁止喊话
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],1)

    def test_anchor_to_user_forbid_visit(self):
        """
        测试主播对普通用户禁止访问
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToUser,self).tearDown()
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})







class TestBlackUserAjaxAnchorToNormalAdmin(BaseCase):
    """
    黑名单(主播对普通管理)
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToNormalAdmin, self).setUp()
        for x in ['forbid_speak', 'forbid_shout', 'forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'blacker_type': x})
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})

    def test_anchor_to_admin_forbid_speak(self):
        """
        测试主播对普通管理禁言
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get(
            {'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_admin_forbid_shout(self):
        """
        测试主播对普通管理禁止喊话
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get(
            {'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_admin_forbid_visit(self):
        """
        测试主播对普通管理禁止访问
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get(
            {'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToNormalAdmin, self).tearDown()
        for x in ['forbid_speak', 'forbid_shout', 'forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'blacker_type': x})
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})







class TestBlackUserAjaxAnchorToHighAdmin(BaseCase):
    """
    黑名单(主播对高管)
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToHighAdmin, self).setUp()
        for x in ['forbid_speak', 'forbid_shout', 'forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'blacker_type': x})
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})

    def test_anchor_to_high_admin_forbid_speak(self):
        """
        测试主播对高管禁言
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get(
            {'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_high_admin_forbid_shout(self):
        """
        测试主播对高管禁止喊话
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get(
            {'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_high_admin_forbid_visit(self):
        """
        测试主播对高管禁止访问
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get(
            {'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToHighAdmin, self).tearDown()
        for x in ['forbid_speak', 'forbid_shout', 'forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'blacker_type': x})
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})








class TestBlackUserAjaxAnchorToGuard(BaseCase):
    """
    黑名单(主播对守护用户)
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToGuard,self).setUp(user_id=self.user_id,anchor_id=self.anchor_id)
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)

    def test_anchor_to_bronze_forbid_speak(self):
        """
        测试主播对青铜守护禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def test_anchor_to_bronze_forbid_shout(self):
        """
        测试主播对青铜守护禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_bronze_forbid_visit(self):
        """
        测试主播对青铜守护禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=588000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 1, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_silver_forbid_speak(self):
        """
        测试主播对白银守护禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 2)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def test_anchor_to_silver_forbid_shout(self):
        """
        测试主播对白银守护禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 2)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_silver_forbid_visit(self):
        """
        测试主播对白银守护禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1176000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 2, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 2)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_gold_forbid_speak(self):
        """
        测试主播对黄金守护禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def test_anchor_to_gold_forbid_shout(self):
        """
        测试主播对黄金守护禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_gold_forbid_visit(self):
        """
        测试主播对黄金守护禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=1764000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 3, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 3)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_diamond_forbid_speak(self):
        """
        测试主播对钻石守护禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def test_anchor_to_diamond_forbid_shout(self):
        """
        测试主播对钻石守护禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_diamond_forbid_visit(self):
        """
        测试主播对钻石守护禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=7056000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

        buy_guard_ajax = BuyGuardAjax(self.user_mobile)
        buy_guard_ajax.get({'room_id': self.room_id, 'guard_id': 12, 'currency': 'gold'})
        self.assertEqual(buy_guard_ajax.get_resp_code(), 0)
        buy_guard_result = buy_guard_ajax.get_resp_result()
        # 校验守护成功开通
        guard_list = buy_guard_result['guard_list']
        user_guard_obj = guard_list[0]['user_guard_obj']
        self.assertEqual(user_guard_obj['user_id'], self.user_id)
        self.assertEqual(user_guard_obj['guard_rank'], 4)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)


    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToGuard,self).tearDown(user_id=self.user_id,anchor_id=self.anchor_id)
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})
        MysqlOperation(user_id=self.user_id).clean_user_guard()
        Redis().clean_user_buy_guard(self.user_id, self.anchor_id)






class TestBlackUserAjaxAnchorToNoble(BaseCase):
    """
    黑名单(主播对贵族用户)
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToNoble,self).setUp(user_id=self.user_id)
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)

    def test_anchor_to_knight_forbid_speak(self):
        """
        测试主播对骑士禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=24000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_knight_forbid_shout(self):
        """
        测试主播对骑士禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=24000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_knight_forbid_visit(self):
        """
        测试主播对骑士禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=24000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 1,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_baron_forbid_speak(self):
        """
        测试主播对男爵禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=40000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 2,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 2)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_baron_forbid_shout(self):
        """
        测试主播对男爵禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=40000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 2,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 2)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_baron_forbid_visit(self):
        """
        测试主播对男爵禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=40000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 2,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 2)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_viscount_forbid_speak(self):
        """
        测试主播对子爵禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=80000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 3,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 3)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_viscount_forbid_shout(self):
        """
        测试主播对子爵禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=80000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 3,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 3)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_viscount_forbid_visit(self):
        """
        测试主播对子爵禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=80000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 3,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 3)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_earl_forbid_speak(self):
        """
        测试主播对伯爵禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=400000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 4,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 4)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_earl_forbid_shout(self):
        """
        测试主播对伯爵禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=400000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 4,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 4)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_earl_forbid_visit(self):
        """
        测试主播对伯爵禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=400000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 4,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 4)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_marquis_forbid_speak(self):
        """
        测试主播对侯爵禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=800000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 5,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 5)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_marquis_forbid_shout(self):
        """
        测试主播对侯爵禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=800000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 5,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 5)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 1)

    def test_anchor_to_marquis_forbid_visit(self):
        """
        测试主播对侯爵禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=800000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 5,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 5)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_duck_forbid_speak(self):
        """
        测试主播对公爵禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=2400000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 6,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 6)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.user_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'], 'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.user_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'], 0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'], 1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'], 0)

    def test_anchor_to_duck_forbid_shout(self):
        """
        测试主播无法对公爵禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=2400000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 6,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 6)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 411151)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不足，禁止喊话失败')

    def test_anchor_to_duck_forbid_visit(self):
        """
        测试主播无法对公爵禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=2400000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 6,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 6)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 411152)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不足，踢出房间失败')

    def test_anchor_to_emperor_forbid_speak(self):
        """
        测试主播对帝王禁言
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=24000000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 7,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 7)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 411150)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不足，禁言失败')


    def test_anchor_to_emperor_forbid_shout(self):
        """
        测试主播对帝王禁止喊话
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=24000000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 7,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 7)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 411151)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不足，禁止喊话失败')

    def test_anchor_to_emperor_forbid_visit(self):
        """
        测试主播对帝王禁止访问
        :return:
        """
        # 用户加钱
        mysql_operation = MysqlOperation(user_id=self.user_id)
        mysql_operation.fix_user_account(gold_num=24000000)
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)
        # 购买贵族
        buy_noble_ajax = BuyNobleAjax(self.user_mobile)
        buy_noble_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'noble_id': 7,
                            'num': 1, 'currency': 'gold'})
        self.assertEqual(buy_noble_ajax.get_resp_code(), 0)

        result = buy_noble_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        # 校验贵族等级
        self.assertEqual(identity_obj['noble_rank'], 7)

        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,
                                 'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(), 411152)
        self.assertEqual(add_black_user_ajax.get_resp_message(), '权限不足，踢出房间失败')


    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToNoble,self).tearDown(user_id=self.user_id)
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'blacker_type': x})
        MysqlOperation(user_id=self.user_id).clean_user_noble()
        RedisHold().clean_redis_user_detail(self.user_id)
        time.sleep(0.3)







class TestBlackUserAjaxAnchorToAnchor(BaseCase):
    """
    黑名单(主播对主播)
    """
    room_id = settings.TEST_ROOM
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    other_anchor_mobile = '15710607010'
    other_anchor_id = '20059012'
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToAnchor,self).setUp()
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_anchor_id,'blacker_type': x})

    def test_anchor_to_user_forbid_speak(self):
        """
        测试主播对普通用户禁言
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_anchor_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.other_anchor_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_speak')

        live_new_server_ajax = LiveNewServer(self.other_anchor_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def test_anchor_to_user_forbid_shout(self):
        """
        测试主播对普通用户禁止喊话
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_anchor_id,'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.other_anchor_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_shout')

        live_new_server_ajax = LiveNewServer(self.other_anchor_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],1)

    def test_anchor_to_user_forbid_visit(self):
        """
        测试主播对普通用户禁止访问
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.anchor_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_anchor_id,'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),0)
        time.sleep(self.time_sleep)
        black_user_detail = MysqlOperation(user_id=self.other_anchor_id).get_black_user_details()
        self.assertEqual(black_user_detail['type'],'forbid_visit')

        live_new_server_ajax = LiveNewServer(self.other_anchor_mobile)
        live_new_server_ajax.get({'room_id': self.room_id})
        self.assertEqual(live_new_server_ajax.get_resp_code(), 0)

        result = live_new_server_ajax.get_resp_result()
        identity_obj = result['identity_obj']
        self.assertEqual(identity_obj['blacker_type']['forbid_visit'],1)
        self.assertEqual(identity_obj['blacker_type']['forbid_speak'],0)
        self.assertEqual(identity_obj['blacker_type']['forbid_shout'],0)

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxAnchorToAnchor,self).tearDown()
        for x in ['forbid_speak','forbid_shout','forbid_visit']:
            del_black_user_ajax = DelBlackUserAjax(self.anchor_mobile)
            del_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_anchor_id,'blacker_type': x})





