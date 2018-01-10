import glob
from datetime import datetime

import mistune

POST_SUMMARY = """
<a href="{}" class="summary">
  <h1>{}</h1>
  <h2>{}</h2>
</a>
"""
TEMPLATE = open('template.html').read()
TAG = "Experiment, study, share"

class Renderer(mistune.Renderer):
    title = {}

    def header(self, text, level, *args, **kwargs):
        self.title[level] = text
        return super().header(text, level, *args, **kwargs)

    def block_code(self, code, lang=""):
        code = code.rstrip('\n')
        if not lang:
            code = escape(code, smart_amp=False)
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
            f.write(TEMPLATE.format(post=output + "<hr />", title=title, tag=(TAG or title)))

    post_data.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
    post_data.reverse()
    post = "\n".join([POST_SUMMARY.format(*args) for args in post_data])
    with open('dist/index.html', 'w') as f:
        f.write(TEMPLATE.format(post=post, title=TAG, tag=TAG))

    with open('dist/style.css', 'w') as fw:
        with open('style.css') as fr:
            fw.write(fr.read())


if __name__ == '__main__':
    main()
