import re, os, json, subprocess, urllib.request

def slugify(text):
    # GitHub's heading ids, exactly, so every link written against GitHub's renderer works here:
    # drop punctuation, one hyphen per space, never collapse ("A + B" is "a--b")
    return re.sub(r'[^\w\- ]', '', text.strip().lower()).replace(' ', '-')

REPO = 'https://github.com/ravindu644/Droidspaces-OSS'

def fix_link(url):
    """A docs page links to another page (.md becomes .html), or to a file the site does not host,
    which goes to the repository on GitHub instead of a 404."""
    if url.startswith(('http', '#', 'mailto:', '/')):
        return url
    path, _, frag = url.partition('#')
    frag = f'#{frag}' if frag else ''
    if path.startswith('../'):
        return f'{REPO}/blob/main/{path[3:]}{frag}'
    path = path.removeprefix('./')
    if path.endswith('.md') or path.endswith('.html'):
        return path.lower().replace('.md', '.html') + frag
    return f'{REPO}/tree/main/Documentation/{path}{frag}'

from html import escape, unescape
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

COPY_BUTTON = '<button class="icon-button copy-btn" onclick="copyCode(this)" aria-label="Copy"><span class="icon" aria-hidden="true">content_copy</span></button>'

def render_code(self, tokens, idx, options, env):
    # Highlighted at build time, so the page needs no script and no third-party request to colour code
    tok = tokens[idx]
    lang = tok.info.strip().split()[0].lower() if tok.info.strip() else ''
    try:
        code = highlight(tok.content, get_lexer_by_name(lang), HtmlFormatter(nowrap=True))
    except ClassNotFound:
        code = escape(tok.content)
    label = f'<span class="code-lang">{escape(lang)}</span>' if lang else ''
    return f'<div class="code-block">{label}{COPY_BUTTON}<pre><code>{code}</code></pre></div>\n'

MD = (MarkdownIt('commonmark', {'html': True})  # html: the docs use <details> and <a id> anchors
      .enable(['table', 'strikethrough'])
      .use(anchors_plugin, min_level=1, max_level=4, slug_func=slugify, permalink=True, permalinkSymbol='#'))
MD.add_render_rule('fence', render_code)
MD.add_render_rule('code_block', render_code)

def md_to_html(md):
    html = MD.render(md)
    # GitHub alerts: > [!NOTE] becomes the site's callout
    html = re.sub(r'<blockquote>\s*<p>\[!(\w+)\]\s*(?:</p>\s*<p>|<br\s*/?>\s*)?(.*?)</blockquote>',
                  lambda m: f'<div class="callout callout-{m.group(1).lower()}"><strong class="callout-title">{m.group(1).capitalize()}</strong><p>{m.group(2).strip()}</div>',
                  html, flags=re.S)
    html = re.sub(r'<p>\s*</p>', '', html)
    html = html.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    def link(m):
        url = m.group(1)
        ext = ' rel="noopener noreferrer"' if url.startswith('http') else ''
        return f'href="{fix_link(url)}"{ext}'
    return re.sub(r'href="([^"]+)"', link, html)

def plain(html):
    return unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip())  # text, not HTML: escaped again where it is written

