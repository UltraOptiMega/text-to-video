import base64
import os
import json
import shutil

from moviepy import (
    AudioFileClip,
    ImageClip,
    VideoClip,
    concatenate_videoclips,
)
import requests
from flask import current_app

from src import constants

from .utils import (
    list_file_names,
    cut_sent,
    get_browser,
    AppError,
    get_db,
    get_token,
)


def generate_video(form, task_id):
    sents = cut_sent(form.split_by_line, form.content.data)
    if not sents:
        raise AppError('未能切分出有效的句子')

    video_dst = f'{constants.VIDEO_ROOT}/{task_id}'
    if not os.path.exists(video_dst):
        os.makedirs(video_dst)

    clips = []

    img_paths = generate_images(sents, video_dst)
    audio_paths = []
    for i, sent in enumerate(sents):
        audio_dst = os.path.join(video_dst, f'{i}.mp3') 
        generate_audio(sent, form.speaker.data, audio_dst)

        audio_paths.append(audio_dst)

    clips = []
    for audio_dst, img_dst in zip(audio_paths, img_paths):
        audio_clip = AudioFileClip(audio_dst)
        img_clip = ImageClip(img_dst, duration=audio_clip.duration).resized(width=1980, height=1080).with_audio(audio_clip)

        clips.append(img_clip)

    clip = concatenate_videoclips(clips, method='compose')
    dst = f'{video_dst}.mp4'
    clip.write_videofile(dst, threads=8, fps=2)
    shutil.rmtree(video_dst)
    with get_db() as db:
        db.execute('INSERT INTO video(name, content, sentences, dst) VALUES(?, ?, ?, ?)', (form.name.data, form.content.data, json.dumps(sents), dst))
    return dst


def get_tts_params():
    keys = set(['volcengine.tts.appkey', 'volcengine.tts.service', 'volcengine.tts.region', 'volcengine.tts.token_version',
                'volcengine.access_key', 'volcengine.access_secret'])
    with get_db() as db:
        db.execute(f'SELECT * FROM setting WHERE name IN ({", ".join("?" * len(keys))})', tuple(keys))
        params = {r['name']: r['value'] for r in db.fetchall()}
        for key in keys:
            if key not in params:
                raise AppError(f'{key}未配置,请在setting页面配置')
            if not params[key]:
                raise AppError(f'{key}值为空,请在setting页面配置')
        return params


def get_volcengine_tts_token():
    key = 'volcengine_tts_token'
    token = current_app.cache.get(key)
    if token:
        return token
    params = get_tts_params()
    token = get_token(params['volcengine.access_key'], params['volcengine.access_secret'],
                      params['volcengine.tts.appkey'], params['volcengine.tts.token_version'],
                      params['volcengine.tts.region'], params['volcengine.tts.service'])
    current_app.cache.set(key, token, expire=24 * 3600 - 100)
    return token


def generate_audio(content, speaker, dst):
    token = get_volcengine_tts_token()
    params = get_tts_params()
    namespace = 'TTS'
    current_app.logger.info('start to generate audio, text: %s', content)
    url = f'https://sami.bytedance.com/api/v1/invoke?version=v4&token={token}&appkey={params["volcengine.tts.appkey"]}&namespace={namespace}'
    payload = {'text': content, 'speaker': speaker, 'audio_config': {
        'format': 'wav',
        'sample_rate': 16000
    }}
    x = requests.post(url, json={'payload': json.dumps(payload)})
    current_app.logger.info(
        'audio response, input: %s, response_text: %s, status_code: %s', content, x.text, x.status_code)
    resp_json = x.json()
    payload = json.loads(resp_json['payload'])
    stream = resp_json['data']
    binary_data = base64.b64decode(stream)
    with open(dst, 'wb') as f:
        f.write(binary_data)
    current_app.logger.info('audio generated, text: %s, dst: %s', content, dst)


def generate_images(sents, dst):
    image_paths = []
    with get_browser() as browser:
        for s in sents:
            current_app.logger.info('start get image for text: %s', s)
            path = browser.download_pics(s, dst)
            image_paths.append(path[0])
    return image_paths


def list_videos():
    with get_db() as db:
        db.execute('SELECT * FROM video ORDER BY id DESC')
        return db.fetchall()
