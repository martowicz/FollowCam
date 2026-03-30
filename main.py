import argparse
import logging
import signal
import sys

from flask import Flask, Response, render_template_string
from face_tracking import FaceTracker

# Silence Flask request logs — they're noisy and waste I/O on Pi Zero W
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# HTML page — lightweight, no external dependencies, auto-reconnects on drop
# ---------------------------------------------------------------------------

HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Face Tracker</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: #0d0d0d;
      color: #e5e5e5;
      font-family: ui-monospace, "Cascadia Code", "Fira Mono", monospace;
      min-height: 100dvh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 16px;
      padding: 16px;
    }

    header {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: #22c55e;
      box-shadow: 0 0 6px #22c55e;
      animation: pulse 2s ease-in-out infinite;
    }
    .dot.offline { background: #ef4444; box-shadow: 0 0 6px #ef4444; animation: none; }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50%       { opacity: 0.4; }
    }

    h1 {
      font-size: 0.85rem;
      font-weight: 500;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #a3a3a3;
    }

    .video-wrap {
      position: relative;
      width: 100%;
      max-width: 640px;
      border-radius: 8px;
      overflow: hidden;
      background: #111;
      outline: 1px solid #2a2a2a;
    }

    .video-wrap img {
      display: block;
      width: 100%;
      height: auto;
    }

    .overlay {
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,0.7);
      font-size: 0.78rem;
      color: #ef4444;
      letter-spacing: 0.08em;
      opacity: 0;
      transition: opacity 0.3s;
      pointer-events: none;
    }
    .overlay.visible { opacity: 1; }

    footer {
      font-size: 0.7rem;
      color: #525252;
      letter-spacing: 0.06em;
    }
  </style>
</head>
<body>
  <header>
    <span class="dot" id="dot"></span>
    <h1>Face Tracker &mdash; live</h1>
  </header>

  <div class="video-wrap">
    <img id="stream" src="/video_feed" alt="Live stream"/>
    <div class="overlay" id="overlay">STREAM OFFLINE &mdash; RECONNECTING&hellip;</div>
  </div>

  <footer id="info">connecting&hellip;</footer>

  <script>
    const img     = document.getElementById('stream');
    const overlay = document.getElementById('overlay');
    const dot     = document.getElementById('dot');
    const info    = document.getElementById('info');

    function setOnline() {
      overlay.classList.remove('visible');
      dot.classList.remove('offline');
      info.textContent = 'stream active';
    }

    function setOffline() {
      overlay.classList.add('visible');
      dot.classList.add('offline');
      info.textContent = 'reconnecting...';
    }

    // Sprawdzaj co sekundę, czy obrazek "żyje"
    setInterval(() => {
      if (img.complete && img.naturalWidth > 0) {
        setOnline();
      } else {
        setOffline();
      }
    }, 1000);

    img.onerror = () => {
      setOffline();
      setTimeout(() => {
        img.src = '/video_feed?' + Date.now();
      }, 2000);
    };
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Face-tracking MJPEG stream — optimised for Raspberry Pi Zero W.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Camera
    parser.add_argument("--camera-index",   type=int,   default=0)
    parser.add_argument("--camera-backend", choices=["auto", "v4l2"], default="auto")
    parser.add_argument("--frame-width",    type=int,   default=320)
    parser.add_argument("--frame-height",   type=int,   default=240)
    parser.add_argument("--source-fps",     type=int,   default=10,
                        help="FPS cap pushed to the V4L2 driver.")

    # Detection
    parser.add_argument("--scale-factor",     type=float, default=1.2)
    parser.add_argument("--min-neighbors",    type=int,   default=4)
    parser.add_argument("--detection-scale",  type=float, default=0.5,
                        help="Fraction of frame size used for Haar analysis (0.25 → 80x60).")
    parser.add_argument("--frame-skip",       type=int,   default=5,
                        help="Run face detection every Nth frame.")

    # Encoding
    parser.add_argument("--jpeg-quality", type=int, default=35,
                        help="JPEG quality 1-95. Lower = smaller payload, less CPU.")

    # Server
    parser.add_argument("--host", default="192.168.0.43",
                        help="Bind address")
    parser.add_argument("--port", type=int, default=5000)

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Flask app factory
# ---------------------------------------------------------------------------

def build_app(tracker: FaceTracker) -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template_string(HTML_PAGE)

    @app.get("/video_feed")
    def video_feed() -> Response:
        return Response(
            tracker.frames(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
            # Prevent proxies / browsers from buffering the stream
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/healthz")
    def healthz() -> Response:
        """Lightweight health-check endpoint — useful for monitoring."""
        return Response("ok", mimetype="text/plain")

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    tracker = FaceTracker(
        camera_index=args.camera_index,
        camera_backend=args.camera_backend,
        frame_width=args.frame_width,
        frame_height=args.frame_height,
        source_fps=args.source_fps,
        scale_factor=args.scale_factor,
        min_neighbors=args.min_neighbors,
        detection_scale=args.detection_scale,
        frame_skip=args.frame_skip,
        jpeg_quality=args.jpeg_quality,
    )

    app = build_app(tracker)

    # Graceful shutdown on SIGTERM (e.g. systemd stop) in addition to Ctrl-C
    def _shutdown(signum, frame):
        print("\n[main] signal received — shutting down…")
        tracker.release()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)

    print("--- FollowCam Server ---")
    print(f"  URL       : http://{args.host}:{args.port}")
    print(f"  Resolution: {args.frame_width}x{args.frame_height} @ {args.source_fps} fps")
    print(f"  Detection : every {args.frame_skip} frames "
          f"on {int(args.frame_width * args.detection_scale)}x"
          f"{int(args.frame_height * args.detection_scale)} px thumbnail")
    print(f"  JPEG      : quality {args.jpeg_quality}")

    try:
        # use_reloader=False is critical — the reloader forks a second process
        # on Pi Zero W that doubles memory and CPU usage for no benefit.
        app.run(
            host=args.host,
            port=args.port,
            threaded=True,
            use_reloader=False,
            debug=False,
        )
    except KeyboardInterrupt:
        print("\n[main] keyboard interrupt — shutting down…")
    finally:
        tracker.release()


if __name__ == "__main__":
    main()