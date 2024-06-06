
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

def llm_explain(content:str) -> str:
    print("执行了")
    # 星火认知大模型Spark3.5 Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
    SPARKAI_URL = 'ws://spark-api.xf-yun.com/v1.1/chat'
    # 星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
    SPARKAI_APP_ID = '47b256c8'
    SPARKAI_API_SECRET = 'ZTVjYjlkNWU2Yjc3MDM0ZjYwM2VjYmJj'
    SPARKAI_API_KEY = '2e6a20480ace3d0d0ecfe21db8d6d4be'
    # 星火认知大模型Spark3.5 Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
    SPARKAI_DOMAIN = 'general'
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [ChatMessage(
        role="user",
        content="请概括下文的主要内容\n" + content
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    print("生成完毕")
    return a.generations[0][0].text

if __name__ == '__main__':
    content = '''
    ...
    '''
    answer = llm_explain(content)
    print(answer)
