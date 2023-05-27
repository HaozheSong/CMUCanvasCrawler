import os

folder_path = ""
os.chdir(folder_path)
files = os.listdir()
recordings = []
for f in files:
    [name, extension] = f.split(".")
    if extension != "mp4":
        continue
    else:
        # [index, video_type, date, time, class_type] = name.split("_")
        [index, video_type, date, time] = name.split("_")
        recordings.append({
            "index": int(index),
            "video_type": video_type,
            "date": date,
            "time": time,
            # "class_type": class_type,
            "original_name": f
        })
        os.rename(f, f + ".temp")

recordings.sort(key=lambda r: r["index"])
max_index = recordings[-1]["index"]
for r in recordings:
    new_index = max_index + 1 - r["index"]
    # new_name = f"{new_index}_{r['video_type']}_{r['date']}_{r['time']}_{r['class_type']}.mp4"
    new_name = f"{new_index}_{r['video_type']}_{r['date']}_{r['time']}.mp4"
    print(new_name)
    os.rename(r["original_name"] + ".temp", new_name)
