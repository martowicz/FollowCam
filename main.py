import argparse
from flask import Flask, Response, render_template_string

from face_tracking import FaceTracker


HTML_PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Face Tracking</title>
    <style>
      :root {
        color-scheme: light;
      }

      body {
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f4f6f8;
        color: #1f2937;
      }

      .container {
        max-width: 920px;
        margin: 32px auto;
        padding: 0 16px;
      }

      h1 {
        margin-bottom: 8px;
      }

      p {
        margin-top: 0;
        margin-bottom: 16px;
      }

      .video-wrap {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        background: #000;
      }

      img {
        display: block;
        width: 100%;
        height: auto;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="video-wrap">
        <img src="/video_feed" alt="Live webcam stream" />
      </div>
    </div>
  </body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Face tracking web app using built-in webcam and OpenCV."
    )
    parser.add_argument(
        "--camera-backend",
        choices=["auto", "opencv", "picamera2"],
        default="auto",
        help="Camera backend: auto (default), opencv, or picamera2.",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Webcam index to use (default: 0 for built-in webcam).",
    )
    parser.add_argument(
        "--scale-factor",
        type=float,
        default=1.2,
        help="How much the image size is reduced at each image scale.",
    )
    parser.add_argument(
        "--min-neighbors",
        type=int,
        default=5,
        help="How many neighbors each candidate rectangle should have.",
    )
    parser.add_argument(
        "--frame-width",
        type=int,
        default=640,
        help="Requested camera frame width.",
    )
    parser.add_argument(
        "--frame-height",
        type=int,
        default=480,
        help="Requested camera frame height.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface for the web server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for the web server.",
    )
    return parser.parse_args()


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
        )

    return app


def main() -> None:
    args = parse_args()
    tracker = FaceTracker(
    camera_backend=args.camera_backend,
        camera_index=args.camera_index,
        scale_factor=args.scale_factor,
        min_neighbors=args.min_neighbors,
    frame_width=args.frame_width,
    frame_height=args.frame_height,
    )
    app = build_app(tracker)

    print(f"Open http://{args.host}:{args.port} in your browser")
    try:
        app.run(host=args.host, port=args.port, threaded=True)
    finally:
        tracker.release()


if __name__ == "__main__":
    main()
