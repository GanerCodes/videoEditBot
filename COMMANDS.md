Commands
===========

These are commands that the bot supports.

A command is declared as `filtername=value`. For example, to add 100 bass boost, use `bass=100`.

To chain multiple commands, use a comma `,` to separate them. For example, bass boost + hypercam would be `bass=100, hypercam`.

You can also use pipes `|` to separate groups of commands to be processed. For example, `ytp=100|hcycle=3`.

To use the bot on Discord, prefix your command with "destroy". An empty command or "random" selects random parameters.

| Command         | Shorthand   | Type   | Min  | Max          | Description                                                                                         |
|-----------------|-------------|--------|------|--------------|-----------------------------------------------------------------------------------------------------|
| `abr`           | `abr`       | Number | 0    | 100          | Audio Bit Reduction - Reduces audio quality                                                         |
| `vbr`           | `vbr`       | Number | 0    | 100          | Video bit reduction, worsens quality of video                                                       |
| `bandicam`      | `bndc`      | -      | -    | -            | Adds a Bandicam watermark                                                                           |
| `bass`          | `bs`        | Number | 0    | 100          | Bass boost                                                                                          |
| `bottomcaption` | `bc`        | Text   | 0    | 100          | Bottom caption, in motivational text style                                                          |
| `bottomtext`    | `bt`        | Text   | 0    | 100          | Bottom text in impact font                                                                          |
| `cap`           | `cap`       | Text   | 0    | 100          | Bold, centered, white caption at top                                                                |
| `crush`         | `cr`        | Number | 1    | 100          | Obliterates audio                                                                                   |
| `datamosh`      | `dm`        | Number | 0    | 100          | Corrupts video by removing non-delta frames                                                         |
| `deepfry`       | `df`        | Number | 0    | 100          | Deep fries the video, reduces quality (with added saturation and contrast)                          |
| `delfirst`      | `delf`      | -      | -    | -            | When selection is enabled, deletes parts of video before `start`                                    |
| `dellast`       | `dell`      | -      | -    | -            | When selection is enabled, deletes parts of video after `end`                                       |
| `earrape`       | `er`        | Number | 0    | 100          | Earrapes the video, by making the video very loud and distorted.                                    |
| `end`           | `e`         | Number | 0    | End of video | Time when video ends, in seconds. (Or end of effect with `selection`)                               |
| `fisheye`       | `fe`        | Number | 1    | 2            | Adds a fisheye effect on the video                                                                  |
| `hcycle`        | `huec`      | Number | 0    | 100          | Rotates the hue of the video by a certain speed                                                     |
| `hmirror`       | `hm`        | Number | 1    | 2            | Horizontal mirror, 1 is the left half, 2 is the right half                                          |
| `holdframe`     | `hf`        | Number | 0.1  | 12           | Makes the video only the first frame, for # of seconds                                              |
| `hscale`        | `hs`        | Number | 0    | 100          | Horizontal scale, sets the vertical resolution                                                      |
| `hue`           | `hue`       | Number | 0    | 100          | Changes the hue of the video                                                                        |
| `hypercam`      | `hypc`      | -      | -    | -            | Adds an "Unregistered Hypercam 2" watermark to the video                                            |
| `invert`        | `inv`       | -      | -    | -            | Inverts video color                                                                                 |
| `lag`           | `lag`       | Number | 1    | 100          | Reverses frames in chunks.                                                                          |
| `rlag`          | `rlag`      | Number | 1    | 100          | Shuffles frames in chunks.                                                                          |
| `music`         | `mus`       | Text   | -    | -            | Music is added using a YouTube video ID (the text after ?watch=). The song must be under 5 minutes. |
| `musicdelay`    | `musd`      | Number | 0    | End of video | Number of seconds corresponding to when the added music starts                                      |
| `musicskip`     | `muss`      | Number | 0    | End of music | Starts the song at a given time of the song (in seconds)                                            |
| `mute`          | `mt`        | -      | -    | -            | Mutes the audio                                                                                     |
| `normalcaption` | `nc`        | Text   | -    | -            | Standard caption at the top, like in screenshotted twitter posts.                                   |
| `pitch`         | `pch`       | Number | -100 | 100          | Sets the audio pitch to be higher or lower                                                          |
| `framerate`     | `fps`       | Number | 1    | 30           | Lowers the video's framerate                                                                        |
| `playreverse`   | `prev`      | Number | 1    | 2            | 1 = plays, then reverses. 2 = reverses, then plays the video                                        |
| `reverb`        | `rvb`       | Number | 0    | 100          | Adds a reverb, or echo, effect                                                                      |
| `reverbdelay`   | `rvd`       | Number | 0    | 100          | Echo response time, 100 means it takes the longest for an echo to bounce back                       |
| `reverse`       | `rev`       | -      | -    | -            | Reverses the video and audio                                                                        |
| `ricecake`      | `rc`        | Number | 1    | 100          | Clones delta frames (corrupting video) and clones audio                                             |
| `selection`     | `se`        | -      | -    | -            | Makes `start` and `end` correspond to when the effects are applied                                  |
| `sfx`           | `sfx`       | Number | 1    | 100          | Adds random sound effects                                                                           |
| `shake`         | `shk`       | Number | 1    | 100          | Shakes the video around                                                                             |
| `sharpen`       | `shp`       | Number | -100 | 100          | Applies a heavy sharpening filter. Negative numbers cause it to become more pixelly.                |
| `shuffle`       | `sh`        | -      | -    | -            | Shuffles the whole video                                                                            |
| `speed`         | `sp`        | Number | 0.5  | 25           | Slows down or speeds up video                                                                       |
| `start`         | `s`         | Number | 0    | End of Video | Time when video begins, in seconds. (Or start of effect with `selection`)                           |
| `stutter`       | `st`        | Number | 0    | 100          | Adds random stutters to the video                                                                   |
| `timecode`      | `timc`      | Number | 1    | 4            | Messes with the video's timecode metadata. Only applies to Discord bot.                             |
| `topcaption`    | `tc`        | Text   | -    | -            | Top caption, in motivational text style                                                             |
| `toptext`       | `tt`        | Text   | -    | -            | Top text in impact font                                                                             |
| `vmirror`       | `vm`        | Number | 1    | 2            | Mirrors vertically, `1` = mirrors top half of video, `2` = mirrors bottom half of video             |
| `volume`        | `vol`       | Number | 0    | 2000         | Multiplies volume. Higher number results in louder video.                                           |
| `watermark`     | `wtm`       | Number | 0    | 100          | Adds random watermarks to a video. Higher numbers add more.                                         |
| `wobble`        | `wub`       | Number | 1    | 100          | Makes the audio wobbly.                                                                             |
| `wscale`        | `ws`        | Number | -500 | 500          | Sets the horizontal resolution.                                                                     |
| `ytp`           | `ytp`       | Number | 0    | 100          | Adds random plays and reverses to a video.                                                          |
| `zoom`          | `zm`        | Number | -15  | 15           | Zooms towards the middle of the video. Negative values do the same, but more pixellated.
