@echo OFF
cd /d %~dp0
SET /p inpath="输入 wiki 语料库文件完整路径："
SET /p outpath="输入输出文件夹路径："
SET /p minlenth="输入最小文本长度："
python WikiExtractor.py --min_text_length %minlenth% -o "%outpath%" -b 20G "%inpath%"
ECHO.
ECHO job done！
PAUSE 