curl -LO https://github.com/GyanD/codexffmpeg/releases/download/8.0/ffmpeg-8.0-full_build-shared.zip
tar -xzf ffmpeg-8.0-full_build-shared.zip 
move ffmpeg-8.0-full_build-shared ffmpeg
copy ffmpeg\bin\*.dll wabash
del ffmpeg-8.0-full_build-shared.zip
