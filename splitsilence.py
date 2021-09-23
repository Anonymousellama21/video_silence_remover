#usage:
#python splitsilence.py <input_file_path> <output_file_path> <silence_threshold_db (default -30)> <min_silence_length_seconds (default 0.5)>

import time
import os
import sys
import subprocess
import shlex
import re

input_file = sys.argv[1]

if len(sys.argv) < 4:
    threshold = -30
else:
    threshold = sys.argv[3]

if len(sys.argv) < 5:
    min_duration = 0.5
else:
    min_duration = sys.argv[4]

def find_prefixed_floats(prefix, string):
    matches = re.finditer("(?<=" + prefix + ")\d+(?:\.\d+)?", string)
    return list(map(lambda m: float(m[0]), matches))

def iter_issorted(iter, check):
    old = next(iter)
    elem = next(iter)
    try:
        while True:
            if not check(old, elem): return False
            old, elem = elem, next(iter)
    except StopIteration:
        return True

def validate(startarr, endarr):
    assert len(startarr) == len(endarr), "dimension mismatch"
    
    assert iter_issorted(iter(startarr), lambda a, b: float(a) < float(b)), "out of order start time"
    assert iter_issorted(iter(endarr), lambda a, b: float(a) < float(b)), "out of order end time"

    assert all(map(lambda s: float(s[0]) < float(s[1]), zip(startarr, endarr))), "negative duration"
    assert all(map(lambda s: float(s[0]) > float(s[1]), zip(startarr[1:], endarr[:-1]))), "concurent silence"

#get timestamps for silent parts of input video
timestamps = subprocess.check_output("ffmpeg -hide_banner -i " + input_file + " -vn -af \"silencedetect=n=" + str(threshold) + "dB:d=" + str(min_duration) + "\" -f null - 2>&1",# \
                                     #awk \'/silence_end/ {print $5-$8,$8}\' | sed -e \"s/ /\\n/g\"",
                                     shell=True)
#loudnorm=I=-5:LRA=11:TP=-1.5,
timestamps = timestamps.decode()

silence_starts = find_prefixed_floats("silence_start: ", timestamps)
silence_ends = find_prefixed_floats("silence_end: ", timestamps)

print(silence_starts, silence_ends)

command = "ffmpeg -hwaccel cuda -hwaccel_output_format cuda -c:v h264_cuvid -i {} -c:v h264_nvenc -filter_complex ".format(input_file)

command += "[0:v]trim=end={0},setpts=PTS-STARTPTS[0v];[0:a]atrim=end={0},asetpts=PTS-STARTPTS[0a];".format(silence_starts[0])
concat = "[0v][0a]"
for i in range(len(silence_starts)-1):
    command += "[0:v]trim=start={0}:end={1},setpts=PTS-STARTPTS[{2}v];[0:a]atrim=start={0}:end={1},asetpts=PTS-STARTPTS[{2}a];".format(silence_ends[i], silence_starts[i+1], i+1)
    concat += "[{0}v][{0}a]".format(i+1)
command += "{}concat=n={}:v=1:a=1[outv][outa] -map [outv] -map [outa] {}".format(concat, len(silence_starts), sys.argv[2])

print(command)

subprocess.call(shlex.split(command))

