{
  description = "";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat/master";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};

      # defaultCompiler = "python311";
      # pythonPackages = pkgs."${defaultCompiler}Packages";

      # use particular python that kodi uses
      pythonPackages = pkgs.kodi.pythonPackages;

      compiler = pythonPackages.python;
    in {
      devShells.default = pkgs.mkShell {
        packages = [
          (compiler.withPackages (ps: with ps; [
            python-lsp-server
          ]))
          self.packages.${system}."kodistubs"
        ];
        nativeBuildInputs = with pkgs; [
          nil # lsp language server for nix
          nixpkgs-fmt
        ];
      };
    });
}