import argparse
p=argparse.ArgumentParser(); p.add_argument("--model"); p.add_argument("--prompt"); a=p.parse_args(); raise SystemExit(0 if a.prompt else 1)
