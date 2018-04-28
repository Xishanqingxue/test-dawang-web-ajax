# -*- coding:utf-8 -*-
from ajax.live_black_user import AddBlackUserAjax
from ajax.live_supervisor import AddSupervisorAjax,DelSupervisorAjax
from utilities.mysql_helper import MysqlOperation
from base.base_case import BaseCase
import settings


class TestBlackUserAjaxUserToNorAdmin(BaseCase):
    """
    黑名单(普通用户对普管)
    """
    admin_user_mobile = settings.TEST_USER_MOBILE
    admin_user_id = settings.TEST_USER_ID
    room_id = settings.TEST_ROOM
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    user_mobile = '13309090909'
    user_id = '22017468'
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxUserToNorAdmin,self).setUp()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id})

    def test_user_to_normal_admin_forbid_speak(self):
        """
        测试普通用户无法对普管禁言
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.admin_user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_normal_admin_forbid_shout(self):
        """
        测试普通用户无法对普管禁止喊话
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.admin_user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id,'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_normal_admin_forbid_visit(self):
        """
        测试普通用户无法对普管禁止访问
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id, 'type': '40'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.admin_user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_normal_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id,'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxUserToNorAdmin,self).tearDown()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id})








class TestBlackUserAjaxUserToHighAdmin(BaseCase):
    """
    黑名单(普通用户对高管)
    """
    admin_user_mobile = settings.TEST_USER_MOBILE
    admin_user_id = settings.TEST_USER_ID
    room_id = settings.TEST_ROOM
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    user_mobile = '13309090909'
    user_id = '22017468'
    time_sleep = 1

    def setUp(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxUserToHighAdmin,self).setUp()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id})

    def test_user_to_high_admin_forbid_speak(self):
        """
        测试普通用户无法对高管禁言
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id, 'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.admin_user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_high_admin_forbid_shout(self):
        """
        测试普通用户无法对高管禁止喊话
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id, 'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.admin_user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id,'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_high_admin_forbid_visit(self):
        """
        测试普通用户无法对高管禁止访问
        :return:
        """
        add_supervisor_ajax = AddSupervisorAjax(self.anchor_mobile)
        add_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id, 'type': '60'})
        self.assertEqual(add_supervisor_ajax.get_resp_code(), 0)

        super_visor_details = MysqlOperation(user_id=self.admin_user_id).get_anchor_room_supervisor_details()
        self.assertEqual(super_visor_details['is_advance_admin'], 1)

        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id,'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def tearDown(self, user_id=None, anchor_id=None):
        super(TestBlackUserAjaxUserToHighAdmin,self).tearDown()
        del_supervisor_ajax = DelSupervisorAjax(self.anchor_mobile)
        del_supervisor_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.admin_user_id})






class TestBlackUserAjaxUserToAnchor(BaseCase):
    """
    黑名单(普通用户对主播)
    """
    user_mobile = settings.TEST_USER_MOBILE
    user_id = settings.TEST_USER_ID
    room_id = settings.TEST_ROOM
    anchor_id = settings.TEST_ANCHOR_ID
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    time_sleep = 1


    def test_user_to_anchor_forbid_speak(self):
        """
        测试普通用户无法对主播禁言
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.anchor_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_anchor_forbid_shout(self):
        """
        测试普通用户无法对主播禁止喊话
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.anchor_id,'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_anchor_forbid_visit(self):
        """
        测试普通用户无法对主播禁止访问
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.anchor_id,'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')







class TestBlackUserAjaxUserToUser(BaseCase):
    """
    黑名单(普通用户对普通用户)
    """
    user_mobile = settings.TEST_USER_MOBILE
    user_id = settings.TEST_USER_ID
    room_id = settings.TEST_ROOM
    anchor_id = settings.TEST_ANCHOR_ID
    other_user_mobile = '13309090909'
    other_user_id = '22017468'
    time_sleep = 1


    def test_user_to_user_forbid_speak(self):
        """
        测试普通用户无法对普通用户禁言
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_user_id,'blacker_type': 'forbid_speak'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_user_forbid_shout(self):
        """
        测试普通用户无法对普通用户禁止喊话
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_user_id,'blacker_type': 'forbid_shout'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')

    def test_user_to_user_forbid_visit(self):
        """
        测试普通用户无法对普通用户禁止访问
        :return:
        """
        add_black_user_ajax = AddBlackUserAjax(self.user_mobile)
        add_black_user_ajax.get({'room_id': self.room_id, 'anchor_id': self.anchor_id, 'user_id': self.other_user_id,'blacker_type': 'forbid_visit'})
        self.assertEqual(add_black_user_ajax.get_resp_code(),801018)
        self.assertEqual(add_black_user_ajax.get_resp_message(),'权限不够')









