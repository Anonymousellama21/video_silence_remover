ffmpeg -hide_banner -i input.mp4 -vn -af "silencedetect=n=-30dB:d=0.5" -f null - |& awk '/silence_end/ {print $5-$8,$5}' | grep "[0-9] [0-9]" | tac
