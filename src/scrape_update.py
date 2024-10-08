# 更新本地的帖子数据
# 此过程将帖子新增的数据融入本地数据中。
# 对于已被删除的帖子，会继续保留本地数据。
# 实现数据的持续扩充和更新,最大程度地保留数据。

# NOTE 注意事项:
# 1. 爬取采用的是异步的方式，把一个主题帖分成多段，异步并发。所以爬取的过程不是一个按照楼层线性的过程。
# 2. 爬取是一个过程, 不是瞬间完成的。所以可能会出现在爬取的过程中，帖子有了新的数据的情况。如果找出哪些是新增数据的来节省更新时间？
# 2.1. 所有在爬取时间段中新增的数据都错过了爬取。eg1:在已爬完的post下回复了新的subpost; eg2:在已爬完的分页下回复了post。
# 这种情况更新操作只要找的本地数据中所有(post & subpost) 中最大的max_pid。大于max_pid就是新增的数据。其中包含了初次爬取的过程中新增的数据。
# 2.2. 所有在爬取时间段中新增的数据都还在等待爬取。
# eg1:在未爬完的post下回复了新的subpost;
# eg2:在未爬完的分页下回复了post。
# 这种情况的处理方法与 2.1 一样。
# 2.3. 新增的数据中，有些已经错过了爬取，有些还在等待爬取。
# eg1:在已爬完的post下回复了新的subpost1，在未爬完的分页下回复了post2。
# 这种情况的会导致爬取完成时pid较大的post2被保存到本地。如果继续使用 2.1 的方法就会导致pid较小的subpost1被忽略。
# 这种情况需要 max_pid 和 max_sub_pid 两个种类的数据。max_pid 来处理新增的post. max_sub_pid 来处理每个post下的新增subpost。
# 因为max_pid 在 post 线性域 。 max_sub_pid 在 subpost 线性域。
# 3. updateThreshold = min(max_pid, max_sub_pid) 是一个极点。所有新增的数据都在这个极点之后。


import asyncio

from modules.scrape_update_module import scrape_update


def main():
    path = input("请输入本地帖子数据的路径: ")
    asyncio.run(scrape_update(path))


if __name__ == "__main__":
    main()
