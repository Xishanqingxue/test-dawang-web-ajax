# -*- coding:utf-8 -*-
from base.login_base import LoginBase


class GetHistoryAjax(LoginBase):
    """
    红包发放历史
    """
    url = '/ajax/redpacket/gethistorynew'


class SendRedPacketAjax(LoginBase):
    """
    发红包
    """
    url = '/ajax/redpacket/sendRedPacketNew'

    def build_custom_param(self, data):
        return {'conf_id':data['conf_id'],'room_id':data['room_id'],'num':data['num'],'currency':data['currency']}


class GetRedPacketAjax(LoginBase):
    """
    可抢红包列表
    """
    url = '/ajax/redpacket/getredpacketnew'

    def build_custom_param(self, data):
        return {'room_id':data['room_id']}


class GrabRedPacketAjax(LoginBase):
    """
    抢红包
    """
    url = '/ajax/redpacket/grabRedPacketNew'

    def build_custom_param(self, data):
        return {'red_packet_id':data['red_packet_id'],'room_id':data['room_id']}


class GetGrabRedPacketLogAjax(LoginBase):
    """
    获取抢红包列表
    """
    url = '/ajax/redpacket/getredpacketlognew'

    def build_custom_param(self, data):
        return {'red_packet_id':data['red_packet_id']}