# -*- coding:utf-8 -*-
from base.login_base import UserLoginBase


class OpenAnchorGroupAjax(UserLoginBase):
    """
    开通主播团
    """
    url = '/ajax/group/openGroup'


class AddAnchorToGroup(UserLoginBase):
    """
    将主播纳入主播团
    """

    url = '/ajax/group/addanchortogroup'

    def build_custom_param(self, data):
        return {'position': data['position'], 'anchor_id': data['anchor_id'], 'grab_flag': data['grab_flag'],
                'change_flag': data['change_flag']}
