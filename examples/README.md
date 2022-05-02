a short and easy guide on how to setup Kana

## [PM2]("https://pm2.keymetrics.io/", "PM2")

Replace the following in `kanapy.json`:
- `name` - [ Optional ] you can change the name of the process.
- `interpreter` - with the path to your Python Interpreter. ( you can get this path with `which python3`, `python3` here being your python interpreter)

And then, move `kanapy.json` to your [CWD](https://en.wikipedia.org/wiki/Working_directory, "Current Working Directory") and run `pm2 start kanapy.json`.

[ Optional ] run `pm2 save` to save the current processes. And to gracefully start Kana on startup, follow the instructions when you do `pm2 startup`

## [systemd]("https://systemd.io/", "systemd")

Replace the following in `kanapy.service`:
- `Description` - [ Optional ] you can change this to anything
- `WorkingDirectory` - with your [CWD](https://en.wikipedia.org/wiki/Working_directory, "Current Working Directory").
- `ExecStart` - with the path to your Python Interpreter. ( you can get this path with `which python3`, `python3` here being your python interpreter)
- `User` - with your user

And then move `kanapy.service` to the `/etc/systemd/system/`, and run `systemctl start kanapy`.

[ Optional ] run `sudo systemctl enable kanapy` to enable the service. this will allow Kana to start gracefully after a system reboot automatically.
