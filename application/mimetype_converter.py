import os
import sys
import subprocess
import magic
from shutil import copyfile
import time
global p
def convert_video(video_input, video_output):
    cmds = ['ffmpeg', '-i', video_input, video_output]
    print "This is input " +video_input
    print "This is output " +video_output
    p = subprocess.Popen(cmds)

    # time.sleep(60)
    #os.killpg(os.getpgid(p.pid), signal.SIGTERM)
    

def convert_audio(audio_input, audio_output):
    cmds = ['ffmpeg', '-i', audio_input, audio_output]
    print "This is input " +audio_input
    print "This is output " +audio_output
    p=subprocess.Popen(cmds)
    #p.kill()    



src = '/home/sheetal/Desktop/mimetype_converter.py'

user_input = raw_input("Enter the path of your file: ")
os.chdir(user_input)
dst=user_input+'/mimetype_converter.py'
print "this is destination"+dst
#copyfile(src,dst)
for subdir, dirs, files in os.walk(user_input):
    for file in files:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file)
        print "The first file is"+file
        print "The file type is " +mime_type
        if mime_type == "video/mp4": 
                print "The Files" +file
                split_file = os.path.splitext(file)[0]
            	print "The Video Files splitted are "+split_file
                convert_video(file,split_file +'.webm')
                time.sleep(60)
                os.remove(file)
                lat_fn=os.rename(split_file+'.webm',split_file)
                print "latest converted audio filename:",split_file
        # print "The Video is converted "
        
	
		


        elif mime_type == "audio/mpeg":
            	print "The Files" +file;
            	split_file = os.path.splitext(file)[0]
            	print "The Audio Files splitted are " +split_file
                convert_audio(file,split_file+'.ogg')
                time.sleep(35)
                os.remove(file)
                lat_fn=os.rename(split_file+'.ogg',split_file)
                print "latest converted audio filename:",split_file
		print "The Audio is converted "
        else:

            print "End of search" 

