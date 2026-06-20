"""Render a STATIC preview of the app (uses Jinja2 only) into site_preview/.

Doubles as (a) a way to verify the templates/data without running a server, and
(b) an optional static export. The deployable runtime is the FastAPI app in app/main.py;
both share app/templates and app/profiles.py.
"""
import os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.profiles import build_profiles, facets, initials

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site_preview")
env = Environment(loader=FileSystemLoader(os.path.join(ROOT, "app", "templates")),
                  autoescape=select_autoescape(["html"]))


def main():
    profiles = build_profiles()
    for p in profiles:
        p["initials"] = initials(p["name"])
        p["url"] = f"p/{p['slug']}.html"
    fac = facets(profiles)
    if os.path.exists(OUT):
        shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "p"), exist_ok=True)
    shutil.copytree(os.path.join(ROOT, "app", "static"), os.path.join(OUT, "static"), dirs_exist_ok=True)

    env.get_template("index.html").stream(
        profiles=profiles, facets=fac, home_url="index.html", static="static"
    ).dump(os.path.join(OUT, "index.html"))

    for p in profiles:
        pp = dict(p, url=p["slug"] + ".html")  # sibling links within p/
        env.get_template("profile.html").stream(
            p=pp, profiles=profiles, facets=fac, home_url="../index.html", static="../static"
        ).dump(os.path.join(OUT, "p", f"{p['slug']}.html"))
    print(f"Rendered {len(profiles)} profiles -> {OUT}/index.html")


if __name__ == "__main__":
    main()
