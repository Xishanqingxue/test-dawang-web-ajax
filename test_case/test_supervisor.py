# -*- coding:utf-8 -*-
from ajax.live_supervisor import AddSupervisorAjax,DelSupervisorAjax
from utilities.mysql_helper import MysqlOperation
from base.base_case import BaseCase
import settings


class TestSupervisorAjax(BaseCase):
    """
    添加管理/取消管理
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE

    def setUp(self, user_id=None, anchor_id=None):
        super(TestSupervisorAjax,self).setUp()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})

    def test_add_supervisor_40_success(self):
        """
        测试主播设置普通管理成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'],1)

    def test_add_supervisor_60_success(self):
        """
        测试主播设置高管成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'],1)

    def test_del_supervisor_40_success(self):
        """
        测试主播取消普通管理成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'],1)

        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})
        self.assertEqual(del_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertIsNone(super_visor_details)

    def test_del_supervisor_60_success(self):
        """
        测试主播取消高管成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'],1)

        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})
        self.assertEqual(del_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertIsNone(super_visor_details)

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestSupervisorAjax,self).tearDown()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})


class TestSupervisorAjaxAbnormal(BaseCase):
    """
    添加管理/取消管理-异常
    """
    user_mobile = settings.TEST_USER_MOBILE
    room_id = settings.TEST_ROOM
    user_id = settings.TEST_USER_ID
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE

    def setUp(self, user_id=None, anchor_id=None):
        super(TestSupervisorAjaxAbnormal,self).setUp()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})

    def test_add_supervisor_room_id_null(self):
        """
        测试请求添加管理接口房间ID为空，可以成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': None, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

    def test_add_supervisor_room_id_error(self):
        """
        测试请求添加管理接口房间ID不存在，可以成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': '909090', 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

    def test_add_supervisor_anchor_id_null(self):
        """
        测试请求添加管理接口主播ID为空
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': None, 'user_id': self.user_id,'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),402005)
        self.assertEqual(add_supervisor_ajax.get_resp_message(),'主播ID不能为空')

    def test_add_supervisor_anchor_id_error(self):
        """
        测试请求添加管理接口主播ID不存在
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': '90909090', 'user_id': self.user_id,'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),801017)
        self.assertEqual(add_supervisor_ajax.get_resp_message(),'房间信息不存在')

    def test_add_supervisor_user_id_null(self):
        """
        测试请求添加管理接口用户ID为空
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': None, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 801020)
        self.assertEqual(add_supervisor_ajax.get_resp_message(), '用户id不能为空')

    def test_add_supervisor_user_id_error(self):
        """
        测试请求添加管理接口用户ID不存在
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': '90909090', 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 801027)
        self.assertEqual(add_supervisor_ajax.get_resp_message(), '用户信息不存在')

    def test_add_supervisor_type_null(self):
        """
        测试请求添加管理接口类型为空
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': None})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 411127)
        self.assertEqual(add_supervisor_ajax.get_resp_message(), '管理员类型不能为空')

    def test_add_supervisor_type_error(self):
        """
        测试请求添加管理接口类型不存在
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id, 'type': '87'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 900003)
        self.assertEqual(add_supervisor_ajax.get_resp_message(), '管理员类型异常')

    def test_del_supervisor_room_id_null(self):
        """
        测试请求取消管理接口房间ID为空,可以成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'],1)

        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': None, 'anchor_id': self.anchor_id, 'user_id': self.user_id})
        self.assertEqual(del_supervisor_ajax.get_resp_code(),0)

    def test_del_supervisor_room_id_error(self):
        """
        测试请求取消管理接口房间ID不存在,可以成功
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id,'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(),0)

        super_visor_details = MysqlOperation(user_id=self.user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'],1)

        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': '909090', 'anchor_id': self.anchor_id, 'user_id': self.user_id})
        self.assertEqual(del_supervisor_ajax.get_resp_code(),0)

    def test_del_supervisor_anchor_id_null(self):
        """
        测试请求取消管理接口主播ID为空
        :return:
        """
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': None, 'user_id': self.user_id})
        self.assertEqual(del_supervisor_ajax.get_resp_code(),402005)
        self.assertEqual(del_supervisor_ajax.get_resp_message(),'主播ID不能为空')


    def test_del_supervisor_anchor_id_error(self):
        """
        测试请求取消管理接口主播ID不存在
        :return:
        """
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': '90909090', 'user_id': self.user_id})
        self.assertEqual(del_supervisor_ajax.get_resp_code(),801017)
        self.assertEqual(del_supervisor_ajax.get_resp_message(),'房间信息不存在')

    def test_del_supervisor_user_id_null(self):
        """
        测试请求取消管理接口用户ID为空
        :return:
        """
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': None})
        self.assertEqual(del_supervisor_ajax.get_resp_code(), 801020)
        self.assertEqual(del_supervisor_ajax.get_resp_message(), '用户id不能为空')


    def test_del_supervisor_user_id_error(self):
        """
        测试请求取消管理接口用户ID不存在
        :return:
        """
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': '90909090'})
        self.assertEqual(del_supervisor_ajax.get_resp_code(), 801027)
        self.assertEqual(del_supervisor_ajax.get_resp_message(), '用户信息不存在')


    def tearDown(self, user_id=None, anchor_id=None):
        super(TestSupervisorAjaxAbnormal,self).tearDown()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.user_id})