def headings(html):
    """(level, id, text) for every h2 and h3, for the on-this-page list and the search index."""
    out = []
    for m in re.finditer(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', html, re.S):
        text = plain(re.sub(r'<a class="header-anchor".*?</a>', '', m.group(3), flags=re.S))
        out.append((int(m.group(1)), m.group(2), text))
    return out

def toc(html):
    items = ''.join(f'<li class="toc-h{lvl}"><a href="#{hid}">{escape(text)}</a></li>' for lvl, hid, text in headings(html))
    return f'<nav class="toc" aria-label="On this page"><p class="toc-title">On this page</p><ul>{items}</ul></nav>' if items else ''

DEVICE_FILTER = ('<div class="device-filter" hidden><label for="device-filter">Filter devices</label>'
                 '<input id="device-filter" type="search" placeholder="Device, model, kernel or maintainer" autocomplete="off"></div>')

SECTION_ORDER = {'Basics': 0, 'Guides': 1, 'Recipes': 2, 'Reference': 3}

FALLBACK_TITLES = {
    'installation-android': 'Android Installation',
    'installation-linux': 'Linux Installation', 'features': 'Features Deep Dive',
    'gpu-acceleration': 'GPU Acceleration', 'kernel-configuration': 'Kernel Configuration',
    'usage-android-app': 'Android App Usage', 'linux-cli': 'Linux CLI Usage',
    'cool-things-you-can-do': 'Cool Things You Can Do', 'common-errors': 'Common Errors',
    'troubleshooting': 'Troubleshooting', 'community-supported-devices': 'Supported Devices',
    'nix-nixos': 'Nix / NixOS', 'uninstallation': 'Uninstallation',
}

FALLBACK_SECTIONS = {
    'installation-android': 'Basics', 'installation-linux': 'Basics',
    'features': 'Guides', 'gpu-acceleration': 'Guides', 'kernel-configuration': 'Guides',
    'usage-android-app': 'Guides', 'linux-cli': 'Guides',
    'cool-things-you-can-do': 'Recipes',
    'common-errors': 'Reference', 'troubleshooting': 'Reference',
    'community-supported-devices': 'Reference', 'nix-nixos': 'Reference', 'uninstallation': 'Reference',
}

FALLBACK_ORDER = {
    'installation-android': 1, 'installation-linux': 2,
    'features': 1, 'gpu-acceleration': 2, 'kernel-configuration': 3,
    'usage-android-app': 4, 'linux-cli': 5,
    'cool-things-you-can-do': 1,
    'troubleshooting': 1, 'common-errors': 2,
    'community-supported-devices': 3, 'nix-nixos': 4, 'uninstallation': 5,
}

FALLBACK_DESC = {
    'installation-android': 'Step-by-step Android installation guide for Droidspaces. Root your device, install the APK, set up the backend, and run Linux containers with zero terminal commands.',
    'installation-linux': 'Install Droidspaces on Linux desktop or server. Download the tarball, extract the binary, create a rootfs image, and boot your first container.',
    'features': 'Deep dive into every Droidspaces feature: namespace isolation, init system support, OverlayFS volatile mode, GPU acceleration, cgroup isolation, seccomp shields, and Android-specific tuning.',
    'gpu-acceleration': 'Enable GPU acceleration in Droidspaces containers on Android and Linux. Covers Termux-X11, VirGL, Turnip for native Adreno, and desktop GPU passthrough.',
    'kernel-configuration': 'Complete guide to compiling a custom Android kernel with Droidspaces support. Covers non-GKI and GKI kernels with kABI-safe patches.',
    'usage-android-app': 'Complete guide to the Droidspaces Android app. Manage containers, configure networking, stats, terminal, and kernel settings.',
    'linux-cli': 'Full Droidspaces Linux CLI reference. Every command, flag, and config option explained.',
    'cool-things-you-can-do': 'Cool projects with Droidspaces: secure mobile server with Tailscale + UFW + Fail2Ban, and Docker containers nested inside Droidspaces.',
    'common-errors': 'Complete collection of Droidspaces error solutions: GrapheneOS unsupported, ENOKEY, mount errors, systemd hangs, paranoid networking, and more.',
    'troubleshooting': 'Troubleshoot Droidspaces containers: systemd hangs, paranoid networking, SELinux corruption, OverlayFS f2fs, sparse image reclaim, WiFi power save.',
    'community-supported-devices': 'Community-maintained compatibility list of Android devices verified to run Droidspaces.',
    'nix-nixos': 'Run NixOS inside Droidspaces containers. Build tarballs, configure compatibility, and try the experimental Finix system.',
    'uninstallation': 'Safely uninstall Droidspaces from Android and Linux. Remove containers, backend data, APK, and system files completely.',
}

FALLBACK_KEYWORDS = {
    'installation-android': 'install Droidspaces Android, rooted Android container, APK install, atomic backend, sparse image',
    'installation-linux': 'install Droidspaces Linux, Linux container runtime, rootfs tarball, ext4 image, Linux namespaces',
    'features': 'Droidspaces features, namespace isolation, cgroup v2, OverlayFS, volatile mode, init system, GPU hardware access',
    'gpu-acceleration': 'GPU acceleration Android container, Turnip Adreno, VirGL GPU, Termux X11, llvmpipe',
    'kernel-configuration': 'kernel configuration Droidspaces, GKI kABI patches, Android kernel compile, namespace kernel config',
    'usage-android-app': 'Droidspaces Android app, container manager Android, NAT mode, built-in terminal, systemd service manager',
    'linux-cli': 'Droidspaces CLI, Linux container command line, droidspaces command reference, bind mount, NAT networking',
    'cool-things-you-can-do': 'Droidspaces mobile server, Tailscale Android container, UFW Fail2Ban container, Docker nested',
    'common-errors': 'Droidspaces common errors, ENOKEY fix, GrapheneOS, SuSFS conflict, container mount error, systemd hang',
    'troubleshooting': 'Droidspaces troubleshooting, systemd hang legacy kernel, paranoid networking, ping permission denied',
    'community-supported-devices': 'Droidspaces supported devices, Android kernel list, device compatibility, custom kernel downloads',
    'nix-nixos': 'NixOS Droidspaces, Nix container, Flake, systemd v259 legacy kernel, Finix experimental',
    'uninstallation': 'uninstall Droidspaces, remove Android container runtime, delete rootfs, remove backend files',
}

def parse_metadata(md):
    m = re.match(r'^\s*<!--\s*(.*?)-->\s*', md, re.DOTALL)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).split('\n'):
        line = line.strip()
        kv = re.match(r'(\w+):\s*(.*)', line)
        if kv:
            meta[kv.group(1).lower()] = kv.group(2).strip()
    return meta

