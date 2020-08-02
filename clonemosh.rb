require 'aviglitch'

name = ARGV[0]
times = ARGV[1].to_i
datamosh = false
if ARGV.size > 2
	datamosh = true
end

system("ffmpeg -hide_banner -loglevel fatal -i #{name}.mp4 #{name}.avi")
File.delete("#{name}.mp4")

a = AviGlitch.open "#{name}.avi"
frameCount = a.frames.size
am = 0
minIndex = 5

if times > 0
	i = 0
	while true do
		i += 1
		if i > 400 or minIndex > a.frames.size - 1 or frameCount > a.frames.size
			break
		end
		index = [rand(minIndex..(minIndex + 1.2 * frameCount / times)), frameCount].min()
		newFrame = a.frames[index]
		if newFrame == nil
			break
		end
		if newFrame.is_audioframe?
			PFrames = a.frames.map{|x| x.is_pframe?}
			PFrames.each_with_index do |f, i|
				if f == true
					PFrames[i] = i
				end
			end
			PFrames.delete(false)

			nearestPFrameIndex = PFrames.min_by{|x| (index - x).abs}
			nearestPFrame = a.frames[nearestPFrameIndex]

			#p index, nearestPFrameIndex

			amount = rand(30..60)

			duplicatedAudioFrames = [newFrame] * amount
			duplicatedVideoFrames = [nearestPFrame] * (amount / 1.32)
			collectiveNewFrames = duplicatedAudioFrames + duplicatedVideoFrames
			a.frames.insert(index, *collectiveNewFrames)
			minIndex = index + collectiveNewFrames.size + 1
			frameCount += collectiveNewFrames.size - 1
			am += 1
			#if am > times
			#	break
			#end
		end
	end
end

if datamosh
	n = 0
	a.glitch :keyframe do |f|
		n += 1
		if n > 1
			nil
		else
			f
		end
	end
end

a.output("#{name}.avi")
system("ffmpeg -hide_banner -loglevel fatal -i #{name}.avi #{name}.mp4")
File.delete("#{name}.avi")