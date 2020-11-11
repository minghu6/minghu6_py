"""藏经阁 cli
https://www.tangzhekan2.cc/
使用腾讯的OCR进行最关键的图片识别，我是没想到这么简单的图片，都不能用tesseract、cnocr、Baidu等常用字识别都搞不定
只有腾讯的普通及以上文字识别才好使, 但是也认不全
而且腾讯的好贵，1000次/84元
"""

import requests
from bs4 import BeautifulSoup
from docopt import docopt
from color import color

from minghu6.graphic.captcha.get_image import get_image
from minghu6.http.request import headers
from minghu6.etc.importer import check_module
from minghu6.algs.operator import getone
from minghu6.algs.decorator import cli_handle_exception
from minghu6.text.pattern import han
import minghu6

from urllib.parse import urlparse, urljoin
from pathlib import Path
from collections import defaultdict
import os
import json
from types import MethodType
from collections import OrderedDict
from typing import Mapping, Tuple, Union, TypeVar, OrderedDict, List
import re
import traceback
import atexit


# Local、Origin  本地数据库
# Upstream       网站

HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR.joinpath('.cangjingge')
TEXT_DATABASE_DIR = CONFIG_DIR.joinpath('texts')
PACKAGE_PARENT_DIR = Path(__file__).parents[2]
RESOURCES_DIR = PACKAGE_PARENT_DIR.joinpath('resources')
IMG2CHAR_CONFIG_DIR = RESOURCES_DIR.joinpath('cangjingge')
CLEAN_PAT_CONFIG_DIR = IMG2CHAR_CONFIG_DIR
HANDIMG_DIR = IMG2CHAR_CONFIG_DIR.joinpath('hand_imgs')

BASE_DOMAIN = 'https://www.tangzhekan2.cc'


VERBOSE = False

try:
    import lxml
except ImportError:
    PARSER = 'html.parser'
else:
    PARSER = 'lxml'


# build img database
def build_img_dict():
    img_dict = defaultdict(list)
    HANDIMG_DIR_PATH =  Path(HANDIMG_DIR)
    for child in Path(HANDIMG_DIR).iterdir():
        with child.open('rb') as fr:
            img_dict[child.stem[0]].append(fr.read())

    return img_dict


def search_in_img_dict(img_dict, img_url):
    while True:
        try:
            r = requests.get(img_url, headers=headers, timeout=5)
        except Exception as ex:
            color.print_err(str(ex) + '  ' + img_url)
        else:
            break

    if r.status_code != 200:
        raise GetPageError(r)

    img_content = r.content

    for key, vlist in img_dict.items():
        if img_content in vlist:
            return key


def getone_config(config_path: Path):
    if config_path.exists():
        with config_path.open() as fp:
            config_dict = json.load(fp)
    else:
        config_dict = {}

    return config_dict


class Config:
    def __init__(self, fn, config_dir:Path=CONFIG_DIR):
        self._config_path = config_dir.joinpath(fn)
        self._config_dict = getone_config(self._config_path)

        # 感觉自己在写旧式的Java，TM的匿名内部类都出来了，没有闭包绝对是Python的固有缺陷！！！
        # 从这一点上Python的表现能力已经不如1.8版本以后的Java了
        class LexClosureMethod:
            def __init__(self, method_name):
                self.method_name = method_name

            def __call__(self, other_self, *args, **kwargs):
                return getattr(other_self._config_dict, self.method_name)(*args, **kwargs)

        def enabled_methods(method_name):
            if method_name.startswith('_'):
                return False
            return True

        for method_name in filter(enabled_methods, dir(dict)):
            method = LexClosureMethod(method_name)
            setattr(self, method_name, MethodType(method, self))

        atexit.register(self.save)

    def save(self):
        with self._config_path.open('w') as fp:
            json.dump(self._config_dict, fp, indent=4)

    def __len__(self):
        return self._config_dict.__len__()


class Img2CharConfig(Config):
    def __init__(self):
        super().__init__('img2char.json', IMG2CHAR_CONFIG_DIR)

        for k, v in self._config_dict.items():
            self._config_dict[k] = v.strip()


class CleanPatConfig(Config):
    def __init__(self):
        super().__init__('clean_pat.json', config_dir=CLEAN_PAT_CONFIG_DIR)


class Text2PathConfig(Config):
    def __init__(self):
        super().__init__('text2path.json')


class TencentCloudAppConfig(Config):
    def __init__(self):
        super().__init__('tencent_cloud_app.json')


