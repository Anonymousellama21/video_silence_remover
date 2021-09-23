# video_silence_remover
remove silent parts of a video

python splitsilence.py <input_file_path> <output_file_path> <silence_threshold_db (default -30)> <min_silence_length_seconds (default 0.5)>

working when I checked last
gpu acceleration may not work if you dont have similar hardware

TODO:
add deletion of temporary files
normalize audio before getting timestamps
fix command too long