def load_pages(docs_dir):
    pages = []
    for fname in sorted(os.listdir(docs_dir)):
        if not fname.endswith('.md'):
            continue
        slug = fname.replace('.md', '').lower()
        with open(os.path.join(docs_dir, fname)) as f:
            md = f.read()
        meta = parse_metadata(md)
        title = meta.get('title', FALLBACK_TITLES.get(slug, slug.replace('-', ' ').title()))
        section = meta.get('section', FALLBACK_SECTIONS.get(slug, 'Guides'))
        order = int(meta.get('order', FALLBACK_ORDER.get(slug, 99)))
        desc = meta.get('desc', FALLBACK_DESC.get(slug, f'Droidspaces documentation - {title}'))
        keywords = meta.get('keywords', FALLBACK_KEYWORDS.get(slug, 'Droidspaces, Linux containers, Android containers'))
        pages.append((slug, title, section, order, desc, keywords, fname))
    pages.sort(key=lambda p: (SECTION_ORDER.get(p[2], 99), p[3]))
    return pages

def sidebar(pages, slug):
    groups = {}
    for p in pages:
        groups.setdefault(p[2], []).append((p[0], p[1]))
    lines = []
    for section in ['Basics', 'Guides', 'Recipes', 'Reference']:
        if section not in groups:
            continue
        # native <details>, so a group collapses without a script
        lines.append(f'<details class="sidebar-group" open><summary class="sidebar-heading">{section}</summary>')
        for href, label in groups[section]:
            active = ' aria-current="page"' if href == slug else ''
            lines.append(f'<a href="{href}.html" class="sidebar-link"{active}>{label}</a>')
        lines.append('</details>')
    return '\n'.join(lines)

def nav_buttons(pages, slug):
    slugs = [p[0] for p in pages]
    labels = {p[0]: p[1] for p in pages}
    try:
        idx = slugs.index(slug)
    except ValueError:
        return ''
    prev_link = next_link = ''
    if idx > 0:
        p = slugs[idx - 1]
        prev_link = f'<a href="{p}.html" class="doc-nav-prev"><small>Previous</small>{labels[p]}</a>'
    if idx < len(slugs) - 1:
        n = slugs[idx + 1]
        next_link = f'<a href="{n}.html" class="doc-nav-next"><small>Next</small>{labels[n]}</a>'
    return f'<nav class="doc-nav" aria-label="Pages">{prev_link}{next_link}</nav>'

def breadcrumb(pages, slug):
    m = {p[0]: (p[2], p[1]) for p in pages}
    if slug not in m:
        return '<span>Docs</span>'
    section, label = m[slug]
    parts = ['<span>Docs</span>']
    if section != label:
        parts.append('<span class="bc-sep">/</span>')
        parts.append(f'<span class="bc-section">{section}</span>')
    parts.append('<span class="bc-sep">/</span>')
    parts.append(f'<span class="bc-label">{label}</span>')
    return ''.join(parts)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fill(template_path, values):
    """Fill {{KEY}} placeholders. Plain replace, not format(), so page content may contain braces."""
    page = open(template_path).read()
    for key, value in values.items():
        page = page.replace('{{' + key + '}}', value)
    return page

