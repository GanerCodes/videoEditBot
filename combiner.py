import ffmpeg  # Very nice and pretty
from ffprobe import FFProbe as ffprobe # eew ugle ):<

def combiner(videos, output = "video.mp4", SILENCE = "./SILENCE.mp3", print_info = True):
    maxRes = (0, 0)
    maxFPS = 0
    filteredVids = []
    for vid in videos:
        r = ffprobe(vid)
        if r.video:
            newVid = (vid, vm := r.video[0], r.audio)
            maxRes = (max(int(vm.width), maxRes[0]), max(int(vm.height), maxRes[1]))
            maxFPS = max(vm.framerate, maxFPS)
            filteredVids.append(newVid)
        else:
            if print_info: print(f"""File {vid} does not contain any video streams, skipping.""")
    assert len(filteredVids) > 0, "Error: Found no suitable videos."
    
    preparedVids = []
    for filename, vidProps, audProps in filteredVids:
        f = ffmpeg.input(filename).video
        if (size := (vidProps.width, vidProps.height)) != maxRes:
            f = f.filter('scale', size = f"{maxRes[0]}x{maxRes[1]}", force_original_aspect_ratio = "decrease")
            f = f.filter('pad', maxRes[0], maxRes[1], "(ow-iw)/2", "(oh-ih)/2")
        f = f.filter("setsar", "1")
        preparedVids.append(f)
        if audProps:
            preparedVids.append(ffmpeg.input(filename).audio)
        else:
            preparedVids.append(ffmpeg.input(SILENCE).audio)
    
    final = ffmpeg.concat(*preparedVids, n = len(filteredVids), v = 1, a = 1).output(output).global_args("-y").global_args("-vsync", "2").global_args("-hide_banner").global_args("-loglevel", "error")
    final.run()
    if print_info: print(f"Finished! Exported video ({maxRes[0]}x{maxRes[1]}p{maxFPS})")

if __name__ == "__main__":
    from os import listdir
    from sys import argv
    combiner(argv[2:] if len(argv) > 2 else sorted(["videos/"+i for i in listdir("videos")]), argv[1] if len(argv) > 1 else "video.mp4")