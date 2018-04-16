for i in old/*.mkv
do

num=$(mkvmerge -i "$i" | grep h.264 | awk -F'[ :]' '{print $6}')

mkvextract tracks "$i" $num:video.h264

cat sei.h264 video.h264 > fix.h264

rm video.h264

mkvmerge -D "$i" fix.h264 -o fix/"$i"

rm fix.h264

done
