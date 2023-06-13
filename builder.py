#!/usr/bin/env python3

import re
import os
from PIL import Image
import glob

class Part():
    id = None
    title = None
    content = None

    def __init__(self, id, title, content):
        self.id = id
        self.title = title
        self.content = content

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

lnk = lambda url, to: f"""<a href="{url}">{to}</a>"""

#===========================================================
# about
#===========================================================

img = svg("resources/sandr0.svg")
img = re.sub(r"<svg",f'<svg class="sandr0"',img)

about_data = [
  '<a href="https://hxp.io" title="hxp"><img src="/icon_hxp.webp" alt="hxp logo"></a>',
  '<a class="kompilers" href="https://kompilers.com/" title="kompilers">k</a>',
  '<a href="mailto:freelancing@sandr0.xyz" title="Hire me as a freelancer"><i class="fas fa-laptop-code fa-2x"></i></a>',
  '<a href="https://github.com/Sandr0x00" title="Github"><img src="/github.svg" alt="GitHub logo"></a>',
  '<a href="https://www.linkedin.com/in/sandr0x00/" title="LinkedIn"><img src="/linkedin.png" alt="LinkedIn logo"></a>',
  '<a href="https://twitter.com/Sandr0x00" title="Twitter"><img src="/twitter.svg" alt="Twitter logo"></a>',
  '<a rel="me" href="https://infosec.exchange/@sandr0" title="Mastodon"><img src="/mastodon.svg" alt="Mastodon logo"></a>',
]

parts.append(Part("about", "About", " | ".join(about_data)))

#===========================================================
# projects
#===========================================================

web_data = [
  # website, description, file
  ["https://recipes.sandr0.xyz", "My personal recipe collection", "recipes.jpg"],
  ["https://series-tracker.sandr0.xyz", "The status of my series", "series.jpg"],
  ["https://github.com/Sandr0x00/find-the-chicken", "Gameboy CTF challenge for hxp CTF 2020", "find-the-chicken.png"],
  ["https://github.com/Sandr0x00/gameboy-is-you", "Gameboy CTF challenge for hxp CTF 2021", "gameboy-is-you.png"],
]

content = ""
for i in web_data:
  domain, description, file_name = i
  fallback, sizes = resize(file_name)
  content += f"""<a class="client-work" href="{domain}" title="{description}">
<img sizes="(min-width: 576px) 50vw, (min-width: 1200px) 33vw, 100vw" src="{fallback}" class="client-work" alt="{file_name}" srcset="{sizes}">
</a>"""

parts.append(Part("projects", "Personal Projects", content))

#===========================================================
# CTF
#===========================================================

