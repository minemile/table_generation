import glob
import os


def load_faces(font_dir: str):
    fonts_paths = glob.glob(font_dir.rstrip('/') + '/**/*.TTF', recursive=True) \
                  + glob.glob(font_dir.rstrip('/') + '/**/*.ttf', recursive=True) \
                  + glob.glob(font_dir.rstrip('/') + '/**/*.woff', recursive=True)

    faces = [
        "@font-face {\n"
        "    font-family: 'pickedfont';\n"
        f"    src: url({i});\n"
        "}" for i in fonts_paths]
    return faces
