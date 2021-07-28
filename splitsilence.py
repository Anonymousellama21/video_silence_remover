#usage:
#python splitsilence.py <input_file_path> <output_file_path> <silence_threshold_db (default -30)> <min_silence_length_seconds (default 0.5)>

import time
import os
import sys
import subprocess

input_file = sys.argv[1]

if len(sys.argv) < 4:
    threshold = -30
else:
    threshold = sys.argv[3]

if len(sys.argv) < 5:
    min_duration = 0.5
else:
    min_duration = sys.argv[4]

#get timestamps for silent parts of input video
timestamps = subprocess.check_output("ffmpeg -i " + input_file + " -vn -af \"silencedetect=n=" + threshold + "dB:d=" + min_duration + "\" -f null - 2>&1 | \
                                     awk \'/silence_end/ {print $5-$8,$8}\' | grep \"^[^-][0-9]\" | sed -e \"s/ /\\n/g\"",
                                     shell=True)
#loudnorm=I=-5:LRA=11:TP=-1.5,

timestamps = timestamps.decode().split('\n')[:-1]
print(timestamps)

splits_path = os.path.splitext(input_file)[0]+"_splits"
os.mkdir(splits_path)

#split video around silence
os.system("ffmpeg -hide_banner -i " + input_file + " -to " + timestamps[0] + " -c copy " + splits_path + "/000000" + os.path.splitext(input_file)[1])

for i in range(1, len(timestamps)-2, 2):
    os.system("ffmpeg -hide_banner -ss " + str(float(timestamps[i-1])+float(timestamps[i])) + " -i " + input_file + " -to " + timestamps[i] + " -c copy " + splits_path + "/" + str(int((i+1)/2)).zfill(6) + os.path.splitext(input_file)[1])

os.system("ffmpeg -hide_banner -ss " + str(float(timestamps[-2])+float(timestamps[-1])) + " -i " + input_file + " -c copy " + splits_path + "/" + str(int(len(timestamps)/2)+1).zfill(6) + os.path.splitext(input_file)[1])

#concat all splits
with open("tmp.txt", 'a+') as f:
    for i in os.listdir(splits_path):
        if os.path.splitext(i)[1] == os.path.splitext(input_file)[1]:
            f.write("file " + splits_path + "/" + i + "\n")
            
time.sleep(1)#idk if this is necessary but it maybe helps

os.system("ffmpeg -f concat -i tmp.txt -c copy " + sys.argv[2])
