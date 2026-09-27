import re, os, json, urllib.request

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\u4e00-\u9fff-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def fix_link(url):
    if url.endswith('.md') or '.md#' in url:
        url = url.lower().replace('.md', '.html')
    elif (url.endswith('.html') or '.html#' in url) and not url.startswith('http'):
        url = url.lower()
    return url

def inline_format(text):
    code_spans = []
    def save_code(m):
        code_spans.append(m.group(1))
        return f'\x00CODE{len(code_spans)-1}\x00'
    text = re.sub(r'`([^`]+)`', save_code, text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'<a href="{fix_link(m.group(2))}" rel="noopener noreferrer">{m.group(1)}</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', text)
    for i, cs in enumerate(code_spans):
        text = text.replace(f'\x00CODE{i}\x00', f'<code>{cs}</code>')
    return text

def consume_code(lines, i):
    lang = lines[i].lstrip()[3:].strip()
    indent = len(lines[i]) - len(lines[i].lstrip())
    buf = []
    i += 1
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith('```'):
            i += 1
            break
        if indent > 0 and len(lines[i]) >= indent:
            buf.append(lines[i][indent:] + '\n')
        else:
            buf.append(lines[i] + '\n')
        i += 1
    return f'<div class="code-block"><button class="icon-button copy-btn" onclick="copyCode(this)" aria-label="Copy"><span class="icon" aria-hidden="true">content_copy</span></button><pre><code>{"".join(buf)}</code></pre></div>', i

