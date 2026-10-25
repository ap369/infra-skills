#!/usr/bin/env python3
"""Generate documented-command catalogs for the DevOps skills from the tools' official reference docs.

Usage (from repo root): python3 scripts/gen_cli_catalogs.py <tool> <source dir> <version> <out.md>

tool          source dir (official, from the project's own repository)
docker        docker/cli               docs/reference/commandline/
kubectl       kubernetes/website       content/en/docs/reference/kubectl/generated/
helm          helm/helm-www            docs/helm/
argocd        argoproj/argo-cd         docs/user-guide/commands/
terraform     hashicorp/web-unified-docs content/terraform/<ver>/docs/cli/commands/
flux          fluxcd/flux2             cmd/flux/            (cobra Go source of the CLI)
monaco        Dynatrace/dynatrace-configuration-as-code cmd/monaco/ (cobra Go source)
promtool      prometheus/prometheus    docs/command-line/promtool.md
icinga2       Icinga/icinga2           doc/11-cli-commands.md

The output lists command paths and their own flags (inherited/global flags and --help are left out).
Only names are copied, never descriptions, so the catalogs are short factual indexes of the docs.
"""
import html
import os
import pathlib
import re
import sys
from datetime import date

SKIP_FLAGS = {"-h", "--help"}
TITLE_OVERRIDE = os.environ.get("CATALOG_TITLE", "")  # compose | buildx: docker-format docs of a sibling tool


def flags_from_text(text):
    out = []
    for m in re.finditer(r"(?<![\w-])(-{1,2}[a-zA-Z][\w-]*)", text):
        f = m.group(1)
        if f not in SKIP_FLAGS and f not in out:
            out.append(f)
    return out


def docker(src):
    rows = []
    for f in sorted(pathlib.Path(src).glob("*.md")):
        t = f.read_text()
        gen = t.split("<!---MARKER_GEN_START-->", 1)[-1].split("<!---MARKER_GEN_END-->", 1)[0]
        al = re.search(r"### Aliases\s+`([^`]+)`", gen)
        cmd = al.group(1) if al else ("docker" if f.stem == "docker" else "docker " + f.stem.replace("_", " "))
        opts = gen.split("### Options", 1)[1] if "### Options" in gen else ""
        fl = []
        for row in re.findall(r"^\|\s*(.+?)\s*\|", opts, re.M):
            for x in re.findall(r"`(-{1,2}[\w-]+)`", row):
                if x not in SKIP_FLAGS and x not in fl:
                    fl.append(x)
        rows.append((cmd, fl, f.name))
        if al:
            for alias in re.findall(r"`([^`]+)`", gen.split("### Aliases", 1)[1].split("###", 1)[0]):
                if alias != cmd:
                    rows.append((alias, fl, f"alias of `{cmd}`"))
    return rows


def kubectl(src):
    rows = []
    for f in sorted(pathlib.Path(src).rglob("*.md")):
        if f.name == "_index.md" and f.parent.name == "generated":
            continue
        t = f.read_text()
        title = re.search(r"^title:\s*(.+)$", t, re.M)
        if not title:
            continue
        cmd = title.group(1).strip()
        opts = t.split('heading "options"', 1)[1].split('heading "parentoptions"', 1)[0] if 'heading "options"' in t else ""
        fl = []
        for cell in re.findall(r'<td colspan="2">(.*?)</td>', opts):
            for x in re.findall(r"(?<![\w-])(-{1,2}[a-zA-Z][\w-]*)", html.unescape(cell)):
                if x not in SKIP_FLAGS and x not in fl:
                    fl.append(x)
        rows.append((cmd, fl, str(f.relative_to(src))))
    return rows


def cobra_md(src, prefix):
    rows = []
    for f in sorted(pathlib.Path(src).glob(f"{prefix}*.md")):
        t = f.read_text()
        title = re.search(r"^## (\S.*)$", t, re.M)
        cmd = title.group(1).strip() if title else f.stem.replace("_", " ")
        opts = re.split(r"### Options inherited", t)[0]
        opts = opts.split("### Options", 1)[1] if "### Options" in opts else ""
        block = re.search(r"```(.*?)```", opts, re.S)
        fl = []
        for line in (block.group(1).splitlines() if block else []):
            for x in re.findall(r"^\s*(?:(-\w), )?(--[\w-]+)", line):
                for y in x:
                    if y and y not in SKIP_FLAGS and y not in fl:
                        fl.append(y)
        rows.append((cmd, fl, f.name))
    return rows


