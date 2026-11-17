#!/usr/bin/env python3
"""Bundle the whole site into one standalone HTML file for review.

    python3 scripts/preview.py OUT.html

The review page is served sandboxed and cannot fetch the site's other files,
so every page is inlined (CSS, JS, images as data: URIs) and shown in an
iframe via srcdoc. Links between pages are caught inside the frame and passed
to the parent, which swaps the frame's content; that keeps the site clickable
without a server.
"""
import base64
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

css = (ROOT / "assets/css/site.css").read_text()
js = (ROOT / "assets/js/site.js").read_text()


def data_uri(rel):
    p = ROOT / rel
    mime = {".webp": "image/webp", ".jpg": "image/jpeg", ".svg": "image/svg+xml"}[p.suffix]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


ME = data_uri("assets/images/me.webp")

# Inside the frame: page links go to the parent, outside links open a new tab.
BRIDGE = """<script>
document.addEventListener('click', function (e) {
  var a = e.target.closest('a'); if (!a) return;
  var h = a.getAttribute('href') || '';
  if (h.startsWith('#')) return;
  e.preventDefault();
  if (h.startsWith('/')) parent.postMessage({ go: h }, '*');
  else window.open(a.href, '_blank', 'noopener');
}, true);
</script>"""


def inline(page_html):
    s = page_html
    s = s.replace('<link rel="stylesheet" href="/assets/css/site.css">', f"<style>{css}</style>")
    s = s.replace('<script src="/assets/js/site.js" defer></script>', f"<script>{js}</script>{BRIDGE}")
    s = re.sub(r'<source srcset="/assets/images/me\.(avif|webp)" type="[^"]+">\s*', "", s)
    s = re.sub(r'(src|href)="/assets/images/me\.(jpg|webp)"', lambda m: f'{m.group(1)}="{ME}"', s)
    s = re.sub(r'src="/assets/icons/([a-z]+)\.svg"', lambda m: f'src="{data_uri("assets/icons/" + m.group(1) + ".svg")}"', s)
    return s


posts = build.load_posts()
pages = {"/": inline((ROOT / "index.html").read_text()), "/blog/": inline((ROOT / "blog/index.html").read_text())}
for p in posts:
    pages[p["path"]] = inline((ROOT / f"blog/{p['slug']}/index.html").read_text())

texts = {
    "/llms.txt": (ROOT / "llms.txt").read_text(),
    "/sitemap.xml": (ROOT / "sitemap.xml").read_text(),
    "/robots.txt": (ROOT / "robots.txt").read_text(),
}

post_items = "".join(
    f"""<button class="item" data-go="{p['path']}"><span class="tag">{html.escape(p['tag'])} · {p['minutes']} دقیقه</span><b>{html.escape(p['title'])}</b><small>{html.escape(p['description'])}</small></button>"""
    for p in posts
)

