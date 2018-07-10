# -*- coding:utf-8 -*-
from base.base_case import BaseCase
from ajax.ajax_quiz import SetQuestionAjax
from utilities.mysql_helper import MysqlOperation
import settings
import json


class TestSetQuestionsAjax(BaseCase):
    """
    竞猜-添加题目到题库
    """
    anchor_mobile = settings.TEST_ANCHOR_MOBILE
    anchor_id = settings.TEST_ANCHOR_ID
    room_id = settings.TEST_ROOM
    questions = '自动化测试添加题目。'
    option_a = '选项A'
    option_b = '选项B'
    other_room = '123200'


    def test_set_questions_success(self):
        """
        测试添加题目到题库成功
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        response = set_questions_api.post({'room_id': self.room_id, 'question': self.questions,'option_a':self.option_a,'option_b':self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(),0)

        result = json.loads(response.content)['result']
        self.assertEqual(len(result),1)

        db_questions = MysqlOperation(room_id=self.room_id).get_questions()
        self.assertEqual(len(db_questions),1)
        self.assertEqual(db_questions[0]['question'],self.questions)

    # def test_set_questions_other_room(self):
    #     """
    #     测试添加题目到其他房间题库失败
    #     :return:
    #     """
    #     set_questions_api = SetQuestionAjax(self.anchor_mobile)
    #     set_questions_api.post({'room_id': self.other_room, 'question': self.questions,'option_a':self.option_a,'option_b':self.option_b})
    #     self.assertEqual(set_questions_api.get_resp_code(),505301)
    #     self.assertEqual(set_questions_api.get_resp_message(),u'权限不足')

    def test_set_questions_room_id_null(self):
        """
        测试请求接口房间ID为空
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post({'room_id': None, 'question': self.questions, 'option_a': self.option_a,
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 480001)
        self.assertEqual(set_questions_api.get_resp_message(),u'房间id不能为空')

    def test_set_questions_question_null(self):
        """
        测试请求接口问题参数为空
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post({'room_id': self.room_id, 'question': None, 'option_a': self.option_a,
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 505401)
        self.assertEqual(set_questions_api.get_resp_message(),u'问题不能为空')

    def test_set_questions_answer_a_null(self):
        """
        测试请求接口答案A为空
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post(
            {'room_id': self.room_id, 'question': self.questions, 'option_a': None,
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 505206)
        self.assertEqual(set_questions_api.get_resp_message(),u'竞猜选项不能为空')

    def test_set_questions_answer_b_null(self):
        """
        测试请求接口答案B为空
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post(
            {'room_id': self.room_id, 'question': self.questions, 'option_a': self.option_a,
             'option_b': None})
        self.assertEqual(set_questions_api.get_resp_code(), 505206)
        self.assertEqual(set_questions_api.get_resp_message(),u'竞猜选项不能为空')

    def test_set_questions_question_too_long(self):
        """
        测试问题字数超过20个字
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post(
            {'room_id': self.room_id, 'question': self.questions * 2 + '1', 'option_a': self.option_a,
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 505410)
        self.assertEqual(set_questions_api.get_resp_message(),u'输入文字超过规定长度')

    def test_set_questions_question_20(self):
        """
        测试问题字数20个字
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post(
            {'room_id': self.room_id, 'question': self.questions * 2, 'option_a': self.option_a,
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 0)

    def test_set_questions_option_too_long(self):
        """
        测试选项字数超过6个字
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post(
            {'room_id': self.room_id, 'question': self.questions, 'option_a': self.option_a * 2 + '1',
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 505410)
        self.assertEqual(set_questions_api.get_resp_message(),u'输入文字超过规定长度')

    def test_set_questions_option_6(self):
        """
        测试选项字数6个字
        :return:
        """
        set_questions_api = SetQuestionAjax(self.anchor_mobile)
        set_questions_api.post(
            {'room_id': self.room_id, 'question': self.questions, 'option_a': self.option_a * 2,
             'option_b': self.option_b})
        self.assertEqual(set_questions_api.get_resp_code(), 0)

    def test_set_questions_20(self):
        """
        测试添加20个题目到题库成功
        :return:
        """
        for x in range(20):
            set_questions_api = SetQuestionAjax(self.anchor_mobile)
            set_questions_api.post({'room_id': self.room_id, 'question': self.questions + str(x), 'option_a': self.option_a,
                 'option_b': self.option_b})
            self.assertEqual(set_questions_api.get_resp_code(), 0)

        db_questions = MysqlOperation(room_id=self.room_id).get_questions()
        self.assertEqual(len(db_questions),20)

    def tearDown(self,*args):
        super(TestSetQuestionsAjax,self).tearDown()
        for x in [self.other_room,self.room_id]:
            MysqlOperation(room_id=x).clean_questions()







#
# class TestStartQuizApi(BaseCase):
#     """
#     竞猜-开始新一局竞猜
#     """
#     anchor_mobile = settings.TEST_ANCHOR_MOBILE
#     anchor_id = settings.TEST_ANCHOR_ID
#     room_id = settings.TEST_ROOM
#     questions = '自动化测试添加题目。'
#     option_a = '选项A'
#     option_b = '选项B'
#     other_room = '123200'
#
#     def test_start_quiz_three_success(self):
#         """
#         测试选择三道题目开始竞猜成功
#         :return:
#         """
#         for x in range(3):
#             set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#             set_questions_api.get({'room_id': self.game_room, 'question': self.questions + str(x), 'option_a': self.option_a,
#                  'option_b': self.option_b})
#             self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),3)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         response = start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),0)
#         act_id = json.loads(response.content)['result']['act_id']
#         self.assertEqual(act_id,1)
#         self.assertEqual(json.loads(response.content)['result']['room_id'],self.game_room)
#
#         quiz_questions = MysqlOperation(room_id=self.game_room).get_quiz_questions()
#         self.assertEqual(len(quiz_questions),3)
#
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         response = get_questions_api.get({'room_id': self.game_room})
#         self.assertEqual(get_questions_api.get_code(),0)
#         question_list = json.loads(response.content)['result']['question_list']
#         self.assertEqual(len(question_list),3)
#
#         for x in question_list:
#             self.assertEqual(int(x['act_id']),int(act_id))
#             self.assertEqual(x['room_id'],self.game_room)
#             self.assertIn(self.questions,x['question'])
#             self.assertEqual(x['total_pool'],u'0')
#             self.assertEqual(x['init_pool'],u'0')
#             self.assertEqual(x['currency'],u'gold')
#             self.assertEqual(x['status'],u'1')
#             self.assertIsNone(x['result'])
#             self.assertEqual(x['my_result'],0)
#             self.assertIsNone(x['end_time'])
#             now_time_format = datetime.datetime.now().strftime("%Y-%m-%d")
#             self.assertIn(now_time_format,x['start_time'])
#
#             options = x['options']
#             self.assertEqual(len(options),2)
#             self.assertEqual(options['A']['content'],self.option_a)
#             self.assertEqual(options['A']['answer'],self.option_a)
#             self.assertEqual(options['A']['odds'],u'1.0')
#             self.assertEqual(options['A']['option_amount'],0)
#             self.assertEqual(options['A']['user_amount'],0)
#             self.assertEqual(options['A']['persent'],0)
#             self.assertEqual(options['B']['content'],self.option_b)
#             self.assertEqual(options['B']['answer'],self.option_b)
#             self.assertEqual(options['B']['odds'],u'1.0')
#             self.assertEqual(options['B']['option_amount'],0)
#             self.assertEqual(options['B']['user_amount'],0)
#             self.assertEqual(options['B']['persent'],0)
#
#     def test_start_quiz_two_success(self):
#         """
#         测试选择两道题目开始竞猜成功
#         :return:
#         """
#         for x in range(2):
#             set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#             set_questions_api.get({'room_id': self.game_room, 'question': self.questions + str(x), 'option_a': self.option_a,
#                  'option_b': self.option_b})
#             self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),2)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         response = start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),0)
#         act_id = json.loads(response.content)['result']['act_id']
#         self.assertEqual(act_id,1)
#         self.assertEqual(json.loads(response.content)['result']['room_id'],self.game_room)
#
#         quiz_questions = MysqlOperation(room_id=self.game_room).get_quiz_questions()
#         self.assertEqual(len(quiz_questions),2)
#
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         response = get_questions_api.get({'room_id': self.game_room})
#         self.assertEqual(get_questions_api.get_code(),0)
#         question_list = json.loads(response.content)['result']['question_list']
#         self.assertEqual(len(question_list),2)
#
#         for x in question_list:
#             self.assertEqual(int(x['act_id']),int(act_id))
#             self.assertEqual(x['room_id'],self.game_room)
#             self.assertIn(self.questions,x['question'])
#             self.assertEqual(x['total_pool'],u'0')
#             self.assertEqual(x['init_pool'],u'0')
#             self.assertEqual(x['currency'],u'gold')
#             self.assertEqual(x['status'],u'1')
#             self.assertIsNone(x['result'])
#             self.assertEqual(x['my_result'],0)
#             self.assertIsNone(x['end_time'])
#             now_time_format = datetime.datetime.now().strftime("%Y-%m-%d")
#             self.assertIn(now_time_format,x['start_time'])
#
#             options = x['options']
#             self.assertEqual(len(options),2)
#             self.assertEqual(options['A']['content'],self.option_a)
#             self.assertEqual(options['A']['answer'],self.option_a)
#             self.assertEqual(options['A']['odds'],u'1.0')
#             self.assertEqual(options['A']['option_amount'],0)
#             self.assertEqual(options['A']['user_amount'],0)
#             self.assertEqual(options['A']['persent'],0)
#             self.assertEqual(options['B']['content'],self.option_b)
#             self.assertEqual(options['B']['answer'],self.option_b)
#             self.assertEqual(options['B']['odds'],u'1.0')
#             self.assertEqual(options['B']['option_amount'],0)
#             self.assertEqual(options['B']['user_amount'],0)
#             self.assertEqual(options['B']['persent'],0)
#
#     def test_start_quiz_one_success(self):
#         """
#         测试选择一道题目开始竞猜成功
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         response = start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),0)
#         act_id = json.loads(response.content)['result']['act_id']
#         self.assertEqual(act_id,1)
#         self.assertEqual(json.loads(response.content)['result']['room_id'],self.game_room)
#
#         quiz_questions = MysqlOperation(room_id=self.game_room).get_quiz_questions()
#         self.assertEqual(len(quiz_questions),1)
#
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         response = get_questions_api.get({'room_id': self.game_room})
#         self.assertEqual(get_questions_api.get_code(),0)
#         question_list = json.loads(response.content)['result']['question_list']
#         self.assertEqual(len(question_list),1)
#
#         for x in question_list:
#             self.assertEqual(int(x['act_id']),int(act_id))
#             self.assertEqual(x['room_id'],self.game_room)
#             self.assertIn(self.questions,x['question'])
#             self.assertEqual(x['total_pool'],u'0')
#             self.assertEqual(x['init_pool'],u'0')
#             self.assertEqual(x['currency'],u'gold')
#             self.assertEqual(x['status'],u'1')
#             self.assertIsNone(x['result'])
#             self.assertEqual(x['my_result'],0)
#             self.assertIsNone(x['end_time'])
#             now_time_format = datetime.datetime.now().strftime("%Y-%m-%d")
#             self.assertIn(now_time_format,x['start_time'])
#
#             options = x['options']
#             self.assertEqual(len(options),2)
#             self.assertEqual(options['A']['content'],self.option_a)
#             self.assertEqual(options['A']['answer'],self.option_a)
#             self.assertEqual(options['A']['odds'],u'1.0')
#             self.assertEqual(options['A']['option_amount'],0)
#             self.assertEqual(options['A']['user_amount'],0)
#             self.assertEqual(options['A']['persent'],0)
#             self.assertEqual(options['B']['content'],self.option_b)
#             self.assertEqual(options['B']['answer'],self.option_b)
#             self.assertEqual(options['B']['odds'],u'1.0')
#             self.assertEqual(options['B']['option_amount'],0)
#             self.assertEqual(options['B']['user_amount'],0)
#             self.assertEqual(options['B']['persent'],0)
#
#     def test_start_quiz_four(self):
#         """
#         测试开始竞猜时最多选择三道题目
#         :return:
#         """
#         for x in range(4):
#             set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#             set_questions_api.get({'room_id': self.game_room, 'question': self.questions + str(x), 'option_a': self.option_a,
#                  'option_b': self.option_b})
#             self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),4)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),505412)
#         self.assertEqual(start_quiz_api.get_response_message(),u'问题设置不能超过三个')
#
#     def test_start_quiz_room_id_null(self):
#         """
#         测试请求接口房间ID为空
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':None,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),402000)
#         self.assertEqual(start_quiz_api.get_response_message(),u'房间ID不能为空')
#
#     def test_start_quiz_room_id_error(self):
#         """
#         测试请求接口房间ID错误
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':'123200','question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),505404)
#         self.assertEqual(start_quiz_api.get_response_message(),u'权限不足')
#
#     def test_start_quiz_questions_id_null(self):
#         """
#         测试请求接口问题ID为空
#         :return:
#         """
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':None})
#         self.assertEqual(start_quiz_api.get_code(),505401)
#         self.assertEqual(start_quiz_api.get_response_message(),u'问题不能为空')
#
#     def test_start_quiz_questions_id_error(self):
#         """
#         测试请求接口问题ID不存在
#         :return:
#         """
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':json.dumps(['999','998'])})
#         self.assertEqual(start_quiz_api.get_code(),505405)
#         self.assertEqual(start_quiz_api.get_response_message(),u'问题不存在')
#
#     def test_start_quiz_unfinished_last_time(self):
#         """
#         测试上一次精彩未结束时开始新的竞猜
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         response = start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),0)
#         act_id = json.loads(response.content)['result']['act_id']
#         self.assertEqual(act_id,1)
#         self.assertEqual(json.loads(response.content)['result']['room_id'],self.game_room)
#
#         quiz_questions = MysqlOperation(room_id=self.game_room).get_quiz_questions()
#         self.assertEqual(len(quiz_questions),1)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id': self.game_room, 'question_bank_ids': question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(), 505411)
#         self.assertEqual(start_quiz_api.get_response_message(),u'请先设置竞猜结果')
#
#     def test_get_questions_room_id_null(self):
#         """
#         测试请求获取问题列表接口房间ID为空
#         :return:
#         """
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         get_questions_api.get({'room_id':None})
#         self.assertEqual(get_questions_api.get_code(),402000)
#         self.assertEqual(get_questions_api.get_response_message(),u'房间ID不能为空')
#
#     def test_start_quiz_stop_last_not_set_answer(self):
#         """
#         测试上一局竞猜停止后未设置答案开启新的竞猜
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),0)
#
#         quiz_questions_id = MysqlOperation(room_id=self.game_room).get_quiz_questions()[0]['id']
#
#         stop_quiz_api = StopQuizApi(self.game_anchor_login_name)
#         stop_quiz_api.get({'question_id':quiz_questions_id})
#         self.assertEqual(stop_quiz_api.get_code(),0)
#
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         response = get_questions_api.get({'room_id': self.game_room})
#         self.assertEqual(get_questions_api.get_code(), 0)
#         self.assertEqual(json.loads(response.content)['result']['question_list'][0]['status'],2)
#         now_time_format = datetime.datetime.now().strftime("%Y-%m-%d")
#         self.assertIn(now_time_format, json.loads(response.content)['result']['question_list'][0]['end_time'])
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id': self.game_room, 'question_bank_ids': question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(), 505411)
#         self.assertEqual(start_quiz_api.get_response_message(),u'请先设置竞猜结果')
#
#     def test_start_quiz_stop_last_and_set_answer(self):
#         """
#         测试上一局竞猜停止后并且设置答案后开启新的竞猜
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),0)
#
#         quiz_questions_id = MysqlOperation(room_id=self.game_room).get_quiz_questions()[0]['id']
#
#         stop_quiz_api = StopQuizApi(self.game_anchor_login_name)
#         stop_quiz_api.get({'question_id':quiz_questions_id})
#         self.assertEqual(stop_quiz_api.get_code(),0)
#
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         response = get_questions_api.get({'room_id': self.game_room})
#         self.assertEqual(get_questions_api.get_code(), 0)
#
#         self.assertEqual(json.loads(response.content)['result']['question_list'][0]['status'],2)
#         now_time_format = datetime.datetime.now().strftime("%Y-%m-%d")
#         self.assertIn(now_time_format, json.loads(response.content)['result']['question_list'][0]['end_time'])
#
#         set_answer_api = SetAnswerApi(self.game_anchor_login_name)
#         response = set_answer_api.get({'question_id': quiz_questions_id,'option':'A'})
#         self.assertEqual(set_answer_api.get_code(),0)
#         question_obj = json.loads(response.content)['result']['question_obj']
#         self.assertEqual(question_obj['status'],3)
#         self.assertEqual(question_obj['result'],u'A')
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         response = start_quiz_api.get({'room_id': self.game_room, 'question_bank_ids': question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(), 0)
#         self.assertEqual(json.loads(response.content)['result']['act_id'],2)
#
#     def test_start_quiz_normal_user(self):
#         """
#         测试普通用户开启竞猜通道
#         :return:
#         """
#         set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#         set_questions_api.get({'room_id': self.game_room, 'question': self.questions, 'option_a': self.option_a,
#              'option_b': self.option_b})
#         self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),1)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.user_login_name)
#         start_quiz_api.get({'room_id':self.game_room,'question_bank_ids':question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(),505404)
#         self.assertEqual(start_quiz_api.get_response_message(),u'权限不足')
#
#     def test_start_quiz_two_questions_onr_not_set_answer(self):
#         """
#         测试选择两道题目其中一道未设置答案时开启竞猜失败
#         :return:
#         """
#         for x in range(2):
#             set_questions_api = SetQuestionsApi(self.game_anchor_login_name)
#             set_questions_api.get({'room_id': self.game_room, 'question': self.questions + str(x), 'option_a': self.option_a,
#                  'option_b': self.option_b})
#             self.assertEqual(set_questions_api.get_code(), 0)
#
#         db_questions = MysqlOperation(room_id=self.game_room).get_questions()
#         self.assertEqual(len(db_questions),2)
#         question_ids = []
#         for x in db_questions:
#             question_ids.append(x['id'])
#         question_ids_json = json.dumps(question_ids)
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id': self.game_room, 'question_bank_ids': question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(), 0)
#
#         quiz_questions_ids = MysqlOperation(room_id=self.game_room).get_quiz_questions()
#         self.assertEqual(len(quiz_questions_ids),2)
#         quiz_questions_id = quiz_questions_ids[0]['id']
#
#         stop_quiz_api = StopQuizApi(self.game_anchor_login_name)
#         stop_quiz_api.get({'question_id': quiz_questions_id})
#         self.assertEqual(stop_quiz_api.get_code(), 0)
#
#         get_questions_api = GetQuestionsApi(self.game_anchor_login_name)
#         response = get_questions_api.get({'room_id': self.game_room})
#         self.assertEqual(get_questions_api.get_code(), 0)
#
#         self.assertEqual(json.loads(response.content)['result']['question_list'][0]['status'], 2)
#         now_time_format = datetime.datetime.now().strftime("%Y-%m-%d")
#         self.assertIn(now_time_format, json.loads(response.content)['result']['question_list'][0]['end_time'])
#
#         set_answer_api = SetAnswerApi(self.game_anchor_login_name)
#         response = set_answer_api.get({'question_id': quiz_questions_id, 'option': 'A'})
#         self.assertEqual(set_answer_api.get_code(), 0)
#         question_obj = json.loads(response.content)['result']['question_obj']
#         self.assertEqual(question_obj['status'], 3)
#         self.assertEqual(question_obj['result'], u'A')
#
#         start_quiz_api = StartQuizApi(self.game_anchor_login_name)
#         start_quiz_api.get({'room_id': self.game_room, 'question_bank_ids': question_ids_json})
#         self.assertEqual(start_quiz_api.get_code(), 505411)
#         self.assertEqual(start_quiz_api.get_response_message(),u'请先设置竞猜结果')
#
#
#     def tearDown(self,*args):
#         super(TestStartQuizApi,self).tearDown()
#         mysql_operation = MysqlOperation(room_id=self.game_room)
#         quiz_question = mysql_operation.get_quiz_questions()
#         quiz_question_ids = [x['id'] for x in quiz_question]
#         mysql_operation.clean_questions()
#         Redis().clean_quiz_questions(room_id=self.game_room,question_ids=quiz_question_ids)
#         # time.sleep(0.5)