def terraform(src):
    rows = []
    for f in sorted(pathlib.Path(src).rglob("*.mdx")):
        t = f.read_text()
        usage = re.search(r"Usage:\s*`([^`]+)`", t) or re.search(r"^\s*(?:\$ )?(terraform [a-z -]+?)(?: \[| <| [A-Z]|$)", t, re.M)
        cmd = usage.group(1).split(" [")[0].split(" <")[0].strip() if usage else "terraform " + f.stem
        cmd = " ".join(w for w in cmd.split() if not w.isupper())   # drop placeholders such as NAME, ADDRESS
        rel = f.relative_to(src)
        if rel.parts[0] == "stacks":          # Terraform Stacks CLI pages: a separate tool
            continue
        if rel.as_posix() == "index.mdx":     # global options page (e.g. -chdir)
            cmd = "terraform"
        elif not cmd.startswith("terraform") or f.stem == "index" or " -" in cmd:
            continue
        fl = []
        found = re.findall(r"^\s*[-*] `(-[a-z][\w-]*)", t, re.M)              # option lists
        found += re.findall(r"^\|\s*`(-[a-z][\w-]*)", t, re.M)                 # option tables
        found += re.findall(r"`(-[a-z][\w-]*)(?:=[^`]*)?` (?:command line )?(?:option|flag)", t)  # "the `-x` option"
        found += re.findall(r"^\s{2}(-[a-z][\w-]*)(?:=\S+)?\s{2,}\S", t, re.M)   # help-output blocks
        found += [y for pair in re.findall(r"Either `(-[a-z][\w-]*)` or `(-[a-z][\w-]*)`", t) for y in pair]
        for x in found:
            if x not in fl:
                fl.append(x)
        rows.append((cmd, fl, str(f.relative_to(src))))
    return rows


def cobra_go(src, root):
    """Reconstruct the cobra command tree from Go source: vars with Use:, AddCommand calls, Flags() calls."""
    cmds, parent, flags, files = {}, {}, {}, {}
    for f in sorted(pathlib.Path(src).rglob("*.go")):
        if f.name.endswith("_test.go"):
            continue
        t = f.read_text()
        for m in re.finditer(r"(\w+)\s*:?=\s*&cobra\.Command\{(.*?)\n\}", t, re.S):
            use = re.search(r'Use:\s*"([^"]+)"', m.group(2))
            if use:
                cmds[m.group(1)] = use.group(1).split()[0]
                files[m.group(1)] = f.name
        for m in re.finditer(r"(\w+)\.AddCommand\(([^)]*)\)", t):
            for child in re.findall(r"\w+", m.group(2)):
                parent.setdefault(child, m.group(1))
        for m in re.finditer(r'(\w+)\.(?:Persistent)?Flags\(\)\.(\w+)\([^"]*"([\w-]+)"(?:,\s*"(\w)")?', t):
            fl = flags.setdefault(m.group(1), [])
            for x in ["--" + m.group(3)] + (["-" + m.group(4)] if m.group(2).endswith("P") and m.group(4) else []):
                if x not in fl:
                    fl.append(x)

    def path(v, seen=()):
        if v in seen:
            return cmds.get(v, v)
        p = parent.get(v)
        if p and p in cmds:
            return path(p, seen + (v,)) + " " + cmds[v]
        return root if cmds.get(v) == root else root + " " + cmds[v]

    rows = [(path(v), flags.get(v, []), files[v]) for v in cmds]
    main_go = pathlib.Path(src) / "main.go"
    if main_go.exists() and "genericclioptions.NewConfigFlags" in main_go.read_text():
        # kubeconfig flags come from k8s.io/cli-runtime ConfigFlags.AddFlags(rootCmd.PersistentFlags())
        rows = [(c, list(f) + ["--kubeconfig", "--context", "-n", "--namespace"] if c == root else f,
                 src_f + " (+ cli-runtime kubeconfig flags)" if c == root else src_f) for c, f, src_f in rows]
    return sorted(set((a, tuple(b), c) for a, b, c in rows))


def promtool(src):
    t = pathlib.Path(src).read_text()
    rows = []
    parts = re.split(r"^#{3,6} `(promtool[^`]*)`\s*$", t, flags=re.M)
    for i in range(1, len(parts), 2):
        body = parts[i + 1]
        fl = []
        for x in re.findall(r"^\|\s*<code class=\"text-nowrap\">(-{1,2}[a-zA-Z][\w.-]*)", body, re.M) + re.findall(r"^\|\s*`?(-{1,2}[a-zA-Z][\w.-]*)", body, re.M):
            if x not in SKIP_FLAGS and x not in fl:
                fl.append(x)
        rows.append((parts[i], fl, "promtool.md"))
    return rows


