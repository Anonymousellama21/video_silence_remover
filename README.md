# video_silence_remover
remove silent parts of a video

python splitsilence.py <input_file_path> <output_file_path> <silence_threshold_db (default -30)> <min_silence_length_seconds (default 0.5)>

working when I checked last

TODO:
add deletion of temporary files
normalize audio before getting timestamps
align video to keyframes to prevent stutter
