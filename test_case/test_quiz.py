# # -*- coding:utf-8 -*-
# from base.base_case import BaseCase
# from ajax.ajax_quiz import SetQuestionAjax
# from utilities.mysql_helper import MysqlOperation
# import settings
# import json
#
#
# class TestSetQuestionsAjax(BaseCase):
#     """
#     竞猜-添加题目到题库
#     """
#     anchor_mobile = settings.TEST_ANCHOR_MOBILE
#     anchor_id = settings.TEST_ANCHOR_ID
#     room_id = settings.TEST_ROOM
#     questions = u'自动化测试添加题目。'
#     option_a = u'选项A'
#     option_b = u'选项B'
#     other_room = '123200'
#
#
#     def test_set_questions_success(self):
#         """
#         测试添加题目到题库成功
#         :return:
#         """
#         set_questions_api = SetQuestionAjax(self.anchor_mobile)
#         response = set_questions_api.get({'room_id': self.room_id, 'question': self.questions,'option_a':self.option_a,'option_b':self.option_b})
#         self.assertEqual(set_questions_api.get_resp_code(),0)
#
#         result = json.loads(response.content)['result']
#         self.assertEqual(len(result),1)
#
#         db_questions = MysqlOperation(room_id=self.room_id).get_questions()
#         self.assertEqual(len(db_questions),1)
#         self.assertEqual(db_questions[0]['question'],self.questions)
#
#     def test_set_questions_other_room(self):
#         """
#         测试添加题目到其他房间题库失败
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.other_room, 'question': self.questions,'option_a':self.option_a,'option_b':self.option_b})
#         self.assertEqual(set_questions_api.get_code(),505404)
#         self.assertEqual(set_questions_api.get_response_message(),u'权限不足')
#
#     def test_set_questions_room_id_null(self):
#         """
#         测试请求接口房间ID为空
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': None, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 402000)
#         self.assertEqual(set_questions_api.get_response_message(),u'房间ID不能为空')
#
#     def test_set_questions_question_null(self):
#         """
#         测试请求接口问题参数为空
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': None, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 505401)
#         self.assertEqual(set_questions_api.get_response_message(),u'问题不能为空')
#
#     def test_set_questions_answer_a_null(self):
#         """
#         测试请求接口答案A为空
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': self.questions, 'option_a': None,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 505402)
#         self.assertEqual(set_questions_api.get_response_message(),u'答案不能为空')
#
#     def test_set_questions_answer_b_null(self):
#         """
#         测试请求接口答案B为空
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': None})
#         self.assertEqual(set_questions_api.get_code(), 505402)
#         self.assertEqual(set_questions_api.get_response_message(),u'答案不能为空')
#
#     def test_set_questions_question_too_long(self):
#         """
#         测试问题字数超过20个字
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': self.questions * 2 + '1', 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 505410)
#         self.assertEqual(set_questions_api.get_response_message(),u'输入文字超过规定长度')
#
#     def test_set_questions_question_20(self):
#         """
#         测试问题字数20个字
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': self.questions * 2, 'option_a': self.option_a,
#              'option_b': self.option_b},identity_in_cookies=True)
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#     def test_set_questions_option_too_long(self):
#         """
#         测试选项字数超过6个字
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a * 2 + '1',
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 505410)
#         self.assertEqual(set_questions_api.get_response_message(),u'输入文字超过规定长度')
#
#     def test_set_questions_option_6(self):
#         """
#         测试选项字数6个字
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get(
#             {'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a * 2,
#              'option_b': self.option_b},identity_in_cookies=True)
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#     def test_set_questions_20(self):
#         """
#         测试添加20个题目到题库成功
#         :return:
#         """
#         for x in range(20):
#             set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#             set_questions_api.get({'room_id': self.game_room, 'question': self.questions + str(x), 'option_a': self.option_a,
#                  'option_b': self.option_b},identity_in_cookies=True)
#             self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),20)
#
#     def tearDown(self,*args):
#         super(TestSetQuestionsAjax,self).tearDown()
#         for x in [self.other_room,self.room_id]:
#             MysqlOperation(room_id=x).clean_questions()
#
