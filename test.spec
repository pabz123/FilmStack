# -*- mode: python -*-
a = Analysis(['start_movieflix.py'])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, name='test', console=True)
coll = COLLECT(exe, a.binaries, a.datas, name='test')