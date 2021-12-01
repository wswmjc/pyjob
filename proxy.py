# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import time
from datetime import datetime
from scrapy import Request, core
from twisted.internet import error as net_error
from conf import SLEEP_TIME, BANNED_RATE_SECOND_MAX, CHECKED_BANNED_TIMES, TRY_TIME_MAX
from .proxies.httpproxy import xdaili_proxy, zhima_proxy
from .proxies.tunnelproxy import abyunproxy

logger = logging.getLogger(__name__)


class ProxyMiddleware:
    # 当前激活代理索引号，0 为优先级最高的代理 最低为 len(self) - 1
    active_proxy_index = 0
    # banned 次数
    banned_times = 0
    # 请求总数
    total_request_num = 0
    # 代理使用开始时间
    start_time = datetime.now()
    # 尝试次数 遍历一遍代理池 算一次
    try_times = 0
    # 代理不可用的数量
    disabled_count = 0

    def __init__(self):
        self.pond = [abyunproxy, zhima_proxy]

    def __len__(self):
        return len(self.pond)

    @property
    def proxypool(self):
        return self.get_proxy_pool()

    @property
    def proxy(self):
        try:
            return self.proxypool.get()
        except Exception as error:
            if not isinstance(error, (net_error.TimeoutError, net_error.ConnectError, core.downloader.handlers.http11.TunnelError)):
                self.disabled_count += 1
                self.switch()
                logger.error("Get Proxy Exception, %s", error)
            else:
                time.sleep(1)
                return self.proxy

    def need_switch(self):
        '''
            检测是否需要切换代理
            如果每秒被banned次数超过约束的上限（BANNED_RATE_SECOND_MAX），
            则切换，检测从一定时间（CHECKED_BANNED_TIMES）之后开始检测
        '''
        check_time = datetime.now()
        time_span = check_time - self.start_time
        total_sec = time_span.seconds
        banned_times_per_second = 0 if total_sec == 0 else self.banned_times // total_sec
        need_switch = False
        if total_sec > CHECKED_BANNED_TIMES:
            need_switch = banned_times_per_second > BANNED_RATE_SECOND_MAX
        if need_switch:
            logger.info(
                f'''代理池即将进行切换， 当前代理请求共{self.total_request_num}次，
                共执行{total_sec}秒，被banned次数为{self.banned_times}，频率为{banned_times_per_second}每秒''')
        return need_switch

    def switch(self):
        '''
            切换代理池
        '''
        if self.active_proxy_index == len(self) - 1:
            self.active_proxy_index = 0
            self.try_times += 1
        else:
            self.active_proxy_index += 1
        self.banned_times = 0
        self.total_request_num = 0
        self.start_time = datetime.now()

    def need_restart(self):
        '''
            检测是否需要重置代理池
            尝试次数触顶（TRY_TIME_MAX）
            如果所有代理都不可用 需要进行重启策略
        '''
        if self.try_times > TRY_TIME_MAX:
            logger.warning(f'代理池已经尝试{self.try_times}轮， 爬虫程序将会休眠{SLEEP_TIME // 60}分钟，然后重启')
            return True

        if self.disabled_count >= len(self):
            logger.error(f'代理池被检测到均不可用， 爬虫程序将会休眠{SLEEP_TIME // 60}分钟，然后重启')
            return True

        return False

    def restart(self):
        '''
            重置代理池
        '''
        self.active_proxy_index = 0
        self.banned_times = 0
        self.total_request_num = 0
        self.try_times = 0
        self.disabled_count = 0
        self.start_time = datetime.now()
        logger.info(f'代理池重置于{self.start_time}')

    def get_proxy_pool(self):
        '''
            获取代理池
        '''
        if self.need_switch():
            self.switch()
        elif self.need_restart():
            time.sleep(SLEEP_TIME)
            self.restart()
        return self.pond[self.active_proxy_index]

    def is_anti_spider(self, response):
        '''
            判断是否出现反爬
        '''
        return (
            not response.body
            or
            'FAIL_SYS_USER_VALIDATE' in response.text
            or
            '抱歉！系统繁忙' in response.text
            or
            'login.taobao.com' in response.text
        )

    def process_request(self, request: Request, spider):
        if request.meta.get('_proxy_required') or 1:
            logger.debug(f'proxy { request.url } over { self.proxy }')
            request.meta['proxy'] = self.proxy
            # 只计算通过代理的请求
            self.total_request_num += 1
        else:
            request.meta.pop('proxy', None)

    def reproxy_request(self, request: Request):
        invalid_proxy = request.meta.get('proxy')
        new_req = request.copy()
        # new_req.meta['proxy'] = self.proxy
        # 获取代理后进行旧的代理移除处理
        self.proxypool.remove(invalid_proxy)
        new_req.dont_filter = True
        self.total_request_num += 1
        return new_req

    def process_response(self, request, response, spider):
        if self.is_anti_spider(response):
            logger.info(f'Banned request: {request.url}. Then replace the proxy')
            self.banned_times += 1
            return self.reproxy_request(request)
        else:
            return response

    def process_exception(self, request, exception, spider):
        new_req = self.reproxy_request(request)
        if not isinstance(exception, (net_error.TimeoutError, net_error.ConnectError, core.downloader.handlers.http11.TunnelError)):
            raise exception

        logger.exception(exception)
        return new_req