def md_to_html(md):
    lines = md.split('\n')
    html = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.lstrip().startswith('```'):
            code_html, i = consume_code(lines, i)
            html.append(code_html)
            continue
        if re.match(r'^[-*_]{3,}\s*$', line):
            html.append('<hr>')
            i += 1
            continue

        # Inline anchor tag before heading
        am = re.match(r'^<a\s+id="([^"]+)"\s*/?>\s*</a>\s*$', line.strip())
        if am:
            aid = am.group(1)
            i += 1
            if i < len(lines) and re.match(r'^(#{1,6})\s+', lines[i]):
                hm = re.match(r'^(#{1,6})\s+(.+)$', lines[i])
                level = len(hm.group(1))
                text = inline_format(hm.group(2))
                html.append(f'<h{level} id="{aid}">{text}</h{level}>')
                i += 1
                continue
            else:
                html.append(f'<a id="{aid}"></a>')
                continue

        # Headings
        hm = re.match(r'^(#{1,6})\s+(.+)$', line)
        if hm:
            level = len(hm.group(1))
            text = hm.group(2)
            ain = re.search(r'<a\s+id="([^"]+)"\s*/?>\s*</a>\s*', text)
            if ain:
                aid = ain.group(1)
                text = re.sub(r'<a\s+id="[^"]+"\s*/?>\s*</a>\s*', '', text).strip()
            else:
                aid = slugify(text)
            html.append(f'<h{level} id="{aid}">{inline_format(text)}</h{level}>')
            i += 1
            continue

        # GFM Alerts
        al = re.match(r'>\s*\[!(\w+)\]\s*$', line)
        if al:
            atype = al.group(1).upper()
            i += 1
            qlines = []
            while i < len(lines):
                ql = lines[i]
                if ql.startswith('> '):
                    qlines.append(ql[2:].strip())
                    i += 1
                elif ql.strip() == '>':
                    i += 1
                else:
                    break
            content = '\n'.join(qlines)
            content = inline_format(content)
            html.append(f'<div class="callout callout-{atype.lower()}"><strong class="callout-title">{atype}</strong> {content}</div>')
            continue

        # Multi-line blockquote
        if line.startswith('> ') and not re.match(r'>\s*\[!\w+\]', line):
            qlines = []
            while i < len(lines) and (lines[i].startswith('> ') or lines[i].strip() == '>'):
                if lines[i].strip() == '>':
                    i += 1
                    continue
                qlines.append(lines[i][2:].strip())
                i += 1
            content = ' '.join(qlines)
            content = inline_format(content)
            html.append(f'<blockquote><p>{content}</p></blockquote>')
            continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                rows.append(lines[i])
                i += 1
            html.append(convert_table(rows))
            continue

        # Lists (ordered and unordered) — stack-based recursive nesting
        def is_list_item(ln):
            return bool(re.match(r'^(\s*)(?:\d+\.|[-*+])\s+', ln))

        def item_indent(ln):
            m = re.match(r'^(\s*)', ln)
            return len(m.group(1)) if m else 0

        def item_tag(ln):
            """Return 'ol' for ordered, 'ul' for unordered."""
            stripped = ln.lstrip()
            return 'ol' if re.match(r'^\d+\.\s+', stripped) else 'ul'

        def item_text_content(ln):
            return re.sub(r'^\s*(?:\d+\.|[-*+])\s+', '', ln)

        def consume_list(lines, start, base_indent):
            """Recursively parse a list starting at `start` with `base_indent`.
            Returns (html_string, next_line_index)."""
            i = start
            tag = item_tag(lines[i])
            parts = [f'<{tag}>']
            while i < len(lines):
                ln = lines[i]
                if not ln.strip():
                    # blank line — peek ahead to see if list continues
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and is_list_item(lines[j]) and item_indent(lines[j]) >= base_indent:
                        i = j
                        continue
                    break
                if not is_list_item(ln):
                    break
                ind = item_indent(ln)
                if ind < base_indent:
                    break
                if ind > base_indent:
                    # deeper — recurse as nested list inside current <li>
                    nested_html, i = consume_list(lines, i, ind)
                    parts.append(nested_html)
                    continue
                # Same indent — new sibling list item
                # Close previous <li> if open
                if parts[-1] != f'<{tag}>':
                    parts.append('</li>')
                text = inline_format(item_text_content(ln))
                parts.append(f'<li>{text}')
                i += 1
                # Consume continuation content (code blocks, blockquotes, plain text)
                while i < len(lines):
                    cont = lines[i]
                    if not cont.strip():
                        # blank — check if continuation follows
                        j = i + 1
                        while j < len(lines) and not lines[j].strip():
                            j += 1
                        if j < len(lines):
                            cind = item_indent(lines[j]) if is_list_item(lines[j]) else (len(lines[j]) - len(lines[j].lstrip()))
                            if cind > base_indent:
                                i = j
                                continue
                        break
                    s = cont.lstrip()
                    cind = len(cont) - len(s)
                    if is_list_item(cont) and item_indent(cont) > base_indent:
                        nested_html, i = consume_list(lines, i, item_indent(cont))
                        parts.append(nested_html)
                    elif is_list_item(cont) and item_indent(cont) == base_indent:
                        break
                    elif cind > base_indent and s.startswith('```'):
                        ch, i = consume_code(lines, i)
                        parts.append(ch)
                    elif cind > base_indent and s.startswith('> '):
                        parts.append(f'<blockquote>{inline_format(s[2:])}</blockquote>')
                        i += 1
                    elif cind > base_indent and s.strip():
                        parts.append(f'<p>{inline_format(s)}</p>')
                        i += 1
                    else:
                        break
            # Close any open <li>
            if parts and parts[-1] != f'<{tag}>':
                parts.append('</li>')
            parts.append(f'</{tag}>')
            return '\n'.join(parts), i

        if is_list_item(line):
            base = item_indent(line)
            list_html, i = consume_list(lines, i, base)
            html.append(list_html)
            continue

        # Paragraph
        para = []
        while i < len(lines) and lines[i].strip():
            if lines[i].lstrip().startswith('```'):
                break
            text = inline_format(lines[i].rstrip())
            if lines[i].endswith('  '):
                text += '<br>'
            para.append(text)
            i += 1
        if para:
            html.append(f'<p>{" ".join(para)}</p>')
        if i < len(lines) and lines[i].lstrip().startswith('```'):
            code_html, i = consume_code(lines, i)
            html.append(code_html)
    return '\n'.join(html)

