#!/usr/bin/env python3

import glob
import os
import pathlib
import re
import shutil

import jinja2
import mistune
from mistune.plugins.footnotes import footnotes
from PIL import Image
from pygments import highlight
from pygments.formatters import html
from pygments.lexers import get_lexer_by_name

tmpl_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates")
)
output_dir = pathlib.Path("static")

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
    img = re.sub(r"fill:#010101;", "fill:#1a84ff;", img)
    img = re.sub(r"fill:#020202;", "fill:#bbbbbb;", img)
    img = re.sub(r"fill:#030303;", "fill:#ffffff;", img)
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
img = re.sub(r"<svg",'<svg class="sandr0"',img)

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
    def __init__(self, date, post, title, html):
        self.date = date
        self.post = post
        self.title = title
        self.html = html

blog_data = [
    BlogData(
        date="2026-01-01",
        post="2026-01-catgpt",
        title="From Bug Bounty to CTF Challenge",
        html=f"""In December 2025, we hosted our latest {lnk("https://2025.ctf.link", "hxp CTF at 39C3")}. This is a writeup including backstory of how how my best web challenge (so far) came to be.""",
    ),
    BlogData(
        date="2025-03-15",
        post="2025-03-tirreno",
        title="tirreno - how to respectfully treat researchers",
        html=f"""In January 2025, I found an XSS in {lnk("https://tirreno.com", "tirreno")}. The response was objectively the best I ever got to a security report: Quick, high quality and respectful.""",
    ),
    BlogData(
        date="2024-04-07",
        post="2024-04-archiva",
        title="Technical Writeup for CVE-2023-28158",
        html=f"""In March 2023, I got the opportunity to identify and report a stored XSS vulnerability in {lnk("https://archiva.apache.org/", "Apache Archiva 2.2.9")}. The vulnerability got awarded {lnk("https://www.cve.org/CVERecord?id=CVE-2023-28158", "CVE-2023-28158")}.""",
    ),
    BlogData(
        date="2023-08-01",
        post="2023-08-pentest-report",
        title="Redacted Pentest Report of a PHP Web App",
        html=f"""In February 2023, I got hired to do a whitebox pentest of a PHP web app. The redacted report can be found here {lnk("/blog/2023-08-pentest-report/pentest_report_redacted.pdf", "[PDF]")}.""",
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
        domain="https://recipes.sandr0.xyz",
        desc="My personal recipe collection",
        file="recipes.jpg"
    ),
    ProjectData(
        domain="https://series-tracker.sandr0.xyz",
        desc="The status of my series",
        file="series.jpg"
    ),
    ProjectData(
        domain="https://github.com/Sandr0x00/find-the-chicken",
        desc="Gameboy CTF challenge for hxp CTF 2020",
        file="find-the-chicken.png"
    ),
    ProjectData(
        domain="https://github.com/Sandr0x00/gameboy-is-you",
        desc="Gameboy CTF challenge for hxp CTF 2021",
        file="gameboy-is-you.png"
    ),
    ProjectData(
        domain="https://doktor-eisenbarth.de",
        desc="Web Development for Doktor Eisenbarth Festspielverein Oberviechtach",
        file="doktor-eisenbarth.jpg"
    ),
    ProjectData(
        domain="https://www.michael-konstantin.de",
        desc="Web Development for Michael Konstantin",
        file="michael-konstantin.jpg"
    ),
    ProjectData(
        domain="https://almenrausch-pirkhof.de",
        desc="Web Development for Almenrausch Pirkhof Schützenverein Pirkhof",
        file="almenrausch-pirkhof.jpg"
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
    CtfData(
        name="CatGPT",
        cat="web",
        desc=f"""A web challenge for {lnk("https://2025.ctf.link","hxp 39C3 CTF")} focusing on a bug in {lnk("https://github.com/matomo-org/device-detector", "device-detector")} where it allowed a 1-byte arbitrary match. [{lnk("https://2025.ctf.link/internal/challenge/215a7124-8c97-49e3-9979-b2eeee05b572/","challenge")}, {lnk("/blog/2026-01-catgpt","writeup")}]"""),
    CtfData(
        name="sponsored",
        cat="msc",
        desc=f"""A pyjail challenge for {lnk("https://2025.ctf.link","hxp 39C3 CTF")} focusing on hardening the challenge <code>excepython</code> from SECCON 14 Qualifiers by removing exceptions and loops. [{lnk("https://2025.ctf.link/internal/challenge/254cdc49-74bb-4224-bc34-5e1c9d2f7dae/","challenge")}]"""),
    CtfData(
        name="shell(de)coding",
        cat="msc",
        desc=f"""A simple shellcoding challenge for {lnk("https://2025.ctf.link","hxp 39C3 CTF")} to code "base64 decode" in the shortest bytes possible on order to decode random 32 bytes. The current shortest known (feasible, only support <code>A-Za-z</code>) solution for this challenge is <code>b104ac2c413c1976022c06c1e30608c7e2f089d80fc8abffcfebe5</code> (by "Tethys"). [{lnk("https://2025.ctf.link/internal/challenge/d411c024-6c0e-47fa-960e-21701937f25e/","challenge")}]"""),
    CtfData(
        name="algorave",
        cat="rev",
        desc=f"""A reversing challenge for {lnk("https://2025.ctf.link","hxp 39C3 CTF")} displaying the flag via the pianoroll feature of {lnk("https://strudel.cc/", "strudel.cc")}. The flag consists of notes which are picked based on a modified recursive (and therefore unperformant) fibonacci like algorithm. [{lnk("https://2025.ctf.link/internal/challenge/0e43c947-7da0-41e0-b80b-01d7f6863631/","challenge")}]"""),
    CtfData(
        name="NeedForSpeed",
        cat="msc",
        desc=f"""A miscellaneous challenge for {lnk("https://2024.ctf.link","hxp 38C3 CTF")} focusing on insecure default behaviour of the {lnk("https://en.wikipedia.org/wiki/Network_File_System", "Network File System")} server. The challenge was created as a collaboration with {lnk("https://github.com/philipp-tg", "philipp-tg")} and {lnk("https://github.com/edermi", "edermi")}. [{lnk("https://2024.ctf.link/internal/challenge/b964e61c-5d98-41b9-9f3a-1bb129e6ce24/","challenge")}, {lnk("https://hxp.io/blog/111/","writeup")}, {lnk("https://www.hvs-consulting.de/en/nfs-security-identifying-and-exploiting-misconfigurations/", "further research")}]"""),
    CtfData(
        name="HaRlEm ShAkE",
        cat="rev",
        desc=f"""A Rust reversing challenge for {lnk("https://2024.ctf.link","hxp 38C3 CTF")} focusing on funny and weird X11 features. [{lnk("https://2024.ctf.link/internal/challenge/168a3050-bd0b-4053-930a-366d0fe82294/","challenge")}, {lnk("https://hxp.io/blog/112/","writeup")}]"""),
    CtfData(
        name="archived",
        cat="zaj",
        desc=f"""A zero-day web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} targeting Apache Archiva 2.2.9. The challenge is based on a vulnerability I discovered which was assigned {lnk("https://www.cve.org/CVERecord?id=CVE-2023-28158","CVE-2023-28158")}. [{lnk("https://2022.ctf.link/internal/challenge/b2ca2268-f49f-4103-9943-2a417244a955","challenge")}, {lnk("https://hxp.io/blog/100/","writeup")}]"""),
    CtfData(
        name="required",
        cat="rev",
        desc=f"""A challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} using the prototype pollution discussed in the challenge {lnk("https://ctf.zeyu2001.com/2022/balsnctf-2022/2linenodejs","2linenodejs")} as a way to obfuscate NodeJS code. [{lnk("https://2022.ctf.link/internal/challenge/7e3e425c-865d-4025-9005-09806d951cca","challenge")}, {lnk("https://hxp.io/blog/103/","writeup")}]"""),
    CtfData(
        name="sqlite_web",
        cat="web",
        desc=f"""A web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} focusing on a insecure design choice in {lnk("https://github.com/coleifer/sqlite-web","sqlite-web")} leading to remote code execution. {lnk("https://github.com/coleifer/sqlite-web/issues/111","Remains unfixed.")} [{lnk("https://2022.ctf.link/internal/challenge/dbb4626c-3390-43d2-88bf-4d4c22c33315","challenge")}, {lnk("https://hxp.io/blog/102/","writeup")}]"""),
    CtfData(
        name="valentine",
        cat="web",
        desc=f"""A web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} exploring {lnk("https://github.com/mde/ejs","ejs")} 3.1.8 after {lnk("https://eslam.io/posts/ejs-server-side-template-injection-rce/","CVE-2022-29078")} was fixed. [{lnk("https://2022.ctf.link/internal/challenge/8f5b680d-d57a-4609-94e9-37593f9d4f2a","challenge")}, {lnk("https://hxp.io/blog/101/","short writeup")}, {lnk("https://github.com/ispoleet/ctf-writeups/tree/master/hxp_ctf_2022/required","extended writeup")}]"""),
    CtfData(
        name="baba is you",
        cat="msc",
        desc=f"""A misc challenge for {lnk("https://2021.ctf.link","hxp CTF 2021")} inspired by {lnk("https://hempuli.com/baba/","baba is you")} written in C for Gameboy. [{lnk("https://2021.ctf.link/internal/challenge/52c2a607-7e05-456f-b8c0-68952304f2a4/","challenge")}, {lnk("https://baba.hxp.io/","scoreboard")}, {lnk("https://github.com/Sandr0x00/gameboy-is-you/blob/","source")}, {lnk("https://github.com/Sandr0x00/gameboy-is-you/blob/main/writeup/readme.md","writeup")}]"""),
    CtfData(
        name="find the chicken",
        cat="msc",
        desc=f"""A gameboy challenge for {lnk("https://2020.ctf.link","hxp CTF 2020")} written in C. Reverse the game and find the chicken. [{lnk("https://2020.ctf.link/internal/challenge/7e09f315-2f7b-4f0a-bcaf-934cc298e263/","challenge")}, {lnk("https://chicken.hxp.io/","scoreboard")}, {lnk("https://github.com/Sandr0x00/find-the-chicken","source")}, {lnk("https://hxp.io/blog/80/","solution run")}]"""),
],
[
    CtfData(
        name="PDF-Xfiltration",
        cat="",
        desc=f"""My {lnk("https://hxp.io/blog/93/Insomnihack-2022-PDF-Xfiltration","writeup")} to a challenge from Insomni'hack 2022 about breaking PDF signatures using JavaScript."""),
    CtfData(
        name="pypypypy",
        cat="",
        desc=f"""My {lnk("https://hxp.io/blog/85/0CTFTCTF-2021-Quals-selected-writeups#pypypypy","writeup")} to a python sandbox escape from 0CTF 2021 Quals."""),
    CtfData(
        name="Cloud Computing",
        cat="",
        desc=f"""My {lnk("https://hxp.io/blog/74/0CTF%202020%20writeups#cloud-computing","writeup")} for a PHP sandbox escape from 0CTF 2020 Quals."""),
    CtfData(
        name="Bonzi Scheme",
        cat="",
        desc=f"""My {lnk("https://hxp.io/blog/71/PlaidCTF-2020-Bonzi-Scheme","totally serious guide")} of how to "hack hex with hyx" solving a challenge of PlaidCTF 2020."""),
    CtfData(
        name="PlayCAP",
        cat="",
        desc=f"""My {lnk("https://hxp.io/blog/59/Teaser-Dragon-CTF-2019-PlayCAP-writeup","writeup")} for a challenge at Teaser Dragon CTF 2019 about reversing a PCAP to find pressed buttons of an XBOX controller."""),
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
img = re.sub(r"<svg",'<svg class="logo"',img)

# sandr0.xyz/
template = tmpl_env.get_template("main.html")
with open(output_dir / "index.html", "w") as f:
    f.write(template.render(img=img, parts=parts))

# sandr0.xyz/blog
template = tmpl_env.get_template("blog.html")
output = output_dir / "blog"
output.mkdir(parents=True, exist_ok=True)
with open(output / "index.html", "w") as f:
    f.write(template.render(img=img, blog_data=blog_data, parts=parts))

class HighlightRenderer(mistune.HTMLRenderer):
    def __init__(self):
        super().__init__(escape=False)

    def block_code(self, code, info=None):
        if info:
            # print(code)
            highlighted_rows = []
            for c, line in enumerate(code.splitlines()):
                if line.startswith("!!"):
                    highlighted_rows.append(c + 1)
            code = code.replace("!!", "")
            # print(highlighted_rows)
            lexer = get_lexer_by_name(info, stripall=True)
            formatter = html.HtmlFormatter(linenos="table", hl_lines=highlighted_rows)
            return highlight(code, lexer, formatter)
        return '<pre><code>' + mistune.escape(code) + '</code></pre>'

template = tmpl_env.get_template("blog-post.html")
markdown = mistune.Markdown(HighlightRenderer(), plugins=[footnotes])

# sandr0.xyz/blog/*
for root, dirs, files in os.walk("blog"):
    # print(root, dirs, files)
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

        # print(p)
