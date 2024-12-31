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


class EditSettingForm(FlaskForm):
    name = StringField('名称', render_kw={'readonly': True})
    value = TextAreaField(
        '值', render_kw={"rows": 2}, validators=[DataRequired(), Length(1, 1000)])
    submit = SubmitField('保存')