doc = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>پیش‌نمایش efazati.org</title>
<style>
:root {{ --bg:#0b0f1c; --panel:#11172a; --line:rgba(255,255,255,.09); --text:#d6dcef; --muted:#8e99b8; --blue:#7CA8FF; --brand:#0077FF; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:15px/1.6 system-ui, "Vazirmatn", Tahoma, sans-serif; height:100vh; display:grid; grid-template-columns:330px 1fr; }}
aside {{ border-left:1px solid var(--line); background:var(--panel); overflow-y:auto; padding:18px 14px 30px; }}
h1 {{ font-size:18px; margin:0 0 4px; color:#fff; }}
.sub {{ color:var(--muted); font-size:13px; margin:0 0 16px; }}
.sub a {{ color:var(--blue); }}
h2 {{ font-size:12px; color:var(--muted); margin:20px 6px 8px; font-weight:600; }}
.item {{ display:block; width:100%; text-align:right; background:none; border:1px solid transparent; border-radius:10px; padding:9px 10px; color:var(--text); cursor:pointer; font:inherit; margin-bottom:4px; }}
.item:hover {{ background:rgba(255,255,255,.04); }}
.item.on {{ background:rgba(0,119,255,.14); border-color:rgba(0,119,255,.4); }}
.item b {{ display:block; color:#fff; font-weight:600; font-size:14px; direction:ltr; text-align:left; }}
.item small {{ display:block; color:var(--muted); font-size:12px; line-height:1.5; margin-top:3px; direction:ltr; text-align:left; }}
.item .tag {{ display:block; font-size:11.5px; color:var(--blue); }}
.notes {{ font-size:13px; color:var(--text); background:rgba(255,255,255,.03); border:1px solid var(--line); border-radius:10px; padding:10px 12px; margin:0 0 6px; }}
.notes li {{ margin-bottom:4px; }}
.notes ul {{ margin:0; padding-right:18px; }}
main {{ display:flex; flex-direction:column; min-width:0; }}
.bar {{ display:flex; align-items:center; gap:8px; padding:10px 14px; border-bottom:1px solid var(--line); background:var(--panel); flex-wrap:wrap; }}
.url {{ flex:1; min-width:160px; direction:ltr; font:13px ui-monospace, monospace; color:var(--muted); background:var(--bg); border:1px solid var(--line); border-radius:8px; padding:6px 10px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.seg button {{ background:var(--bg); color:var(--text); border:1px solid var(--line); padding:6px 12px; cursor:pointer; font:inherit; font-size:13px; }}
.seg button:first-child {{ border-radius:0 8px 8px 0; }} .seg button:last-child {{ border-radius:8px 0 0 8px; }}
.seg button.on {{ background:var(--brand); border-color:var(--brand); color:#fff; }}
.stage {{ flex:1; overflow:auto; display:flex; justify-content:center; background:#05070f; }}
iframe {{ border:0; width:100%; height:100%; background:#060914; }}
.stage.mobile {{ padding:20px; }}
.stage.mobile iframe {{ width:390px; height:844px; flex:none; border-radius:28px; border:8px solid #1d2338; box-shadow:0 20px 60px rgba(0,0,0,.6); }}
pre.txt {{ margin:0; padding:20px; direction:ltr; white-space:pre-wrap; font:13px/1.6 ui-monospace, monospace; color:var(--text); width:100%; }}
.menu-toggle {{ display:none; }}
@media (max-width: 820px) {{
  body {{ grid-template-columns:1fr; grid-template-rows:auto 1fr; }}
  aside {{ display:none; position:fixed; inset:0 0 0 15%; z-index:9; box-shadow:0 0 40px rgba(0,0,0,.6); }}
  body.side aside {{ display:block; }}
  .menu-toggle {{ display:inline-block; }}
  .seg {{ display:none; }}
}}
</style>
</head>
<body>
<aside id="side">
  <h1>efazati.org: پیش‌نمایش</h1>
  <p class="sub">شاخهٔ <code>redesign-blog-llms</code>، <a href="https://github.com/efazati/efazati/pull/1" target="_blank">PR #1</a>. هنوز منتشر نشده.</p>
  <div class="notes"><ul>
    <li>لینک‌های داخل سایت کار می‌کنن؛ لینک‌های بیرونی تب تازه باز می‌کنن.</li>
    <li>دکمهٔ «موبایل» بالا، منو رو هم می‌شه تست کرد: بیرونش بزنی بسته می‌شه.</li>
    <li>آمادگی برای کار: فقط «open to new work» در hero و «from a second opinion to building it with you» در بخش تماس.</li>
  </ul></div>
  <h2>صفحه‌ها</h2>
  <button class="item" data-go="/"><b>Home</b><small>efazati.org</small></button>
  <button class="item" data-go="/blog/"><b>Writing</b><small>/blog/, the full list</small></button>
  <h2>پست‌ها ({len(posts)})</h2>
  {post_items}
  <h2>فایل‌های متنی</h2>
  <button class="item" data-go="/llms.txt"><b>llms.txt</b></button>
  <button class="item" data-go="/sitemap.xml"><b>sitemap.xml</b></button>
  <button class="item" data-go="/robots.txt"><b>robots.txt</b></button>
</aside>
<main>
  <div class="bar">
    <button class="item menu-toggle" style="width:auto;margin:0" onclick="document.body.classList.toggle('side')">☰ فهرست</button>
    <div class="url" id="url">https://efazati.org/</div>
    <div class="seg"><button data-dev="desktop" class="on">دسکتاپ</button><button data-dev="mobile">موبایل</button></div>
  </div>
  <div class="stage" id="stage"><iframe id="frame" title="preview"></iframe></div>
</main>
<script>
const PAGES = {json.dumps(pages).replace("</", "<\\/")};
const TEXTS = {json.dumps(texts).replace("</", "<\\/")};
const stage = document.getElementById('stage');
function go(path) {{
  const [p, hash] = path.split('#');
  const key = p || '/';
  document.getElementById('url').textContent = 'https://efazati.org' + path;
  document.querySelectorAll('aside .item').forEach(b => b.classList.toggle('on', b.dataset.go === key));
  document.body.classList.remove('side');
  if (TEXTS[key] !== undefined) {{
    stage.innerHTML = '';
    const pre = document.createElement('pre'); pre.className = 'txt'; pre.textContent = TEXTS[key]; stage.appendChild(pre);
    return;
  }}
  if (!PAGES[key]) return;
  stage.innerHTML = '<iframe id="frame" title="preview"></iframe>';
  const f = stage.querySelector('iframe');
  f.srcdoc = hash ? PAGES[key].replace('</body>', `<script>addEventListener('load',()=>{{const t=document.getElementById(${{JSON.stringify(hash)}});t&&t.scrollIntoView()}})<\\/script></body>`) : PAGES[key];
}}
document.querySelectorAll('aside .item').forEach(b => b.onclick = () => go(b.dataset.go));
document.querySelectorAll('.seg button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.seg button').forEach(x => x.classList.toggle('on', x === b));
  stage.classList.toggle('mobile', b.dataset.dev === 'mobile');
}});
addEventListener('message', e => {{ if (e.data && e.data.go) go(e.data.go); }});
if (innerWidth <= 820) stage.classList.add('mobile-native');
go('/');
</script>
</body>
</html>
"""

out = pathlib.Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(doc)
print(f"wrote {out} ({out.stat().st_size // 1024} KB, {len(pages)} pages)")
