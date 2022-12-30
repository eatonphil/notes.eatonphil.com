Basic steps:

```
$ sudo dnf update -y
$ sudo dnf install -y caddy fail2ban git
$ cd /usr/share/caddy
$ sudo rm -rf *
$ cd ~
$ git clone https://github.com/eatonphil/notes.eatonphil.com
```

Tips:

* /usr/share/caddy directory should all be owned by caddy:caddy: `sudo chown -R caddy:caddy /usr/share/caddy`
* If you get permission denied errors, [you should `restorecon` to fix `SELiunx` settings](https://caddy.community/t/caddy-file-server-gives-403-error-forbidden-if-started-with-systemctl/11296/6): `sudo restorecon -r /usr/share/caddy/`
