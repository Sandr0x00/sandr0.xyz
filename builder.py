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

parts = []

#===========================================================
# about
#===========================================================

parts.append(Part("about", "About", "Hi, I'm Sandro. I like to cook and code and hack."))

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

parts.append(Part("web", "Freelance Work / Web Development", content))
# <a href="https://schreiner-suess.de" title="Website for Schreinerei Andreas Süß Fuchsberg"><img class="client-work" src="schreiner-suess.png" alt="schreiner-suess"></a>

#===========================================================
# CTF
#===========================================================

ctf = {
  "Insomni'hack 2022": [("PDF-Xfiltration", "https://hxp.io/blog/93/Insomnihack-2022-PDF-Xfiltration")],
  "hxp CTF 2021": [("gameboy is you", "https://github.com/Sandr0x00/gameboy-is-you/blob/main/writeup/readme.md")],
  "0CTF 2021 Quals": [("pypypypy", "https://hxp.io/blog/85/0CTFTCTF-2021-Quals-selected-writeups#pypypypy")],
  "hxp CTF 2020": [("find the chicken", "https://hxp.io/blog/80/hxp-CTF-2020-find-the-chicken")],
  "0CTF 2020 Quals": [("Cloud Computing", "https://hxp.io/blog/74/0CTF%202020%20writeups#cloud-computing")],
  "Plaid CTF 2020": [("Bonzi Scheme", "https://hxp.io/blog/71/PlaidCTF-2020-Bonzi-Scheme")],
  "Teaser Dragon CTF 2019": [("PlayCAP", "https://hxp.io/blog/59/Teaser-Dragon-CTF-2019-PlayCAP-writeup")],
}

content = ""
for i,j in ctf.items():
  assert '"' not in i
  for k,l in j:
    assert '"' not in k
    assert '"' not in l
    content += f"""{i} - <a href="{l}">{k}</a><br>\n"""

parts.append(Part("ctf", "CTF Writeups", f"""
<p>
{content}
</p>
"""))

#===========================================================
# fun
#===========================================================

parts.append(Part("fun", "Fun", """
<p>Don't like the style of my website? Redesign it yourself!</p>
<style style="display:block; background-color: #444; padding:.5em; font-family: monospace;" contenteditable="">
body{
  color:#dddddd;
  background-color:#00060e;
}
.highlight {
    fill: #1a84ff
}
</style><br>
<a href="#" onclick="function f(){}var a=f;for(var b=0;b<100000;++b){a=a.bind();Object.defineProperty(a,Symbol.hasInstance,{})}({})instanceof a;">This link may segfault your Chrome Tab</a> (Ref: <a href="https://twitter.com/GuidoVranken/status/1271059248861138944">@GuidoVranken</a>)
"""))


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

img = svg("resources/sandr0.svg")

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