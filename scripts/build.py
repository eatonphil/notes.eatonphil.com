import glob
import os
from datetime import datetime, timezone

import mistune
from feedgen.feed import FeedGenerator

POST_SUMMARY = """
<div class="summary">
  <a href="/{}">{}</a>
  {}
  <div class="summary-subtitle">{}</div>
</div>
"""
TAG_SUMMARY = """
<div class="summary">
  <a href="/{}">{}</a>
  <div class="summary-subtitle">{}</div>
</div>
"""
TAG_PAGE = """
<div class="summary">
  <h1>{}</h1>
  <div class="summary-subtitle">Tag</div>
</div>
"""
HOME_PAGE = """
<div class="fp-section fp-section--about">
  <h2 class="fp-h2"></h2>
  <p>
    Hello! I'm Phil, a developer and manager in Queens, NY. I'm
    building <a
    href="https://datastation.multiprocess.io">DataStation</a>,
    a data IDE for developers. Check out the <a
    href="https://app.datastation.multiprocess.io">in-browser
    demo</a>.
  </p>
  <p>
    Some of my most viewed posts are on building <a
    href="/tags/interpreter.html">interpreters</a>, <a
    href="/tags/compiler.html">compilers</a>, <a
    href="/tags/database.html">databases</a>, <a
    href="/tags/web-servers.html">servers</a>, and <a
    href="/tags/emulator.html">emulators</a> from scratch.  You can
    also find me on <a href="https://github.com/eatonphil">Github</a>,
    <a href="https://twitter.com/phil_eaton">Twitter</a>, <a
    href="https://www.linkedin.com/in/phil-e-97a490178/">LinkedIn</a>,
    and <a
    href="https://www.goodreads.com/user/show/50930981-phil-eaton">Goodreads</a>.
  </p>
</div>
<div class="fp-section fp-section--notes">
  <h2 class="fp-h2">Archive</h2>
  {notes}
</div>
<!--
<div class="fp-section fp-section--projects">
  <h2 class="fp-h2">Fun</h2>
  <a href="http://ponyo.org" class="fp-project">
    <div>Ponyo</div>
    <p>High-level library and toolkit for programming Standard ML.</p>
  </a>
  <a href="https://github.com/eatonphil/bsdscheme" class="fp-project">
    <div>BSDScheme</div>
    <p>A Scheme interpreter and compiler targeting R7RS written in D.</p>
  </a>
  <a href="https://github.com/eatonphil/jsc" class="fp-project">
    <div>Jsc</div>
    <p>A JavaScript to C++ compiler (using V8) written in TypeScript.</p>
  </a>
  <a href="https://github.com/eatonphil/ulisp" class="fp-project">
    <div>ulisp</div>
    <p>An educational compiler from Lisp to LLVM and x86 assembly, written in JavaScript.</p>
  </a>
  <a href="https://github.com/eatonphil/uweb" class="fp-project">
    <div>uweb</div>
    <p>An educational web server written in JavaScript.</p>
  </a>
  <a href="https://github.com/eatonphil/x86e" class="fp-project">
    <div>x86e</div>
    <p>An x86 emulator and graphical debugger in JavaScript.</p>
  </a>
  <a href="https://github.com/eatonphil/gosql" class="fp-project">
    <div>gosql</div>
    <p>A PostgreSQL implementation in Go.</p>
  </a>
  <a href="https://github.com/eatonphil/dbcore" class="fp-project">
    <div>dbcore</div>
    <p>A code generation tool and API specification powered by your database.</p>
  </a>
  <a href="https://github.com/eatonphil/go-amd64-emulator" class="fp-project">
    <div>go-amd64-emulator</div>
    <p>A userland linux/amd64 emulator and terminal debugger in Go.</p>
  </a>
</div>
<div class="fp-section fp-section--talks">
  <h2 class="fp-h2">Talks</h2>
  <div class="fp-project">
    <a href="https://www.meetup.com/TypeScriptNYC/events/260291994/">Interpreting TypeScript</a>
    <div>
      <a href="https://docs.google.com/presentation/d/e/2PACX-1vQOSorW7HGPvt1qURVK4d82bTxUVzlDUyCtFtbSgvA8CXhg2yw2FLpBD9cCBNvplSUmj-KezR1X1DBt/pub">Slides</a>
    </div>
    <p>April 17, 2019</p>
  </div>
  <div class="fp-project">
    <a href="https://www.meetup.com/nodejs/events/258732362/">AOT-compilation of Javascript with V8</a>
    <div>
      <a href="https://docs.google.com/presentation/d/e/2PACX-1vQRIjLOcxdbZEDWI8LH2iPtzo4YVTueg1JTlFgJRRjcRDKMOYZ_XS1C-Q9DLpER3AoivyHFzzWT8HQK/pub">Slides</a>
    </div>
    <p>February 20, 2019</p>
  </div>
  <div class="fp-project">
    <a href="https://www.meetup.com/JS-NYC/events/mwwrjqyxqbqb/">Compiler basics: Lisp to Assembly</a>
    <div>
      <a href="https://docs.google.com/presentation/d/e/2PACX-1vQE2HWfQwFzmFkvfGssqp-93dN5no0ozzNwqO6nNF7-yUm_Kv_TOhbBqoIhy1y8imUj6AwPmF1UZaqG/pub">Slides</a>
    </div>
    <p>December 20, 2018</p>
  </div>
</div>
-->
"""
TEMPLATE = open('template.html').read()
TAG = "Notes on software, organizations, product development, and professional growth"

