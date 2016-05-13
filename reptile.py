# 爬虫脚本
# 能够爬取新浪网往日新闻
import datetime
import re
import urllib.error
import urllib.request
import FileOperator
import gzip


# 对于to_match_str中的所有匹配正则表达式pattern_str的字串进行func操作
def forEachMatch(*, pattern_str, to_match_str, func):
    pattern = re.compile(pattern_str, re.S)
    for match in pattern.finditer(to_match_str):
        func(match)


# 存储详细新闻页面到文件
def saveContentOfURL(target_url):
    # 如果已经访问过这个URL了不重复访问,即去重
    if target_url in searched_url:
        return
    try:
        # 尝试GET请求target_url
        article_response = urllib.request.urlopen(target_url)
        raw_data = article_response.read()
        # 如果返回内容是gzip压缩过的话就解压
        if article_response.getheader("Content-Encoding") == "gzip":
            raw_data = gzip.decompress(raw_data)
        # gb2312解码,然而有些页面还是会存在一些乱码,实在是没办法
        article_data = raw_data.decode('gb2312', 'ignore')
        # 对于每一个<p></p>中的元素clean过后存储
        forEachMatch(pattern_str='<p>(.*?)</p>', to_match_str=article_data,
                     func=lambda match: file_operator.writeFile(cleanArticle(match.group(1))))
    except urllib.error.URLError:
        print(target_url, 'is a wrong url')
    except BaseException as message:
        print(message)
    # 记录已经访问过这个URL
    searched_url.add(target_url)


# 清理<p></p>中的内容,主要是去除标签
def cleanArticle(article):
    # 如果article的长度超过10000就认为是乱七八糟的东西
    # 因为发现网页中有<font></font></font></font>这样嵌套了一千多次的情况,如果不排除掉下面的正则表达式会卡死
    if len(article) > 10000:
        return ""
    # 如果是table或者script,那么里面的内容就直接不要了
    pattern_tag = re.compile(r"<(table)[^>]*>(.*?)</table>|<(script)[^>]*>(.*?)</script>",
                             re.S)
    clean_article = pattern_tag.sub("", article)
    # 如果是其他配对的标签,则去除标签保留里面的内容
    pattern_tag = re.compile(r"<(\S*?)[^>]*>(.*?)</\1>", re.S)
    clean_article = pattern_tag.sub(r"\2", clean_article)
    # 如果还剩下没配对的标签,则去除
    pattern_tag = re.compile(r"<(\S*?)[^>]*>|<.*?/>", re.S)
    clean_article = pattern_tag.sub("", clean_article)
    # 去除html注释
    pattern_blank = re.compile("\s|<!--.*?-->", re.S)
    no_blank_article = pattern_blank.sub("", clean_article)

    return no_blank_article

# 开始爬的新浪新闻日期
now_date = datetime.datetime(2006, 5, 26)
# 结束爬的新浪新闻日期,到2009年12月31日约950M,2010年开始就是动态生成的了,不好爬,需要有js解释器
destination_date = datetime.datetime(2010, 1, 1)
# 保存已经访问过的URL
searched_url = {""}
# 保存已经爬到的语料大小
total_size = 0
# 打log
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

while total_size < 1000000000 and now_date < destination_date:
    now_date_str = now_date.strftime('%Y%m%d')
    # 初始化并打开文件准备开始写
    file_operator = FileOperator.FileOperator(now_date, mode='w')
    # 打log
    print(now_date.strftime("Now running: %Y-%m-%d's news"))
    # 拼接URL
    url = "http://news.sina.com.cn/hotnews/" + now_date_str + ".shtml"
    try:
        # 尝试访问URL
        response = urllib.request.urlopen(url)
        data = response.read()
        # 如果返回是gzip压缩的就解压缩
        if response.getheader("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
        # gb2312解码
        index_data = data.decode('gb2312', 'ignore')
        # 对于其中的每一个链接都去saveContentOfURL
        forEachMatch(
            pattern_str='<a href="?(http://[\w.]*?.sina.com.cn/[^<>" ]*)"?[^<>]*target="?_blank"?[^<>]*>([^<>]*)</a>',
            to_match_str=index_data,
            func=lambda match: saveContentOfURL(match.group(1)))
    except urllib.error.URLError:
        print(url, 'is a wrong url')
    except BaseException as msg:
        print(msg)
    # 关闭文件
    file_operator.closeFile()
    # 更新已经爬到的语料大小
    total_size += file_operator.getFileSize()
    # 打log
    print("total size:", total_size / 1024 / 1024, "M")
    now_date = now_date + datetime.timedelta(days=1)

# 打log
print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
