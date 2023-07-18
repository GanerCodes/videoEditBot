FROM artixlinux/openrc

COPY . /app
WORKDIR /app

RUN sed -i '/\[lib32\]/s/^#//g' /etc/pacman.conf
RUN sed -i '/^#Include/s/^#//g' /etc/pacman.conf
RUN pacman --noconfirm --disable-download-timeout -Syu python3 python-pip ffmpeg sox git wine

RUN pip install --break-system-packages -r requirements.txt

CMD ["python", "discordBot.py"]
