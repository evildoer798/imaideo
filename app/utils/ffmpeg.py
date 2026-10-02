import shutil, subprocess
from pathlib import Path
def ffmpeg_available(): return shutil.which("ffmpeg") is not None
def make_mock_video(path:Path,label:str,duration:int=2):
 path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+".part")
 if ffmpeg_available():
  cmd=["ffmpeg","-y","-f","lavfi","-i","color=c=0x202b45:s=720x1280:r=24","-vf",f"drawtext=text='{label}':fontcolor=white:fontsize=56:x=(w-text_w)/2:y=(h-text_h)/2","-t",str(duration),"-c:v","libx264","-pix_fmt","yuv420p","-an",str(tmp)]
  try: subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  except (subprocess.CalledProcessError,OSError): tmp.write_bytes(b"MOCK-MP4:"+label.encode())
 else: tmp.write_bytes(b"MOCK-MP4:"+label.encode())
 tmp.replace(path); return path
def compose_videos(inputs:list[Path],output:Path):
 output.parent.mkdir(parents=True,exist_ok=True); tmp=output.with_suffix(output.suffix+".part")
 if ffmpeg_available() and inputs:
  concat=output.with_suffix(".concat.txt"); concat.write_text("\n".join("file '"+str(p).replace("'","'\''")+"'" for p in inputs),encoding="utf-8")
  cmd=["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c:v","libx264","-c:a","aac",str(tmp)]
  try: subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  except (subprocess.CalledProcessError,OSError):
   tmp.write_bytes(b"MOCK-COMPOSE\n"+b"\n".join(p.read_bytes() for p in inputs))
  concat.unlink(missing_ok=True)
 else: tmp.write_bytes(b"MOCK-COMPOSE\n"+b"\n".join(p.read_bytes() for p in inputs))
 tmp.replace(output); return output
