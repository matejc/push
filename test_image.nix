{ pkgs ? import <nixpkgs> {}}:
let
  buildImage = pkgs.dockerTools.buildImage;
  bash = pkgs.bash;
in
buildImage {
    name = "my-echo";
    tag = "latest";
    contents = bash;
    config = {
      Cmd = [ "${bash}/bin/bash" "-c" "echo test hello!" ];
    };
  }
