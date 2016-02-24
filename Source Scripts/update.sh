cd ~/Github/Random/Source\ Scripts
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/autoexec.cfg tf/autoexec.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/classreset.cfg tf/classreset.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/scout.cfg tf/scout.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/soldier.cfg tf/soldier.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/pyro.cfg tf/pyro.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/demoman.cfg tf/demoman.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/heavyweapons.cfg tf/heavyweapons.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/engineer.cfg tf/engineer.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/medic.cfg tf/medic.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/sniper.cfg tf/sniper.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Team\ Fortress\ 2/tf/cfg/spy.cfg tf/spy.cfg

cp ~/Library/Application\ Support/Steam/steamapps/common/Counter-Strike\ Global\ Offensive/csgo/cfg/autoexec.cfg csgo/autoexec.cfg
cp ~/Library/Application\ Support/Steam/steamapps/common/Left\ 4\ Dead\ 2/left4dead2/cfg/autoexec.cfg l4d2/autoexec.cfg

git add ./*
git commit -m "Auto-updating scripts on $(date)"
git push
