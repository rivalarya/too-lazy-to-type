import PyInstaller.__main__
import os
import shutil

# Clean previous build
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# Configuration
app_name = "TooLazyToType"
main_script = "main.py"
icon_file = "media/icon.ico"

# Build command
PyInstaller.__main__.run([
    main_script,
    "--name=%s" % app_name,
    "--onefile",
    "--windowed",
    "--add-data=README.md;.",
    "--add-data=LICENCE;.",
    "--icon=%s" % icon_file,
])

print(f"Build completed: {os.path.join('dist', app_name + '.exe')}")