def icinga2(src):
    t = pathlib.Path(src).read_text()
    listed = re.search(r"Supported commands:\n(.*?)\n\n", t, re.S)
    cmds = ["icinga2 " + re.match(r"\s*\* ([a-z -]+?) \(", l).group(1) for l in listed.group(1).splitlines()
            if re.match(r"\s*\* ([a-z -]+?) \(", l)]
    rows = []
    for cmd in cmds:
        fl = []
        m = re.search(r"Usage:\s*\n\s*" + re.escape(cmd) + r" \[", t)
        if m:
            block = t[m.end(): t.find("```", m.end())]
            glob_opts = set(flags_from_text(t[t.find("Global options:"): t.find("Report bugs")]))
            fl = [x for x in flags_from_text(block) if x.startswith("--") and x not in glob_opts]
            fl += [x for x in re.findall(r"^\s+(-[A-Za-z]) \[ --[\w-]+ \]", block, re.M) if x not in glob_opts and x not in SKIP_FLAGS]
        rows.append((cmd, fl, "11-cli-commands.md"))
    return rows


def monaco(src):
    """monaco builds commands in functions: derive the path from the package directories that are commands."""
    base = pathlib.Path(src)
    found = []
    for f in sorted(base.rglob("*.go")):
        if f.name.endswith("_test.go"):
            continue
        t = f.read_text()
        for m in re.finditer(r"&cobra\.Command\{(.*?)\n\t*\}", t, re.S):
            use = re.search(r'Use:\s*"([^"]+)"', m.group(1))
            if use:
                fl = []
                consts = dict(re.findall(r'(\w+)\s*=\s*"([\w-]{2,})"', t))
                for lit, const in re.findall(r'\.(?:Persistent)?Flags\(\)\.\w+\(\s*(?:&[\w.]+,\s*)?(?:"([\w-]{2,})"|(\w+)\s*,)', t):
                    x = lit or consts.get(const)
                    if x and "--" + x not in fl:
                        fl.append("--" + x)
                found.append((f, use.group(1).split()[0], fl))
    words = {w for _, w, _ in found}
    rows = []
    for f, word, fl in found:
        dirs = [d for d in f.relative_to(base).parent.parts if d in words and d != word]
        cmd = " ".join(["monaco"] + dirs + ([word] if word != "monaco" else []))
        rows.append((cmd, fl, str(f.relative_to(base))))
    return rows


TOOLS = {
    "docker": docker, "kubectl": kubectl, "terraform": terraform, "promtool": promtool, "icinga2": icinga2,
    "helm": lambda s: cobra_md(s, "helm"), "argocd": lambda s: cobra_md(s, "argocd"),
    "flux": lambda s: cobra_go(s, "flux"), "monaco": monaco,
}


def main():
    if len(sys.argv) != 5 or sys.argv[1] not in TOOLS:
        sys.exit(__doc__)
    tool, src, version, out = sys.argv[1:]
    rows, seen = [], set()
    for cmd, fl, f in sorted(TOOLS[tool](src)):
        if cmd not in seen:  # alias pages (e.g. docker ps / docker container ls) list the same command
            seen.add(cmd)
            rows.append((cmd, fl, f))
    title = {"compose": "Docker Compose", "buildx": "Docker Buildx"}.get(TITLE_OVERRIDE, tool)
    lines = [f"<!-- GENERATED by scripts/gen_cli_catalogs.py ({tool} {version}, {date.today()}). Regenerate, don't edit. -->",
             f"# {title} {version}: documented commands and flags", "",
             f"> **Command verification status:** every command path and flag below appears in the official reference for "
             f"**{title} {version}** (source file in the last column). A command or flag listed here is `[doc]` for that version; "
             "a different version may differ, so confirm with the tool's `--help` on the target (`[help]`). "
             "Flags shown on a parent command (persistent flags) also apply to its subcommands. "
             "Anything not listed is `[unverified]` (command-verification.md). Only names are listed: read the official page "
             "for semantics before using a flag in a change.", "",
             f"{len(rows)} commands.", "", "| Command | Flags | Source |", "|---|---|---|"]
    for cmd, fl, f in rows:
        lines.append(f"| `{cmd}` | {' '.join(f'`{x}`' for x in fl) or '—'} | {f} |")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out).write_text("\n".join(lines) + "\n")
    print(f"{title} {version}: {len(rows)} commands -> {out}")


if __name__ == "__main__":
    main()
