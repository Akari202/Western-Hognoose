{
  description = "Reusable Python helper utilities";

  inputs = {
    # nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    supportedSystems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];

    forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f (import nixpkgs {inherit system;}));
  in {
    packages = forAllSystems (pkgs: {
      default = pkgs.python3.pkgs.buildPythonPackage {
        pname = "western-hognoose";
        version = "0.1.0";
        src = ./.;

        pyproject = true;

        nativeBuildInputs = with pkgs.python3.pkgs; [
          hatchling
        ];

        propagatedBuildInputs = [];

        # nativeCheckInputs = with pkgs.python3.pkgs; [
        #   pytestCheckHook
        #   pytest-mock
        # ];
        #
        # doCheck = true;
        #
        # pytestFlagsArray = ["src/test.py"];
      };
    });
  };
}
