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
<style>header, footer { display: none !important; }</style>
<div class="fp-section fp-section--about">
<h2 class="fp-h2">Bio</h2>
  <p>
    Hello! I'm Phil, an Engineering Manager at a <a
    href="https://www.linkedin.com/in/phil-e-97a490178/">software
    company</a> in New York City. The next career challenge will be in
    senior engineering management or cofounding.
  </p>
  <p>
    I'm interested in compilers, databases, networks, and operating
    systems. At some point I'd like to work in agriculture, renewable
    energy, shipping, Internet services, manufacturing, hardware, and
    graphics.
  </p>
  <p>
    Having studied Chinese and Japanese in school, and with family in
    Korea, I'd also like to spend some years working in East Asia.
  </p>
  <p>
    You can find me elsewhere on <a
    href="https://github.com/eatonphil">Github</a>, <a
    href="https://twitter.com/phil_eaton">Twitter</a>, and <a
    href="https://www.goodreads.com/eatonphil">Goodreads</a>.
  </p>
  <p>
    <a class="subscribe"
    href="https://docs.google.com/forms/d/e/1FAIpQLSchaYjB6mq0SHmFL_J1wbB7E4SwUk23Dja2K7mfjtYH5o48fw/viewform?usp=sf_link">Subscribe
    to blog updates and a weekly-ish newsletter.</a>
  </p>
</div>
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
    <p>A code generation tool and API specification powered by your database</p>
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
<div class="fp-section fp-section--notes">
  <h2 class="fp-h2">Notes</h2>
"""
TEMPLATE = open('template.html').read()
TAG = "My notes"

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
        tags += '<a href="/tags/{}.html" class="tag">{}</a>'.format(tag, tag)
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
        with open('dist/' + out_file, 'w') as f:
            f.write(TEMPLATE.format(post=output, title=title, subtitle=date, tag=title, tags=tags_html))

    post_data.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
    post_data.reverse()
    home_page = HOME_PAGE
    home_page += "\n".join([POST_SUMMARY.format(*args[:2], args[5], *args[2:3]) for args in post_data])
    with open('dist/index.html', 'w') as f:
        f.write(TEMPLATE.format(post=home_page, title="", tag=TAG, subtitle="", tags=""))

    with open('dist/style.css', 'w') as fw:
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
    fg.rss_file('dist/rss.xml')

    if not os.path.exists('dist/tags'):
        os.makedirs('dist/tags')
    for tag in all_tags:
        posts = all_tags[tag]
        with open('dist/tags/%s.html' % tag, 'w') as f:
            posts.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
            posts.reverse()
            tag_page = TAG_PAGE.format(tag)
            tag_page += "\n".join([TAG_SUMMARY.format(*args) for args in posts])
            f.write(TEMPLATE.format(post=tag_page, title="", tag=TAG, subtitle="", tags=""))


if __name__ == '__main__':
    main()
