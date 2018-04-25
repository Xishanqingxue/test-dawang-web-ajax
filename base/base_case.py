# -*- coding:utf-8 -*-
from unittest import TestCase
from base.base_log import BaseLogger
from utilities.mysql_helper import MysqlOperation
from utilities.redis_helper import RedisHold

logging = BaseLogger(__name__).get_logger()


class BaseCase(TestCase):

    def init_user_and_room(self, user_id, anchor_id):
        """
        初始化用户信息或房间信息
        :param user_id:
        :param room_id:
        :return:
        """
        if user_id:
            logging.info('正在初始化用户信息...')
            if isinstance(user_id, (str, int)):
                MysqlOperation(user_id=user_id).fix_user_account().fix_user_rank_and_experience(). \
                    clean_user_exp_log().clean_user_account_log().clean_user_intimacy_rank().clean_user_contribution()
                RedisHold().clean_redis_user_detail(user_id)
            elif isinstance(user_id, (list, tuple, set)):
                for i in user_id:
                    MysqlOperation(user_id=i).fix_user_account().fix_user_rank_and_experience(). \
                        clean_user_exp_log().clean_user_account_log().clean_user_intimacy_rank().clean_user_contribution()
                    RedisHold().clean_redis_user_detail(i)
            logging.info('初始化用户信息完成!')
        else:
            logging.info('无需初始化用户信息!')

        if anchor_id:
            logging.info('正在初始化主播信息...')
            if isinstance(anchor_id, (str, int)):
                MysqlOperation(anchor_id=anchor_id,
                               user_id=anchor_id).fix_anchor_rank_and_exp().clean_user_account_log().fix_user_rank_and_experience()
                RedisHold().clean_redis_user_detail(anchor_id)
            elif isinstance(anchor_id, (list, tuple, set)):
                for i in anchor_id:
                    MysqlOperation(anchor_id=anchor_id,
                                   user_id=anchor_id).fix_anchor_rank_and_exp().clean_user_account_log().fix_user_rank_and_experience()
                    RedisHold().clean_redis_user_detail(i)
            logging.info('初始化主播信息完成!')
        else:
            logging.info('无需初始化主播信息!')

    def setUp(self, user_id=None, anchor_id=None):
        """
        用例执行前初始化用户或房间信息
        :param user_id:
        :param room_id:
        :return:
        """
        logging.info('正在执行用例SetUp...')
        self.init_user_and_room(user_id, anchor_id)

    def tearDown(self, user_id=None, anchor_id=None):
        """
        用例执行完成后初始化用户或房间信息
        :param user_id:
        :param room_id:
        :return:
        """
        logging.info('正在执行用例TearDown...')
        self.init_user_and_room(user_id, anchor_id)