def make_page(title, body, slug, nav_template, footer_template, pages, fname=''):
    s = sidebar(pages, slug)
    nav_btns = nav_buttons(pages, slug)
    bc_html = breadcrumb(pages, slug)
    seo = {}
    for p in pages:
        if p[0] == slug:
            seo = {'desc': p[4], 'keywords': p[5]}
            break
    desc = seo.get('desc', f'Droidspaces documentation - {title}')
    keywords = seo.get('keywords', 'Droidspaces, Linux containers, Android containers')

    nav_html = nav_template.replace('{{DOCS_ATTR}}', ' aria-current="page"').replace('{{DOWNLOADS_ATTR}}', '')
    if slug == 'community-supported-devices':
        # right above the first device table, where the reader is when they want it
        body = body.replace('<div class="table-wrap">', DEVICE_FILTER + '<div class="table-wrap">', 1)
    edit = f'https://github.com/ravindu644/Droidspaces-OSS/edit/main/Documentation/{fname}'
    return fill(os.path.join(ROOT, 'template.html'), {
        'TITLE': title, 'DESC': desc, 'KEYWORDS': keywords, 'SLUG': slug, 'NAV': nav_html,
        'BREADCRUMB': bc_html, 'SIDEBAR': s, 'BODY': body, 'DOC_NAV': nav_btns, 'FOOTER': footer_template,
        'TOC': toc(body), 'EDIT_URL': edit})

def fix_img_paths(html):
    return re.sub(r'Documentation/resources/', r'assets/resources/', html)

def fetch_stars():
    # None on any failure, so the last stamped value stays
    req = urllib.request.Request('https://api.github.com/repos/ravindu644/Droidspaces-OSS')
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return f"{json.loads(resp.read())['stargazers_count']:,}"
    except Exception:
        return None


def count_contributors(repo):
    # Commit authors plus Co-authored-by trailers, which is where Weblate credits its translators.
    # The REST contributors endpoint misses both, and GitHub's own count drops anyone whose email
    # is not on a GitHub account, so history is the only complete source. None if there is no history.
    try:
        log = subprocess.run(
            ['git', '-C', repo, 'log', '--format=%aN <%aE>%n%(trailers:key=Co-authored-by,valueonly)'],
            capture_output=True, text=True, check=True).stdout
    except Exception:
        return None
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    for line in set(log.splitlines()):
        m = re.match(r'\s*(.+?)\s*<([^>]+)>', line)
        if not m or re.search(r'weblate\.org|\[bot\]|copilot@github|noreply@anthropic', line, re.I):
            continue  # Weblate's own accounts, bots and AI agents are not people
        # the same name or the same email is the same person
        parent[find('n:' + m.group(1).lower())] = find('e:' + m.group(2).lower())
    return f"{len({find(k) for k in parent}):,}" if parent else None


def fetch_latest_release():
    try:
        url = 'https://api.github.com/repos/ravindu644/Droidspaces-OSS/releases?per_page=5'
        req = urllib.request.Request(url)
        token = os.environ.get('GITHUB_TOKEN')
        if token:
            req.add_header('Authorization', f'Bearer {token}')
        with urllib.request.urlopen(req, timeout=10) as resp:
            releases = json.loads(resp.read())
    except Exception:
        return None

    if not releases:
        return None

    latest = releases[0]
    version = latest.get('tag_name', 'v6.2.0')
    date = latest.get('published_at', '2026-05-22')[:10]
    apk_url = ''
    tar_url = ''
    for a in latest.get('assets', []):
        name = a.get('name', '')
        if name.endswith('.apk'):
            apk_url = a.get('browser_download_url', '')
        elif name.endswith('.tar.gz'):
            tar_url = a.get('browser_download_url', '')
    body = latest.get('body', '')
    changelog = md_to_html(body) if body else '<p>No changelog available.</p>'

    older_rows = []
    for r in releases[1:]:
        tag = r.get('tag_name', '')
        rd = r.get('published_at', '')[:10]
        rn = r.get('name', tag)
        older_rows.append(
            f'<tr><td>{rn}</td><td>{rd}</td>'
            f'<td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/{tag}" rel="noopener noreferrer">Release page</a></td></tr>'
        )
    older_html = (
        '<div class="table-wrap"><table><thead><tr><th>Version</th><th>Date</th><th></th></tr></thead><tbody>'
        + '\n'.join(older_rows)
        + '</tbody></table></div>'
        if older_rows else ''
    )

    return {
        'version': version,
        'date': date,
        'apk_url': apk_url,
        'tar_url': tar_url,
        'changelog': changelog,
        'older_html': older_html,
    }


