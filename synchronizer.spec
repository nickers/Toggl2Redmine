# -*- mode: python -*-

block_cipher = None


a = Analysis(['toggltoredmine\\synchronizer.py'],
             pathex=['d:\\projects\\Toggl2Redmine'],
             binaries=None,
             datas=[ ('config.yml.example', '.'), ],
             hiddenimports=['redmine.resources'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='synchronizer',
          debug=False,
          strip=False,
          upx=True,
          console=True )
