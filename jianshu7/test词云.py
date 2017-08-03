import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba

text = open('E:\SCRAPY\jianshu7\w.txt').read()
wordlist_after_jieba = jieba.cut(text, cut_all = True)
wl_space_split = " ".join(wordlist_after_jieba)
my_wordcloud = WordCloud().generate(wl_space_split)
plt.imshow(my_wordcloud)

plt.axis("off")
plt.show()