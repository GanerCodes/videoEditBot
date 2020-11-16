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
| `watermark`     | `wtm`       | Number | 0    | 100          | Adds random watermarks to a video. Higher numbers add more.                                         |
| `bandicam`      | `bndc`      | -      | -    | -            | Adds a Bandicam watermark                                                                           |
| `hypercam`      | `hypc`      | -      | -    | -            | Adds an "Unregistered Hypercam 2" watermark to the video                                            |
| `topcaption`    | `tc`        | Text   | -    | -            | Top caption, in motivational text style                                                             |
| `bottomcaption` | `bc`        | Text   | 0    | 100          | Bottom caption, in motivational text style                                                          |
| `toptext`       | `tt`        | Text   | -    | -            | Top text in impact font                                                                             |
| `bottomtext`    | `bt`        | Text   | 0    | 100          | Bottom text in impact font                                                                          |
| `normalcaption` | `nc`        | Text   | -    | -            | Standard caption at the top, like in screenshotted twitter posts.                                   |
| `topcap`        | `cap`       | Text   | 0    | 100          | Bold, centered, white caption at top                                                                |
| `bottomcap`     | `bcap`      | Text   | 0    | 100          | Bold, centered, white caption at bottom                                                             |
| `holdframe`     | `hf`        | Number | 0.1  | 12           | Makes the video only the first frame, for # of seconds                                              |
| `speed`         | `sp`        | Number | 0.5  | 25           | Slows down or speeds up video                                                                       |
| `deepfry`       | `df`        | Number | 0    | 100          | Deep fries the video, reduces quality (via added saturation)                                        |
| `contrast`      | `ct`        | Number | 0    | 100          | Adds extra contrast to the video                                                                    |
| `sharpen`       | `shp`       | Number | -100 | 100          | Applies a heavy sharpening filter. Negative numbers cause it to become more pixelly.                |
| `hue`           | `hue`       | Number | 0    | 100          | Changes the hue of the video                                                                        |
| `hcycle`        | `huec`      | Number | 0    | 100          | Rotates the hue of the video by a certain speed                                                     |
| `vreverse`      | `vrev`      | -      | -    | -            | Reverses video                                                                                      |
| `areverse`      | `arev`      | -      | -    | -            | Reverses audio                                                                                      |
| `reverse`       | `rev`       | -      | -    | -            | Reverses the video and audio                                                                        |
| `playreverse`   | `prev`      | Number | 1    | 2            | 1 = plays, then reverses. 2 = reverses, then plays the video                                        |
| `hmirror`       | `hm`        | Number | 1    | 2            | Mirrors horizontal, 1 is the left half, 2 is the right half                                         |
| `vmirror`       | `vm`        | Number | 1    | 2            | Mirrors vertically, 1 is the top half, 2 is the bottom half                                         |
| `invert`        | `inv`       | -      | -    | -            | Inverts video color                                                                                 |
| `wscale`        | `ws`        | Number | -500 | 500          | Sets the horizontal resolution.                                                                     |
| `hscale`        | `hs`        | Number | 0    | 100          | Horizontal scale, sets the vertical resolution                                                      |
| `hcrop`         | `hcp`       | Number | 1    | 95           | How much to horizontally crop the video, in terms of precent.                                       |
| `vcrop`         | `vcp`       | Number | 1    | 95           | How much to vertically crop the video, in terms of precent.                                         |
| `hflip`         | `hflp`      | Number | -    | -            | Flips video horizontally.                                                                           |
| `vflip`         | `vflp`      | Number | -    | -            | Flips video vertically.                                                                             |
| `zoom`          | `zm`        | Number | -15  | 15           | Zooms towards the middle of the video. Negative values do the same, but more pixellated.            |
| `shake`         | `shk`       | Number | 1    | 100          | Shakes the video around                                                                             |
| `lag`           | `lag`       | Number | 1    | 100          | Reverses frames in chunks.                                                                          |
| `rlag`          | `rlag`      | Number | 1    | 100          | Shuffles frames in chunks.                                                                          |
| `framerate`     | `fps`       | Number | 1    | 30           | Lowers the video's framerate                                                                        |
| `acid`          | `acid`      | Number | 1    | 100          | Makes it look like your on acid                                                                     |
| `fisheye`       | `fe`        | Number | 1    | 2            | Adds a fisheye effect on the video                                                                  |
| `wave`          | `wav`       | Number | 1    | 100          | Adds a wave to the video; higher values means the wave scrolls faster.                              |
| `waveamount`    | `wava`      | Number | 1    | 100          | Controls amount of waves.                                                                           |
| `wavestrength`  | `wavs`      | Number | 1    | 100          | Controls how big waves are                                                                          |
| `selection`     | `se`        | -      | -    | -            | Makes `start` and `end` correspond to when the effects are applied                                  |
| `start`         | `s`         | Number | 0    | End of Video | Time when video begins, in seconds. (Or start of effect with `selection`)                           |
| `end`           | `e`         | Number | 0    | End of video | Time when video ends, in seconds. (Or end of effect with `selection`)                               |
| `delfirst`      | `delf`      | -      | -    | -            | When selection is enabled, deletes parts of video before `start`                                    |
| `dellast`       | `dell`      | -      | -    | -            | When selection is enabled, deletes parts of video after `end`                                       |
| `volume`        | `vol`       | Number | 0    | 2000         | Multiplies volume. Higher number results in louder video.                                           |
| `mute`          | `mt`        | -      | -    | -            | Mutes the audio                                                                                     |
| `wobble`        | `wub`       | Number | 1    | 100          | Makes the audio wobbly.                                                                             |
| `bass`          | `bs`        | Number | 0    | 100          | Bass boost                                                                                          |
| `pitch`         | `pch`       | Number | -100 | 100          | Sets the audio pitch to be higher or lower                                                          |
| `reverb`        | `rvb`       | Number | 0    | 100          | Adds a reverb, or echo, effect                                                                      |
| `reverbdelay`   | `rvd`       | Number | 0    | 100          | Echo response time, 100 means it takes the longest for an echo to bounce back                       |
| `crush`         | `cr`        | Number | 1    | 100          | Obliterates audio                                                                                   |
| `earrape`       | `er`        | Number | 0    | 100          | Earrapes the video, by making the video very loud and distorted.                                    |
| `music`         | `mus`       | Text   | -    | -            | Music is added using a YouTube video ID (the text after ?watch=). The song must be under 5 minutes. |
| `musicdelay`    | `musd`      | Number | 0    | End of video | Number of seconds corresponding to when the added music starts                                      |
| `musicskip`     | `muss`      | Number | 0    | End of music | Starts the song at a given time of the song (in seconds)                                            |
| `sfx`           | `sfx`       | Number | 1    | 100          | Adds random sound effects                                                                           |
| `datamosh`      | `dm`        | Number | 0    | 100          | Corrupts video by removing non-delta frames                                                         |
| `ytp`           | `ytp`       | Number | 0    | 100          | Adds random plays and reverses to a video.                                                          |
| `shuffle`       | `sh`        | -      | -    | -            | Shuffles the whole video                                                                            |
| `stutter`       | `st`        | Number | 0    | 100          | Adds random stutters to the video                                                                   |
| `ricecake`      | `rc`        | Number | 1    | 100          | Clones delta frames (corrupting video) and clones audio                                             |
| `glitch`        | `glch`      | Number | 1    | 100          | Makes the video corrupted                                                                           |
| `repeatuntil`   | `repu`      | Number | 1    | 45           | Repeats video until this time is reached                                                            |
| `timecode`      | `timc`      | Number | 1    | 4            | Messes with the video's timecode metadata. Only applies to Discord bot.                             |
