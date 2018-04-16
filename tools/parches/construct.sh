if [[ -f "do.bat" ]]; then
rm do.bat
fi

if [[ -f "li.sh" ]]; then
rm li.sh
fi

echo '@echo off' >> do.bat
echo 'REM Script based in AnimeTeam script' >> do.bat
echo >> do.bat

echo '#!/usr/bin/env bash' >> li.sh
echo '#Script based in AnimeTeam script' >> li.sh
echo >> li.sh

for i in {01..12}
do
fi=$(dir *$i*"("*)

sed 's/$i/Gate Jieitai Kanochi nite, Kaku Tatakaeri - '$i' (BDrip 1920x1080 x264 Hi444p).mkv/g' dos.bat | sed 's/$p/'$i'.xdelta/g' | sed 's/$d/'"$fi"'/g' >> do.bat


sed 's/$i/Gate Jieitai Kanochi nite, Kaku Tatakaeri - '$i' (BDrip 1920x1080 x264 Hi444p).mkv/g' linux.sh | sed 's/$p/'$i'.xdelta/g' | sed 's/$d/'"$fi"'/g' >> li.sh

done

echo >> do.bat
echo 'echo "Finalizado"' >> do.bat
echo 'pause' >> do.bat

echo >> li.sh
echo 'echo "Finalizado"' >> li.sh
echo 'exit 0' >> li.sh
