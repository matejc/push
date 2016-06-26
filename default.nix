{ pkgs ? import <nixpkgs> {} }:
let
  python35Packages = pkgs.python35Packages;
  stdenv = pkgs.stdenv;
in
python35Packages.buildPythonPackage rec {
  name = "push-${version}";
  version = "0.0.1";

  src = { outPath = ./.; };
  # src = pkgs.fetchFromGitHub {
  #   owner = "matejc";
  #   repo = "push";
  #   rev = version;
  #   sha256 = "";
  # };

  propagatedBuildInputs = [ python35Packages.requests2 ];

  meta = {
    homepage = "http://github.com/matejc/push/";
    description = "Utility to push tar.gz docker images to v2 registry";
    license = stdenv.licenses.bsd3;
    maintainers = with stdenv.maintainers; [ matejc ];
  };
}
