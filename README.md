# Sina news crawler + word segementation
## Project Structure
- [Crawler Script](./reptile.py)
- [File operation(with date as filename)](./FileOperator.py)
- [n-gram word segmentation](./nGram.py)
- [Final result n-gram](./result/)
- [Requirement of the project](./20160426作业.pdf)

- [Github address](https://github.com/sunshineclt/n-gram)

## Usage
- Method1 (Without news material)
	- Change the start date and end date for news crawler
	- Run Crawler
	- Change start date and end date in nGram.py
	- Change parameters(Frequency, Freedom, Condensation) in nGram.py
	- Run nGram.py
	- Wait for nGram.py
	- 1Gram.txt-5Gram.txt will be generated when nGram.py ends
- Method2 (With news material)
	- Change parameters(Frequency, Freedom, Condensation) in nGram.py
	- Run nGram.py
	- Wait for nGram.py
	- 1Gram.txt-5Gram.txt will be generated when nGram.py ends

## Advantages
- Several crawler interferences are solved, such as
	- gzip compress
	- Other html attribute in <p></p> (Some webpage even has <font><font></font></font> nested more than 1k times, which causes Rugular Expression to be dead)
	- I don't use HTTPParser as required but to use Regular Expression
- n-gram word segmentation
	- [references](http://www.matrix67.com/blog/archives/5044)
	- adopt three measurement to decide word segmentation
		- Work Frequency
		- Condensation（即“电影院”不是“电”+“影院”或“电影”+“院“）
		- Freedom（即“伊拉克”不是“伊拉”，也不是”拉客“）
- Good Comment
	- Almost every line of code has comments
- 2-character, 3-character words' performance is extremely great

## Disadvantages
- Crawler may encounter some encoding problems, some of them are Sina's matter but some are due to my decoding method (Some of the webpage are not encoded with gb2312)
- n-gram word segmentation requires a large amount of memory, although I've used some memory control method
- n-gram word segmentation could be improved in time complexity, although it may require even bigger space complexity
- n-gram word segmentation did not consider function word such as 3-character word: “激烈的”
- 4-character and 5-character words' performance is relatively bad. There is no 5-character words in 200M news material even though I've lower the standard for 5-character word.

## Authored By Chen Letian at 2016.05.14

