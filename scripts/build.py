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
    Hello! I'm Phil, based in Queens, NY. I've been a developer and
    manager in the past. Some of the most viewed posts on this site are about
    building <a href="/tags/compilers.html">compilers</a>, <a
    href="/tags/databases.html">databases</a>, and <a
    href="/tags/emulators.html">emulators</a> from scratch.
  </p>
  <p>
    I am building <a href="https://multiprocess.io/">Multiprocess
    Labs</a> around <a
    href="https://datastation.multiprocess.io">DataStation</a>, an
    open-source data IDE to help you create dashboards and exports on
    data from every database, API, and file without cumbersome ETL
    processes.
  </p>
  <p>
    I also run a <a href="https://discord.gg/PmmShtF7WS">Discord community
    for developers</a> working on or interested in challenging
    programming projects like compilers, databases, emulators,
    etc. Come to share and learn from other folks!
  </p>
  <p>
    You can find me elsewhere on <a
    href="https://github.com/eatonphil">Github</a>, <a
    href="https://twitter.com/phil_eaton">Twitter</a>, <a
    href="https://www.linkedin.com/in/phil-e-97a490178/">LinkedIn</a>,
    and <a
    href="https://www.goodreads.com/user/show/50930981-phil-eaton">Goodreads</a>.
  </p>
  <p>
    I love <a href="mailto:me@eatonphil.com">hearing from you</a>!
  </p>
</div>
<div class="fp-section fp-section--tags">
  <h2 class="fp-h2">Frequent Topics</h2>
  <div class="tags">
    {tags}
  </div>
  <p>
    <a href="/tags/">View all</a>
  </p>
</div>
<div class="fp-section fp-section--notes">
  <h2 class="fp-h2">Archive</h2>
  {notes}
</div>
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
        tags += '<a href="/tags/{}.html" class="tag">{}</a>'.format(tag.replace(' ', '-').replace('/', '-'), tag)
        #else:
        #    tags += '<span style="display: none;">{}</span>'.format(tag)
    if tags:
        return '<div class="tags">{}</div>'.format(tags)

    return ''


def main():
    all_tags = {}
    post_data = []
    tags_with_counts = {}
    for post in get_posts():
        print('Processing ' + post)
        out_file = post[len('posts/'):]
        output, title = get_post_data(post)
        header, date, tags_raw = title[1], title[2], title.get(6, "")

        tags = tags_raw.split(",")
        tags_html = get_html_tags(tags)

        post_data.append((out_file, title[1], title[2], post, output, tags_html))
        for tag in tags:
            if tag not in all_tags:
                all_tags[tag] = []
            if tag not in tags_with_counts:
                tags_with_counts[tag] = 0
            tags_with_counts[tag] += 1

            all_tags[tag].append((out_file, title[1], title[2]))

    frequent_tags_data = sorted(tags_with_counts.items(), key=lambda x: x[1], reverse=True)
    frequent_tags = []
    for tag, count in [t for t in frequent_tags_data if t[0] != 'external'][:20]:
        frequent_tags.append(f'<a href="/tags/{tag.replace(" ", "-").replace("/", "-")}.html" class="tag">{tag} ({count})</a>')
    frequent_tags = "".join(frequent_tags)

    showfeedback = "<style>.feedback{display:initial;}</style>"
    for (out_file, title, date, _, output, tags_html) in post_data:
        with open('docs/' + out_file, 'w') as f:
            f.write(TEMPLATE.format(post=output+showfeedback, title=title, subtitle=date, tag=title, tags=tags_html, meta="", frequent_tags=frequent_tags))

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
        notes="\n".join(notes),
        tags=frequent_tags)
    with open('docs/index.html', 'w') as f:
        meta = '<meta name="google-site-verification" content="s-Odt0Dj7WZzEk6hLV28wLyR5LeGQFoopUV3IDNO6bM" />\n    '
        f.write(TEMPLATE.format(post=home_page, title="", tag=TAG, subtitle="", tags="", meta=meta, frequent_tags=""))

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
    # Write tag index
    tag_index_data = sorted(tags_with_counts.items(), key=lambda x: x[1], reverse=True)
    tag_index = []
    for tag, count in tag_index_data:
        tag_index.append(f'<a href="/tags/{tag.replace(" ", "-").replace("/", "-")}.html" class="tag {"tag--common" if i < 20 else ""}">{tag} ({count})</a>')
    with open('docs/tags/index.html', 'w') as f:
        index_page = f'<div class="tags">{"".join(tag_index)}</div>'
        f.write(TEMPLATE.format(post=index_page, title="All Topics", tag="All Topics", subtitle="", tags="", meta="", frequent_tags=""))

    # Write each individual tag page
    for tag in all_tags:
        posts = all_tags[tag]
        with open('docs/tags/%s.html' % tag.replace(' ', '-').replace('/', '-'), 'w') as f:
            posts.sort(key=lambda post: datetime.strptime(post[2], '%B %d, %Y'))
            posts.reverse()
            tag_page = TAG_PAGE.format(tag)
            tag_page += "\n".join([TAG_SUMMARY.format(*args) for args in posts])
            f.write(TEMPLATE.format(post=tag_page, title="", tag=TAG, subtitle="", tags="", meta="", frequent_tags=""))


if __name__ == '__main__':
    main()