def build_downloads_page(root, nav_template, footer_template):
    dl_nav = nav_template.replace('{{DOCS_ATTR}}', '').replace('{{DOWNLOADS_ATTR}}', ' aria-current="page"')
    release_info = fetch_latest_release()
    if release_info:
        version = release_info['version']
        date = release_info['date']
        apk_url = release_info['apk_url']
        tar_url = release_info['tar_url']
        changelog = release_info['changelog']
        older_html = release_info['older_html']
    else:
        version = 'v6.2.0'
        date = '2026-05-22'
        apk_url = 'https://github.com/ravindu644/Droidspaces-OSS/releases/download/v6.2.0/Droidspaces-universal-v6.2.0-2026-05-22.apk'
        tar_url = 'https://github.com/ravindu644/Droidspaces-OSS/releases/download/v6.2.0/droidspaces-v6.2.0-2026-05-22.tar.gz'
        changelog = md_to_html('''## What's Changed
* fix(terminal): resolve hostname before opening tabs/picker
* fix(terminal/panel): unified OSInfo stream eliminates hostname/metrics null bug
* droidspaces: bump v6.2.0
* Translated using Weblate (#144)
* fix: prevent UI remount and terminal state loss on screen rotation
* fix(service): update terminal session notification count and localize strings
* post_extract_fixes: configure systemd-networkd for eth0 and restrict systemd-resolved for NAT networking
* pipewire: use env for pw-cli in audio setup
* fix(service): update notification tap action and improve foreground service strings
* fix: allow webview dom storage for better js dialog handling
* Translated using Weblate (Chinese (Simplified))
* Translated using Weblate (Turkish)
* Translated using Weblate (Ukrainian)''')
        older_html = '<div class="table-wrap"><table><thead><tr><th>Version</th><th>Date</th><th></th></tr></thead><tbody><tr><td>v6.1.5</td><td>2026-05-15</td><td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/v6.1.5" rel="noopener noreferrer">Release page</a></td></tr><tr><td>v6.1.0</td><td>2026-05-13</td><td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/v6.1.0" rel="noopener noreferrer">Release page</a></td></tr><tr><td>v6.0.0</td><td>2026-04-24</td><td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/v6.0.0" rel="noopener noreferrer">Release page</a></td></tr></tbody></table></div>'
    html = fill(os.path.join(root, 'template-downloads.html'), {
        'NAV': dl_nav, 'FOOTER': footer_template, 'VERSION': version, 'DATE': date,
        'APK_URL': apk_url, 'TAR_URL': tar_url, 'CHANGELOG': changelog, 'OLDER': older_html})
    with open(os.path.join(root, 'downloads.html'), 'w') as f:
        f.write(html)
    print("OK: downloads.html")