ctf = {
  f"""Stuff I created for {lnk("https://ctf.link",'<img src="/icon_hxp-ctf.webp" alt="hxp CTF logo">')}""": [
    ("archived", "zaj",
    f"""A zero-day web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} targeting Apache Archiva 2.2.9. The challenge is based on a vulnerability I discovered which was assigned {lnk("https://www.cve.org/CVERecord?id=CVE-2023-28158","CVE-2023-28158")}. [{lnk("https://2022.ctf.link/internal/challenge/b2ca2268-f49f-4103-9943-2a417244a955","challenge")}, {lnk("https://hxp.io/blog/100/hxp-CTF-2022-archived/","writeup")}]"""),
    ("required", "rev",
    f"""A challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} using the prototype pollution discussed in the challenge {lnk("https://ctf.zeyu2001.com/2022/balsnctf-2022/2linenodejs","2linenodejs")} as a way to obfuscate NodeJS code. [{lnk("https://2022.ctf.link/internal/challenge/7e3e425c-865d-4025-9005-09806d951cca","challenge")}, {lnk("https://hxp.io/blog/103/hxp-CTF-2022-required/","writeup")}]"""),
    ("sqlite_web", "web",
    f"""A web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} focusing on a insecure design choice in {lnk("https://github.com/coleifer/sqlite-web","sqlite-web")} leading to remote code execution. {lnk("https://github.com/coleifer/sqlite-web/issues/111","Remains unfixed.")} [{lnk("https://2022.ctf.link/internal/challenge/dbb4626c-3390-43d2-88bf-4d4c22c33315","challenge")}, {lnk("https://hxp.io/blog/102/hxp-CTF-2022-sqlite_web/","writeup")}]"""),
    ("valentine", "web",
    f"""A web challenge for {lnk("https://2022.ctf.link","hxp CTF 2022")} exploring {lnk("https://github.com/mde/ejs","ejs")} 3.1.8 after {lnk("https://eslam.io/posts/ejs-server-side-template-injection-rce/","CVE-2022-29078")} was fixed. [{lnk("https://2022.ctf.link/internal/challenge/8f5b680d-d57a-4609-94e9-37593f9d4f2a","challenge")}, {lnk("https://hxp.io/blog/101/hxp-CTF-2022-valentine/","short writeup")}, {lnk("https://github.com/ispoleet/ctf-writeups/tree/master/hxp_ctf_2022/required","extended writeup")}]"""),
    ("baba is you", "msc",
    f"""A misc challenge for {lnk("https://2021.ctf.link","hxp CTF 2021")} inspired by {lnk("https://hempuli.com/baba/","baba is you")} written in C for Gameboy. [{lnk("https://2021.ctf.link/internal/challenge/52c2a607-7e05-456f-b8c0-68952304f2a4/","challenge")}, {lnk("https://baba.hxp.io/","scoreboard")}, {lnk("https://github.com/Sandr0x00/gameboy-is-you/blob/","source")}, {lnk("https://github.com/Sandr0x00/gameboy-is-you/blob/main/writeup/readme.md","writeup")}]"""),
    ("find the chicken", "msc",
    f"""A gameboy challenge for {lnk("https://2020.ctf.link","hxp CTF 2020")} written in C. Reverse the game and find the chicken. [{lnk("https://2020.ctf.link/internal/challenge/7e09f315-2f7b-4f0a-bcaf-934cc298e263/","challenge")}, {lnk("https://chicken.hxp.io/","scoreboard")}, {lnk("https://github.com/Sandr0x00/find-the-chicken","source")}, {lnk("https://hxp.io/blog/80/hxp-CTF-2020-find-the-chicken","solution run")}]"""),
  ],
  f"""Stuff I broke with {lnk("https://hxp.io",'<img src="/icon_hxp.webp" alt="hxp logo">')} (excerpt)""": [
    ("PDF-Xfiltration", "",
    f"""My {lnk("https://hxp.io/blog/93/Insomnihack-2022-PDF-Xfiltration","writeup")} to a challenge from Insomni'hack 2022 about breaking PDF signatures using JavaScript."""),
    ("pypypypy", "",
    f"""My {lnk("https://hxp.io/blog/85/0CTFTCTF-2021-Quals-selected-writeups#pypypypy","writeup")} to a python sandbox escape from 0CTF 2021 Quals."""),
    ("Cloud Computing", "",
    f"""My {lnk("https://hxp.io/blog/74/0CTF%202020%20writeups#cloud-computing","writeup")} for a PHP sandbox escape from 0CTF 2020 Quals."""),
    ("Bonzi Scheme", "",
    f"""My {lnk("https://hxp.io/blog/71/PlaidCTF-2020-Bonzi-Scheme","totally serious guide")} of how to "hack hex with hyx" solving a challenge of PlaidCTF 2020."""),
    ("PlayCAP", "",
    f"""My {lnk("https://hxp.io/blog/59/Teaser-Dragon-CTF-2019-PlayCAP-writeup","writeup")} for a challenge at Teaser Dragon CTF 2019 about reversing a PCAP to find pressed buttons of an XBOX controller."""),
  ],
}

for ico in ["icon_web", "icon_zaj", "icon_hxp-ctf", "icon_hxp", "icon_msc", "icon_rev"]:
  icon(ico, 100)

content = ""
for title, ctf_challs in ctf.items():
  content += f"<h3>{title}</h3>"
  for chall_name, chall_type, chall_desc in ctf_challs:
    assert '"' not in chall_name
    # assert '"' not in chall_writeup
    content += f"""<div class="post">"""
    if chall_type:
      content += f"""<img src="/icon_{chall_type}.webp" alt="hxp CTF icon for {chall_type} challenges">"""
    content += f"""<strong>{chall_name}</strong><br/>
<p class="desc">{chall_desc}</p>
</div>\n"""

parts.append(Part("ctf", "CTF Writeups", f"""
<p>
{content}
</p>
"""))

