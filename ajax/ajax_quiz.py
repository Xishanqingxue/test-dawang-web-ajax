# -*- coding:utf-8 -*-
from base.login_base import H5LoginBase
from base.login_base import LoginBase


class GetQuestionAjax(H5LoginBase):
    """
    获取竞猜列表
    """
    url = '/ajax/jc/getQuestion'

    def build_custom_param(self, data):
        return {'room_id': data['room_id']}


class SetQuestionAjax(LoginBase):
    """
    创建题目
    """
    url = '/ajax/jc/setQuestions'

    def build_custom_param(self, data):
        return {'question': data['question'], 'option_a': data['option_a'], 'option_b': data['option_b'],
                'room_id': data['room_id']}


class DelQuestionAjax(LoginBase):
    """
    删除题目
    """
    url = '/ajax/jc/delQuestions'

    def build_custom_param(self, data):
        return {'question_bank_ids':data['question_bank_ids'],'room_id':data['room_id']}


class StartQuizAjax(LoginBase):
    """
    开始竞猜
    """
    url = '/ajax/jc/startQuiz'

    def build_custom_param(self, data):
        return {'question_bank_ids':data['question_bank_ids'],'room_id':data['room_id']}


class StopQuizAjax(LoginBase):
    """
    停止竞猜
    """
    url = '/ajax/jc/stopquiz'

    def build_custom_param(self, data):
        return {'question_id':data['question_id']}


class SetAnswerAjax(LoginBase):
    """
    设置答案
    """
    url = '/ajax/jc/setAnswer'

    def build_custom_param(self, data):
        return {'question_id':data['question_id'],'option':data['option']}


