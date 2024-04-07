#!/usr/bin/env python3

import re
import os
from PIL import Image
import glob
import jinja2
import pathlib
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html
from mistune.plugins.footnotes import footnotes
import shutil

tmpl_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates")
)

class Part():

    def __init__(self, id, title, data):
        self.id = id
        self.title = title
        self.data = data

        file_name = f"resources/{self.id}.svg"
        print(file_name)
        if not os.path.exists(file_name):
            file_name = "resources/blank.svg"

        self.img = svg(file_name)

def resize(file_name):
    if not os.path.exists("static/img"):
        os.mkdir("static/img")
    sizes = []
    if (m := re.search(r"^(?P<name>.*)\.(?P<ext>...)$", file_name)):
        file_name = m.group("name")
        ext = m.group("ext")
    else:
        ext = "jpg"
    im = Image.open(f"resources/{file_name}.{ext}")
    im.save(f"static/img/{file_name}.{ext}")
    for s in [im.width, 1400, 1000, 800, 600, 400]:
        sizes.append(f"img/{file_name}-{s}.webp {s}w")
        if os.path.exists(f"static/img/{file_name}-{s}.webp"):
            continue
        im.thumbnail((s, s))
        im.save(f"static/img/{file_name}-{s}.webp", "webp")
    return (f"img/{file_name}.{ext}", ', '.join(sizes))

def icon(file_name, height):
    im = Image.open(f"resources/{file_name}.png")
    if os.path.exists(f"static/{file_name}.webp"):
        return
    im.thumbnail((1000, height))
    im.save(f"static/{file_name}.webp", "webp")

def svg(file_name):
    '''
    Read file and return it as inline svg
    '''
    with open(file_name, "r") as f:
        img = f.read()
    # print(img)
    img = re.sub(r'<\?xml version="1.0" encoding="UTF-8" standalone="no"\?>', "", img)
    img = re.sub(r'(style=".*)fill:#010101;', r'class="highlight" \g<1>', img)
    img = re.sub(r"fill:#010101;",f"fill:#1a84ff;",img)
    img = re.sub(r"fill:#020202;",f"fill:#bbbbbb;",img)
    img = re.sub(r"fill:#030303;",f"fill:#ffffff;",img)
    return img

parts = []

def lnk(url, to, title=None, others=None):
    if title:
        title = f""" title="{title}" """
    return f"""<a href="{url}" {title} {others}>{to}</a>"""


#===========================================================
# about
#===========================================================

img = svg("resources/sandr0.svg")
img = re.sub(r"<svg",f'<svg class="sandr0"',img)

about_data = [
    lnk(
        "https://hxp.io",
        '<img src="/icon_hxp.webp" alt="hxp logo">',
        title="hxp",
    ),
    lnk(
        "https://kompilers.com/",
        'k',
        title='kompilers',
        others='class="kompilers"',
    ),
    lnk(
        "https://github.com/Sandr0x00",
        '<img src="/github.svg" alt="GitHub logo">',
        title="Github",
    ),
    lnk(
        "https://www.linkedin.com/in/sandr0x00/",
        '<img src="/linkedin.png" alt="LinkedIn logo">',
        title="LinkedIn",
    ),
    lnk(
        "https://twitter.com/Sandr0x00",
        '<img src="/twitter.svg" alt="Twitter logo">',
        title="Twitter",
    ),
    lnk(
        "https://infosec.exchange/@sandr0",
        '<img src="/mastodon.svg" alt="Mastodon logo">',
        title="Mastodon",
        others='rel="me"'
    ),
]

parts.append(Part("about", "About", about_data))


#===========================================================
# blog
#===========================================================

class BlogData:
    def __init__(self, post, title, html):
        self.post = post
        self.title = title
        self.html = html

blog_data = [
    BlogData(
        "01-pentest-report",
        "Redacted Pentest Report of a PHP Web App",
        f"""In February 2023, I got hired to do a whitebox pentest of a PHP web app. The redacted report can be found here {lnk("/blog/01-pentest-report/pentest_report_redacted.pdf", "[PDF]")}.""",
    ),
    BlogData(
        "02-archiva",
        "Technical Writeup for CVE-2023-28158",
        f"""In March 2023, I got the opportunity to identify and report a stored XSS vulnerability in {lnk("https://archiva.apache.org/", "Apache Archiva 2.2.9")}. The vulnerability got awarded {lnk("https://www.cve.org/CVERecord?id=CVE-2023-28158", "CVE-2023-28158")}.""",
    ),
]

