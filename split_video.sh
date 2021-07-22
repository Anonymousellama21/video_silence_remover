ffmpeg -hide_banner -i input.mp4 -vn -af "silencedetect=n=-30dB:d=0.5" -f null - 2>&1 | grep "silence_end" 2>&1 | awk '{print $8-$5,$8}'
