
workfolder = Path('./video')
source_folder = workfolder / "source"
inframes_root = workfolder / "inframes"
audio_root = workfolder / "audio"
outframes_root = workfolder / "outframes"
result_folder = workfolder / "result"



def clean_mem():
    # torch.cuda.empty_cache()
    gc.collect()

def get_fps(source_path: Path) -> str:
    print(source_path)
    probe = ffmpeg.probe(str(source_path))
    stream_data = next(
        (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
        None,
    )
    return stream_data['avg_frame_rate']

def download_video_from_url(source_url, source_path: Path, quality: str):
    if source_path.exists():
        source_path.unlink()

    ydl_opts = {
        'format': 'bestvideo[height<={}][ext=mp4]+bestaudio[ext=m4a]/mp4'.format(quality),
        'outtmpl': str(source_path),
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([source_url])

def preProcess(imag_path_l, multiple):
  '''Need to resize images for blurred model (needs to be multiples of 16)'''
  for img_path in imag_path_l:
    im = Image.open(img_path)
    h, w = im.size
    # resize so they are multiples of 4 or 16 (for blurred)
    h = h - h % multiple
    w = w - w % multiple
    im = im.resize((h,w))
    im.save(img_path)

def purge_images(dir):
  for f in os.listdir(dir):
    if re.search('.*?\.jpg', f):
      os.remove(os.path.join(dir, f))

def extract_raw_frames(source_path: Path):
    inframes_folder = inframes_root / (source_path.stem)
    inframe_path_template = str(inframes_folder / '%5d.jpg')
    inframes_folder.mkdir(parents=True, exist_ok=True)
    purge_images(inframes_folder)
    ffmpeg.input(str(source_path)).output(
        str(inframe_path_template), format='image2', vcodec='mjpeg', qscale=0
    ).run(capture_stdout=True)

def make_subfolders(img_path_l, chunk_size):
  i = 0
  subFolderList = []
  source_img_path = Path('/content/EDVR/codes/video/inframes/video_subfolders')
  source_img_path.mkdir(parents=True, exist_ok=True)
  for img in img_path_l:
    if i % chunk_size == 0:
      img_path = source_img_path / str(i)
      img_path.mkdir(parents=True, exist_ok=True)
      subFolderList.append(str(img_path))
    i+=1
    img_name = osp.basename(img)
    img_path_name = img_path / img_name
    shutil.copyfile(img, img_path_name)

  return subFolderList

def remove_subfolders():
  shutil.rmtree('/content/EDVR/codes/video/inframes/video_subfolders', ignore_errors=True, onerror=None)



