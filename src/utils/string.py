import re
import os
import time

from flask import render_template


def cut_sent(split_by_line, para):
    if split_by_line:
        return [e.strip() for e in para.split('\n') if e.strip()]
    para = re.sub('([,，;:、。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return [e.strip() for e in para.split('\n') if e.strip()]


def list_file_names(file_dir):
    for _, _, files in os.walk(file_dir):
        return files


def render(file_path, **kwargs):
    return render_template(file_path, **kwargs)


#         self.created_at = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(created_at))
