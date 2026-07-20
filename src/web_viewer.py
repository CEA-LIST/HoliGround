from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, List
from urllib.parse import unquote


def load_annotations(path: Path, limit: int | None = None) -> List[dict[str, Any]]:
    records: List[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as handle:
        for line in handle:
            if not line.strip():
                continue
            records.append(json.loads(line))
            if limit and len(records) >= limit:
                break
    return records


def build_html(payload: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Annotation Viewer</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 1.5rem;
      background: #f6f6f6;
      color: #222;
    }}
    #container {{
      max-width: 960px;
      margin: 0 auto;
      background: #fff;
      padding: 1.5rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.08);
      border-radius: 8px;
    }}
    img {{
      max-width: 100%;
      border-radius: 6px;
      margin-bottom: 1rem;
    }}
    .controls {{
      display: flex;
      justify-content: space-between;
      margin: 1rem 0;
    }}
    button {{
      padding: 0.6rem 1.2rem;
      border: none;
      border-radius: 4px;
      background: #0057d9;
      color: #fff;
      cursor: pointer;
      font-size: 1rem;
    }}
    button:disabled {{
      background: #9cb6e3;
      cursor: not-allowed;
    }}
    h2 {{
      margin-top: 0;
    }}
    .steps {{
      margin-top: 1rem;
    }}
    .step {{
      padding: 0.6rem 0;
      border-bottom: 1px solid #eee;
    }}
    .step:last-child {{
      border-bottom: none;
    }}
    code {{
      background: #eef2ff;
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
  <div id="container">
    <div class="controls">
      <button id="prev">Previous</button>
      <div id="status"></div>
      <button id="next">Next</button>
    </div>
    <h2 id="question"></h2>
    
    <p><strong>Semantic:</strong> <span id="semantic_str"></span></p>
    <p><strong>Metrics:</strong> <span id="metrics"></span></p>
    <p><strong>Image ID:</strong> <span id="image-id"></span></p>
    <img id="sample-image" alt="Sample image"/>
    <div class="steps">
      <h3>Reasoning Steps</h3>
      <div id="steps"></div>
    </div>
    <p><strong>Answer:</strong> <span id="answer"></span></p>
    <p><strong>Full Answer:</strong> <span id="full_answer"></span></p>
  </div>
  <script>
    const DATA = {payload};
    let index = 0;

    function updateButtons() {{
      document.getElementById('prev').disabled = (index === 0);
      document.getElementById('next').disabled = (index === DATA.length - 1);
      document.getElementById('status').textContent = `Sample ${{index + 1}} / ${{DATA.length}}`;
    }}

    function render() {{
      const sample = DATA[index] || {{}};
      document.getElementById('question').textContent = sample.question || '[missing question]';
      document.getElementById('answer').textContent = sample.answer || '[missing answer]';
      document.getElementById('full_answer').textContent = sample.full_answer || '[missing full answer]';
      document.getElementById('semantic_str').textContent = sample.semantic_str || '[missing semanticStr]';
      document.getElementById('metrics').textContent = JSON.stringify(sample.metrics) || '[missing metrics]';


      document.getElementById('image-id').textContent = sample.image_id || 'N/A';
      const img = document.getElementById('sample-image');
      if (sample.image_id) {{
        img.src = `/image/${{encodeURIComponent(sample.image_id)}}`;
        img.style.display = 'block';
      }} else {{
        img.style.display = 'none';
      }}
      const stepsContainer = document.getElementById('steps');
      stepsContainer.innerHTML = '';
      (sample.reasoning_steps || []).forEach((step, idx) => {{
        const div = document.createElement('div');
        div.className = 'step';
        const op = step.operation || 'step';
        const rationale = step.rationale || '';
        const argument = step.argument || '';
        const vc = step.atomic_vc || '';
        div.innerHTML = `<strong>Step ${'{'}idx + 1{'}'} - ${'{'}op{'}'}: ${'{'}argument{'}'} | ${'{'}vc{'}'}</strong><div>${'{'}rationale{'}'}</div>`;
        stepsContainer.appendChild(div);
      }});
      const fullAnswerContainer = document.getElementById('full-answer');
      updateButtons();
    }}

    document.getElementById('prev').addEventListener('click', () => {{
      if (index > 0) {{
        index -= 1;
        render();
      }}
    }});
    document.getElementById('next').addEventListener('click', () => {{
      if (index < DATA.length - 1) {{
        index += 1;
        render();
      }}
    }});

    if (DATA.length === 0) {{
      document.getElementById('container').innerHTML = '<p>No annotations available.</p>';
    }} else {{
      render();
    }}
  </script>
</body>
</html>"""


class AnnotationHandler(BaseHTTPRequestHandler):
    annotations: List[dict[str, Any]] = []
    image_pattern: str | None = None

    def do_GET(self):
        if self.path == '/' or self.path.startswith('/?'):
            content = build_html(json.dumps(self.annotations))
            self._send_response(200, content.encode('utf-8'), 'text/html; charset=utf-8')
        elif self.path.startswith('/image/'):
            image_id = unquote(self.path[len('/image/'):])
            self._serve_image(image_id)
        else:
            self.send_error(404, "Not Found")

    def _serve_image(self, image_id: str) -> None:
        if not self.image_pattern:
            self.send_error(404, "Image serving disabled")
            return
        image_path = Path(self.image_pattern.format(image_id=image_id))
        if not image_path.exists():
            self.send_error(404, f"Image {image_id} not found")
            return
        mime_type, _ = mimetypes.guess_type(str(image_path))
        with image_path.open('rb') as handle:
            data = handle.read()
        self._send_response(200, data, mime_type or 'application/octet-stream')

    def _send_response(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal web viewer for annotations.")
    parser.add_argument(
        "--annotations",
        default="output/annotations.jsonl",
        help="Path to the annotations JSONL file.",
    )
    parser.add_argument(
        "--image-pattern",
        default="data/gqa/images/{image_id}.jpg",
        help="Pattern for locating images (must include {image_id}).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit for number of samples to load.",
    )
    args = parser.parse_args()

    annotations_path = Path(args.annotations)
    if not annotations_path.exists():
        raise FileNotFoundError(f"Annotations file not found: {annotations_path}")

    records = load_annotations(annotations_path, limit=args.limit)
    AnnotationHandler.annotations = records
    AnnotationHandler.image_pattern = args.image_pattern

    server = ThreadingHTTPServer((args.host, args.port), AnnotationHandler)
    print(f"Serving {len(records)} samples at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

