#!/usr/bin/env python3
"""Generate evidence-led, distinct resource pages for existing PENGE_MULIGHEDER sites.

Input: /site/seo/pages.json. Output: /site/dist|root/<slug>/index.html,
growth.css, guides/index.html, sitemap.xml, and an idempotent root
guide feature. Does not alter existing checkout targets, assets or email.
"""
from pathlib import Path
from datetime import date
from urllib.parse import quote
from html import escape
import json
import re
import sys
import xml.etree.ElementTree as ET

STYLESHEET = """
:root{--radius:18px;--shadow:0 18px 58px rgba(0,0,0,.08);--space:min(1100px,calc(100% - 44px))}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  background:var(--bg);color:var(--text);margin:0;line-height:1.7;letter-spacing:-.01em;
  background-image:radial-gradient(ellipse 52% 19% at 86% 1%,var(--glow),transparent),linear-gradient(180deg,var(--bg),var(--bg));}
a{color:var(--accent)}a:hover{text-decoration-thickness:2px}
img{max-width:100%}
button,a{touch-action:manipulation}
:focus-visible{outline:3px solid var(--accent2);outline-offset:4px}
.skip{position:absolute;left:12px;top:-100px;padding:10px 18px;background:var(--card);z-index:20}
.skip:focus{top:12px}
.rail{border-bottom:1px solid var(--border);background:color-mix(in srgb,var(--bg) 89%,transparent);
  backdrop-filter:blur(14px);position:sticky;top:0;z-index:15}
.rail-inner{width:var(--space);margin:auto;min-height:75px;display:flex;align-items:center;justify-content:space-between;gap:20px}
.brand{font-weight:900;letter-spacing:-.04em;font-size:17px;text-decoration:none;color:var(--text)}
.brand mark{background:none;color:var(--accent2)}
.navlinks{display:flex;align-items:center;flex-wrap:wrap;gap:18px}
.navlinks a{text-decoration:none;color:var(--muted);font-weight:650;font-size:13px}
.navlinks a:hover,.navlinks .on{color:var(--accent)}
.pill-link{display:inline-flex;align-items:center;gap:8px;padding:8px 15px;
border-radius:99px;border:1px solid var(--border);background:var(--card);white-space:nowrap}
.wrap{width:var(--space);margin:0 auto}
.breadcrumbs{padding-top:36px;color:var(--muted);font-size:13px;display:flex;flex-wrap:wrap;gap:10px}
.breadcrumbs a{color:var(--muted);text-decoration:none}
.breadcrumbs a:hover{color:var(--accent)}
.breadcrumbs .slash{opacity:.6}
.hero{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(270px,.75fr);align-items:center;gap:45px;padding:58px 0 64px;border-bottom:1px solid var(--border)}
.eyebrow{text-transform:uppercase;font-size:12px;letter-spacing:.18em;font-weight:850;color:var(--accent)}
h1,h2,h3{line-height:1.15;letter-spacing:-.045em;color:var(--text)}
h1{font-size:clamp(39px,5vw,70px);margin:15px 0 23px;font-weight:850}
.lede{font-size:clamp(17px,1.95vw,21px);line-height:1.68;color:var(--muted);max-width:690px;margin:0 0 24px}
.hero-tag{display:inline-block;font-size:12px;border:1px solid var(--border);
 padding:6px 11px;border-radius:30px;color:var(--muted);margin-right:7px;margin-top:10px}
.hero-art{min-height:300px;display:flex;align-items:center;justify-content:center;position:relative}
.art-board{position:relative;width:100%;max-width:390px;aspect-ratio:1.05;border-radius:24px;
 padding:26px;display:flex;flex-direction:column;justify-content:space-between;
 border:1px solid var(--border);background:linear-gradient(140deg,var(--card),var(--card2));
 box-shadow:var(--shadow);overflow:hidden;transform:rotate(2deg)}
.art-board:after{content:"";position:absolute;width:220px;height:220px;right:-75px;top:-60px;
 background:radial-gradient(circle,var(--glow),transparent 70%);border-radius:100%}
.art-top{display:flex;justify-content:space-between;color:var(--muted);font-size:10px;letter-spacing:.15em;font-weight:900}
.art-logo{font-size:clamp(25px,3vw,47px);font-weight:950;letter-spacing:-.065em;line-height:1;color:var(--text);margin:20px 0}
.signal{display:flex;gap:6px;align-items:end;height:58px}
.signal i{flex:1;background:var(--accent);border-radius:4px 4px 2px 2px;opacity:.86;height:var(--h)}
.art-foot{display:flex;justify-content:space-between;gap:8px;align-items:center;border-top:1px solid var(--border);padding-top:18px;font-size:11px;color:var(--muted)}
.art-foot b{color:var(--accent);font-size:12px}
.art-img{border-radius:11px;width:100%;max-width:335px;max-height:310px;object-fit:cover;box-shadow:var(--shadow)}
.action{display:flex;flex-wrap:wrap;align-items:center;gap:13px;margin:21px 0}
.btn{display:inline-flex;align-items:center;justify-content:center;padding:14px 21px;border-radius:10px;
text-decoration:none;font-size:14px;line-height:1.2;font-weight:800;transition:transform .15s,background .15s}
.btn:hover{transform:translateY(-2px)}
.btn.primary{background:var(--accent);color:var(--onaccent);box-shadow:0 8px 30px var(--glow)}
.btn.secondary{border:1px solid var(--border);color:var(--text);background:var(--card)}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 245px;align-items:start;gap:48px;padding:52px 0 80px}
.article section{padding-bottom:26px;margin-bottom:32px;border-bottom:1px solid var(--border);scroll-margin-top:100px}
.article h2{font-size:clamp(27px,2.6vw,38px);margin:0 0 18px}
.article p{font-size:16px;color:var(--muted);margin:10px 0 16px}
.article ul,.article ol{padding-left:22px}
.article li{color:var(--muted);margin:10px 0}
.article strong{color:var(--text)}
.example{margin:26px 0;padding:23px;border:1px solid var(--border);border-radius:var(--radius);
 background:var(--card);box-shadow:0 7px 28px rgba(0,0,0,.035)}
.example small{display:block;text-transform:uppercase;letter-spacing:.14em;color:var(--accent);font-weight:800;margin-bottom:9px}
.example pre{margin:0;overflow-x:auto;white-space:pre-wrap;word-break:break-word;
font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:13px;line-height:1.65;color:var(--text)}
.note{background:var(--note);border-left:3px solid var(--accent);padding:18px 21px;
border-radius:0 10px 10px 0;color:var(--text);margin:24px 0}
.aside{position:sticky;top:104px}
.aside-card{background:var(--card);border:1px solid var(--border);border-radius:15px;
padding:24px;box-shadow:0 8px 30px rgba(0,0,0,.03)}
.aside-card h3{margin:0 0 12px;font-size:19px}
.aside-card p{color:var(--muted);font-size:13px;line-height:1.65}
.aside-card .btn{width:100%;font-size:13px;margin-top:9px}
.toc{font-size:13px;color:var(--muted);padding:25px 0}
.toc b{text-transform:uppercase;letter-spacing:.12em;font-size:11px;color:var(--text)}
.toc a{display:block;color:var(--muted);text-decoration:none;margin:10px 0;line-height:1.4}
.toc a:hover{color:var(--accent)}
.faq{padding-top:10px}
.faq h2{font-size:33px;margin-bottom:25px}
.faq details{border-bottom:1px solid var(--border);padding:18px 0}
.faq summary{cursor:pointer;font-size:17px;font-weight:750;line-height:1.4;color:var(--text)}
.faq details p{color:var(--muted);font-size:15px}
.offer{background:linear-gradient(112deg,var(--card2),var(--card));border:1px solid var(--border);
 padding:clamp(26px,4vw,52px);border-radius:22px;margin:37px 0 72px;display:grid;
 grid-template-columns:1.3fr .7fr;align-items:center;gap:35px;box-shadow:var(--shadow)}
.offer h2{font-size:clamp(27px,3vw,43px);margin:0 0 13px}
.offer p{color:var(--muted);margin:0}
.offer .btn{width:100%}
.related{padding:10px 0 75px}
.related h2{font-size:28px;margin-bottom:22px}
.related-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.tile{display:block;padding:22px;background:var(--card);border:1px solid var(--border);
 border-radius:15px;color:var(--text);text-decoration:none;min-height:140px}
.tile:hover{border-color:var(--accent)}
.tile small{text-transform:uppercase;letter-spacing:.12em;font-size:11px;color:var(--accent);font-weight:800}
.tile strong{display:block;line-height:1.25;font-size:18px;margin-top:12px;letter-spacing:-.025em}
.site-footer{border-top:1px solid var(--border);color:var(--muted);padding:34px 0 55px;font-size:13px}
.site-footer .wrap{display:flex;justify-content:space-between;flex-wrap:wrap;gap:20px}
.site-footer a{color:var(--muted);margin-left:14px;text-decoration:none}
.library-head{padding:70px 0 32px}
.library-head h1{max-width:880px}
.category{padding:26px 0 45px}
.category h2{font-size:29px;margin:0 0 19px}
.library-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.library-tile{background:var(--card);border:1px solid var(--border);border-radius:16px;
 padding:25px;display:block;text-decoration:none;color:var(--text);min-height:220px}
.library-tile:hover{border-color:var(--accent);box-shadow:var(--shadow)}
.library-tile small{color:var(--accent);font-size:11px;text-transform:uppercase;letter-spacing:.15em;font-weight:800}
.library-tile h3{font-size:23px;line-height:1.25;margin:22px 0 10px}
.library-tile p{color:var(--muted);font-size:14px;line-height:1.6}
@media(max-width:900px){.hero{grid-template-columns:1fr;gap:22px}.hero-art{min-height:235px}
.art-board{max-width:500px;aspect-ratio:1.8}.layout{grid-template-columns:1fr;gap:0}
.aside{position:static;order:-1;padding:0 0 35px;display:block}.toc{display:none}
.related-grid,.library-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.offer{grid-template-columns:1fr}.offer .btn{width:auto}}
@media(max-width:600px){:root{--space:calc(100% - 32px)}
.rail-inner{min-height:70px;flex-wrap:wrap;padding:13px 0;gap:7px}
.navlinks{gap:12px}.navlinks a{font-size:11px}.pill-link{padding:6px 10px}
.breadcrumbs{padding-top:23px}.hero{padding:35px 0 38px}
.hero-art{min-height:190px}.art-board{aspect-ratio:1.55;padding:19px}
.layout{padding-top:32px}.related-grid,.library-grid{grid-template-columns:1fr}
.offer{padding:24px}.brand{font-size:16px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.btn{transition:none}.btn:hover{transform:none}}
"""