class TencentOcr:
    def __init__(self, config=TencentCloudAppConfig()):
        tencent_cloud_app_config = config

        check_module('tencentcloud', 'tencentcloud-sdk-python')
        from tencentcloud.common import credential
        from tencentcloud.common.profile.client_profile import ClientProfile
        from tencentcloud.common.profile.http_profile import HttpProfile
        from tencentcloud.ocr.v20181119 import ocr_client


        secret_id = tencent_cloud_app_config.get('secret_id')
        secret_key = tencent_cloud_app_config.get('secret_key')
        ap_site = tencent_cloud_app_config.get('ap_site')  # such as "ap-shanghai"

        cred = credential.Credential(secret_id, secret_key)
        http_profile = HttpProfile()
        http_profile.endpoint = "ocr.tencentcloudapi.com"

        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        client = ocr_client.OcrClient(cred, ap_site, client_profile)

        self.client = client

    def request(self, img_url):
        from tencentcloud.ocr.v20181119 import models
        from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


        #req = models.GeneralHandwritingOCRRequest()
        req = models.GeneralAccurateOCRRequest()
        req.ImageUrl = img_url
        retry = 1

        while retry:
            try:
                resp = self.client.GeneralAccurateOCR(req)

            except TencentCloudSDKException as ex:
                print(str(ex)+'  ' + img_url)
                if ex.get_code() == 'FailedOperation.DownLoadError':
                    continue
                retry -= 1

                if retry < 0:
                    raise ex
            else:
                return resp.TextDetections[0].DetectedText


class UnrecognizedTextNameError(BaseException):
    def __init__(self, text_name):
        self.text_name = text_name

        super().__init__()

    def __str__(self):
        return f'Unrecognized text name: {self.text_name}\nPlease Add name2path mapping to config file'


class GetPageError(BaseException):
    def __init__(self, resp):
        self.req = resp.request
        self.resp = resp

        super().__init__()

    def __str__(self):
        return f'Get {self.req.url} page failed\n\t{self.resp.status_code},{self.resp.reason}'


def get_page(url: str) -> BeautifulSoup:
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise GetPageError(r)
    return BeautifulSoup(r.content, PARSER)


UrlType = str
ChapterNameType = str
LineNoType = TypeVar('LineNoType', int, str)
LocalChapterType = OrderedDict[ChapterNameType, LineNoType]
UpstreamChapterType = OrderedDict[ChapterNameType, UrlType]
PatchType = OrderedDict[ChapterNameType, Tuple[UrlType, LineNoType]]
OriginContentType = List[str]

CHAPTER_TITLE_PAT = re.compile('[*]{2}.*[\d|一|二|三|四|五|六|七|八|九|十]+.*[*]{2}')


# build clean pat list
def gen_clean_pat_list() -> List[Tuple[re.Pattern, str]]:
    clean_pat_config = CleanPatConfig()

    if normal_lines := clean_pat_config.get('normal_lines'):
        clean_pat_list = [(f'^(.*)(\s*{line}\s*)(.*)$', r'\1\3') for line in normal_lines]
    else:
        clean_pat_list = []


    return [(re.compile(item[0]), item[1]) for item in clean_pat_list]


CLEAN_PAT_LIST = gen_clean_pat_list()


def list_local_texts() -> List[Path]:
    return [Path(TEXT_DATABASE_DIR, fn)  for fn in filter(lambda fn: fn.endswith('.txt'), os.listdir(TEXT_DATABASE_DIR))]


