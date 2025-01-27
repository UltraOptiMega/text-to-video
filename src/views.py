import uuid
import os
import json
from traceback import format_exc

from loguru import logger
from flask import Blueprint, request, flash, redirect, url_for, send_file, current_app

from . import forms, constants, biz

from .utils import render, get_db


index_bp = Blueprint('index', __name__)


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    form = forms.video.AddTextToVideoForm(speaker='zh_male_qinqie')
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                biz.generate_video(form, f'{uuid.uuid4().hex}')
                flash('视频创建成功')
            except Exception as e:
                logger.error(format_exc())
                flash(str(e), 'error')
                return redirect(url_for('.index'))
            return redirect(url_for('.list_videos'))
    return render('video/add_text_to_video.html', form=form)


@index_bp.route('/videos', methods=['GET', 'POST'])
def list_videos():
    videos = biz.list_videos()
    return render('video/list.html', videos=videos)


@index_bp.route('/videos/<int:id_>', methods=['GET'])
def download_video(id_):
    with get_db() as db:
        db.execute('SELECT * FROM video WHERE id = ?', (id_,))
        row = db.fetchone()
        if not row:
            flash('视频不存在', 'error')
            return redirect(url_for('.list_videos'))
        return send_file(f'{os.getcwd()}/{row["dst"]}')


@index_bp.route('/videos/<int:id_>', methods=['POST'])
def delete_video(id_):
    with get_db() as db:
        db.execute('SELECT * FROM video WHERE id = ?', (id_,))
        row = db.fetchone()
        if not row:
            flash('视频不存在', 'error')
        db.execute('DELETE FROM video WHERE id = ?', (id_,))
        os.remove(f'{os.getcwd()}/{row["dst"]}')
        flash('视频删除成功')
        return redirect(url_for('.list_videos'))


@index_bp.route('/settings')
def list_settings():
    with get_db() as db:
        db.execute('SELECT * FROM setting')
        rows = db.fetchall()
        return render('setting/list.html', settings=rows)


@index_bp.route('/settings/<int:id_>', methods=['GET', 'POST'])
def edit_setting(id_):
    with get_db() as db:
        db.execute('SELECT * FROM setting WHERE id = ?', (id_,))
        row = db.fetchone()
        if not row:
            flash('参数不存在', 'error')
            return redirect(url_for('.list_settings'))

        if request.method == 'GET':
            form = forms.setting.EditSettingForm(name=row['name'], value=row['value'])
            return render('setting/edit.html', form=form)

        form = forms.setting.EditSettingForm()
        db.execute('UPDATE setting SET value = ? WHERE id = ?', (form.value.data.strip(), id_))
        flash('保存成功')

        return redirect(url_for('.list_settings'))