def generate_sitemap(root, pages):
    # every page the build rendered, so a page added or removed upstream is never stale here
    base = 'https://www.droidspaces.org'
    today = __import__('datetime').date.today().isoformat()
    urls = [('/', 1.0), ('/downloads.html', 0.9)]
    urls += [(f'/docs/{p[0]}.html', 0.9 if p[2] == 'Basics' else 0.7) for p in pages]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pri in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{base}{loc}</loc>')
        lines.append(f'    <lastmod>{today}</lastmod>')
        lines.append(f'    <changefreq>monthly</changefreq>')
        lines.append(f'    <priority>{pri}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    with open(os.path.join(root, 'sitemap.xml'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print("OK: sitemap.xml")

def stamp_assets(root):
    """GitHub Pages lets browsers cache CSS, JS and fonts for four hours, so a deploy would pair new
    HTML with old styles. Each asset URL carries a hash of the file, which changes only when it does.
    Fonts and tokens are stamped inside site.css first, so a new font also gives site.css a new hash."""
    import hashlib, glob
    def ver(path):
        return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:10]
    css_path = os.path.join(root, 'assets/css/site.css')
    css = open(css_path).read()
    css = re.sub(r'url\("\.\./fonts/([\w.-]+)(?:\?v=\w+)?"\)',
                 lambda m: f'url("../fonts/{m.group(1)}?v={ver(os.path.join(root, "assets/fonts", m.group(1)))}")', css)
    css = re.sub(r'@import url\("tokens\.css(?:\?v=\w+)?"\)',
                 lambda m: f'@import url("tokens.css?v={ver(os.path.join(root, "assets/css/tokens.css"))}")', css)
    open(css_path, 'w').write(css)
    for page in glob.glob(os.path.join(root, '*.html')) + glob.glob(os.path.join(root, 'docs/*.html')):
        if os.path.basename(page).startswith('template'):
            continue
        html = open(page).read()
        stamped = re.sub(r'(/assets/(?:css|js)/[\w.-]+)(?:\?v=\w+)?"',
                         lambda m: f'{m.group(1)}?v={ver(os.path.join(root, m.group(1).lstrip("/")))}"', html)
        if stamped != html:
            open(page, 'w').write(stamped)
    print("OK: asset versions")

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs_dir = os.path.join(root, 'docs/content')
    out_dir = os.path.join(root, 'docs')

    with open(os.path.join(root, '_nav.html')) as f:
        nav_template = f.read()
    with open(os.path.join(root, '_footer.html')) as f:
        footer_template = f.read()

    pages = load_pages(docs_dir)
    search_index = []

    for slug, title, section, order, desc, keywords, fname in pages:
        path = os.path.join(docs_dir, fname)
        if not os.path.exists(path):
            print(f"SKIP: {fname} not found")
            continue
        with open(path) as f:
            md = f.read()
        md = re.sub(r'^\s*<!--.*?-->\s*', '', md, flags=re.DOTALL)
        body = md_to_html(md)
        body = fix_img_paths(body)
        slug = fname.replace('.md', '').lower()
        page = make_page(title, body, slug, nav_template, footer_template, pages, fname)
        search_index.append({'title': title, 'url': f'{slug}.html', 'section': section,
                             'headings': [[hid, text] for _, hid, text in headings(body)], 'text': plain(body)})
        out_path = os.path.join(out_dir, slug + '.html')
        with open(out_path, 'w') as f:
            f.write(page)
        print(f"OK: {slug}.html")
    with open(os.path.join(out_dir, 'search.json'), 'w') as f:
        json.dump(search_index, f, ensure_ascii=False, separators=(',', ':'))
    print("OK: search.json")

    # Stamp index.html
    index_path = os.path.join(root, 'index.html')
    with open(index_path) as f:
        index_html = f.read()
    index_nav = nav_template.replace('{{DOCS_ATTR}}', '').replace('{{DOWNLOADS_ATTR}}', '')
    index_html = re.sub(
        r'<!--NAV_START-->.*?<!--NAV_END-->',
        f'<!--NAV_START-->\n{index_nav}\n<!--NAV_END-->',
        index_html,
        flags=re.DOTALL
    )
    release_info = fetch_latest_release()
    if release_info:
        version = release_info['version']
        index_html = re.sub(
            r'(<span data-version>)v[^<]+(</span>)',
            lambda m: f'{m.group(1)}{version}{m.group(2)}',
            index_html,
        )
        index_html = re.sub(
            r'("softwareVersion"\s*:\s*")v?[^"\n]+(",)',
            lambda m: f'{m.group(1)}{version.lstrip("v")}{m.group(2)}',
            index_html,
        )
    stats = {'stars': fetch_stars(),
             'contributors': count_contributors(os.environ.get('SOURCE_REPO', '/tmp/source'))}
    for key, value in stats.items():
        if value:
            index_html = re.sub(
                rf'(<span data-{key}>)[^<]*(</span>)',
                lambda m: f'{m.group(1)}{value}{m.group(2)}',
                index_html,
            )
    index_html = index_html.replace('{{FOOTER}}', footer_template)
    with open(index_path, 'w') as f:
        f.write(index_html)
    print("OK: index.html")

    # Generate downloads.html
    build_downloads_page(root, nav_template, footer_template)

    # Generate 404.html
    four04_nav = nav_template.replace('{{DOCS_ATTR}}', '').replace('{{DOWNLOADS_ATTR}}', '')
    four04_html = fill(os.path.join(root, 'template-404.html'), {'NAV': four04_nav, 'FOOTER': footer_template})
    with open(os.path.join(root, '404.html'), 'w') as f:
        f.write(four04_html)
    print("OK: 404.html")

    generate_sitemap(root, pages)
    stamp_assets(root)
