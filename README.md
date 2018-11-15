# 裁判文书网爬虫
仅用于个人学习和技术交流，不可用于商业用途。请合理设置对应线程池参数和IP地址，建立对应表

**使用到PYTHON库**:

|    Python库 | 用途 | 安装 ｜ 备注 |
|:-------|:-------------| ----------|
| aiohttp  | 协程，异步IO | *pip3 install aiohttp* |比requests等库高效，比scrapy简单 |
| PyExecJS  | 执行js | *pip3 install PyExecJS* | |

**LINUX服务器环境配置**:

|    环境 | 用途 | 备注 |
|:-------|:-------------|:----------|
|   nodejs  | 执行复杂的JavaScript | 注意代码使用的JavaScript环境 |
|   redis  | 任务信息数据交互等 | 如果单机模式，不使用分布式部署，可不使用redis |

## 设计思想
1. 架构思想是：使用一台master管理服务器，生成任务队列。另外部署任意N台spider,进行爬取。然后入库
2. 任务划分：分为3个节点，且下一节点需要在上一节点完成后再进行爬取
3. IP资源很稀少，所以代理池的代理本者最大利于原则，失败次数到了一定配置次数才会置为不可用，重新拿取IP
--------
| 任务节点 | 执行脚本 | 说明 | 备注 |
|:-------|:-------------|:----------|:----------|
| [下载搜索目录加密返回结果](lawyer/case/doc/redis_case_plan_schema_task_master.sh) | *sh redis_case_plan_schema_task_master.sh* |  |  |
|   [解析加密文档id](lawyer/case/doc/redis_case_plan_schema_detail_master.sh)  | *sh redis_case_plan_schema_detail_master.sh* |  |  |
|   [根据文档id，下载文档JavaScript内容](redis_case_detail_master.sh) | *sh redis_case_detail_master.sh* |  |  |
|   [本地正则解析JavaScript内容](redis_case_detail_master.sh) | *sh doc_formater.sh* |  |  |

