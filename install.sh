#!/bin/bash
echo "[+] SKYRIPPER INSTALL – TURNING KALI INTO DRONE APOCALYPSE"

# 1. System deps
apt update && apt install -y \
    python3-pip python3-tk python3-dev \
    rtl-sdr kismet gnuradio \
    hackrf libhackrf-dev \
    flask leaflet numpy torch torchvision

# 2. Python deps
pip3 install -r requirements.txt

# 3. RTL-SDR blacklist
cat > /etc/modprobe.d/norl.conf << EOF2
blacklist dvb_usb_rtl28xxu
blacklist rtl_2832
blacklist r820t
blacklist rtl_2830
EOF2
update-initramfs -u

# 4. Download SigDigger
wget -O sigdigger/SigDigger.AppImage \
    https://github.com/BatchDrake/SigDigger/releases/download/0.4.0/SigDigger-0.4.0-x86_64.AppImage
chmod +x sigdigger/SigDigger.AppImage

# 5. Download pre-trained model
wget -O models/drone_burst_cnn.pth \
    https://huggingface.co/dronehunter/skyripper-cnn/resolve/main/model.pth

echo "[+] DONE. RUN: ./run.sh"