parts.append(Part("blog", "Blog", blog_data))


#===========================================================
# projects
#===========================================================

class ProjectData:
    def __init__(self, domain, desc, file):
        self.domain = domain
        self.desc = desc
        self.file = file
        fallback, sizes = resize(file)
        self.fallback = fallback
        self.sizes = sizes

web_data = [
    ProjectData(
        "https://recipes.sandr0.xyz",
        "My personal recipe collection",
        "recipes.jpg"
    ),
    ProjectData(
        "https://series-tracker.sandr0.xyz",
        "The status of my series",
        "series.jpg"
    ),
    ProjectData(
        "https://github.com/Sandr0x00/find-the-chicken",
        "Gameboy CTF challenge for hxp CTF 2020",
        "find-the-chicken.png"
    ),
    ProjectData(
        "https://github.com/Sandr0x00/gameboy-is-you",
        "Gameboy CTF challenge for hxp CTF 2021",
        "gameboy-is-you.png"
    ),
    ProjectData(
        "https://doktor-eisenbarth.de",
        "Web Development for Doktor Eisenbarth Festspielverein Oberviechtach",
        "doktor-eisenbarth.jpg"
    ),
    ProjectData(
        "https://www.michael-konstantin.de",
        "Web Development for Michael Konstantin",
        "michael-konstantin.jpg"
    ),
    ProjectData(
        "https://almenrausch-pirkhof.de",
        "Web Development for Almenrausch Pirkhof Schützenverein Pirkhof",
        "almenrausch-pirkhof.jpg"
    ),
    # <a href="https://schreiner-suess.de" title="Website for Schreinerei Andreas Süß Fuchsberg"><img class="client-work" src="schreiner-suess.png" alt="schreiner-suess"></a>
]

parts.append(Part("projects", "Personal Projects", web_data))


#===========================================================
# CTF
#===========================================================

class CtfData:
    def __init__(self, name, cat, desc):
        self.name = name
        self.cat = cat
        self.desc = desc

ctf = ([
    CtfData("archived", "zaj",
    f"""A zero-day web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} targeting Apache Archiva 2.2.9. The challenge is based on a vulnerability I discovered which was assigned {lnk("https://www.cve.org/CVERecord?id=CVE-2023-28158","CVE-2023-28158")}. [{lnk("https://2022.ctf.link/internal/challenge/b2ca2268-f49f-4103-9943-2a417244a955","challenge")}, {lnk("https://hxp.io/blog/100/hxp-CTF-2022-archived/","writeup")}]"""),
    CtfData("required", "rev",
    f"""A challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} using the prototype pollution discussed in the challenge {lnk("https://ctf.zeyu2001.com/2022/balsnctf-2022/2linenodejs","2linenodejs")} as a way to obfuscate NodeJS code. [{lnk("https://2022.ctf.link/internal/challenge/7e3e425c-865d-4025-9005-09806d951cca","challenge")}, {lnk("https://hxp.io/blog/103/hxp-CTF-2022-required/","writeup")}]"""),
    CtfData("sqlite_web", "web",
    f"""A web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} focusing on a insecure design choice in {lnk("https://github.com/coleifer/sqlite-web","sqlite-web")} leading to remote code execution. {lnk("https://github.com/coleifer/sqlite-web/issues/111","Remains unfixed.")} [{lnk("https://2022.ctf.link/internal/challenge/dbb4626c-3390-43d2-88bf-4d4c22c33315","challenge")}, {lnk("https://hxp.io/blog/102/hxp-CTF-2022-sqlite_web/","writeup")}]"""),
    CtfData("valentine", "web",
    f"""A web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} exploring {lnk("https://github.com/mde/ejs","ejs")} 3.1.8 after {lnk("https://eslam.io/posts/ejs-server-side-template-injection-rce/","CVE-2022-29078")} was fixed. [{lnk("https://2022.ctf.link/internal/challenge/8f5b680d-d57a-4609-94e9-37593f9d4f2a","challenge")}, {lnk("https://hxp.io/blog/101/hxp-CTF-2022-valentine/","short writeup")}, {lnk("https://github.com/ispoleet/ctf-writeups/tree/master/hxp_ctf_2022/required","extended writeup")}]"""),
    CtfData("baba is you", "msc",
    f"""A misc challenge for {lnk("https://2021.ctf.link","hxp CTF 2021")} inspired by {lnk("https://hempuli.com/baba/","baba is you")} written in C for Gameboy. [{lnk("https://2021.ctf.link/internal/challenge/52c2a607-7e05-456f-b8c0-68952304f2a4/","challenge")}, {lnk("https://baba.hxp.io/","scoreboard")}, {lnk("https://github.com/Sandr0x00/gameboy-is-you/blob/","source")}, {lnk("https://github.com/Sandr0x00/gameboy-is-you/blob/main/writeup/readme.md","writeup")}]"""),
    CtfData("find the chicken", "msc",
    f"""A gameboy challenge for {lnk("https://2020.ctf.link","hxp CTF 2020")} written in C. Reverse the game and find the chicken. [{lnk("https://2020.ctf.link/internal/challenge/7e09f315-2f7b-4f0a-bcaf-934cc298e263/","challenge")}, {lnk("https://chicken.hxp.io/","scoreboard")}, {lnk("https://github.com/Sandr0x00/find-the-chicken","source")}, {lnk("https://hxp.io/blog/80/hxp-CTF-2020-find-the-chicken","solution run")}]"""),
],
[
    CtfData("PDF-Xfiltration", "",
    f"""My {lnk("https://hxp.io/blog/93/Insomnihack-2022-PDF-Xfiltration","writeup")} to a challenge from Insomni'hack 2022 about breaking PDF signatures using JavaScript."""),
    CtfData("pypypypy", "",
    f"""My {lnk("https://hxp.io/blog/85/0CTFTCTF-2021-Quals-selected-writeups#pypypypy","writeup")} to a python sandbox escape from 0CTF 2021 Quals."""),
    CtfData("Cloud Computing", "",
    f"""My {lnk("https://hxp.io/blog/74/0CTF%202020%20writeups#cloud-computing","writeup")} for a PHP sandbox escape from 0CTF 2020 Quals."""),
    CtfData("Bonzi Scheme", "",
    f"""My {lnk("https://hxp.io/blog/71/PlaidCTF-2020-Bonzi-Scheme","totally serious guide")} of how to "hack hex with hyx" solving a challenge of PlaidCTF 2020."""),
    CtfData("PlayCAP", "",
    f"""My {lnk("https://hxp.io/blog/59/Teaser-Dragon-CTF-2019-PlayCAP-writeup","writeup")} for a challenge at Teaser Dragon CTF 2019 about reversing a PCAP to find pressed buttons of an XBOX controller."""),
])

