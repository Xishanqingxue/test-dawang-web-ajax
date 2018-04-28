# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class TaskListAjax(LoginBase):
    """
    任务列表
    """
    url = '/ajax/user/myTask'


class GetTaskRewardAjax(LoginBase):
    """
    领取奖励
    """
    url = '/ajax/user/getTaskAward'

    def build_custom_param(self, data):
        return {'task_behavior':data['task_behavior'],'room_id':data['room_id'],'anchor_id':data['anchor_id']}