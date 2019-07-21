import glob
from datetime import datetime

import mistune

POST_SUMMARY = """
<div class="summary">
  <a href="{}">{}</a>
  <div class="summary-subtitle">{}</div>
</div>
"""
HOME_PAGE = """
<style>header, footer { display: none !important; }</style>
<div class="fp-section fp-section--about">
<h2 class="fp-h2">Bio</h2>
  <p>
    Hello! I'm an engineering manager in Brooklyn. I lead a fantastic
    group of humans building SIEM tools at a <a
    href="https://capsule8.com">kick-eass Linux security
    startup</a>. Before this, I led the frontend group at a <a
    href="https://linode.com">Linux hosting company in Philly</a>.
  </p>
  <p>
    I'm interested in compilers, networks, and operating systems. At
    some point I'd like to work in shipping, Internet services,
    manufacturing, hardware, and graphics. Having studied Chinese and
    Japanese in school, and with family in Korea, I'd also like to
    spend some years working in East Asia.
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
    to updates</a>
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
    <p>An educational compiler from Lisp to LLVM written in JavaScript.</p>
  </a>
  <a href="https://github.com/eatonphil/uweb" class="fp-project">
    <div>uweb</div>
    <p>An educational web server written in JavaScript.</p>
  </a>
  <a href="https://github.com/eatonphil/x86e" class="fp-project">
    <div>x86e</div>
    <p>An x86 emulator and graphical debugger in JavaScript.</p>
  </a>
</div>
<div class="fp-section fp-section--talks">
  <h2 class="fp-h2">Talks</h2>
  <a href="https://www.meetup.com/TypeScriptNYC/events/260291994/" class="fp-project">
    <div>
      Interpreting TypeScript
      <a href="https://docs.google.com/presentation/d/e/2PACX-1vQOSorW7HGPvt1qURVK4d82bTxUVzlDUyCtFtbSgvA8CXhg2yw2FLpBD9cCBNvplSUmj-KezR1X1DBt/pub">Slides</a>
    </div>
    <p>April 17, 2019</p>
  </a>
  <a href="https://www.meetup.com/nodejs/events/258732362/" class="fp-project">
    <div>
      AOT-compilation of Javascript with V8
      <a href="https://docs.google.com/presentation/d/e/2PACX-1vQRIjLOcxdbZEDWI8LH2iPtzo4YVTueg1JTlFgJRRjcRDKMOYZ_XS1C-Q9DLpER3AoivyHFzzWT8HQK/pub">Slides</a>
    </div>
    <p>February 20, 2019</p>
  </a>
  <a href="https://www.meetup.com/JS-NYC/events/mwwrjqyxqbqb/" class="fp-project">
    <div>
      Compiler basics: Lisp to Assembly
      <a href="https://docs.google.com/presentation/d/e/2PACX-1vQE2HWfQwFzmFkvfGssqp-93dN5no0ozzNwqO6nNF7-yUm_Kv_TOhbBqoIhy1y8imUj6AwPmF1UZaqG/pub">Slides</a>
    </div>
    <p>December 20, 2018</p>
  </a>
</div>
<div class="fp-section fp-section--notes">
  <h2 class="fp-h2">Notes</h2>
"""
TEMPLATE = open('template.html').read()
TAG = "Notes by a software developer"

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


def get_tags(tags_raw):
    tags = ''

    for i, tag in enumerate(tags_raw.split(",")):
        if not tag:
            continue
        if i < 3:
            tags += '<span class="tag">' + tag + '</span>'
        else:
            tags += '<span style="display: none;">' + tag + '</span>'
    if tags:
        return '<div class="tags">' + tags + '</div>'

    return ''


def main():
    post_data = []
    for post in get_posts():
        out_file = post[len('posts/'):]
        output, title = get_post_data(post)
        header, date, tags_raw = title[1], title[2], title.get(6, "")

        tags = get_tags(tags_raw)

        post_data.append((out_file, title[1], title[2]))

        title = title[1]
        with open('dist/' + out_file, 'w') as f:
            f.write(TEMPLATE.format(post=output, title=title, subtitle=date, tag=title, tags=tags))

    post_data.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
    post_data.reverse()
    home_page = HOME_PAGE
    home_page += "\n".join([POST_SUMMARY.format(*args) for args in post_data])
    with open('dist/index.html', 'w') as f:
        f.write(TEMPLATE.format(post=home_page, title="", tag=TAG, subtitle="", tags=""))

    with open('dist/style.css', 'w') as fw:
        with open('style.css') as fr:
            fw.write(fr.read())


if __name__ == '__main__':
    main()