for ico in ["icon_web", "icon_zaj", "icon_hxp-ctf", "icon_hxp", "icon_msc", "icon_rev"]:
    icon(ico, 100)

parts.append(Part("ctf", "CTF Writeups", ctf))


#===========================================================
# fun
#===========================================================

parts.append(Part("fun", "Fun", ""))


#===========================================================
# formatting
#===========================================================

img = svg("resources/sandr0.xyz.svg")

# print(img)
img = re.sub(r"<svg",f'<svg class="logo"',img)
# print(img)


template = tmpl_env.get_template("main.html")

output_dir = pathlib.Path("static")

with open(output_dir / "index.html", "w") as f:
    f.write(template.render(img=img, parts=parts))

class HighlightRenderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__(escape=False)

    def block_code(self, code, info=None):
        if info:
            print(code)
            highlighted_rows = []
            for c, l in enumerate(code.splitlines()):
                if l.startswith("!!"):
                    highlighted_rows.append(c + 1)
            code = code.replace("!!", "")
            print(highlighted_rows)
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = html.HtmlFormatter(linenos="table", hl_lines=highlighted_rows)
            return highlight(code, lexer, formatter)
        return '<pre><code>' + mistune.escape(code) + '</code></pre>'

template = tmpl_env.get_template("blog.html")
output = output_dir / "blog"
output.mkdir(parents=True, exist_ok=True)
with open(output / "index.html", "w") as f:
    f.write(template.render(img=img, blog_data=blog_data, parts=parts))

template = tmpl_env.get_template("blog-post.html")
markdown = mistune.Markdown(HighlightRenderer(), plugins=[footnotes])

for root, dirs, files in os.walk("blog"):
    print(root, dirs, files)
    for file in files:
        p = pathlib.Path(root)
        output = output_dir / root
        output.mkdir(parents=True, exist_ok=True)
        if file == "index.md":
            with open(p / "index.md") as f:
                md = f.read()
            output_html = markdown(md)

            with open(output / "index.html", "w") as f:
                f.write(template.render(img=img, content=output_html, parts=parts))
        else:
            shutil.copyfile(p / file, output / file)


        print(p)