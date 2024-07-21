import asyncio


# 队列大小由生产等待和消费等待的时间来绝对。如果的处理时间都很长就需要大的队列来缓冲
class ProducerConsumerContact:
    def __init__(
            self,
            queue_maxsize: int,
            producers_num: int,
            consumers_num: int,
            consumer_await_timeout: int = 1,
    ) -> None:
        self.queue_maxsize = queue_maxsize
        self.producers_num = producers_num
        self.consumers_num = consumers_num
        self.consumer_await_timeout = consumer_await_timeout

        self.tasks_queue = asyncio.Queue(maxsize=queue_maxsize)
        self.running_producers = self.producers_num
