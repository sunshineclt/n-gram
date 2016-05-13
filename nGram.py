# 此脚本以reptile.py运行结果为语料分析n-gram词语
# 也可在命令行中给予第一个参数来表示语料文件
# 使用词频,凝固程度,自由程度三个指标来衡量是否为词
# 参考文章: http://www.matrix67.com/blog/archives/5044

import sys
import datetime
import re
import FileOperator
import math


# 在sentence中抽取长度为n的字串放入words
def calculateNGram(*, n, sentence):
    for index in range(0, len(sentence) - n + 1):
        word = sentence[index: index + n]
        if word in words:
            words[word] += 1
        else:
            words[word] = 1
        words_count[n] += 1


# 计算n-gram
def calculate(sentence):
    for n in range(1, 6):
        calculateNGram(n=n, sentence=sentence)


# 将各种标点符号视为停词来断段落
def clearPunctuation(article):
    pattern = re.compile('[●┊\-■：∶%；！？;&.,:?!．‘’“”"\'、，。><（()）\[\]\{\}【】―《》/／・…a-zA-Z0-9_\p{P}]+')
    return pattern.split(article)


# 打印结果至文件
def outputWords(output_words):
    for n in range(1, 6):
        output_file = open(str(n) + 'Gram' + '.txt', 'w')
        for (word, frequency) in output_words[n].items():
            print(word, frequency, "times", file=output_file)
        output_file.close()


# 根据不同的n规定成为n-gram词的词频要求
def frequency_filter(frequency, n):
    if n == 1:
        criteria = 1000
    elif n == 2:
        criteria = 1000
    elif n == 3:
        criteria = 500
    elif n == 4:
        criteria = 300
    elif n == 5:
        criteria = 10
    if frequency > criteria:
        return True
    else:
        return False


# 根据不同的n规定成为n-gram词的信息熵要求
def entropy_filter(entropy, n):
    if n == 1:
        criteria = 5
    elif n == 2:
        criteria = 5
    elif n == 3:
        criteria = 4.5
    elif n == 4:
        criteria = 3.5
    elif n == 5:
        criteria = 2
    if entropy > criteria:
        return True
    else:
        return False


# 从文段中提取出来的未加甄别的n-gram(raw n-gram)
words = {}
# 从文段中提取出来的未加甄别的各个长度n-gram的个数,words_count[1~5]代表n-gram的数量,0无意义
words_count = [0, 0, 0, 0, 0, 0]

if len(sys.argv) > 1:
    # 如果是指定语料文件的话

    file = open(sys.argv[1], 'r')
    data = file.read()
    file.close()
    for segment in clearPunctuation(data):
        calculate(segment)
else:
    # 如果不是指定语料文件的话,就按照reptile所保存的文件结构来读取语料并分析

    # 读取语料的开始日期
    now_date = datetime.datetime(2004, 7, 4)
    # 读取语料的末尾日期,从04.07.04到06.1.1约为220M语料
    destination_date = datetime.datetime(2006, 1, 1)
    # 从开始日期到末尾日期依次读取语料并提取raw n-gram
    while now_date < destination_date:
        now_date_str = now_date.strftime('%Y%m%d')
        # 打log
        print(now_date.strftime("Now running: %Y-%m-%d's news"))
        # 读取文件
        file_operator = FileOperator.FileOperator(now_date, mode='r')
        data = file_operator.readFile()
        # 将各种标点符号视为停词来断段落后找出所有的n-gram
        for segment in clearPunctuation(data):
            calculate(segment)
        now_date = now_date + datetime.timedelta(days=1)

# 将所有的raw词按照字典序排列,方便计算右信息熵
words_left = sorted(words.items(), key=lambda d: d[0])
# 将所有的raw词按照每个词从右到左的字典序排序(如"阿斯顿"应该排在"斯顿"的后面),方便计算左信息熵
words_right = sorted(words.items(), key=lambda d: d[0][::-1])
# n_gram_words中保存经过甄别的词,n_gram_words[1~5]代表n-gram,0无意义
n_gram_words = [{}, {}, {}, {}, {}, {}]
# 所有的raw词总数
total_length = len(words_left)

