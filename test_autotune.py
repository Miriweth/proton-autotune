"""Checks the option-picking logic. Run: python3 test_autotune.py"""
import importlib.machinery, importlib.util, os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proton-autotune")
spec = importlib.util.spec_from_loader("pa", importlib.machinery.SourceFileLoader("pa", path))
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)
s = pa.suggest

assert s(["A=1 %command%"] * 2) is None, "too few reports must give no opinion"
assert s(["A=1 %command% -dx11"] * 3 + ["B=2 %command%"] * 3 + [""] * 4) == "A=1 B=2 %command% -dx11", \
    "options with >= 3 mentions and >= 30 % share are kept"
assert s(["A=1 %command%", "", ""]) is None, "one report is not enough, even at 33 %"
assert s(["A=1 %command%"] * 3 + ["A=2 %command%"] * 4) == "A=2 %command%", "the most common value wins"
assert s(["PROTON_LOG=1 mangohud %command%"] * 5) is None, "debug/overlay options are never copied"
assert s(['DXVK_CONFIG="a = b" %command%'] * 3) == "DXVK_CONFIG='a = b' %command%", \
    "quoted values with spaces stay one token and are re-quoted"
assert s(["W='dinput8=n,b' %command%"] * 3) == "W=dinput8=n,b %command%", "harmless quotes are dropped"
assert s(["%command% -w 1920 -h 1080"] * 3) is None, "flags with a value are not copied without it"
assert s(["%command% ; pkill -9 x"] * 3) is None, "commands after a shell operator are ignored"
assert s(["gamescope -f -- %command%"] * 3) is None, "wrapper flags before %command% are not game args"
assert s(["-dx11 -novid"] * 3) == "%command% -dx11 -novid", "options without %command% count as game args"
assert s(["mesa_glthread=true %command%"] * 3) == "mesa_glthread=true %command%", "lowercase env vars work"
print("ok")

import io
reports = [{"a": i, "s": "x" * (i * 7)} for i in range(50)]
for chunk in (1, 7, 64, 1 << 20):  # objects cut at every possible chunk boundary
    got = list(pa.iter_reports(io.StringIO(" [ " + " , ".join(__import__("json").dumps(r) for r in reports) + " ] "), chunk))
    assert got == reports, f"streaming parse broke at chunk size {chunk}"
assert list(pa.iter_reports(io.StringIO("[]"))) == [], "empty array"
print("ok (streaming)")
