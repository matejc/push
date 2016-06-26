Push
====


Push image created by dockerTools (Nix) to Docker registry v2 without docker daemon


Requirements
------------

- `Nix`, to build image
- `Python 3` and python package `requests2`, to push image


Installation
------------

Install it with `Nix`:

```
$ git clone git://github.com/matejc/push
$ cd ./push
$ nix-build
```

the executable will be `./result/bin/push`


Usage
-----


Generate image:

```
$ nix-build test_image.nix -o image.tar.gz
these derivations will be built:
  /nix/store/xg5g57px4jcr005fbk72s4brsqzpvymw-my-echo-config.json.drv
  /nix/store/fk8giwrv2yysac8ny8449vpf3v5ximny-docker-layer.drv
  /nix/store/ccqql37jb5i5nivc9kb4rz6c2ikf7gkx-runtime-deps.drv
  /nix/store/r21k9nszvi7c6bgvk63358385mj9yrpv-my-echo.tar.gz.drv
building path(s) ‘/nix/store/83045vj35r5cajsk375j54fl2hq7ai3a-my-echo-config.json’
building path(s) ‘/nix/store/yczixa8m6q1jy883rpd8na6rss70q3pm-docker-layer’
Adding contents
/tmp/nix-build-docker-layer.drv-0/layer /tmp/nix-build-docker-layer.drv-0
/tmp/nix-build-docker-layer.drv-0
Packing layer
building path(s) ‘/nix/store/8ap63bzwwzrbmy5k6l98b17xkanz1x56-runtime-deps’
building path(s) ‘/nix/store/x5h6wr918kqwbf3gai43vbavmb3alz6q-my-echo.tar.gz’
Adding layer
Adding meta
Cooking the image
/nix/store/x5h6wr918kqwbf3gai43vbavmb3alz6q-my-echo.tar.gz
```


Pushing:

```
$ ./result/bin/push ./image.tar.gz http://localhost:5000
Calculating digest for /tmp/tmpel5zdnw0/2ed41dd9cfe6f617e954eb0ad910b976ecd30f9ee79d483e1078a79ea246bbf8/layer.tar ...
Pushing sha256:c17b5508357a4d255a0eb98621a496b5abb0d24f5ce5a7abdf6de502f3483fc9 ...
Pushed sha256:c17b5508357a4d255a0eb98621a496b5abb0d24f5ce5a7abdf6de502f3483fc9
Pushing sha256:e7abdadd5695178fa4d9ddae87ef1cba37ff934c8dbc7b1dca5b286070e87efd ...
Pushed sha256:e7abdadd5695178fa4d9ddae87ef1cba37ff934c8dbc7b1dca5b286070e87efd
Push successful!
Removing /tmp/tmpel5zdnw0 ...
```


Pull:

```
$ docker pull localhost:5000/my-echo:latest
latest: Pulling from my-echo
c17b5508357a: Pull complete
Digest: sha256:9b4f58441d2e548e61c9353b874094493e9b797d8a548d1db163f724dc410264
Status: Downloaded newer image for localhost:5000/my-echo:latest
```


And run:

```
$ docker run -ti --rm localhost:5000/my-echo:latest
test hello!
```