class Renderer(mistune.Renderer):
    def __init__(self):
        mistune.Renderer.__init__(self)
        self.title = {}

    def header(self, text, level, *args, **kwargs):
        self.title[level] = text
        if level <= 2:
            return ""
        if level == 6:
            return ""
        return "<h{level} id=\"{id}\">{text}</h{level}>".format(**{
            "id": text.lower().replace(' ', '-'),
            "text": text,
            "level": level,
        })

    def block_code(self, code, lang=""):
        code = code.rstrip('\n')
        if not lang:
            code = mistune.escape(code, smart_amp=False)
            return '<pre><code>%s\n</code></pre>\n' % code
        code = mistune.escape(code, quote=True, smart_amp=False)
        return '<pre><code class="hljs %s">%s\n</code></pre>\n' % (lang, code)


def get_posts():
    for post in glob.glob('posts/**'):
        if post.endswith('.html'):
            yield post


def get_post_data(in_file):
    with open(in_file) as f:
        markdown = mistune.Markdown(renderer=Renderer())
        output = markdown(f.read())
        return output, markdown.renderer.title


def get_html_tags(all_tags):
    tags = ''

    for i, tag in enumerate(all_tags):
        if not tag:
            continue
        #if i < 3:
        tags += '<a href="/tags/{}.html" class="tag">{}</a>'.format(tag.replace(' ', '-'), tag)
        #else:
        #    tags += '<span style="display: none;">{}</span>'.format(tag)
    if tags:
        return '<div class="tags">{}</div>'.format(tags)

    return ''


def main():
    all_tags = {}
    post_data = []
    for post in get_posts():
        out_file = post[len('posts/'):]
        output, title = get_post_data(post)
        header, date, tags_raw = title[1], title[2], title.get(6, "")

        tags = tags_raw.split(",")
        tags_html = get_html_tags(tags)

        post_data.append((out_file, title[1], title[2], post, output, tags_html))
        for tag in tags:
            if tag not in all_tags:
                all_tags[tag] = []

            all_tags[tag].append((out_file, title[1], title[2]))

        title = title[1]
        with open('docs/' + out_file, 'w') as f:
            f.write(TEMPLATE.format(post=output, title=title, subtitle=date, tag=title, tags=tags_html, meta=""))

    post_data.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
    post_data.reverse()
    notes = []
    for i, args in enumerate(post_data):
        year = args[2].split(' ')[-1]
        prev_post_year = str(datetime.today().year + 1) if i == 0 else post_data[i-1][2].split(' ')[-1]
        if year != prev_post_year:
            notes.append('<h3>{}</h3>'.format(year))
        note = POST_SUMMARY.format(*args[:2], args[5], *args[2:3])
        notes.append(note)
    home_page = HOME_PAGE.format(
        notes="\n".join(notes))
    with open('docs/index.html', 'w') as f:
        meta = '<meta name="google-site-verification" content="s-Odt0Dj7WZzEk6hLV28wLyR5LeGQFoopUV3IDNO6bM" />\n    '
        f.write(TEMPLATE.format(post=home_page, title="", tag=TAG, subtitle="", tags="", meta=meta))

    with open('docs/style.css', 'w') as fw:
        with open('style.css') as fr:
            fw.write(fr.read())

    fg = FeedGenerator()
    for url, title, date, post, content, _ in reversed(post_data):
        fe = fg.add_entry()
        fe.id('http://notes.eatonphil.com/' + url)
        fe.title(title)
        fe.link(href='http://notes.eatonphil.com/' + url)
        fe.pubDate(datetime.strptime(date, '%B %d, %Y').replace(tzinfo=timezone.utc))
        fe.content(content)

    fg.id('http://notes.eatonphil.com/')
    fg.link(href='http://notes.eatonphil.com/')
    fg.title(TAG)
    fg.description(TAG)
    fg.author(name='Phil Eaton', email='me@eatonphil.com')
    fg.language('en')
    fg.rss_file('docs/rss.xml')

    with open('docs/sitemap.xml', 'w') as f:
        urls = []
        for url, _, date, _, _, _ in reversed(post_data):
            urls.append("""  <url>
    <loc>https://notes.eatonphil.com/{url}</loc>
    <lastmod>{date}</lastmod>
 </url>""".format(url=url, date=datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')))
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>""".format(urls='\n'.join(urls)))

    with open('docs/robots.txt', 'w') as f:
        f.write("""User-agent: *
Allow: /

Sitemap: https://notes.eatonphil.com/sitemap.xml""")

    if not os.path.exists('docs/tags'):
        os.makedirs('docs/tags')
    for tag in all_tags:
        posts = all_tags[tag]
        with open('docs/tags/%s.html' % tag.replace(' ', '-'), 'w') as f:
            posts.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
            posts.reverse()
            tag_page = TAG_PAGE.format(tag)
            tag_page += "\n".join([TAG_SUMMARY.format(*args) for args in posts])
            f.write(TEMPLATE.format(post=tag_page, title="", tag=TAG, subtitle="", tags="", meta=""))


if __name__ == '__main__':
    main()
