# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    IntegerField,
)
from wtforms.validators import (
    DataRequired,
    Length,
)


class AddTextToVideoForm(FlaskForm):
    name = StringField('视频名称')
    content = TextAreaField(
        '视频文案', render_kw={"rows": 20, "placeholder": "最好一行一句"}, validators=[DataRequired(), Length(1, 10000)])
    speaker = StringField('音色(根据需要,从 https://www.volcengine.com/docs/6489/93478 获取)', render_kw={'placeholder': '默认值zh_male_qinqie'})
    submit = SubmitField('生成视频')


class GetVideoForm(FlaskForm):
    id = IntegerField('视频ID', render_kw={'readonly': True})
    product_type = StringField('套餐', render_kw={'readonly': True})
    title = StringField('视频标题', render_kw={'readonly': True})
    text = TextAreaField(
        '视频文案', render_kw={"rows": 20, 'readonly': True})
    status = StringField('状态', render_kw={'readonly': True})
    url = StringField('下载链接', render_kw={'readonly': True})
