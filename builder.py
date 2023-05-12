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

#===========================================================
# about
#===========================================================

img = svg("resources/sandr0.svg")
img = re.sub(r"<svg",f'<svg class="sandr0"',img)

about_data = [
  f'I am {img}',
  '<span class="hidden">I am</span> a <a href="https://hxp.io">CTF player</a>',
  '<span class="hidden">I am</span> a <a class="kompilers" href="https://kompilers.com/">kompiler</a>',
  '<span class="hidden">I am</span> a <a href="mailto:job@sandr0.xyz">freelancer</a>',
  '<span class="hidden">I am</span> a <a href="https://www.cve.org/CVERecord?id=CVE-2023-28158">hacker</a>',
  '<span class="hidden">I am</span> a <a href="https://github.com/Sandr0x00">developer</a>',
  '<span class="hidden">I am</span> a <a href="/recipes">cook</a>',
]

parts.append(Part("about", "About", '<br/>'.join(about_data)))

#===========================================================
# projects
#===========================================================

web_data = [
  # website, description, file
  ["/recipes", "My personal recipe collection", "recipes.jpg"],
  ["/series", "The status of my series", "series.jpg"],
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
  "Stuff I created": [
    ("archived", "zaj",
    """A zero-day web challenge for hxp CTF 2022 targeting Apache Archiva 2.2.9. The challenge is based on a vulnerability I discovered which was assigned <a href="https://www.cve.org/CVERecord?id=CVE-2023-28158">CVE-2023-28158</a>. [<a href="https://2022.ctf.link/internal/challenge/b2ca2268-f49f-4103-9943-2a417244a955">challenge</a>, <a href="https://hxp.io/blog/100/hxp-CTF-2022-archived/">writeup</a>]"""),
    ("required", "rev",
    """A challenge for hxp CTF 2022 using the prototype pollution discussed in the challenge <a href="https://ctf.zeyu2001.com/2022/balsnctf-2022/2linenodejs">2linenodejs</a> as a way to obfuscate NodeJS code. [<a href="https://2022.ctf.link/internal/challenge/7e3e425c-865d-4025-9005-09806d951cca">challenge</a>, <a href="https://hxp.io/blog/103/hxp-CTF-2022-required/">writeup</a>]"""),
    ("sqlite_web", "web",
    """A web challenge for hxp CTF 2022 focusing on a insecure design choice in <a href="https://github.com/coleifer/sqlite-web">sqlite-web</a> leading to remote code execution. <a href="https://github.com/coleifer/sqlite-web/issues/111">Remains unfixed.</a> [<a href="https://2022.ctf.link/internal/challenge/dbb4626c-3390-43d2-88bf-4d4c22c33315">challenge</a>, <a href="https://hxp.io/blog/102/hxp-CTF-2022-sqlite_web/">writeup</a>]"""),
    ("valentine", "web",
    """A web challenge for hxp CTF 2022 exploring <a href="https://github.com/mde/ejs">ejs</a> 3.1.8 after <a href="https://eslam.io/posts/ejs-server-side-template-injection-rce/">CVE-2022-29078</a> was fixed. [<a href="https://2022.ctf.link/internal/challenge/8f5b680d-d57a-4609-94e9-37593f9d4f2a">challenge</a>, <a href="https://hxp.io/blog/101/hxp-CTF-2022-valentine/">short writeup</a>, <a href="https://github.com/ispoleet/ctf-writeups/tree/master/hxp_ctf_2022/required">extended writeup</a>]"""),
    ("baba is you", "msc",
    """A misc challenge for hxp CTF 2021 inspired by <a href="https://hempuli.com/baba/">baba is you</a> written in C for Gameboy. [<a href="https://2021.ctf.link/internal/challenge/52c2a607-7e05-456f-b8c0-68952304f2a4/">challenge</a>, <a href="https://baba.hxp.io/">scoreboard</a>, <a href="https://github.com/Sandr0x00/gameboy-is-you/blob/">source</a>, <a href="https://github.com/Sandr0x00/gameboy-is-you/blob/main/writeup/readme.md">writeup</a>]"""),
    ("find the chicken", "msc",
    """A gameboy challenge for hxp CTF 2020 written in C. Reverse the game and find the chicken. [<a href="https://2020.ctf.link/internal/challenge/7e09f315-2f7b-4f0a-bcaf-934cc298e263/">challenge</a>, <a href="https://chicken.hxp.io/">scoreboard</a>, <a href="https://github.com/Sandr0x00/find-the-chicken">source</a>, <a href="https://hxp.io/blog/80/hxp-CTF-2020-find-the-chicken">solve run</a>]"""),
  ],
  "Stuff I broke": [
    ("PDF-Xfiltration", "",
    """My <a href="https://hxp.io/blog/93/Insomnihack-2022-PDF-Xfiltration">writeup</a> to a challenge from Insomni'hack 2022 about breaking PDF signatures using JavaScript."""),
    ("pypypypy", "",
    """My <a href="https://hxp.io/blog/85/0CTFTCTF-2021-Quals-selected-writeups#pypypypy">writeup</a> to a python sandbox escape from 0CTF 2021 Quals."""),
    ("Cloud Computing", "",
    """My <a href="https://hxp.io/blog/74/0CTF%202020%20writeups#cloud-computing">writeup</a> for a PHP sandbox escape from 0CTF 2020 Quals."""),
    ("Bonzi Scheme", "",
    """My <a href="https://hxp.io/blog/71/PlaidCTF-2020-Bonzi-Scheme">totally serious guide</a> of how to "hack hex with hyx" solving a challenge of PlaidCTF 2020."""),
    ("PlayCAP", "",
    """My <a href="https://hxp.io/blog/59/Teaser-Dragon-CTF-2019-PlayCAP-writeup">writeup</a> for a challenge at Teaser Dragon CTF 2019 about reversing a PCAP to find pressed buttons of an XBOX controller."""),
  ],
}

content = ""
for ctf_name, ctf_challs in ctf.items():
  assert '"' not in ctf_name
  content += f"<h3>{ctf_name}</h3>"
  for chall_name, chall_type, chall_desc in ctf_challs:
    assert '"' not in chall_name
    # assert '"' not in chall_writeup
    content += f"""<div class="post">"""
    if chall_type:
      content += f"""<img src="/icon_{chall_type}.png">"""
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
<html>
<head>
	<meta charset="UTF-8">
  <link rel="stylesheet" href="css.css">
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

page += """</div></nav>

<div class="right">
<div>
<a href="https://twitter.com/Sandr0x00"><i class="fab fa-twitter fa-2x"></i></a>
<a href="https://github.com/Sandr0x00"><i class="fab fa-github fa-2x"></i></a>
<a rel="me" href="https://infosec.exchange/@sandr0"><i class="fab fa-mastodon fa-2x"></i></a>
</div>
</div>
"""
comment = """
  <div class="container">
    <div class="row">
      <div id="about" class="col-sm-4">
        I'm - still - a bavarian computer science student at <a href="https://www.tum.de/en/">TUM</a>. In my spare time I do some coding (see projects) and <a href="https://hxp.io/">ctf</a> (see writeups).
        <h4>About</h4>
      </div>
    </div>
    <div class="row">
      <div id="fun" class="col-sm-12">
        <b></b>
        <br>
        <br>
        <h4>Fun</h4>
      </div>
    </div>
    </div>
  </div>
"""
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