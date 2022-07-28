# 
### This is a pretty basic Starlette App to serve the Avatar History.
This runs alongside the bot with some janky IPC ( in reality the Starlette server has the bot instance ), you need to hook up some sort of reverse proxy to serve this to the internet. I'll be using [nginx](https://nginx.org) for this particular setup, feel free to use whatever.

I'd also recommend setting up [Cloudflare caching](https://developers.cloudflare.com/cache) (specfically, to the `/static/*` path) to reduce bandwith, and overall avoid any sort of "[DDoS **attack**](https://en.wikipedia.org/wiki/Denial-of-service_attack)".

### Nginx Setup:
- Edit the file `examples/avyh.conf-example` and replace `server_name` with your domain, and `root` with the [CWD](https://en.wikipedia.org/wiki/Working_directory, "Current Working Directory") of `Kanapy`
- Then rename the file and remove `-example` suffix, and copy the file over to `/etc/nginx/conf.d`.
- Run `(sudo) nginx -s reload`, and you should be done.

### FAQ:
- by default this runs on port `1643` (This is a random number, so chances of conflict with other ports are low, but never none.). You can change that by,
    - setting a variable `AVYH_PORT` port in the (global) `.env` file.
    - editing the `nginx` file and changing the port (what's after `http://127.0.0.1:`) in `proxy_pass`

<!-- i don't even know why im writing this, just contact me if you want to run this on your own server for whatever bizzaire reason. -->
#
