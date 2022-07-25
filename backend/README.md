# 
### This is a pretty basic Starlette App to serve the avatar history.
You need to run this separately, and hook up some sort of reverse proxy to 
serve this to the internet. I'll be using [nginx](https://nginx.org) for this particular setup, feel free to use whatever.

I'd also recommend setting up [Cloudflare caching](https://developers.cloudflare.com/cache) (specfically, to the `/static/*` path) to reduce bandwith, and overall avoid any sort of "[DDoS attack](https://en.wikipedia.org/wiki/Denial-of-service_attack)".

### Nginx Setup
- Edit the file `avyh.conf-example` and replace `server_name` with your domain, and `root` with the [CWD](https://en.wikipedia.org/wiki/Working_directory, "Current Working Directory") of `Kanapy`
- Then rename the file and remove `-example` suffix, and copy the file over to `/etc/nginx/conf.d`.
- Run `(sudo) nginx -s reload`, and you should be done.

### Starlette Setup
I'll be using [systemd]("https://systemd.io/", "systemd") to keep the webserver running.
Replace the following in `avyh.service-example`:

- `Description` - [ `Optional` ] you can change this to anything
- `WorkingDirectory` - with your [CWD](https://en.wikipedia.org/wiki/Working_directory, "Current Working Directory").
- `ExecStart` - with the path to your Python Interpreter ( you can get this path with `which python3` ).
- `User` - with your user

And then rename `avyh.service-example` to `avyh.service` and move it to `/etc/systemd/system/`, and run `systemctl start avyh`.

[ `Optional` ] run `(sudo) systemctl enable avyh` to enable the service. this will allow avyh to start gracefully after a system reboot automatically.

# FAQ
- by default this runs on port `1643`. You can change that by,
    - edit the `systemd` file and change the `port` flag in `ExecStart`.
    - edit the `nginx` file and change the `port` in `proxy_pass`

<!-- i don't even know why im writing this, just contact me if you want to run this on your own server for whatever bizzaire reason. -->