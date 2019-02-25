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
<h2 class="fp-h2">About</h2>
  <p>
    Hello! I'm an engineer and manager in Brooklyn. As an engineer my
    interests are in compilers and interpreters; operating systems;
    and complex, intuitive user-interfaces. As a manager my interests
    are in effective, minimal processes and changes; transparency
    within teams and organizations; and education (for employees and
    for the public).
  </p>
  <p>
    I lead a team of software developers on the business-logic API and
    user-facing frontend at a <a href="https://capsule8.com">Linux
    security startup</a>.
  </p>
  <p>
    Find me on <a
    href="https://github.com/eatonphil">Github</a>, <a
    href="https://twitter.com/phil_eaton">Twitter</a>, and <a
    href="https://www.goodreads.com/eatonphil">Goodreads</a>.
    (I'm always looking for book recommendations.)
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
    <p>A Javascript to C++ compiler (using V8) written in Rust.</p>
  </a>
</div>
<div class="fp-section fp-section--talks">
  <h2 class="fp-h2">Talks</h2>
  <a href="https://www.meetup.com/nodejs/events/258732362/" class="fp-project">
    <div>
      AOT-compilation of Javascript with V8
      <a href="https://www.slideshare.net/philipeaton35/aotcompilation-of-javascript-with-v8">Slides</a>
    </div>
    <p>February 20, 2019</p>
  </a>
  <a href="https://www.meetup.com/JS-NYC/events/mwwrjqyxqbqb/" class="fp-project">
    <div>
      Compiler basics: Lisp to Assembly
      <a href="https://www.slideshare.net/philipeaton35/compiler-basics-lisp-to-assembly">Slides</a>
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
    title = {}

    def header(self, text, level, *args, **kwargs):
        self.title[level] = text
        if level <= 2:
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


def main():
    post_data = []
    for post in get_posts():
        out_file = post[len('posts/'):]
        output, title = get_post_data(post)
        header, date = title[1], title[2]

        post_data.append((out_file, title[1], title[2]))

        title = title[1]
        with open('dist/' + out_file, 'w') as f:
            f.write(TEMPLATE.format(post=output, title=title, subtitle=date, tag=title))

    post_data.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
    post_data.reverse()
    home_page = HOME_PAGE
    home_page += "\n".join([POST_SUMMARY.format(*args) for args in post_data])
    with open('dist/index.html', 'w') as f:
        f.write(TEMPLATE.format(post=home_page, title="", tag=TAG, subtitle=""))

    with open('dist/style.css', 'w') as fw:
        with open('style.css') as fr:
            fw.write(fr.read())


if __name__ == '__main__':
    main()