def convert_table(rows):
    if len(rows) < 2:
        return ''
    header = rows[0]
    data = rows[2:]
    cols = [c.strip() for c in header.split('|')]
    if cols and not cols[0]: cols = cols[1:]
    if cols and not cols[-1]: cols = cols[:-1]
    html_s = '<div class="table-wrap"><table>\n<thead>\n<tr>'
    for c in cols:
        html_s += f'<th>{inline_format(c)}</th>'
    html_s += '</tr>\n</thead>\n<tbody>\n'
    for row in data:
        cells = [c.strip() for c in row.split('|')]
        if cells and not cells[0]: cells = cells[1:]
        if cells and not cells[-1]: cells = cells[:-1]
        if not any(c for c in cells):
            continue
        html_s += '<tr>'
        for c in cells:
            html_s += f'<td>{inline_format(c)}</td>'
        html_s += '</tr>\n'
    html_s += '</tbody>\n</table></div>'
    return html_s

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
        lines.append('<div class="sidebar-group">')
        lines.append(f'<div class="sidebar-heading">{section}</div>')
        for href, label in groups[section]:
            active = ' aria-current="page"' if href == slug else ''
            lines.append(f'<a href="{href}.html" class="sidebar-link"{active}>{label}</a>')
        lines.append('</div>')
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

TEMPLATE = open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'template.html')).read()

def make_page(title, body, slug, nav_template, footer_template, pages, is_index=False):
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
    page = TEMPLATE
    for key, value in {'TITLE': title, 'DESC': desc, 'KEYWORDS': keywords, 'SLUG': slug, 'NAV': nav_html,
                       'BREADCRUMB': bc_html, 'SIDEBAR': s, 'BODY': body, 'DOC_NAV': nav_btns, 'FOOTER': footer_template}.items():
        page = page.replace('{{' + key + '}}', value)
    return page

def fix_img_paths(html):
    return re.sub(r'Documentation/resources/', r'assets/resources/', html)

