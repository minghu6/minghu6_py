@echo off
  
  :: TODO:��װminghu6 Pacage
 

  color 03
  set input=
  set /p "input=������minghu6 Pacage���ڵ�Ŀ��λ�ã���س�Ĭ��·��Ϊ�����ڵĵ�ǰ·����:"
  if defined input (xcopy /E /I ..\minghu6 %input%\minghu6) else ( set input="." )

 python auto_install.py %input%

 ::�ж�python�汾�Ƿ���ȷ,0 -successful 1-failed
 if %ERRORLEVEL% == 1 (pause && echo Now try to run python3) else (echo minghu6 Pacage��װ·��Ϊ%input% && echo Install successful! && exit)

 python3 auto_install.py %input%
 if %ERRORLEVEL% == 0 (echo minghu6 Pacage��װ·��Ϊ%input% && echo Install successful!) else (echo install Failed)
 

pause