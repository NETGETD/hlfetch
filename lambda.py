#!/usr/bin/env python3
import time, sys, math, os, platform, socket, shutil, datetime, select, getpass

try:
    import tty, termios
    has_termios = True
except:
    has_termios = False

ORANGE = "\033[38;5;208m"
RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
ALT_ON = "\033[?1049h"
ALT_OFF = "\033[?1049l"
CLEAR = "\033[2J"
HOME = "\033[H"

raw_logo = """
                 .:::::.                
             -+###*****##*=:            
          .+##+:..      .-*%#-          
         -%#-   -##%*      .+%*.        
        =%*      ..#%+       :%#.       
       .%#         +%%-       -%*       
       =%-        +%#%%.       #%.      
       +%-      .*@+ +%#       *%.      
       -@+     :#%=   *%+     .%#       
        *%-   =%%-    .#%+++  *%-       
         *%= .++.      :#+=::#%-        
          -##=.           :*%*.         
            -*##+=----=+*##+:           
               :-=+++++=-.              
"""

logo = [l for l in raw_logo.splitlines() if l.strip()]
h = len(logo)
w = max(len(l) for l in logo)
logo = [l.ljust(w) for l in logo]

def mv(r,c):
    return f"\033[{r};{c}H"

def get_os():
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=")[1].strip().strip('"')
    except:
        pass
    return platform.system()

def get_cpu():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    name = line.split(":")[1].strip()
                    for s in ["AMD ", "Intel(R) ", "Core(TM) ", "CPU ", " Graphics"]:
                        name = name.replace(s, "")
                    name = name.replace(" with Radeon Graphics", "")
                    return name.strip()
    except:
        pass
    return platform.processor() or "unknown"

def temp():
    try:
        t = float(open("/sys/class/thermal/thermal_zone0/temp").read())
        if t > 1000:
            t /= 1000
        return f"{t:.1f}°C"
    except:
        return "unknown"

def load():
    try:
        l = os.getloadavg()
        return f"{l[0]:.2f} {l[1]:.2f} {l[2]:.2f}"
    except:
        return "unknown"

def get_iface():
    try:
        with open("/proc/net/dev") as f:
            best = None
            best_total = 0
            for line in f:
                if ":" not in line:
                    continue
                name, data = line.split(":",1)
                name = name.strip()
                if name == "lo":
                    continue
                p = data.split()
                total = int(p[0]) + int(p[8])
                if total > best_total:
                    best_total = total
                    best = name
            return best
    except:
        return None

def read_net(iface):
    try:
        with open("/proc/net/dev") as f:
            for line in f:
                if iface in line:
                    p = line.split()
                    return int(p[1]), int(p[9])
    except:
        pass
    return 0,0

def uptime():
    try:
        u = float(open("/proc/uptime").read().split()[0])
        return f"{int(u//3600)}h {int((u%3600)//60)}m"
    except:
        return "unknown"

def ram():
    try:
        m = {}
        for l in open("/proc/meminfo"):
            k,v = l.split(":",1)
            m[k] = int(v.split()[0])
        return f"{(m['MemTotal']-m['MemAvailable'])//1024}MiB / {m['MemTotal']//1024}MiB"
    except:
        return "unknown"

def disk():
    try:
        d = shutil.disk_usage("/")
        return f"{(d.total-d.free)//(1024**3)}GiB / {d.total//(1024**3)}GiB"
    except:
        return "unknown"

def frame(scale, flip):
    out = []
    tw = max(2, int(w * scale))
    cx = w / 2
    for row in logo:
        line = ""
        for j in range(tw):
            x = cx + (j - tw/2) / scale
            xi = int(x + 0.5)
            line += row[xi] if 0 <= xi < w else " "
        if flip:
            line = line[::-1]
        out.append(line)
    return out

def info(down, up):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    return [
        f"OS:       {get_os()}",
        f"Kernel:   {platform.uname().release}",
        f"Arch:     {platform.machine()}",
        f"Uptime:   {uptime()}",
        f"RAM:      {ram()}",
        f"Disk:     {disk()}",
        f"CPU:      {get_cpu()}",
        f"Temp:     {temp()}",
        f"Load:     {load()}",
        f"Net:      ↓ {down:.0f} KB/s ↑ {up:.0f} KB/s",
        f"Time:     {now}",
        f"Host:     {socket.gethostname()}",
        f"User:     {getpass.getuser()}",
        f"Platform: {platform.system()}",
    ]

def footer():
    return [
        "Sector:   C - Lambda Complex",
        "Clearance:Level 3",
        "Device:   Black Mesa Field Notebook",
        "System Status: stable",
    ]

def main():
    cols,_ = shutil.get_terminal_size()

    top = 5
    left = 4
    right = int(cols * 0.55) - 1

    max_w = right - left - 2
    max_info = cols - right - 3

    iface = get_iface()
    prx, ptx = read_net(iface)
    last_measure = time.time()

    down = up = 0

    frames = [frame(0.2 + 0.8 * abs(math.cos(2*math.pi*k/120)), math.cos(2*math.pi*k/120)<0) for k in range(120)]
    draw_w = min(max(len(l) for f in frames for l in f), max_w)

    sys.stdout.write(ALT_ON + HIDE_CURSOR + CLEAR + HOME)

    title = "BLACK MESA RESEARCH FACILITY"
    sub = "Lambda Complex - Field Operations Terminal"

    sys.stdout.write(mv(1,(cols-len(title))//2)+ORANGE+title+RESET)
    sys.stdout.write(mv(2,(cols-len(sub))//2)+ORANGE+sub+RESET)
    sys.stdout.write(mv(3,1)+ORANGE+"─"*cols+RESET)

    lower = top + h + 1
    sys.stdout.write(mv(lower,1)+ORANGE+"─"*cols+RESET)

    ft = lower + 1
    for i,l in enumerate(footer()):
        sys.stdout.write(mv(ft+i,(cols-len(l))//2)+ORANGE+l+RESET)

    hint = "[ Press any key to exit ]"
    sys.stdout.write(mv(ft+len(footer())+1,(cols-len(hint))//2)+ORANGE+hint+RESET)

    sys.stdout.flush()

    try:
        while True:
            if select.select([sys.stdin],[],[],0)[0]:
                break

            now = time.time()
            if now - last_measure >= 0.1:
                rx, tx = read_net(iface)
                dt = now - last_measure

                down = (rx - prx) / 1024 / dt
                up = (tx - ptx) / 1024 / dt

                prx, ptx = rx, tx
                last_measure = now

            for f in frames:
                data = info(down, up)

                for i in range(h):
                    sys.stdout.write(mv(top+i,left)+" "*draw_w)

                for i,l in enumerate(data):
                    sys.stdout.write(mv(top+i,right)+ORANGE+l.ljust(max_info)+RESET)

                for i in range(h):
                    line = f[i]
                    if len(line) > draw_w:
                        cut = (len(line)-draw_w)//2
                        line = line[cut:cut+draw_w]
                    sys.stdout.write(mv(top+i,left)+ORANGE+line.center(draw_w)+RESET)

                sys.stdout.flush()
                time.sleep(0.05)

    finally:
        sys.stdout.write(SHOW_CURSOR+ALT_OFF)

if __name__ == "__main__":
    main()
