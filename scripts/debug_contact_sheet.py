import sys,cv2,numpy as np
sys.path.insert(0,'scripts'); sys.path.insert(0,'src')
import benchmark_traffic_light as B, detect_traffic_light as det_base
from pathlib import Path
run=Path(sys.argv[1]); step=int(sys.argv[2]); out=sys.argv[3]
fs=sorted(f for f in (run/'frames').iterdir() if f.is_file() and not f.name.endswith('.jpg'))[::step]
tiles=[]
for f in fs:
    a=B.load_annotation(f); img=cv2.imread(str(run/'frames'/a['image_filename']))
    bb=det_base.find_traffic_light_housing(img)
    g=a['bbox_px']
    if g: x,y,w,h=map(int,g); cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),4)
    if bb: x,y,w,h=map(int,bb); cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),4)
    cv2.putText(img,f"{a['frame_idx']} {a['phase']} {img.shape[1]}x{img.shape[0]}",(10,40),0,1.2,(255,255,0),3)
    tiles.append(cv2.resize(img,(480,int(480*img.shape[0]/img.shape[1]))))
while len(tiles)%3: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)]
cv2.imwrite(out,np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,70])
print(len(fs))