# 先按照词频,凝固程度,右信息熵进行第一次筛选
# 遍历所有的按照字典序排列的词
for index in range(0, len(words_left)):
    word = words_left[index][0]
    frequency = words_left[index][1]
    # 根据词频筛选
    if frequency_filter(frequency, len(word)):
        # 根据凝固程度筛选

        # 先计算这个词是拆开的最大可能出现频率(如"电影院"不是电影院,而是"电影"和"院"的偶然组合或"电"和"影院"的偶然组合的最大可能性)
        max_split = 1e-15
        for mid in range(1, len(word)):
            left_word = word[:mid]
            right_word = word[mid:]
            left_frequency = words[left_word] / words_count[len(left_word)]
            right_frequency = words[left_word] / words_count[len(right_word)]
            if left_frequency * right_frequency > max_split:
                max_split = left_frequency * right_frequency
        # 如果这个词实际出现的可能性是上述拆开的偶然组合可能性的100倍以上,则视为通过了凝固程度的筛选
        if frequency / words_count[len(word)] / max_split > 100:
            # 根据右信息熵筛选

            # 先找出所有以word开头的词
            # 由于是按照字典序排好的,那么这种以word开头的词一定是word之后连续的一串
            index_right_neighbor = index + 1
            # 用于记录右邻接词的词频
            right_neighbor = []
            # 用于记录右邻接词的总词频
            right_neighbor_total = 0
            # 由于是按照字典序排好的,那么这种以word开头的词一定是word之后连续的一串
            while index_right_neighbor < len(words_left) and words_left[index_right_neighbor][0].startswith(word):
                right_neighbor.append(words_left[index_right_neighbor][1])
                right_neighbor_total += words_left[index_right_neighbor][1]
                index_right_neighbor += 1
            # 计算右信息熵
            right_info_entropy = 0
            # 对于每一个右邻接词,它所贡献的信息熵为  词频/右邻接词总词频 * ln(词频/右邻接词总词频)
            for neighbor in right_neighbor:
                right_info_entropy -= neighbor/right_neighbor_total * math.log(neighbor/right_neighbor_total, math.e)
            # 根据右信息熵筛选
            if entropy_filter(right_info_entropy, len(word)):
                # 打log,之所以放在这里是因为不想要输出的东西太多,大致的能够看到进度即可
                print("Now filtering: " + str(index) + "/" + str(total_length))
                # 通过了词频,凝固程度,右信息熵的筛选,加入n_gram_words
                n_gram_words[len(word)][word] = frequency

# 再根据右信息熵进行第二次筛选,遍历所有的按照右字典序排列的词(不然不方便计算左信息熵)
for index in range(0, len(words_right)):
    word = words_right[index][0]
    frequency = words_right[index][1]
    # 首先它得是通过第一次筛选的词
    if n_gram_words[len(word)].get(word, False):
        # 根据左信息熵筛选

        # 先找出所有以word结尾的词
        # 由于是按照右字典序排好的,那么这种以word结尾的词一定是word之后连续的一串
        index_left_neighbor = index + 1
        # 用于记录左邻接词的词频
        left_neighbor = []
        # 用于记录左邻接词的总词频
        left_neighbor_total = 0
        # 由于是按照右字典序排好的,那么这种以word结尾的词一定是word之后连续的一串
        while index_left_neighbor < len(words_right) and words_right[index_left_neighbor][0].endswith(word):
            left_neighbor.append(words_right[index_left_neighbor][1])
            left_neighbor_total += words_right[index_left_neighbor][1]
            index_left_neighbor += 1
        # 计算左信息熵
        left_info_entropy = 0
        # 对于每一个左邻接词,它所贡献的信息熵为  词频/左邻接词总词频 * ln(词频/左邻接词总词频)
        for neighbor in left_neighbor:
            left_info_entropy -= neighbor / left_neighbor_total * math.log(neighbor / left_neighbor_total, math.e)
        # 根据左信息熵筛选
        if not entropy_filter(left_info_entropy, len(word)):
            # 打log,之所以放在这里是因为不想要输出的东西太多,大致的能够看到进度即可
            print("Now filtering: " + str(index) + "/" + str(total_length))
            # 如果没有通过左信息熵筛选,就把它从n_gram_words里面删掉
            del (n_gram_words[len(word)][word])

# 输出经过词频,凝固程度,左右信息熵筛选的词
outputWords(n_gram_words)