def h(s): return escape(str(s), quote=True)
def tag_list(items, name='ul'):
    return '<'+name+'>'+''.join('<li>'+h(item)+'</li>' for item in items)+'</'+name+'>'

def theme_css(c):
    p=c['palette'];variables=';'.join('--'+k+':'+v for k,v in p.items())
    return ':root{'+variables+'}\n'+STYLESHEET

def href(c, slug):
    return c['base'].rstrip('/')+'/'+slug.strip('/')+'/' if slug else c['base'].rstrip('/')+'/'

def nav(c):
    navs=c['nav']
    x=''.join('<a href="'+h(href(c, n['slug']))+'">'+h(n['name'])+'</a>' for n in navs)
    return '<a class="skip" href="#content">Skip to content</a><header class="rail"><div class="rail-inner"><a class="brand" href="'+h(href(c,''))+'">'+h(c['brand'])+'</a><nav class="navlinks" aria-label="Primary">'+x+'</nav></div></header>'

def footer(c):
    return '<footer class="site-footer"><div class="wrap"><span>'+h(c['brand'])+' · '+h(c['footnote'])+'</span><span><a href="'+h(href(c,'guides'))+'">Resources</a><a href="mailto:'+h(c['email'])+'">Email</a><a href="'+h(href(c,''))+'">Home</a></span></div></footer>'

