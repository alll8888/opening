#!/usr/bin/env python3
"""產生 opening 的目錄頁 index.html：列出倉庫裡每一個網頁，手機一點就開、可直接分享。

規則：
- 掃描所有 .html（略過根目錄 index.html 本身與 tools/）
- 標題取自每頁的 <title>；沒有就用檔名
- 依最後修改日期（git 紀錄）由新到舊排列
由 GitHub Actions 在每次推送後自動執行，不需手動維護。
"""
import html, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://alll8888.github.io/opening/"


def last_date(path: pathlib.Path) -> str:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", str(path.relative_to(ROOT))],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.strip()
    return out or "—"


def title_of(path: pathlib.Path) -> str:
    m = re.search(r"<title>(.*?)</title>", path.read_text(encoding="utf-8", errors="ignore"), re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else path.stem


def main():
    pages = []
    for p in ROOT.rglob("*.html"):
        rel = p.relative_to(ROOT).as_posix()
        if rel == "index.html" or rel.startswith("tools/") or rel.startswith("."):
            continue
        url = rel[: -len("index.html")] if rel.endswith("/index.html") else rel
        pages.append((last_date(p), title_of(p), url))
    pages.sort(key=lambda x: x[0], reverse=True)

    items = "\n".join(
        f'<li><a href="{html.escape(u)}"><span class="t">{html.escape(t)}</span>'
        f'<span class="d">{d}</span></a></li>'
        for d, t, u in pages
    )
    doc = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>璁導｜公開頁面</title>
<style>
:root{{--bg:#faf8f4;--fg:#1f1d1a;--muted:#7a746b;--line:#e6e1d8;--gold:#9c7a3c}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151412;--fg:#ece8e1;--muted:#9a948a;--line:#2c2a26;--gold:#c9a46a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,"PingFang TC","Noto Sans TC",sans-serif}}
main{{max-width:640px;margin:0 auto;padding:40px 16px}}
h1{{font-size:22px;font-weight:600;margin:0 0 4px}}
p{{color:var(--muted);margin:0 0 24px;font-size:14px}}
ul{{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}}
li a{{display:flex;justify-content:space-between;gap:12px;padding:16px 4px;border-bottom:1px solid var(--line);color:inherit;text-decoration:none}}
li a:active{{background:var(--line)}}
.t{{flex:1}}
.d{{color:var(--muted);font-size:13px;white-space:nowrap}}
footer{{margin-top:32px;font-size:12px;color:var(--muted)}}
footer b{{color:var(--gold);font-weight:600}}
</style>
</head>
<body>
<main>
<h1>公開頁面</h1>
<p>共 {len(pages)} 頁，新的在上面。點進去後用瀏覽器的分享鈕即可傳給別人。</p>
<ul>
{items}
</ul>
<footer><b>璁導</b>｜此目錄自動產生</footer>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(doc, encoding="utf-8")
    print(f"index.html：{len(pages)} 頁")


if __name__ == "__main__":
    main()
