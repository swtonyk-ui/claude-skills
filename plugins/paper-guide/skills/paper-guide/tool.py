"""paper-guide helper.

  extract <out_dir> <pdf> [<pdf> ...]   text per page + embedded figures + contact sheets
  preview <pdf> <out_png>               page thumbnails of a rendered PDF on one sheet

Run with:  python3 tool.py ...   (needs: pip install pymupdf pillow)
"""
import sys
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw


def extract(out, pdfs):
    out = Path(out)
    (out / "img").mkdir(parents=True, exist_ok=True)
    figs = []
    for k, pdf in enumerate(pdfs):
        tag = chr(ord("A") + k)  # A, B, ... per paper
        doc = pymupdf.open(pdf)
        (out / f"{tag}.txt").write_text(
            "\n".join(f"=====PAGE {i + 1}\n{p.get_text()}" for i, p in enumerate(doc)))
        for i, page in enumerate(doc):
            for j, im in enumerate(page.get_images(full=True)):
                x = doc.extract_image(im[0])
                if x["width"] * x["height"] < 40000:  # skip logos / icons
                    continue
                fn = out / "img" / f"{tag}_p{i + 1}_{j}.{x['ext']}"
                fn.write_bytes(x["image"])
                figs.append(fn)
        print(f"{tag}: {pdf} -> {len(doc)} pages")
    # contact sheets, 12 figures each, labelled with file name
    W, H, per = 600, 450, 12
    for n in range(0, len(figs), per):
        chunk = figs[n:n + per]
        sheet = Image.new("RGB", (W * 4, H * ((len(chunk) + 3) // 4)), "white")
        d = ImageDraw.Draw(sheet)
        for k, f in enumerate(chunk):
            im = Image.open(f).convert("RGB")
            im.thumbnail((W - 10, H - 30))
            x, y = (k % 4) * W, (k // 4) * H
            sheet.paste(im, (x + 5, y + 25))
            d.text((x + 5, y + 5), f.name, fill="red")
        sheet.save(out / f"sheet_{n // per + 1}.jpg", quality=80)
    print(f"{len(figs)} figures, {(len(figs) + per - 1) // per} contact sheets in {out}")


def preview(pdf, out_png):
    doc = pymupdf.open(pdf)
    ims = [Image.frombytes("RGB", (p.width, p.height), p.samples)
           for p in (pg.get_pixmap(dpi=40) for pg in doc)]
    w, h = ims[0].size
    cols = 6
    sheet = Image.new("RGB", (w * cols, h * ((len(ims) + cols - 1) // cols)), "grey")
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * w, (k // cols) * h))
    sheet.save(out_png)
    print(f"{len(ims)} pages -> {out_png}")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    if cmd == "extract":
        extract(args[0], args[1:])
    elif cmd == "preview":
        preview(*args)
    else:
        sys.exit(__doc__)
