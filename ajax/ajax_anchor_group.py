# -*- coding:utf-8 -*-
from base.login_base import UserLoginBase


class OpenAnchorGroupAjax(UserLoginBase):
    """
    开通主播团
    """
    url = '/ajax/group/openGroup'