class CangJingGe:
    def __init__(self, text_name, outdir:Path=None):
        CONFIG_DIR.mkdir(exist_ok=True)
        TEXT_DATABASE_DIR.mkdir(exist_ok=True)

        self.ocr = TencentOcr() if TencentCloudAppConfig() else None

        self.text2path_config = Text2PathConfig()
        self.text_name = text_name

        if text_path := self.text2path_config.get(text_name):
            self.MAIN_PAGE = urljoin(BASE_DOMAIN, text_path)
        else:
            raise UnrecognizedTextNameError(text_name)

        self.img2char_config = Img2CharConfig()

        self.outdir = outdir
        if outdir:
            outdir.mkdir(exist_ok=True)

        self.database_text_path = TEXT_DATABASE_DIR.joinpath(text_name + '.txt')
        if not self.database_text_path.exists():
            with self.database_text_path.open('w'):
                pass
            self.origin_contents = []
        else:
            with self.database_text_path.open('r') as fp:
                self.origin_contents = fp.readlines()

        self.imgtag2char_failed = False
        self.img_dict = build_img_dict()


    @staticmethod
    def diff_local_upstream(local_chapters: LocalChapterType,
                            upstream_chapters: UpstreamChapterType) -> PatchType:

        patch = OrderedDict()

        local_chapters_list = list(local_chapters.items())
        offset = 0
        for i, (upstream_chapter_name, url) in enumerate(upstream_chapters.items()):
            local_chapter_index = i - offset
            if local_chapter_item := getone(local_chapters_list, local_chapter_index):  # str or None
                local_chapter_name, _ = local_chapter_item

            if local_chapter_item is None or local_chapter_name != upstream_chapter_name:
                offset += 1

                if item := getone(local_chapters_list, local_chapter_index + 1):
                    insert_index = item[1]
                else:
                    insert_index = 'tail'

                patch[upstream_chapter_name] = url, insert_index

        return patch

    @staticmethod
    def parse_chapter_title(line):
        if match := re.search(CHAPTER_TITLE_PAT, line):
            return match.group(0)[2:-2]

    @staticmethod
    def trip_text(text):
        for clean_pat, rep in CLEAN_PAT_LIST:
            line_list = text.split('\n')
            line_list = [line.lstrip() for line in line_list]
            text = '\n'.join([re.sub(clean_pat, rep, line) for line in line_list])

        return text

    @staticmethod
    def build_local_chapters(origin_content: OriginContentType) -> LocalChapterType:
        local_chapters = OrderedDict()

        for i, line in enumerate(origin_content):
            if chapter_title := CangJingGe.parse_chapter_title(line):
                local_chapters[chapter_title] = i

        return local_chapters

    @staticmethod
    def guess_chapter_div(possible_chapter_divs):
        return possible_chapter_divs[-1]

    def fetch_chapters(self, page_link) -> UpstreamChapterType:
        bs_obj = get_page(page_link)
        possible_chapter_divs = bs_obj.find_all(
            'div', {'class': 'mod block update chapter-list'})

        chapter_div = CangJingGe.guess_chapter_div(possible_chapter_divs)
        chapter_ul = chapter_div.find('ul', {'class': 'list'})

        chapters = OrderedDict()
        for child in filter(lambda child: child.name == 'li', chapter_ul.children):
            atag = child.find('a')
            chapter_name = CangJingGe.trip_text(atag.text)
            chapters[chapter_name] = urljoin(self.MAIN_PAGE, atag['href'])

        next_chapter_list_link = urljoin(
            BASE_DOMAIN, bs_obj.find('a', text='下页')['href'])

        if next_chapter_list_link != page_link:
            chapters.update(self.fetch_chapters(next_chapter_list_link))

        return chapters

    @staticmethod
    def input_imgchar(img_url):
        while True:
            char = input(f'Please input char for {img_url}\n').strip()

            if not re.match(han, char):
                print(f'{char} is not valid char, only for cn char')
            else:
                return char

    def imgtag2char(self, img_tag):
        src = img_tag['src']
        key = Path(src).name
        if (char := self.img2char_config.get(key)) is None:
            img_url = urljoin(BASE_DOMAIN, src)

            if char := search_in_img_dict(self.img_dict, img_url):
                return char

            try:
                char = self.ocr.request(img_url).strip()

                if not re.match(han, char):
                    raise Exception(f'ocr recognize failed{char}\n{img_url}')

            except Exception as ex:
                if VERBOSE:
                    color.print_err(ex)
                # 直接交互解决不识别的字符
                char = CangJingGe.input_imgchar(img_url)
                self.img2char_config.update({key: char})
                self.img2char_config.save()
                self.img_dict = build_img_dict()
                # self.imgtag2char_failed = True
                # char = '<place-holder>'
                # color.print_err(img_url)
            else:
                if VERBOSE:
                    color.print_warn(f'ocr requested for {char}:{key}')

                self.img2char_config.update({key: char})
                self.img2char_config.save()

        return char

    def pull(self, n=None):
        origin_contents = self.origin_contents
        local_chapters = CangJingGe.build_local_chapters(origin_contents)
        color.print_info(f'Pulling from {self.MAIN_PAGE} ...')
        upstream_chapters = self.fetch_chapters(self.MAIN_PAGE)
        chapters_patch = CangJingGe.diff_local_upstream(local_chapters, upstream_chapters)

        patched_chapters_list = list(chapters_patch.items())
        if n:
            patched_chapters_list = patched_chapters_list[:n]

        for chapter_title, (url, index) in patched_chapters_list:
            chapter_content = CangJingGe.trip_text(self.fetch_chapter_content(url, None))
            chapter_title0 = f'**{chapter_title}**\n'

            if isinstance(index, int) and index >= 0:
                origin_contents.insert(index, chapter_title0)
                origin_contents.insert(index, chapter_content)
                origin_contents.insert(index, '\n\n\n')
            else:
                origin_contents.append(chapter_title0)
                origin_contents.append(chapter_content)
                origin_contents.append('\n\n\n')

            if VERBOSE:
                color.print_info(f'fetched {chapter_title}')

        # 字图识别失败不写入，避免污染数据
        if self.imgtag2char_failed:
            return

        origin_content = ''.join(origin_contents)
        with open(self.database_text_path, 'w', newline='\n', errors='ignore') as fp:
            fp.write(origin_content)

        if self.outdir:
            output_path = self.outdir.joinpath(self.text_name + '.txt')
            with self.outdir.open('w', newline='\n') as fp:
                fp.write(origin_content)

        color.print_info(f'Added {len(chapters_patch)} chapters.')
        color.print_ok(f'{self.text_name} was updated.')

    def fetch_chapter_content(self, page_url, next_part_links):
        bs_obj = get_page(page_url)
        page_content_block = bs_obj.find('div', {'class': 'page-content'})

        page_content = page_content_block.find('p')
        contents_list = []
        for child in page_content.children:
            if isinstance(child, str):
                contents_list.append(child)

            if child.name == 'br':
                contents_list.append('\n')

            if child.name == 'img':
                contents_list.append(self.imgtag2char(child))

        content = ''.join(contents_list)

        if next_part_links is None:
            links_block = page_content_block.find(
                'center', {'class': 'chapterPages'})
            next_part_links = [urljoin(self.MAIN_PAGE, atag['href'])
                               for atag in links_block.find_all('a')][1:]
            next_part_links.reverse()

        if next_part_links:
            content = ''.join([content,
                               self.fetch_chapter_content(next_part_links.pop(),
                                                            next_part_links)])

        return content


