from pathlib import Path
import subprocess, tempfile, math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-2500:])
    return p.stdout


def duration(path):
    s = run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)])
    return float(s.strip())


def font_path():
    candidates = [
        'C:/Windows/Fonts/arialbd.ttf',
        'C:/Windows/Fonts/seguisb.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
    ]
    for path in candidates:
        if Path(path).exists(): return path
    return None


def overlay(text, out):
    im = Image.new('RGBA',(720,1280),(0,0,0,0))
    d = ImageDraw.Draw(im)
    fp=font_path()
    font = ImageFont.truetype(fp, 47) if fp else ImageFont.load_default()
    # Fondo semitrasparente solo dietro al testo; una sola scritta per scena.
    box=d.textbbox((0,0),text,font=font,stroke_width=0)
    w=box[2]-box[0]
    if w > 660:
        font=ImageFont.truetype(fp, 35) if fp else ImageFont.load_default()
        box=d.textbbox((0,0),text,font=font);w=box[2]-box[0]
    x=(720-w)//2; y=105
    d.rounded_rectangle((x-19,y-14,x+w+19,y+67),radius=20,fill=(15,31,20,155))
    d.text((x,y),text,font=font,fill=(255,255,255,255),stroke_width=1,stroke_fill=(20,30,20,230))
    im.save(out)


def endcard(out):
    im=Image.new('RGBA',(720,1280),(20,70,48,255))
    d=ImageDraw.Draw(im)
    fp=font_path()
    font=ImageFont.truetype(fp,39) if fp else ImageFont.load_default()
    logo=Image.open(ASSETS/'logo.jpeg').convert('RGBA')
    logo.thumbnail((400,400))
    im.alpha_composite(logo,((720-logo.width)//2,310))
    t='VIENI A TROVARCI!'
    b=d.textbbox((0,0),t,font=font)
    d.text(((720-(b[2]-b[0]))//2,800),t,font=font,fill='white')
    im.save(out)


def render(video_paths, output, captions, max_seconds=22):
    if not video_paths: raise ValueError('Seleziona almeno un video.')
    output=Path(output)
    with tempfile.TemporaryDirectory(prefix='bottega_reel_') as td:
        tmp=Path(td)
        clips=[]
        # Scene da 2.3 s; alterna le sorgenti per ottenere ritmo anche con due video.
        durations=[duration(p) for p in video_paths]
        available=[max(0.0,d-.2) for d in durations]
        if not any(d>=1.0 for d in available): raise ValueError('Video troppo brevi.')
        playheads=[0.1 for _ in video_paths]
        total=0.0; n=0
        valid=[i for i,d in enumerate(available) if d>=1.0]
        while total < max_seconds-2.0 and n < 12:
            idx=valid[n%len(valid)]
            d=durations[idx]
            seg=min(2.3,max_seconds-2.0-total)
            if seg<0.7: break
            if playheads[idx]+seg>d:
                playheads[idx]=0.1
            seg=min(seg,d-playheads[idx]-0.05)
            if seg<0.7: break
            caption=tmp/f'text_{n}.png'
            overlay(captions[n%len(captions)],caption)
            clip=tmp/f'clip_{n:02d}.mp4'
            zoom=1.06 if n%2 else 1.0
            vf=(f'scale=ceil(720*{zoom}/2)*2:ceil(1280*{zoom}/2)*2:force_original_aspect_ratio=increase,'
                f'crop=720:1280,setsar=1,format=yuv420p,'
                f'fps=30')
            # Uso di una sola sovrimpressione temporizzata, non si accumulano scritte.
            run(['ffmpeg','-y','-ss',str(playheads[idx]),'-t',str(seg),'-i',str(video_paths[idx]),
                 '-loop','1','-framerate','30','-i',str(caption),
                 '-filter_complex',f'[0:v]{vf}[v];[v][1:v]overlay=0:0:shortest=1,format=yuv420p[out]',
                 '-map','[out]','-an','-c:v','libx264','-preset','veryfast','-crf','23',
                 '-r','30','-pix_fmt','yuv420p','-t',str(seg),str(clip)])
            clips.append(clip)
            playheads[idx]+=seg+0.2
            total+=seg;n+=1
        card=tmp/'card.png';endcard(card)
        ending=tmp/'ending.mp4'
        run(['ffmpeg','-y','-loop','1','-framerate','30','-t','2','-i',str(card),'-vf','format=yuv420p',
             '-c:v','libx264','-preset','veryfast','-crf','23','-r','30',str(ending)])
        clips.append(ending)
        manifest=tmp/'concat.txt'
        manifest.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in clips),encoding='utf8')
        silent=tmp/'silent.mp4'
        run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(manifest),'-c','copy',str(silent)])
        audio=ASSETS/'funky_original.wav'
        if audio.exists():
            run(['ffmpeg','-y','-i',str(silent),'-stream_loop','-1','-i',str(audio),
                 '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
                 '-shortest','-movflags','+faststart',str(output)])
        else:
            run(['ffmpeg','-y','-i',str(silent),'-c','copy','-movflags','+faststart',str(output)])
    return output