def meta(c, item, slug, typ='WebPage'):
    url=href(c,slug);name=item['title'];description=item['description']
    crumb=[{'@type':'ListItem','position':1,'name':'Home','item':href(c,'')},
           {'@type':'ListItem','position':2,'name':'Guides','item':href(c,'guides')}]
    if slug!='guides':crumb.append({'@type':'ListItem','position':3,'name':name,'item':url})
    ld={'@context':'https://schema.org','@graph':[{
       '@type':typ,'name':name,'headline':name,'url':url,'description':description,
       'inLanguage':'en','dateModified':date.today().isoformat(),
       'author':{'@type':'Person','name':'Philip Lind'},
       'publisher':{'@type':'Organization','name':c['brand']}},{
       '@type':'BreadcrumbList','itemListElement':crumb}]}
    image=c.get('og_image')
    return ('<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="index,follow,max-image-preview:large">'
        '<title>'+h(item['seo_title'])+'</title><meta name="description" content="'+h(description)+'">'
        '<link rel="canonical" href="'+h(url)+'">'
        '<meta property="og:type" content="article"><meta property="og:title" content="'+h(item['seo_title'])+'">'
        '<meta property="og:description" content="'+h(description)+'">'
        '<meta property="og:url" content="'+h(url)+'">'
        + ('<meta property="og:image" content="'+h(image)+'">' if image else '')
        + '<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="'+h(c['palette']['bg'])+'">'
        '<link rel="stylesheet" href="../growth.css">'
        '<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False).replace('</','<\\/')+'</script>')

def section_html(sec, i):
    s='<section id="section-'+str(i)+'"><h2>'+h(sec['heading'])+'</h2>'
    for p in sec.get('paragraphs',[]):s+='<p>'+h(p)+'</p>'
    if sec.get('bullets'):s+=tag_list(sec['bullets'])
    if sec.get('steps'):s+=tag_list(sec['steps'],'ol')
    if sec.get('example'):s+='<div class="example"><small>'+h(sec.get('example_label','WORKED EXAMPLE · ILLUSTRATIVE'))+'</small><pre>'+h(sec['example'])+'</pre></div>'
    if sec.get('note'):s+='<p class="note">'+h(sec['note'])+'</p>'
    return s+'</section>'

def art(c, item):
    if c.get('hero_art'):
        img='<img class="art-img" src="../'+h(c['hero_art'])+'" alt="'+h(c.get('hero_art_alt','Original product artwork'))+'" loading="eager" decoding="async">'
        return '<div class="hero-art">'+img+'</div>'
    heights=[16,39,24,52,35,64,28,44,17,58,39,28,62,33,47]
    bars=''.join('<i style="--h:'+str(n)+'px"></i>' for n in heights)
    return '<div class="hero-art" aria-hidden="true"><div class="art-board"><div class="art-top"><span>'+h(c['brand'])+'</span><span>FIELD / 01</span></div><div class="art-logo">'+h(item['art_title'])+'</div><div class="signal">'+bars+'</div><div class="art-foot"><span>'+h(item['category'])+'</span><b>'+h(item.get('art_tag','CLEAR NEXT STEPS'))+'</b></div></div></div>'

def render_page(c, item, by_slug):
    slug=item['slug'];secs=item['sections'];related=item.get('related')
    if not related:
        related=[p['slug'] for p in by_slug.values() if p['slug']!=slug and p['category']==item['category']][:3]
    related=[s for s in related if s in by_slug and s!=slug][:3]
    call=item.get('cta',c['cta']);toc=''.join('<a href="#section-'+str(i)+'">'+h(s['heading'])+'</a>' for i,s in enumerate(secs,1))
    b='<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="'+h(href(c,''))+'">Home</a><span class="slash">/</span><a href="'+h(href(c,'guides'))+'">Guides</a><span class="slash">/</span><span>'+h(item['category'])+'</span></nav>'
    b+='<section class="hero"><div><p class="eyebrow">'+h(item['category'])+' / '+h(item.get('kicker','Practical guide'))+'</p>'
    b+='<h1>'+h(item['title'])+'</h1><p class="lede">'+h(item['intro'])+'</p>'
    b+='<div class="action"><a class="btn primary" href="'+h(call['url'])+'">'+h(call['label'])+' →</a><a class="btn secondary" href="'+h(href(c,'guides'))+'">Browse more guides</a></div>'
    b+='<span class="hero-tag">Written for real workflows</span><span class="hero-tag">No sign-up to read</span></div>'+art(c,item)+'</section>'
    b+='<div class="layout"><article class="article">'+''.join(section_html(s,i) for i,s in enumerate(secs,1))+'</article>'
    b+='<aside class="aside"><div class="aside-card"><span class="eyebrow">Your next step</span><h3>'+h(call['heading'])+'</h3><p>'+h(call['description'])+'</p><a class="btn primary" href="'+h(call['url'])+'">'+h(call['label'])+' →</a></div>'
    b+='<nav class="toc" aria-label="On this page"><b>On this page</b>'+toc+'</nav></aside></div>'
    if item.get('faq'):
        b+='<section class="faq"><span class="eyebrow">Clear answers</span><h2>Questions worth asking</h2>'
        for f in item['faq']:b+='<details><summary>'+h(f['q'])+'</summary><p>'+h(f['a'])+'</p></details>'
        b+='</section>'
    b+='<section class="offer"><div><p class="eyebrow">'+h(c['brand'])+' / Practical next step</p><h2>'+h(call['heading'])+'</h2><p>'+h(call['description'])+'</p></div><a class="btn primary" href="'+h(call['url'])+'">'+h(call['label'])+' →</a></section>'
    if related:
        b+='<section class="related"><h2>Keep exploring</h2><div class="related-grid">'
        for rs in related:
            p=by_slug[rs]
            b+='<a class="tile" href="'+h(href(c,rs))+'"><small>'+h(p['category'])+'</small><strong>'+h(p['title'])+' →</strong></a>'
        b+='</div></section>'
    return '<!doctype html><html lang="en"><head>'+meta(c,item,slug)+'</head><body>'+nav(c)+'<main id="content" class="wrap">'+b+'</main>'+footer(c)+'</body></html>'

def render_hub(c,items):
    d={'title':c['hub_title'],'seo_title':c['hub_seo_title'],'description':c['hub_description']}
    b='<nav class="breadcrumbs"><a href="'+h(href(c,''))+'">Home</a><span class="slash">/</span><span>Guides</span></nav>'
    b+='<div class="library-head"><p class="eyebrow">'+h(c['brand'])+' / Field notes</p><h1>'+h(c['hub_title'])+'</h1><p class="lede">'+h(c['hub_description'])+'</p><div class="action"><a class="btn primary" href="'+h(c['cta']['url'])+'">'+h(c['cta']['label'])+' →</a><a class="btn secondary" href="'+h(href(c,''))+'">Back to home</a></div></div>'
    categories=list(dict.fromkeys(p['category'] for p in items))
    for cat in categories:
        b+='<section class="category"><h2>'+h(cat)+'</h2><div class="library-grid">'
        for p in items:
            if p['category']!=cat:continue
            b+='<a class="library-tile" href="'+h(href(c,p['slug']))+'"><small>'+h(cat)+'</small><h3>'+h(p['title'])+'</h3><p>'+h(p['description'])+'</p></a>'
        b+='</div></section>'
    b+='<section class="offer"><div><p class="eyebrow">Need an actual quote?</p><h2>'+h(c['cta']['heading'])+'</h2><p>'+h(c['cta']['description'])+'</p></div><a class="btn primary" href="'+h(c['cta']['url'])+'">'+h(c['cta']['label'])+' →</a></section>'
    return '<!doctype html><html lang="en"><head>'+meta(c,d,'guides',typ='CollectionPage')+'</head><body>'+nav(c)+'<main class="wrap" id="content">'+b+'</main>'+footer(c)+'</body></html>'

def attach_home(c,root,items):
    f=root/'index.html'
    if not f.exists():return
    s=f.read_text(encoding='utf-8')
    featured=items[:3]
    links=''.join('<a href="'+h(href(c,p['slug']))+'" style="text-decoration:none;display:block;padding:13px 0;color:#d5f6ef;border-top:1px solid #ffffff25">'+h(p['title'])+' →</a>' for p in featured)
    block=('<!-- SEO_RESOURCE_HUB_START -->\n<section aria-labelledby="seo-resource-title" style="max-width:1100px;margin:45px auto;padding:30px 28px;border-radius:16px;border:1px solid #ffffff28;background:linear-gradient(120deg,#112a31,#17343c);color:white">'
        '<p style="color:#a6ebd5;font-size:12px;letter-spacing:.17em;font-weight:800;text-transform:uppercase">From the studio / practical resources</p>'
        '<h2 id="seo-resource-title" style="font-size:clamp(24px,3vw,38px);line-height:1.22;color:white;margin:12px 0">A useful answer before you buy.</h2>'
        '<p style="color:#c8d9d8;max-width:680px">Real workflows, examples and clear boundaries—so you can decide whether the service or product fits.</p>'
        +links+'<a href="'+h(href(c,'guides'))+'" style="display:inline-block;padding:11px 19px;border-radius:8px;background:#a9eacb;color:#102b2a;text-decoration:none;font-weight:800;margin-top:14px">Browse the complete resource library →</a>'
        '</section>\n<!-- SEO_RESOURCE_HUB_END -->')
    pattern=r'<!-- SEO_RESOURCE_HUB_START -->.*?<!-- SEO_RESOURCE_HUB_END -->'
    if re.search(pattern,s,re.S):s=re.sub(pattern,lambda m:block,s,flags=re.S)
    elif '</main>' in s:s=s.replace('</main>',block+'\n</main>',1)
    else:print('WARNING: no main in',str(f));return
    f.write_text(s,encoding='utf-8')

def update_sitemap(c,root,items):
    path=root/'sitemap.xml';ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
    if path.exists():
        tree=ET.parse(path);r=tree.getroot()
    else:
        r=ET.Element('{'+ns+'}url');tree=ET.ElementTree(r)
    registered={x.findtext('{'+ns+'}loc') : x for x in list(r)}
    for slug in ['guides']+[p['slug'] for p in items]:
        uri=href(c,slug)
        if uri not in registered:
            x=ET.SubElement(r,'{'+ns+'}url')
            ET.SubElement(x,'{'+ns+'}loc').text=uri
            ET.SubElement(x,'{'+ns+'}lastmod').text=date.today().isoformat()
        else:
            el=registered[uri].find('{'+ns+'}lastmod')
            if el is not None:el.text=date.today().isoformat()
    tree.write(path,encoding='utf-8',xml_declaration=True)

def main(where):
    site=Path(where).resolve()
    source=site/'seo'/'pages.json'
    data=json.loads(source.read_text(encoding='utf-8'))
    c=data['site'];items=data['pages'];slugs=[p['slug'] for p in items]
    assert len(slugs)==len(set(slugs)),'Duplicate slugs'
    assert len(items)>0
    for p in items:
        assert p['sections'] and len(p['sections'])>=3,p['slug']
        assert len(p['description'])<=185,p['slug']
        assert len(p['seo_title'])<=95,p['slug']
        assert len(p['intro'])>=80,p['slug']
        assert p['slug'].replace('-','').isalnum(),p['slug']
        assert all(len(x.get('paragraphs',[])) or x.get('bullets') or x.get('steps') for x in p['sections'])
    root=site/('dist' if (site/'dist').is_dir() else '')
    (root/'growth.css').write_text(theme_css(c),encoding='utf-8')
    by={p['slug']:p for p in items}
    for p in items:
        target=root/p['slug']/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(render_page(c,p,by),encoding='utf-8')
    hub=root/'guides'/'index.html';hub.parent.mkdir(parents=True,exist_ok=True)
    hub.write_text(render_hub(c,items),encoding='utf-8')
    attach_home(c,root,items)
    update_sitemap(c,root,items)
    print(json.dumps({'brand':c['brand'],'root':str(root),'new_pages':len(items)+1,'urls':[href(c,p) for p in ['guides']+slugs]}))

if __name__=='__main__':
    main(sys.argv[1])