def common_exception_handler(ex):
    color.print_err(ex)


@cli_handle_exception(common_exception_handler, [GetPageError])
@cli_handle_exception(lambda _: _, [KeyError])
def cli():
    USAGE = """cjg
    cangjingge AKA 藏经阁的cli（笑）
    Usage:
      cjg list text-registries
      cjg add text-registry <text-name> <text-path>
      cjg rm text-registry <text-name>...
      cjg view img2char
      cjg update text <text-name>... [--outdir=<outdir>] [-n=<n>] [--verbose]
      cjg reclean text [--outdir=<outdir>]

    Options:
      list text             view all text-name-to-path mapping
      add text-mappings     add text-name-to-path mapping
      rm text-mappings      remove item by <text-name?
      reclean text          rerun text clean using current clean_pat.json

      <text-path>  text relative path (for BASE_DOMAIN), sucha as '/14/14438/'
      -o --outdir=<outdir>
      -n=<n>       int, number
      <text-name>  place-holder, "all" is supported!

    """
    arguments = docopt(USAGE, version=minghu6.__version__)

    # 可以使用search根据文件名直接在网站上搜，但不值当的
    if arguments['list'] and arguments['text-registries']:
        text_config = Text2PathConfig()

        if not text_config:
            color.print_info('<Empty>')

        for k, v in text_config.items():
            color.print_info(k, v)

    elif arguments['add'] and arguments['text-registry']:
        text_name = arguments['<text-name>'][0]
        path = arguments['<text-path>']

        text_config = Text2PathConfig()
        text_config.update({text_name: path})

    elif arguments['rm'] and arguments['text-registry']:
        text_config = Text2PathConfig()

        for text_name in arguments['<text-name>']:
            text_path = text_config.pop(text_name)
            text_config.save()
            color.print_err(f'removed {text_name}: {text_path}')

    elif arguments['update'] and arguments['text']:
        if 'all' in arguments['<text-name>']:
            text_config = Text2PathConfig()
            text_names = text_config.keys()
        else:
            text_names = arguments['<text-name>']

        outdir = arguments['--outdir']

        globals().update({'VERBOSE': arguments['--verbose']})

        # globals().update({'VERBOSE': True})  # 还是开着放心

        n = arguments['-n']

        if n:
            n = int(n)

        for text_name in text_names:
            cangjingge = CangJingGe(text_name, outdir)
            cangjingge.pull(n)

    elif arguments['reclean'] and arguments['text']:
        outdir = arguments['--outdir']

        for text in list_local_texts():
            with text.open() as fp:
                origin_content = fp.read()

            origin_content_len = len(origin_content)

            cleaned_content = CangJingGe.trip_text(origin_content)
            cleaned_content_len = len(cleaned_content)

            with open(text, 'w') as fp:
                fp.write(cleaned_content)

            if outdir:
                with Path(outdir).joinpath(text.name).open('w') as fp:
                    fp.write(cleaned_content)

            color.print_info(f'{text.name} has been cleaned {origin_content_len - cleaned_content_len} chars.')


    elif arguments['view'] and arguments['img2char']:
        img2char_config = Img2CharConfig()

        for k, v in img2char_config.items():
            color.print_info(k, v)


if __name__ == "__main__":
    cli()
