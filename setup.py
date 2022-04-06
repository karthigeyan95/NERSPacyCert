from cx_Freeze import setup, Executable

base = None

executables = [Executable("spacyNER.py", base=base)]

packages = ["idna", "os", "google", "spacy", "pdfplumber", "urllib", "json", "sys"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "spacyNER",
    options = options,
    version = "1.0",
    description = 'Extract properties from certificates',
    executables = executables
)
