#!/bin/bash
PORT=8080
echo "=========================================================="
echo "⚡ Android Senior Interview Preparation Portal"
echo "Serving on: http://localhost:$PORT/index.html"
echo "Master Book: http://localhost:$PORT/all_topics_combined.html"
echo "=========================================================="
python3 -m http.server $PORT --bind 127.0.0.1
