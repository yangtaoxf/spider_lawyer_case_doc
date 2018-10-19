# coding=utf8

from util.redis_util import RedisCasePlanSchemaTaskMaster

if __name__ == "__main":
    while True:
        RedisCasePlanSchemaTaskMaster.refresh_case_plan_schema(RedisCasePlanSchemaTaskMaster.KEY, 500)  # 抓取任务队列
