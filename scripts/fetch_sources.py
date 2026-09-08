# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf==6.1.1"]
# ///
"""Retain primary PDFs locally; publish bibliographic notes, not copyrighted PDFs."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import json
import pypdf

SOURCES = {
    'spielman-laplacian': 'https://cs.yale.edu/homes/spielman/561/lect02-15.pdf',
    'spielman-resistance': 'https://cs.yale.edu/homes/spielman/561/lect13-18.pdf',
    'spielman-trees': 'https://www.cs.yale.edu/homes/spielman/561/lect14-18.pdf',
    'chandra-commute': 'https://homes.cs.washington.edu/~ruzzo/papers/resist.pdf',
    'grady-segmentation': 'https://leogrady.net/wp-content/uploads/2017/01/grady2006random.pdf',
    'klein-resistance': 'https://www.math.pku.edu.cn/teachers/yaoy/Fall2011/KleinRandic1993.pdf',
    'spielman-sparsification': 'https://arxiv.org/pdf/0803.0929',
}

def fetch(item):
    sid, url = item
    folder = Path('work/sources')
    folder.mkdir(parents=True, exist_ok=True)
    result = {'id': sid, 'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat()}
    try:
        path = folder / f'{sid}.pdf'
        if path.exists():
            body = path.read_bytes()
        else:
            with urlopen(Request(url, headers={'User-Agent': 'MathematicsAtlas research/0.1'}), timeout=35) as response:
                body = response.read(30_000_000)
            if not body.startswith(b'%PDF'):
                raise ValueError('Expected a primary PDF, received another format')
            path.write_bytes(body)
        reader = pypdf.PdfReader(path)
        text = '\n\n'.join(f'PAGE {i+1}\n{page.extract_text()}' for i, page in enumerate(reader.pages))
        (folder / f'{sid}.txt').write_text(text, encoding='utf-8')
        result.update(status='retrieved', sha256=sha256(body).hexdigest(), bytes=len(body), pages=len(reader.pages), path=path.as_posix())
    except Exception as exc:
        result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    return result

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(fetch, SOURCES.items()))
    report = {'pypdf_version': pypdf.__version__, 'sources': results}
    Path('work/sources/retrieval.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
