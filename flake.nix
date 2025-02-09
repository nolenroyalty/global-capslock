# file: flake.nix
{
  description = "Global Capslock";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix,
    }:
    let
      system = "x86_64-linux";

      pkgs = nixpkgs.legacyPackages.${system};
      inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
      pythonApp = mkPoetryApplication {
        projectDir = ./.;
        preferWheel = true;
        nativeBuildInputs = (pythonApp.nativeBuildInputs or [ ]) ++ [ pkgs.python3Packages.setuptools ];
      }; # This currently will refuse to build complaining about setuptools
    in
    {
      # apps.${system}.default = {
      #   type = "app";
      #   program = "${pythonApp}/bin/global-capslock";

      # };

      devShells.${system}.default = pkgs.mkShell {
        name = "global-capslock";
        packages = with pkgs; [
          poetry
          linuxHeaders
        ];
      };

    };
}