def fetch_kernel_patches():
    base = 'https://api.github.com/repos/ravindu644/Droidspaces-OSS/contents/Documentation/resources/kernel-patches'
    data = json.loads(urllib.request.urlopen(base).read())
    parts = []
    for item in data:
        if item['type'] == 'dir':
            name = item['name']
            sub = json.loads(urllib.request.urlopen(item['url']).read())
            parts.append(f'<div class="patch-group"><h3 class="patch-group-title">{name}</h3>')
            for s in sub:
                if s['type'] == 'dir':
                    sname = s['name']
                    sub2 = json.loads(urllib.request.urlopen(s['url']).read())
                    parts.append(f'<div class="patch-subgroup"><h4 class="patch-subgroup-title">{sname}</h4><ul class="patch-list">')
                    for s2 in sub2:
                        fname = s2['name']
                        parts.append(f'<li><a href="{s2["download_url"]}" download>{fname}</a></li>')
                    parts.append('</ul></div>')
                else:
                    parts.append(f'<ul class="patch-list"><li><a href="{s["download_url"]}" download>{s["name"]}</a></li></ul>')
            parts.append('</div>')
    return '\n'.join(parts)

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
            f'<td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/{tag}" class="dl-secondary">Download</a></td></tr>'
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
    patches_html = '''<div class="patch-group"><h3 class="patch-group-title">GKI</h3>
<div class="patch-subgroup"><h4 class="patch-subgroup-title">below-kernel-6.12</h4><ul class="patch-list">
<li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/GKI/below-kernel-6.12/001.GKI-below-6.12-fix_sysvipc_kabi_1_2_3.patch" download>001.GKI-below-6.12-fix_sysvipc_kabi_1_2_3.patch</a></li>
<li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/GKI/below-kernel-6.12/001.GKI-below-6.12-fix_sysvipc_kabi_3_4_5.patch" download>001.GKI-below-6.12-fix_sysvipc_kabi_3_4_5.patch</a></li>
<li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/GKI/below-kernel-6.12/001.GKI-below-6.12-fix_sysvipc_kabi_6_7_8.patch" download>001.GKI-below-6.12-fix_sysvipc_kabi_6_7_8.patch</a></li>
<li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/GKI/below-kernel-6.12/002.5.10_or_lower_use_android_abi_padding_for_posix_mqueue.patch" download>002.5.10_or_lower_use_android_abi_padding_for_posix_mqueue.patch</a></li>
</ul></div>
<div class="patch-subgroup"><h4 class="patch-subgroup-title">kernel-6.12</h4><ul class="patch-list">
<li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/GKI/kernel-6.12/001.GKI-6.12-or-above-fix_sysvipc_kabi.patch" download>001.GKI-6.12-or-above-fix_sysvipc_kabi.patch</a></li>
</ul></div>
</div>
<div class="patch-group"><h3 class="patch-group-title">non-GKI</h3>
<ul class="patch-list"><li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/non-GKI/01.fix_kernel_panic_in_xt_qtaguid.patch" download>01.fix_kernel_panic_in_xt_qtaguid.patch</a></li></ul>
<ul class="patch-list"><li><a href="https://raw.githubusercontent.com/ravindu644/Droidspaces-OSS/main/Documentation/resources/kernel-patches/non-GKI/02.fix_restore%20cgroup%20file%20prefix%20handling%20.patch" download>02.fix_restore cgroup file prefix handling .patch</a></li></ul>
</div>'''
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
        older_html = '<div class="table-wrap"><table><thead><tr><th>Version</th><th>Date</th><th></th></tr></thead><tbody><tr><td>v6.1.5</td><td>2026-05-15</td><td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/v6.1.5" class="dl-secondary">Download</a></td></tr><tr><td>v6.1.0</td><td>2026-05-13</td><td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/v6.1.0" class="dl-secondary">Download</a></td></tr><tr><td>v6.0.0</td><td>2026-04-24</td><td><a href="https://github.com/ravindu644/Droidspaces-OSS/releases/tag/v6.0.0" class="dl-secondary">Download</a></td></tr></tbody></table></div>'
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Download Droidspaces — APK for Android, tarball for Linux, kernel patches, and changelogs.">
  <title>Downloads - Droidspaces</title>
  <meta property="og:title" content="Downloads - Droidspaces">
  <meta property="og:description" content="Download Droidspaces — APK for Android, tarball for Linux, kernel patches, and changelogs.">
  <meta property="og:url" content="https://www.droidspaces.org/downloads.html">
  <meta property="og:type" content="website">
  <meta property="og:image" content="https://i.ibb.co/d4PLN7Gg/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Downloads - Droidspaces">
  <meta name="twitter:description" content="Download Droidspaces — APK for Android, tarball for Linux, kernel patches, and changelogs.">
  <meta name="twitter:image" content="https://i.ibb.co/d4PLN7Gg/og-image.png">
  <link rel="canonical" href="https://www.droidspaces.org/downloads.html">
  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/favicon.ico">
  <script>(function(){{const t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})();</script>
</head>
<body>
<!--NAV_START-->
{dl_nav}
<!--NAV_END-->
<main>
  <section class="download-hero">
    <div class="container">
      <div class="section-label">Downloads</div>
      <h1>{version}</h1>
      <p class="hero-desc">Released Date: {date}</p>
      <div class="dl-cards">
        <div class="dl-card">
          <div class="dl-card-icon"><i class="fab fa-android"></i></div>
          <h3 class="dl-card-title">Android</h3>
          <p class="dl-card-desc">APK for rooted Android devices. KernelSU, Magisk, or APatch.</p>
          <a href="{apk_url}" class="btn btn-primary dl-card-btn"><i class="fas fa-download"></i> Download APK</a>
        </div>
        <div class="dl-card">
          <div class="dl-card-icon"><i class="fab fa-linux"></i></div>
          <h3 class="dl-card-title">Linux</h3>
          <p class="dl-card-desc">Static tarball for any Linux distribution. Zero dependencies.</p>
          <a href="{tar_url}" class="btn btn-primary dl-card-btn"><i class="fas fa-download"></i> Download Tarball</a>
        </div>
      </div>
      <div style="text-align:center;margin-top:1.5rem">
        <a href="https://github.com/ravindu644/Droidspaces-OSS/releases" class="btn btn-ghost" rel="noopener noreferrer">All Releases &rarr;</a>
      </div>
    </div>
  </section>
  <div class="divider"></div>
  <section class="section">
    <div class="container">
      <div class="section-label">Kernel Patches</div>
      <h2>Download kernel patches</h2>
      <p class="section-desc">Patches for custom kernel builds. Select your kernel type and version.</p>
      {patches_html}
    </div>
  </section>
  <div class="divider"></div>
  <section class="section">
    <div class="container">
      <div class="section-label">Changelog</div>
      <h2>{version}</h2>
      <div class="changelog-wrap">
        <div class="changelog" id="changelog-body">
          {changelog}
        </div>
        <button class="changelog-toggle" id="changelog-toggle" onclick="document.getElementById('changelog-body').classList.toggle('expanded');this.textContent=this.textContent==='Show changelog'?'Hide changelog':'Show changelog'">Show changelog</button>
      </div>
    </div>
  </section>
  <div class="divider"></div>
  <section class="section">
    <div class="container">
      <div class="section-label">Older Versions</div>
      <h2>Previous releases</h2>
      {older_html}
    </div>
  </section>
</main>
{footer_template}
<script src="/assets/js/site.js" defer></script>
</body>
</html>'''
    with open(os.path.join(root, 'downloads.html'), 'w') as f:
        f.write(html)
    print("OK: downloads.html")

def generate_sitemap(root):
    base = 'https://www.droidspaces.org'
    today = '2026-05-23'
    priorities = {
        'index.html': ('/', 1.0),
        'downloads.html': ('/downloads.html', 0.9),
        '404.html': ('/404.html', 0.1),
    }
    doc_priorities = {
        'installation-android': 0.9, 'installation-linux': 0.8,
        'features': 0.7, 'gpu-acceleration': 0.7, 'kernel-configuration': 0.7,
        'usage-android-app': 0.7, 'linux-cli': 0.7, 'cool-things-you-can-do': 0.6,
        'troubleshooting': 0.6, 'community-supported-devices': 0.5,
        'nix-nixos': 0.5, 'uninstallation': 0.5,
    }
    urls = [(loc, pri) for fname, (loc, pri) in priorities.items()]
    urls += [(f'/docs/{slug}.html', pri) for slug, pri in doc_priorities.items()]
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

if __name__ == '__main__':
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs_dir = os.path.join(root, 'docs/content')
    out_dir = os.path.join(root, 'docs')

    with open(os.path.join(root, '_nav.html')) as f:
        nav_template = f.read()
    with open(os.path.join(root, '_footer.html')) as f:
        footer_template = f.read()

    pages = load_pages(docs_dir)

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
        page = make_page(title, body, slug, nav_template, footer_template, pages)
        out_path = os.path.join(out_dir, slug + '.html')
        with open(out_path, 'w') as f:
            f.write(page)
        print(f"OK: {slug}.html")

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
            r'(<div class="hero-badge"><span></span>)v[^<]+( · Open Source</div>)',
            lambda m: f'{m.group(1)}{version}{m.group(2)}',
            index_html,
        )
        index_html = re.sub(
            r'("softwareVersion"\s*:\s*")v?[^"\n]+(",)',
            lambda m: f'{m.group(1)}{version.lstrip("v")}{m.group(2)}',
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
    four04_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="Page not found - Droidspaces">
  <title>404 - Droidspaces</title>
  <meta property="og:title" content="404 - Droidspaces">
  <meta property="og:description" content="Page not found">
  <meta property="og:url" content="https://www.droidspaces.org/404.html">
  <meta property="og:type" content="website">
  <meta property="og:image" content="https://i.ibb.co/d4PLN7Gg/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="404 - Droidspaces">
  <meta name="twitter:description" content="Page not found">
  <meta name="twitter:image" content="https://i.ibb.co/d4PLN7Gg/og-image.png">
  <link rel="canonical" href="https://www.droidspaces.org/404.html">
  <link rel="icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/favicon.ico">
  <link rel="stylesheet" href="/assets/css/site.css">
  <script>(function(){{const t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})();</script>
</head>
<body>
{four04_nav}
  <main style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:calc(100vh - 56px - 80px);padding:2rem;text-align:center">
    <h1 style="font-size:4rem;font-family:var(--mono);color:var(--muted);margin-bottom:0.5rem">404</h1>
    <p style="color:var(--muted);font-size:1rem;margin-bottom:2rem;max-width:400px">The page you're looking for doesn't exist.</p>
    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;justify-content:center">
      <a href="/" class="btn btn-primary">Go Home</a>
      <a href="/docs/" class="btn btn-ghost">Browse Docs</a>
    </div>
  </main>
{footer_template}
<script src="/assets/js/site.js" defer></script>
</body>
</html>'''
    with open(os.path.join(root, '404.html'), 'w') as f:
        f.write(four04_html)
    print("OK: 404.html")

    generate_sitemap(root)