#===========================================================
# web dev
#===========================================================

web_data = [
  # website, description, file
  ["https://www.michael-konstantin.de", "Michael Konstantin", "michael-konstantin"],
  ["https://almenrausch-pirkhof.de", "Almenrausch Pirkhof Schützenverein Pirkhof", "almenrausch-pirkhof"],
  ["http://juliagruber.de", "Julia Gruber", "juliagruber"],
  ["https://doktor-eisenbarth.de", "Doktor Eisenbarth Festspielverein Oberviechtach", "doktor-eisenbarth"],
]

content = ""
for i in web_data:
  domain, description, file_name = i
  fallback, sizes = resize(file_name)
  content += f"""<a class="client-work" href="{domain}" title="Website for {description}">
<img sizes="(min-width: 576px) 50vw, (min-width: 1200px) 33vw, 100vw" class="client-work" src="{fallback}" alt="{file_name}" srcset="{sizes}">
</a>"""

parts.append(Part("web", "Freelance Work (Non NDA) / Web Development", content))
# <a href="https://schreiner-suess.de" title="Website for Schreinerei Andreas Süß Fuchsberg"><img class="client-work" src="schreiner-suess.png" alt="schreiner-suess"></a>


#===========================================================
# fun
#===========================================================

parts.append(Part("fun", "Fun", """
<p>Don't like the style of my website? Redesign it yourself!</p>
<style style="display:block; background-color: #444; padding:.5em; font-family: monospace;" contenteditable="">
body{
  color:#dddddd;
  background-color:#00060e
}
.highlight {
  fill: #1a84ff
}
a:visited,a {
  color: #1a84ff
}
</style><br>
"""))



img = svg("resources/sandr0.xyz.svg")

# print(img)
img = re.sub(r"<svg",f'<svg class="logo"',img)
# print(img)

page = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="css.css">
  <meta name="description" content="Personal webpage of sandr0.">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- generics -->
  <link rel="icon" href="favicon-32.png" sizes="32x32">
  <link rel="icon" href="favicon-57.png" sizes="57x57">
  <link rel="icon" href="favicon-76.png" sizes="76x76">
  <link rel="icon" href="favicon-96.png" sizes="96x96">
  <link rel="icon" href="favicon-128.png" sizes="128x128">
  <link rel="icon" href="favicon-192.png" sizes="192x192">
  <link rel="icon" href="favicon-228.png" sizes="228x228">

  <!-- Android -->
  <link rel="shortcut icon" sizes="196x196" href="favicon-196.png">

  <!-- iOS -->
  <link rel="apple-touch-icon" href="favicon-120.png" sizes="120x120">
  <link rel="apple-touch-icon" href="favicon-152.png" sizes="152x152">
  <link rel="apple-touch-icon" href="favicon-180.png" sizes="180x180">

  <!-- Windows 8 IE 10-->
  <meta name="msapplication-TileColor" content="#FFFFFF">
  <meta name="msapplication-TileImage" content="favicon-144.png">

  <!-- Windows 8.1 + IE11 and above -->
  <meta name="msapplication-config" content="browserconfig.xml" />
  <title>Sandr0.xyz</title>

  <!-- OG -->
  <meta property="og:image" content="https://sandr0.xyz/favicon-228.png" />
  <meta property="og:type" content="website" />
</head>
<body>
    <main>
    <a id="mainLink" href="#">{img}</a>
"""

for part in parts:

    page += f"""
<div class="section" id="{part.id}">
<h2>{part.title}</h2>
<div>{part.content}</div>
</div>
"""
page += """</main>

<nav class="grid-nav"><div class="nav">"""

for part in parts:
    file_name = f"resources/{part.id}.svg"
    if not os.path.exists(file_name):
        file_name = "resources/blank.svg"

    img = svg(file_name)
    page += f"""
    <a class="nav-item" href="#{part.id}" title="{part.title}">{img}</a>
    """

page += """</div></nav>"""

page += """
  <link rel="preload" href="/fontawesome/webfonts/fa-brands-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/fontawesome/css/all.min.css">
</body>
</html>
<!--
      ___     Töröööö
  ,-.() °'_,'
 '|, . ,''
  |_-(_\\
-->"""

with open("static/index.html", "w") as f:
    f.write(page)