FROM artixlinux/openrc

COPY . .

# RUN pacman --noconfirm -S pacman-contrib
# RUN curl -o /etc/pacman.d/mirrorlist "https://gitea.artixlinux.org/packagesA/artix-mirrorlist/raw/branch/master/trunk/mirrorlist"
# RUN cp /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
# RUN rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist
# RUN reflector --latest 5 --sort rate --save /etc/pacman.d/mirrorlist
# RUN sed -i '/^#/d' /etc/pacman.d/mirrorlist
# RUN sed -i '/^$/d' /etc/pacman.d/mirrorlist
RUN sed -i '/\[lib32\]/s/^#//g' /etc/pacman.conf
RUN sed -i '/^#Include/s/^#//g' /etc/pacman.conf
RUN pacman --noconfirm --disable-download-timeout -Syu python3 python-pip ffmpeg sox git wine

RUN pip install -r requirements.txt

CMD ["python", "discordBot.py"]